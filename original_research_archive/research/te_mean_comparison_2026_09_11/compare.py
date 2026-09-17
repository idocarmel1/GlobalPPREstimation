"""Read-only TE comparison using saved balanced models and source diet matrices.

Run from any directory with Python containing numpy, pandas, openpyxl, sympy.
Writes only this study's results.json and results.md; never runs an exporter.
"""
from pathlib import Path
import hashlib
import json
import sys
import warnings

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "PPREstimation"))
from ModelData import ModelData
from utils import remove_cycles


def weighted(values, weights):
    return float(np.average(values, weights=weights)) if np.sum(weights) > 0 else None


def decomposition(diet, producer, detritus):
    """Combined Ap/Ad from EwE Lindeman, with CalcPathsAndCycles=False.

    Real groups only; the imported-diet column is deliberately absent. EwE
    renormalizes internally sourced fractions across levels afterwards. Match
    its matrix-power cutoff (1e-6), stopping rule (1e-5), and group-count cap.
    Double precision here instead of VB Single. No claim of binary identity.
    """
    n = len(diet)
    living = ~detritus
    ap = np.zeros((n + 1, n))
    ad = np.zeros_like(ap)
    ap[0] = producer.astype(float)
    power = diet.copy()
    for k in range(n):
        next_power = power @ diet
        ap[k + 1, living] = (power @ producer.astype(float))[living]
        ad[k + 1, living] = power[np.ix_(living, detritus)].sum(axis=1)
        stop = ap[k + 1, living].sum() + next_power[np.ix_(living, detritus)].sum()
        power[living] = np.where(next_power[living] > 1e-6, next_power[living], 0)
        if stop < 1e-5:
            break
    # EwE sums through n levels for normalization; an n+1 consumer path is
    # impossible without cycles. All selected models terminate before that cap.
    total = (ap[:n] + ad[:n]).sum(axis=0)
    normalize = living & (total > 0) & (total < 1)
    ap[:n, normalize] /= total[normalize]
    ad[:n, normalize] /= total[normalize]
    result = ap + ad
    result[0, detritus] = 1
    assert np.max(ap[n] + ad[n]) < 1e-6, "EwE group-count truncation reached; inspect before reporting"
    return result, total, k + 2


def aggregate(diet, q, catch, flow_det, resp, migration, producer, detritus):
    fractions, internal_share, nlevels = decomposition(diet, producer, detritus)
    predation = (diet * q[:, None]).sum(axis=0)
    # Official cEcoPathModel.UpdateExportCatch: Ex = catch + net migration.
    # Official cEcoNetwork.Lindeman: H = predation + Ex + FlowToDet + Resp.
    # Official cNetworkManager.TotTransferEfficiency: (predation + catch)/H.
    # Biomass accumulation is NOT an export in these EwE routines.
    throughput = predation + catch + migration + flow_det + resp
    numerator = fractions[1:4] @ (predation + catch)
    denominator = fractions[1:4] @ throughput
    assert np.all(denominator > 0)
    efficiencies = numerator / denominator
    assert np.all((efficiencies >= 0) & (efficiencies <= 1))
    return {
        "level_II_III_IV": efficiencies.tolist(),
        "arithmetic": float(efficiencies.mean()),
        "geometric": float(np.prod(efficiencies) ** (1 / 3)),
        "numerators": numerator.tolist(),
        "throughputs": denominator.tolist(),
        "nlevels": nlevels,
        "minimum_internal_source_share": float(internal_share.min()),
        "fraction_sum_max_error": float(np.max(np.abs(fractions.sum(axis=0) - 1))),
    }


def checks():
    # Known three-transfer chain: producer -> herbivore -> carnivore -> top.
    diet = np.zeros((4, 4)); diet[1, 0] = diet[2, 1] = diet[3, 2] = 1
    q = np.array([0., 100., 10., 1.])
    catch = np.array([0., 0., 0., .1])
    flowdet = np.array([0., 90., 9., .9])
    result = aggregate(diet, q, catch, flowdet, q*0, q*0,
                       np.array([True, False, False, False]), np.zeros(4, bool))
    assert np.allclose(result["level_II_III_IV"], .1)
    # Omnivore gets 40% basal food and 60% herbivores, giving TL II/III
    # fractions 0.4/0.6. A fourth row represents detritus.
    diet[2] = [0.4, 0.6, 0, 0]; diet[3] = 0
    fractions, _, _ = decomposition(diet, np.array([1,0,0,0], bool), np.array([0,0,0,1], bool))
    assert np.allclose(fractions[1:3, 2], [.4, .6])
    assert weighted([0.1, 0.2], [0, 0]) is None
    assert np.isclose(weighted([0.1, 0.2], [1, 3]), .175)


def main():
    checks()
    selection = json.loads((ROOT / "data/atlas_selection.json").read_text(encoding="utf-8"))["units"]
    results = []
    for ecosystem, selected in selection.items():
        model = selected["default_model"]
        workbook = ROOT / "PPREstimation/output/top10" / (model + ".xlsx")
        source = ROOT / "PPREstimation/real_models/global_cover_jsons" / (model + ".json")
        health = pd.read_excel(workbook, sheet_name="model_health").iloc[0]
        row = {"ecosystem": ecosystem, "model": model,
               "workbook_sha256": hashlib.sha256(workbook.read_bytes()).hexdigest(),
               "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
               "mass_balanced": bool(health.model_input_is_model_balanced),
               "saved_p_relative_residual": float(health.model_input_p_max_rel_residual),
               "saved_q_relative_residual": float(health.model_input_q_max_rel_residual)}
        results.append(row)
        if not row["mass_balanced"]:
            row["excluded_reason"] = "Fails saved underlying Ecopath mass balance; not rebalanced for this study."
            continue
        g = pd.read_excel(workbook, sheet_name="groups_df").set_index("seq")
        real = g.group_type.ne("Import")
        consumer = g.group_type.eq("Regular")
        # Independently recheck saved identities for every real model group.
        production = g['catch'] + g.predation + g.biomass_accum + g.net_migration + g.M0
        consumption = production + g.egestion + g.respiration
        assert np.all(np.isclose(production[real], g.p[real]))
        assert np.all(np.isclose(consumption[real], g.q[real], atol=1e-6))
        te = (g.p/g.q).fillna(1) * (1-g.M0/g.p).fillna(1)
        assert np.all(np.isfinite(te[consumer]))
        assert np.allclose(te[consumer], (g['ge']*g['ee'])[consumer])
        row.update(consumer_groups=int(consumer.sum()),
                   equal_weight=float(te[consumer].mean()),
                   catch_weight=weighted(te[consumer], g['catch'][consumer]),
                   biomass_weight=weighted(te[consumer], g.biomass[consumer]),
                   consumer_catch_total=float(g['catch'][consumer].sum()))
        model_data = ModelData(str(source))
        with warnings.catch_warnings(record=True) as caught:
            D = ModelData.validate_DC(model_data.DC, model_data.groups_data, normalize=True)
        row["diet_normalization_warnings"] = [str(w.message) for w in caught]
        D = D.reindex(index=g.index, columns=g.index).fillna(0)
        reconstructed_predation = D.mul(g.q, axis=0).sum(axis=0)
        assert np.allclose(reconstructed_predation[real], g.predation[real])
        row["predation_reconstruction_max_absolute_error"] = float(np.max(np.abs(reconstructed_predation[real]-g.predation[real])))
        r = g[real]
        diet = D.loc[r.index, r.index].to_numpy()
        vecs = [r[c].to_numpy(float) for c in ['q','catch','flow_to_det','respiration','net_migration']]
        producer, detritus = r.group_type.eq('PP').to_numpy(), r.group_type.eq('DET').to_numpy()
        row["trophic_EwE_cycles_off"] = aggregate(diet, *vecs, producer, detritus)
        # Independent full-series check without EwE's small-path truncation.
        basal = (producer | detritus).astype(float)
        internal = np.linalg.solve(np.eye(len(r))-diet, basal)
        f = basal.copy(); exact = []
        for level in range(4):
            exact.append(np.divide(f, internal, out=np.zeros_like(f), where=internal>0))
            f = diet @ f
        pred = (diet*vecs[0][:,None]).sum(axis=0)
        H = pred+vecs[1]+vecs[2]+vecs[3]+vecs[4]
        F = np.array(exact)[1:4]
        exact_te = (F@(pred+vecs[1]))/(F@H)
        row["full_series_level_TE"] = exact_te.tolist()
        row["truncation_TE_max_abs_difference"] = float(np.max(np.abs(exact_te-row['trophic_EwE_cycles_off']['level_II_III_IV'])))
        assert row['truncation_TE_max_abs_difference'] < 1e-4
        # Sensitivity uses the PROJECT'S deterministic minimum-flow cycle
        # removal, not a port of EwE's optional cycle routine.
        z = D.mul(g.q, axis=0)
        z0 = remove_cycles(z, new=False)
        removed = z-z0
        assert np.all(z0.to_numpy() >= 0)
        assert np.allclose(removed.sum(axis=0), removed.sum(axis=1))
        import networkx as nx
        assert nx.is_directed_acyclic_graph(nx.from_numpy_array(z0.to_numpy(), create_using=nx.DiGraph))
        d0 = z0.div(z0.sum(axis=1), axis=0).fillna(0)
        q0 = z0.sum(axis=1).loc[r.index].to_numpy(float)
        row["trophic_project_cycle_removal_sensitivity"] = aggregate(
            d0.loc[r.index,r.index].to_numpy(), q0, *vecs[1:], producer, detritus)
        print(ecosystem, ' '.join(f'{100*row[key]:.3f}' if row[key] is not None else 'NA'
              for key in ['equal_weight','catch_weight','biomass_weight']),
              'TL', row['trophic_EwE_cycles_off']['level_II_III_IV'], flush=True)
    (HERE / "results.json").write_text(json.dumps(results, indent=2, allow_nan=False), encoding="utf-8")
    lines = ["# Consumer TE comparison, 11 September 2026", "", "All numbers are percentages. See methodology.md for definitions and limitations.", "",
             "| Ecosystem/model | Equal | Catch | Biomass | Trophic geometric, cycles removed (project) | Trophic geometric, cycles retained (EwE default) | Trophic arithmetic, cycles removed | Trophic arithmetic, cycles retained |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for row in results:
        if not row['mass_balanced']:
            lines.append(f"| {row['model']} | Excluded | Excluded | Excluded | Excluded | Excluded | Excluded | Excluded |")
            continue
        values = [row[k] for k in ['equal_weight','catch_weight','biomass_weight']]
        values += [row['trophic_project_cycle_removal_sensitivity']['geometric'], row['trophic_EwE_cycles_off']['geometric'],
                   row['trophic_project_cycle_removal_sensitivity']['arithmetic'], row['trophic_EwE_cycles_off']['arithmetic']]
        lines.append('| '+row['model']+' | '+' | '.join('Unavailable' if v is None else f'{100*v:.2f}' for v in values)+' |')
    (HERE / "results.md").write_text('\n'.join(lines)+'\n', encoding="utf-8")
    print('Verified toy chain, omnivory, all included balance identities, source-flow agreement, and truncation sensitivity.')


if __name__ == '__main__':
    main()
