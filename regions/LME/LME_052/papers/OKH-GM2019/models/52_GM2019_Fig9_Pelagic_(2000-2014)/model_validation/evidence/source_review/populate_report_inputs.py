"""Create report arithmetic/manuscript from frozen model and adopted mapping rows."""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import math
import re
import sys

E = Path(__file__).resolve().parent
R = E.parents[3]
REGION = E.parents[1]
C = REGION / "models/52_GM2019_Fig9_Pelagic_(2000-2014)"
A = C / "assumption_variants/adopted_balanced_20261003"
I = C / "research_20261003/integration"
sys.path.insert(0, str(R / "tools"))
from validation_percentage_format import format_percent as pct


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def short(v):
    if v is None:
        return "absent"
    if str(v) == "-9999":
        return "unknown"
    if isinstance(v, bool) or str(v) in ("true", "false"):
        return str(v).lower()
    try:
        return format(float(v), ".8g")
    except (ValueError, TypeError):
        return str(v)


def link(label, path):
    return {"text": label, "target": path.relative_to(REGION).as_posix()}


def readable_reason(value):
    value = re.sub(r"\b[MW]\d+\b", "", value)
    value = re.sub(r"\b(source|Source)(\d+)\b(?![.%])", r"\1 group \2", value)
    value = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", value)
    value = re.sub(r"\b(Table|Figure|Assumed|assumed)(?=\d)", r"\1 ", value)
    value = re.sub(r"2019p(\d+)", r"2019 p. \1 ", value)
    value = re.sub(r"\bp(\d+)", r"p. \1", value)
    replacements = {
        "warmseason":"warm season", "pooledwet":"pooled wet", "equalwet":"equal wet", "externalproxy":"external proxy",
        "preyfactor":"prey factor", "EEheadroom":"EE headroom", "directspecies":"direct species",
        "directannualamount":"direct annual amount", "Otherplankton":"Other plankton", "Othernekton":"Other nekton",
        "source1.7%":"source 1.7%", "source2.2%":"source 2.2%", "total minus1.7968":"total minus 1.7968",
        "2:1carbon":"2:1 carbon", "Figurewet-relative":"Figure wet-relative", "rounded87.9%":"rounded 87.9%",
        "2019total320":"2019 total 320", "importedsourceunknown":"imported source unknown", "inside13.2%":"inside 13.2%",
        "Figurewithin":"Figure within", "preservedunallocated":"preserved unallocated", "smallpollock":"small pollock",
        "scaled0.2%":"scaled 0.2%", "toprinted":"to printed", "Figurepath":"Figure path",
        "explicitdecimal":"explicit decimal", "2019aggregate":"2019 aggregate ", "residualstage":"residual stage",
        "IIIplanktivory/IVnektonfeeding":"III planktivory/IV nekton feeding",
    }
    for old,new in replacements.items():
        value = value.replace(old,new)
    value = re.sub(r"(\d+(?:\.\d+)?)%", lambda m:pct(m.group(1)), value)
    return re.sub(r" +", " ", value).strip()


def matrix_review(method, native, names):
    d = read(A / "diagnostics" / f"{method}_full_return.json")
    assert d["model_sha256"] == native["exact_input_sha256"]
    s = d["SPPR"]
    assert len(set(s["index"])) == len(s["index"])
    assert len(set(s["columns"])) == len(s["columns"])
    assert len(s["data"]) == len(s["index"])
    negatives = []
    finite = 0
    for gid, row in zip(s["index"], s["data"]):
        assert len(row) == len(s["columns"])
        for source, value in zip(s["columns"], row):
            assert isinstance(value, (int, float)) and math.isfinite(value)
            finite += 1
            if value < 0:
                negatives.append({"source_id": source, "source_name": names[source], "group_id":gid,"group_name":names[gid],"value":value})
    columns = {x["source_id"] for x in negatives}
    assert len(columns) == d["report"]["divergence"]["n_negative_sources"]
    return d, {"method": method, "model_sha256": d["model_sha256"],"orientation":"group rows by basal-source columns", "row_ids":s["index"],"column_ids":s["columns"],"finite_cells":finite,"negative_entries":negatives,"strict_comparison":"value < 0 without display rounding"}


def rule_rows(audit, component, denominator):
    labels = {
        "M1":"Explicit source assignment to a named taxonomic group.",
        "M3":"Unambiguous documented fit to the source group or stage union.",
        "M4":"Supported extension from listed regional representatives.",
        "M6":"Partial or conflicting ecological fit with a material source mismatch.",
        "M9":"An inferred eligible regional group set with explicit membership assumptions.",
        "M10":"Broad reporting category approximated across a plausible source group set.",
        "M11":"Closest represented ecological or taxonomic analogue with habitat or lineage mismatch.",
        "M12":"Evidenced assignment transferred from the prior whole-Sea model through a group crosswalk.",
        "M8":"No meaningful represented assignment or complete candidate set.",
        "W1":"One reviewed group receives the whole taxon; no numerical split.",
        "W9":"Complete source biomass after unusable native catch, with equal catchability and fixed composition assumed.",
        "W11":"Explicit last-resort equal allocation when source catch is unavailable and unrelated pool biomass is not a defensible composition proxy.",
        "W8":"No defensible numerical allocation without a meaningful candidate set."
    }
    key = "membership" if component == "membership" else "allocation"
    totals = defaultdict(float)
    for row in audit:
        totals[(row[key+"_rule"], row[key+"_confidence"])] += row["simple_ppr_tC"] or 0
    assert abs(sum(totals.values()) - denominator) < max(1e-6, denominator*1e-12)
    ordered = sorted(totals.items(), key=lambda x:(-x[1],x[0]))
    return [[labels[k[0]],k[1],pct(100*v/denominator)] for k,v in ordered]


def main():
    s = read(E / "static_report_content.json")
    ledger = read(A / "source_to_final_ledger.json")
    native = read(A / "native_reload_result.json")
    food = read(A / "food_component_ledger.json")
    flows = read(A / "carbon_food_flows.json")
    figure = read(C / "assumption_variants/researcher_readings_20261003/carbon_reconstruction.json")
    mapping = read(I / "mapping_summary.json")
    audit = read(I / "taxon_audit.json")
    regional_science = read(I / "regional_science_verification.json")
    alternatives = read(A / "alternative_hypotheses.json")
    sensitivity = read(A / "sensitivity/F62_summary.json")
    exact_hash = hashlib.sha256((A / "model.json").read_bytes()).hexdigest()
    assert ledger["exact_final_sha256"] == native["exact_input_sha256"] == exact_hash
    assert native["main_is_model_balanced"] and native["catch_zero"] and native["migration_zero"]
    assert len(audit) == mapping["taxa_count"] == len({x["taxon"] for x in audit})
    groups = ledger["group_parameters"]
    names = {x["group_id"]:x["group"] for x in groups}
    names[23] = "External food import"
    diagnostics = {}
    inspections = []
    for m in ("GE", "TE", "With_Egestion"):
        d, inspected = matrix_review(m, native, names)
        diagnostics[m] = d
        inspections.append(inspected)
    (E / "diagnostic_matrix_inspection.json").write_text(json.dumps(inspections,ensure_ascii=False,indent=2),encoding="utf-8")
    pending = not (E / "map_alignment_confirmed.json").exists()
    s["opening"] = ("Pending alignment draft. " if pending else "") + "This record evaluates the reconstructed 2000–2014 epipelagic food web for LME 052. The native model balances. Its diagnostic warnings, source-number hypotheses and assumption-dependent catch mappings remain scientific limitations for researcher review."
    fields = s["validation_fields"]
    imports = sum(float(v.get("23",0)) for v in flows.values())
    detrow = next(x for x in native["rows"] if x["group_id"] == 22)
    gs = [x["GS"] for x in native["rows"] if x["trophic_info"] == "Regular"]
    fields["Model extraction"] = [
        "All 21 living Figure production values are retained. Twelve arrow magnitudes are reduced by factors of 10 or 100 as Very low confidence scientific decimal hypotheses. They are not demonstrated author typographical errors. Supporting diets repair hyperiid, salmon and jellyfish intake; external food and prey-category allocations are explicit.",
        f"Carbon stocks use source wet stocks and body factors. Microbes share assumed PB = 20 yr⁻¹; Protozoa wet/carbon = 10 is an allowed best guess. Living BA = 0; catch and migration = 0. Standard LIM solves GS freely (range {min(gs):.4f}–{max(gs):.4f}); no default GS is inserted. All mortality and egestion enter detritus; detritus import/export = 0 and BA is positive residual.",
        "Regional unit bridge: saved wet-equivalent SPPR = native carbon SPPR × 9 / the assigned group's source wet/C factor. Regional and map PPR multiply wet catch by that coefficient and divide by 9 exactly once. Native carbon budgets and raw coefficients remain unchanged.",
        [link("Regional currency bridge audit",I/"carbon_unit_bridge.json")],
        [link("Every article departure and native input change",REGION/s["departures_filename"])," | ",link("Exact source to final ledger",A/"source_to_final_ledger.json")]
    ]
    for m in ("GE","TE"):
        report = diagnostics[m]["report"]
        div = report["divergence"]
        entry = ["WARN - four apex groups have EE = 0: Predatory salmon (17), Baleen whales (18), Predatory fish (20), Predatory mammals (21).", "No negative SPPR entries across the basal-source columns.", f"rho_living = {div['rho_living']:.4f}"]
        if m == "GE":
            entry.append(f"b = {div['b']:.4f}")
        entry.append(f"Detritus (22): SPPR = {div['sppr_det']['22']:.4f}")
        if m == "TE":
            entry.append(f"TE gives those four apex groups zero coefficients despite positive consumption. Their fractionally assigned catch is {regional_science['terminal_assigned_catch_tonnes']:,.2f} wet t ({pct(regional_science['terminal_assigned_catch_percent'])} of 2019 landings), representing {pct(regional_science['terminal_assigned_simple_ppr_percent'])} of independent classic PPR. Finite numerical mapping coverage is not scientific coverage.")
        entry.extend(["Model and system balance checks pass; living network converges.", [link("Full source matrix and diagnostic return",A/"diagnostics"/f"{m}_full_return.json")]])
        fields[m+" diagnostics"] = entry
    fields["Other"] = [f"With Egestion is WARN with finite coefficients and convergent living network (rho_living = {diagnostics['With_Egestion']['report']['divergence']['rho_living']:.4f}). Zero model catch makes the native catch footprints zero; regional catch PPR is a separate application. External food totals {imports:.6g} million tC/yr. Balance does not validate the decimal hypotheses, residual food compositions, stage splits or proxy chemical factors.", "Independent import checks report no errors but flag unusual P/Q for copepods (0.641), euphausiids (0.638), chaetognaths (0.553), salmon (0.778), jellyfish (0.614), baleen whales (0.00467) and predatory mammals (0.00960). GS remains unknown in exported inputs; EwE's default 0.2 and its resulting indeterminate checks differ from the native LIM solution. Detritus residual accumulation is 374.43 million tC/yr, 24.16 times its assumed inventory per year; it does not establish stationary stock or measured burial. Annual PPR and map use remain provisional; production eligibility is false, Monte Carlo and global checks are NOT_RUN.", [link("Regional unit bridge and terminal-group exposure",I/"regional_science_verification.json")," | ",link("Import audit actual returns",A/"export_tool_results.json")]]
    d = mapping["total_known_simple_ppr_tC"]
    missing_tl = [r for r in audit if r["tl"] is None]
    unresolved_parts = []
    groups_of_reason = defaultdict(list)
    for r in mapping["unresolved"]:
        groups_of_reason[r["reason"]].append(r["taxon"])
    for reason,taxa in groups_of_reason.items():
        unresolved_parts.append(", ".join(taxa) + ": " + reason)
    verylow = defaultdict(list)
    for row in audit:
        if row["overall_confidence"] == "Very low":
            verylow[row["reason"]].append(row["taxon"])
    assert sum(len(v) for v in verylow.values()) == next(x["taxa"] for x in mapping["confidence"] if x["confidence"]=="Very low")
    s["coverage"] = {
        "reference":f"Reference: {mapping['year']} {mapping['catch_basis']}; all source scope, all catch labels, no model group filter.",
        "inventory":f"22 source groups including detritus, plus 1 computational import; {len(audit)} catch taxa.",
        "total":f"Simple-chain PPR totals {d:,.2f} t C in {mapping['year']}.",
        "missing":f"{len(missing_tl)} labels lack a classic coefficient/TL; all have zero 2019 landings and zero annual PPR. Unknown TL and coefficients remain ?." if missing_tl else "",
        "method":"Method: protected independent simple trophic-chain coefficients.",
        "appendix_link":[link("All taxon mappings and descriptive Sources sheet",REGION/"52_GM2019_Fig9_Pelagic_balanced_(2000-2014)_taxon_mapping_appendix.xlsx")],
        "membership_evidence":["Membership evidence: source Table 3, Figure 9 and source prose; prior whole-Sea taxonomy crosswalk where retained; explicitly weak habitat or lineage analogues. ",link("All taxon decisions",I/"taxon_audit.json")],
        "weight_evidence":["Weights and assumptions: native catch is unavailable as a composition measure. Complete source wet biomass supplies eligible multi-group proportions at Medium allocation confidence, with equal catchability and fixed source-era composition. Gastropoda, Miscellaneous aquatic invertebrates and Mollusca use explicit equal-half, equal-sixth and equal-thirds last-resort allocations because unrelated source pool biomasses do not provide a defensible composition proxy. Carbon coefficients use the assigned group's source body factor, including transfers to weak analogues. ",link("Complete allocation evidence",I/"allocation_ledger.json")],
        "uncertainty":"Unresolved taxa: " + " ".join(unresolved_parts) + f" Very low assignments cover {pct(mapping['very_low_catch_percent'])} of landings and {pct(next(x['simple_ppr_percent'] for x in mapping['confidence'] if x['confidence']=='Very low'))} of independent simple-chain PPR. Numerical coefficient coverage of {mapping['mapping_coverage_percent']:.7f}% does not establish ecological catch-footprint validity; terminal EE = 0 groups receive zero TE coefficients.",
        "confidence_rows":[[x["confidence"],x["taxa"],pct(x["catch_percent"]),pct(x["simple_ppr_percent"])] for x in mapping["confidence"]],
        "membership_rows":rule_rows(audit,"membership",d),
        "allocation_rows":rule_rows(audit,"allocation",d),
        "very_low_rows":[["; ".join(sorted(taxa)),readable_reason(reason)] for reason,taxa in sorted(verylow.items(),key=lambda x: min(x[1]))]
    }
    # Assemble the article-departures document around scientifically distinct changes.
    s["departures_opening"].append(f"The exact native file reloads with main balance True. All 21 living groups have zero biomass accumulation and finite nonnegative respiration, egestion and other mortality. GE, TE and With Egestion return WARN rather than an unqualified scientific pass. Native file SHA256: {exact_hash}.")
    policy = [
        ["Common currency and area", "Source wet stocks and million tC/yr diagram flows", "Native tC/km² stocks and tC/km²/yr flows; effective area 1,544,000 km²", "The area is implied by primary production 694.8 million tC/yr and 450 gC/m²/yr. Prey-specific wet/C conversion is required; the area is not measured author GIS."],
        ["Table 3 carbon-stock header", "The printed stock-column heading includes per year", "Treat stock as million tonnes C, without yr⁻¹", "Biomass and body conversion establish a stock; production and PB carry the time dimension. Original header is preserved, correction is declared."],
        ["Table 7.1 intermediate factor headings", "Intermediate headings suggest carbon/dry ratios", "Use the numerical dry/wet intermediate fractions and independently coherent final wet/C factors", "The source Other row remains discrepant. Proxy factors for absent prey are assumptions rather than a correction that proves every row."],
        ["Microbial stock split", "Pooled carbon B 6.8 million tC; wet B 64 million t; PB 20; separate B unknown", "Bacteria B 5.055; Protozoa B 1.755 million tC; PB 20 for both; implied wet B 65.067 million t", "Production-proportional split preserves P 101.1 + 35.1 = 136.2. Carbon B differs by 0.01 million tC; wet B rises by 1.067 million t. Separate stocks/rates and protozoan chemistry are assumptions."],
        ["Protozoa wet/C", "No unambiguous group-specific measurement", "10 wet tonnes per tonne C", "Explicit best guess. Dissertation page 60 contextual ratio 270/27 is ambiguous because the sentence literally says bacteria."],
        ["Catch and migration", "Not complete source Ecopath inputs", "Catch, immigration and emigration 0 in every group", "Authorized closed migration / zero-catch reconstruction. It does not establish regional catch sustainability or absence of actual animal movements."],
        ["Living BA", "Unknown/free in source reconstruction", "0 in all 21 living groups", "Sustainable-stock best guess under zero catch. This avoids depletion as a numerical repair; it is not measured annual accumulation."],
        ["GS", "Source carbon GS unknown; inherited handling could insert 0.2", f"Unknown in input; actual LIM solves {min(gs):.8g}–{max(gs):.8g} across 20 consumers", "Standard GS bounds 0.10–0.35. The source calorie assimilation 0.70 is not an observed carbon GS 0.30."],
        ["Mortality and unassimilated routing", "Fate of these flows unspecified", "All M0 and U to sole Detritus pool", "Explicit detrital recycling boundary assumption; no alternate sink or export."],
        ["Detritus stock and accumulation", "Detritus B unknown; consumption 310 million tC/yr", f"Assumed B 310/20 = 15.5 million tC; BA {detrow['BA']*1.544:.8g} million tC/yr", "The stock assumes 18.25-day feeding-inventory turnover. Residual BA is 24.16 times assumed inventory each year under zero import/export and all M0/U routing. This large nonsteady accumulation is not measured storage, burial or a stationary detritus stock."],
        ["External food", "Figure-only import 0; unallocated source food remains", f"13.357614 million tC/yr across native imports; synthetic group 23", "Food categories absent from the 22 groups and unknown residual food are retained, with declared proxy factors and allocations. Their origins and donor-web PPR remain uncertain."],
        ["Diet completion", "Figure-only arrows and incomplete prose fractions", "Full source wet totals retained; exact carbon DC derived from completed prey flows", "Unknown food is explicitly imported, not dropped by renormalizing a partial diet. Runtime normalization is disabled; raw and loaded DC totals agree."],
        ["Figure F62 and F67", "F62 disputed 0.023 or 0.025; F67 formerly unread", "F62 0.023 preferred; 0.025 tested. F67 0.05", "Accepted human readings. They do not resolve tentative arrow routes. Values are million tC/yr."],
        ["Figure F77", "Earlier endpoint prey 19", "Prey 15 → consumer 20, 0.01 million tC/yr", "Source-path correction accepted independently of balancing. Source raster and prior extraction remain available."],
        ["Synthetic runtime import group", "No author biological compartment", "Native helper group 23 with dummy B = 1 tC/km² supplies imported food", "Runtime P and Q equal import flux and are computational completion values, not observed biological rates. They are excluded from living source-group counts and source production sums."],
        ["Predatory fish wet/C", "Table 3 alignment assigns 5.43 wet/C to this small pooled fish group", "5.43 wet tonnes per tonne C", "The source row association is tentative; chemistry transfers also affect catch taxa mapped to this weak pelagic analogue."],
        ["EE and zero apex rows", "Source EE unavailable", "EE derived from D/P with BA 0; groups 17,18,20,21 EE 0", "Finite physical bounds are checked. TE assigns these apex groups zero SPPR despite consumption; that software convention is a material limitation."],
    ]
    blocks = [{"heading":"Adopted assumptions and their consequences","paragraphs":["These changes complete a generalized production-flow scheme as a native mass-balance input. Preserved production values constrain the repairs, but balance alone does not establish author intent. Every table value below is rounded for reading; linked JSON ledgers retain the exact values."],"headers":["Change","Article or baseline","Adopted value","Evidence uncertainty and consequence"],"rows":policy,"widths":[1.0,1.6,1.5,2.85],"font_size":9}]
    arrowrows = [[x["flow_id"],f"{names[x['prey']]} ({x['prey']}) → {names[x['consumer']]} ({x['consumer']})",short(x["before"]),short(x["after"]),x["routing_status"]] for x in ledger["article_arrow_changes"]]
    blocks.append({"heading":"Twelve assumed arrow magnitude corrections","paragraphs":["The following source labels are divided by 10 or 100. Their source readings remain unchanged in the preserved extraction. Production-availability closure at zero catch, migration and living BA motivates the choices. No independent source identifies these decimals as errors, and three routes are visually clear. These are Very low confidence scientific hypotheses.","Rejected alternatives include leaving all arrow magnitudes unchanged, using substantial negative stock accumulation, changing verified production boxes, reversing clear arrow heads, and dropping source groups. The source-fed unrepaired case is algebraically balanced but has negative mortality or EE above 1; the accepted case avoids those failures. Sensitivity does not turn the selected decimal hypothesis into source proof."],"headers":["Arrow","Prey to consumer","Source million tC/yr","Adopted million tC/yr","Route evidence"],"rows":arrowrows,"widths":[0.5,2.25,1.15,1.15,1.9],"font_size":9})
    baseline_q = defaultdict(float)
    for f in figure["flows"]:
        baseline_q[f["consumer_id"]] += float(f["adopted_carbon_flow"])
    group_rows = []
    for g in groups:
        n = g["group_id"]
        table = g["source_table"] or {}
        p = g["final_native_parameters"]
        group_rows.append([f"{names[n]} ({n})",short(table.get("biomass_carbon_million_t")),format(g["adopted_B_million_tC"],".6g") if g["adopted_B_million_tC"] is not None else "unknown",short(g["source_figure_production"]),format(baseline_q.get(n),".6g") if n in range(2,22) else "not food intake",format(g["adopted_Q_million_tC"],".6g") if g["adopted_Q_million_tC"] is not None else "unknown",short(table.get("pb_per_year")),format(p["PB"],".6g")])
    blocks.append({"heading":"Source and adopted stocks production intake and rates","paragraphs":["B, P and Q in this table use million tonnes C and years. Source B is the rounded carbon column; adopted B generally derives directly from wet B divided by the primary body factor. Figure production P is held exactly for every living group. PB is derived from that P and adopted B rather than forcing rounded Table 3 stock, production and PB to be simultaneously exact. Producer/detritus runtime self-throughput is distinct from biological food intake."],"headers":["Group","Source B C","Adopted B C","Figure P C/yr","Figure Q C/yr","Adopted Q C/yr","Source PB","Native PB"],"rows":group_rows,"widths":[1.4,0.72,0.78,0.8,0.83,0.83,0.7,0.89],"font_size":8.5})
    blocks.append({"heading":"Recovering the three failed energy budgets","paragraphs":["Hyperiids retain source wet Q 152.5 million tonnes/yr, including copepods 56.7 and Other 95.8. The retained clear euphausiid flow 0.283 million tC/yr accounts for 2.9998 million wet tonnes within Other. The remaining 92.8002 million wet tonnes are assumed 40% chaetognaths, 50% absent larvae/tunicates and 10% gelatinous food. The latter two use wet/C proxies 13.3 and 285.2. This supplies sufficient carbon intake while retaining Figure P 4.752; the split is unmeasured and alternative residual mixtures remain plausible.","Salmon source Table 4.52 supplies residence-integrated total wet Q 1.79694 million tonnes/yr. The 1.7968 leaf sum and 0.00014 residual are both retained. Amphipods map to hyperiids; gelatinous food maps to jellyfish; fish food maps to smelt. Squid prey splits equally between stages using equal source wet stocks. Pteropods, decapods and Oikopleura enter imports with recorded factors. Table 4.54's apparent copepod/amphipod swap is rejected in favor of direct species feeding Table 4.52. These aggregations and proxy factors are assumptions.","Jellyfish complete wet Q 3.1771 million tonnes/yr derives from 2006–2014 large/small feeding tables rather than the 2000–2014 Figure intake sum 0.0505. The stock-period and size-scope mismatch remains. Copepods, euphausiids, hyperiid/amphipod, chaetognath and cannibalistic jellyfish categories use represented prey; absent prey categories and Other use imports. Jellyfish P 0.144 and primary body factor 285.2 remain unchanged. Prey-specific factors explain why wet jellyfish P 41 can exceed wet intake without the same carbon-energy contradiction."],"headers":["Group","Preserved P million tC/yr","Figure Q","Adopted Q","Solved GS","Final R tC/km²/yr"],"rows":[[f"{names[n]} ({n})",short(next(g['source_figure_production'] for g in groups if g['group_id']==n)),short(baseline_q[n]),short(next(g['adopted_Q_million_tC'] for g in groups if g['group_id']==n)),short(next(r['GS'] for r in native['rows'] if r['group_id']==n)),short(next(r['R'] for r in native['rows'] if r['group_id']==n))] for n in [6,8,14]],"widths":[1.6,1.15,0.85,0.85,0.8,1.7],"font_size":9})
    blocks.append({"heading":"Every source feeding component and its conversion","paragraphs":["The table retains every wet quantity used to complete source diets. All quantities are million wet tonnes/yr or million tC/yr. Import means the prey is not represented internally. The basis records the source scope, residual/stage allocation and chemical proxy. Figure paths without a replaced diet remain in the adopted carbon-flow matrix. Primary pooled microheterotroph food is split 2/3 bacteria and 1/3 protozoa by wet mass for copepods, a source-informed but unmeasured split; the initial Figure-proportional split failed microbial availability and is retained as a rejected trial. Euphausiids use the Figure-relative wet split. The squid source 64% zooplankton and 36% nekton are retained in aggregate; unknown plankton splits 90/10 and unknown nekton 20/80 between stages III/IV using their stated feeding roles. Small pollock's approximately 0.2% category-scale adjustment and all residual imports are explicit below.", [link("Exact full food component ledger",A/"food_component_ledger.json")," | ",link("Final carbon flow matrix",A/"carbon_food_flows.json")]],"headers":["Consumer","Prey or external category","Wet food","Wet per C","Carbon food","Source or assumption"],"rows":[[f"{x['consumer']} {names[x['consumer']]}",f"{x['prey']} {x['category']}",short(x['wet_million_t']),short(x['wet_per_carbon']),short(x['carbon_million_t']),x['basis']] for x in food],"widths":[1.05,1.4,0.72,0.7,0.78,2.3],"font_size":8.5})
    solved_rows = [[f"{r['group']} ({r['group_id']})",short(r['EE']),short(r['GS']),short(r['BA']),short(r['R']),short(r['U']),short(r['M0'])] for r in native['rows'] if r['group_id'] <= 22]
    blocks.append({"heading":"Solved physical budgets and scientific limits","paragraphs":["All flows below are tC/km²/yr except EE and GS. The engine's final main model is reloaded from the persisted file and balanced. No failed LIM fallback values or legacy migration-based balanced copy are used. Living BA is 0, detritus BA is positive, all catch/migration values are 0, and all U/M0 flows enter detritus. Detritus residual accumulation of 374.43368 million tC/yr is 24.16 times its assumed 15.5 million tC inventory per year. With zero export/import and all M0/U routed to detritus, this is a large nonsteady residual, not measured burial/storage or a stationary stock. Solver values are a consequence of the selected food and stock assumptions, not independently measured author parameters.","The 12 decimal changes resolve source predation greater than production for squid III, herring, smelt, capelin, squid IV and large pollock. This prevents negative mortality/depletion but materially changes internal predation. Extensive external food preserves total consumer intake; it weakens inference about which local production supports consumers. Scientific validation must assess donor food sources, chemistry, allocation and temporal scope rather than infer validity from algebraic closure."],"headers":["Group","EE","GS","BA","R","U","M0"],"rows":solved_rows,"widths":[1.65,0.68,0.7,0.8,1.03,1.03,1.06],"font_size":9})
    cases = ledger["case_coverage"]
    blocks.append({"heading":"Mandatory baselines and sensitivity outcomes","paragraphs":["Every case uses the actual native runtime. Main balance is an algebraic engine result; physical admissibility independently checks flow signs, EE/GS bounds and the accepted boundaries. Thus the unrepaired text-fed case is rejected even though its main balanced flag is True. F62 = 0.025 gives the same pass/fail classification as the preferred 0.023 in all four structural cases. Raw failed inputs and returns remain available.",f"The complete F62 = 0.025 native model balances and all three direct methods remain WARN with finite coefficients. Maximum relative all-source SPPR changes are {pct(100*sensitivity['max_relative_change_by_method_scope']['GE all'])} for GE, {pct(100*sensitivity['max_relative_change_by_method_scope']['TE all'])} for TE and {pct(100*sensitivity['max_relative_change_by_method_scope']['With Egestion all'])} for With Egestion. These maxima cover native groups; the ambiguous route remains tentative.",[link("Full sensitivity returns and summary",A/"sensitivity/F62_summary.json")," | ",link("Every group and source-scope comparison",A/"sensitivity/F62_scoped_SPPR_comparison.csv")]],"headers":["Case","F62","Main balance","Physical admissibility","Unsolved groups"],"rows":[[x['case'].replace('_',' '),short(x['F62']),str(x['main_balanced']),str(x['physically_admissible']),", ".join(map(str,x['unsolved_groups'])) or "none"] for x in cases],"widths":[2.2,0.7,1.1,1.5,1.45],"font_size":9})
    blocks.append({"heading":"Numerical alternatives to the decimal assumptions","paragraphs":["Preserving unrepaired outgoing predation would require these production or stock/PB multipliers under the declared 95% production availability bound. These large changes are rejected because independently confirmed production boxes are retained. They are nevertheless energy-feasible given the completed food and therefore illustrate non-uniqueness. The selected arrow counts are minimum only within the discrete decimal-reduction search, not proof of a source error or a globally minimal ecological repair. Herring has a different feasible minimum-exponent decimal allocation (F41/10, F42/10 and F71/100), so the adopted allocation remains a choice.",[link("Exact alternative calculations and restricted search",A/"alternative_hypotheses.json")]],"headers":["Group","Source P","Unrepaired predation","Adopted predation","Required multiplier","Alternative P","Changed labels selected/min"],"rows":[[f"{x['group']} ({x['group_id']})",short(x['source_P']),format(x['unrepaired_text_predation'],'.6g'),format(x['chosen_predation'],'.6g'),format(x['stock_or_PB_minimum_multiplier_preserving_outgoing'],'.6g'),format(x['alternative_P'],'.6g'),f"{x['selected_arrow_count']} / {x['minimum_arrow_count']}"] for x in alternatives],"widths":[1.65,.7,.97,.95,.85,.87,.96],"font_size":9})
    blocks.append({"heading":"Import fidelity and unusual production efficiencies","paragraphs":["The eight EwE tables and companion files retain 1,510 cells with all numeric and missing-state values within tolerance (maximum numeric difference 4 × 10⁻¹⁴). Strings are not all exact: normalization of labels is documented. The raw database converter omits nonfeeding fate/import structure and fails native admission with a singular matrix. An explicit constructor-admission copy restores documented schema fields, structural zeros and the native companion; its actual roundtrip state agrees within 10⁻¹². The converter output is not presented as an independently balanced native model.","The interface checker returns 0 errors and 1 warning for 20 blank GS inputs. The indicative mass-balance check returns 0 errors, 8 warnings and 1 note. The database converter reports 20 INDETERMINATE groups because unknown GS causes its indicative default 0.2; this does not replace the actual native LIM result with freely solved GS.","The independent screen flags P/Q beyond its usual 0.02–0.5 range: copepods 0.641, euphausiids 0.638, chaetognaths 0.553, salmon 0.778 and jellyfish 0.614, with baleen whales 0.00467 and predatory mammals 0.00960 below it. These ratios remain scientific physiology or aggregation concerns despite nonnegative energy budgets. The producer has only B and PB as known author-style inputs; native production closure and software import sufficiency are distinct checks.",[link("Actual import tool returns",A/"export_tool_results.json")," | ",link("Detailed database roundtrip",A/"ewe_roundtrip_verification.json")," | ",link("Source fidelity checks",A/"ewe_imports/SOURCE_FIDELITY_CHECK.json")]]})
    hyp = read(E / "source_hypotheses_for_report.json")
    blocks.append({"heading":"Source error hypotheses examined","paragraphs":["The earlier jellyfish source audit examined the following 16 explanations. The final completed diet adds declared assumptions where that audit could only retain missing food; it does not retroactively establish an exact author allocation or chemical factor."],"headers":hyp["headers"],"rows":hyp["rows"],"widths":[1.35,3.1,2.5],"font_size":9})
    scalar = [x for x in ledger['input_cell_changes'] if not x['field'].startswith('diet.')]
    diet = [x for x in ledger['input_cell_changes'] if x['field'].startswith('diet.')]
    blocks.append({"heading":"Every native scalar input change","paragraphs":["This appendix enumerates every changed scalar or input flag relative to the preserved human-reading native model. Unknown means the input sentinel -9999; absent means no original value. Baseline biomass is wet t/km²; final biomass is tC/km². Biomass and habitat biomass repeat the same full-area stock, while PB/QB are yr⁻¹ in both. The manuscript policies above explain the scientific basis; this table also retains computational flags and explicitly written zeros. Numeric display uses eight significant digits; exact original/final strings remain in the linked ledger."],"headers":["Group ID and name","Field","Baseline value","Final input"],"rows":[[f"{x['group']} {x['group_name']}",x['field'],short(x['before']),short(x['after'])] for x in scalar],"widths":[1.8,2.1,1.5,1.55],"font_size":8.5})
    blocks.append({"heading":"Every native diet and detritus fate input change","paragraphs":["Consumer is the native row group. DC is a dimensionless carbon food fraction; fate values are routing fractions, not feeding quantities. Newly explicit zero entries expand the native representation and remain listed. Source-to-final food quantities and their reasons are above; the exact per-cell basis is in the ledger."],"headers":["Native row group","Field","Prey or origin ID","Baseline","Final"],"rows":[[f"{x['group']} {x['group_name']}",x['field'],x.get('prey',''),short(x['before']),short(x['after'])] for x in diet],"widths":[1.7,1.65,1.0,1.3,1.3],"font_size":8.5})
    blocks.append({"heading":"Evidence and reproducibility","paragraphs":[[link("Exact source to final ledger",A/"source_to_final_ledger.json")," records all 448 changed input cells, all 21 unchanged production boxes, accepted readings, case outcomes and uncertainties. ",link("Actual native reload result",A/"native_reload_result.json")," and ",link("Runtime settings",A/"runtime_settings.json")," identify the exact constructor and returned balances. ",link("Independent final gate",C/"research_20261003/completion_integration/independent_final_gate.json")," records an independent reload and physical checks."],"The runtime constructor is PPRCalculator with underdetermined=True, zero_catch=True, zero_biomass_accum=False, default_gs=False, weight_flow=1, weight_guess=1, normalize_DC=False and balance_BA_after_DC_normalization=False. GS is cleared in the native input. Engine code hashes and actual returned values are retained with that input identity.",[link("GE full return",A/"diagnostics/GE_full_return.json")," | ",link("TE full return",A/"diagnostics/TE_full_return.json")," | ",link("With Egestion full return",A/"diagnostics/With_Egestion_full_return.json")," | ",link("Independent source matrix inspection",E/"diagnostic_matrix_inspection.json")],f"All three direct methods return WARN. Their living networks converge and source matrices contain no negative entries. Four apex groups have EE = 0; TE assigns zero source coefficients to them. Their fractionally assigned 2019 landings total {regional_science['terminal_assigned_catch_tonnes']:,.2f} wet t ({pct(regional_science['terminal_assigned_catch_percent'])}), with independent classic PPR {regional_science['terminal_assigned_simple_ppr_tC']:,.2f} tC ({pct(regional_science['terminal_assigned_simple_ppr_percent'])}). {regional_science['taxa_entirely_TE_zero']} taxa are wholly TE-zero, totaling {regional_science['whole_taxon_zero_catch_tonnes']:,.2f} wet t ({pct(regional_science['whole_taxon_zero_catch_percent'])}) and {regional_science['whole_taxon_zero_simple_ppr_tC']:,.2f} tC ({pct(regional_science['whole_taxon_zero_simple_ppr_percent'])}) of classic PPR. Numerical coefficient coverage of {format(mapping['mapping_coverage_percent'],'.7f') + '%'} does not validate ecological catch footprints. Native zero-catch footprint is separate from observed regional catch. Annual/map use is provisional; production eligibility is false and Monte Carlo/global checks are NOT_RUN.",[link("Regional unit bridge and per-taxon TE exposure",I/"regional_science_verification.json")],[link("New validation record",REGION/s['validation_filename'])," | ",link("All taxon mappings and Sources",REGION/"52_GM2019_Fig9_Pelagic_balanced_(2000-2014)_taxon_mapping_appendix.xlsx")],"The researcher review decision remains unsigned. The original article, accepted human-reading variant and prior researcher-edited validation are preserved."]})
    blocks[0]["paragraphs"].append([link("Microbial stock and split consistency",A/"microbial_split_consistency.json")," records the wet-stock increase 64 → 65.067 million tonnes (+1.067 million tonnes; +1.6672%). Copepod bacterial wet-food share rises from 0.652777778 to 0.666666667; protozoan EE falls from 0.957892397 to 0.932837989 under the declared 0.95 availability bound. This deliberate food allocation change is not an author measurement."])
    blocks[4]["paragraphs"].append("Jellyfish source assimilation 70% is expressed in calorie terms and cannot establish carbon GS = 0.30. The actual free native LIM GS is 0.10. Squid IV obtains 88.3064% of its adopted carbon food from imports; its unallocated nekton and assumed 20/80 stage split materially weaken inference about local donor production.")
    blocks[-1]["paragraphs"].insert(-2,["Regional currency bridge: saved wet-equivalent SPPR = native carbon SPPR × 9 / the assigned group's source wet/C factor. Regional/map PPR then multiply wet catch and divide by 9 once. ",link("Exact carbon-to-regional audit",I/"carbon_unit_bridge.json")])
    food_block = next(b for b in blocks if b.get("heading") == "Every source feeding component and its conversion")
    for row, source in zip(food_block["rows"], food):
        row[2:5] = [format(source[k],".6g") for k in ("wet_million_t","wet_per_carbon","carbon_million_t")]
        row[5] = readable_reason(row[5])
    budget_block = next(b for b in blocks if b.get("heading") == "Solved physical budgets and scientific limits")
    budget_block["widths"] = [1.65, 0.75, 0.7, 0.73, 1.03, 1.03, 1.06]
    for row, source in zip(budget_block["rows"], [r for r in native["rows"] if r["group_id"] <= 22]):
        row[1:] = [format(source[k],".6g") for k in ("EE","GS","BA","R","U","M0")]
    rejected = next(x for x in read(A/"case_coverage.json") if x["case"] == "text_plus_figure_unrepaired" and x["F62"] == 0.023)
    bad = {(x["group"],x["field"]):x["value"] for x in rejected["physical_violations"]}
    failed_rows = []
    for gid in (9,10,11,13,16,19):
        final = next(r for r in native["rows"] if r["group_id"] == gid)
        failed_rows.append([f"{names[gid]} ({gid})",format(bad[gid,"EE"],".6g"),format(final["EE"],".6g"),format(bad[gid,"M0"],".6g"),format(final["M0"],".6g")])
    index = next(i for i,b in enumerate(blocks) if b.get("heading") == "Numerical alternatives to the decimal assumptions")
    blocks.insert(index,{"heading":"Why algebraic balance alone fails the unrepaired case","paragraphs":["At preferred F62 = 0.023, the source-fed unrepaired case returns main balance True but the following six groups require negative other mortality and EE above 1. The selected decimal assumptions remove these violations. EE is dimensionless; M0 is tC/km²/yr. These actual returned failures motivate a repair but do not identify author intent.",[link("All eight case inputs and physical violations",A/"case_coverage.json")]],"headers":["Group","Unrepaired EE","Adopted EE","Unrepaired M0","Adopted M0"],"rows":failed_rows,"widths":[2.15,1.05,1.05,1.35,1.35],"font_size":9})
    blocks[-1]["paragraphs"].insert(-1,[link("Complete native evidence inventory",A/"evidence_index.json")," | ",link("Fresh reload consistency",A/"reload_consistency.json")])
    s["departures_blocks"] = blocks
    s["provenance"] = {"model_sha256":exact_hash,"mapping_summary_sha256":hashlib.sha256((I/'mapping_summary.json').read_bytes()).hexdigest(),"pending_map_alignment":pending,"input_changes_count":len(ledger['input_cell_changes']),"food_components_count":len(food),"group_count":len(groups),"matrix_checks":inspections}
    (E / "report_inputs.json").write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"model_sha256":exact_hash,"pending_map_alignment":pending,"input_changes_count":len(ledger['input_cell_changes']),"food_components":len(food),"very_low_reason_rows":len(verylow)}))


if __name__ == "__main__":
    main()
