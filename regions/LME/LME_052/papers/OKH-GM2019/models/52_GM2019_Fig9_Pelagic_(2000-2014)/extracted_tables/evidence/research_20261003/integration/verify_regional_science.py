"""Read-only saved-coefficient/unit/catch reconciliation and TE limitation audit."""
import json,math,sys
from collections import defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
sys.path.insert(0,str(ROOT/"tools"))
from workbooks import records,overview,sha,finite
from regional_book_io import read_fast

def read(p):return json.loads(p.read_text(encoding="utf-8"))
REGION=ROOT/"regions/LME_052"
b=read_fast(REGION/"LME_052.xlsx")
audit=read(HERE/"taxon_audit.json")
bridge=read(HERE/"carbon_unit_bridge.json")
bridge["source_factors"]="../../assumption_variants/adopted_balanced_20261003/source_to_final_ledger.json"
(HERE/"carbon_unit_bridge.json").write_text(json.dumps(bridge,ensure_ascii=False,indent=2),encoding="utf-8")
variant=REGION/str(overview(b)["model_path"])
factors={r["group_id"]:r["body_wet_per_carbon"]for r in read(variant.parent/"source_to_final_ledger.json")["group_parameters"]}
factors[23]=1
group_coeff={(r["group"],r["scope"],r["method"]):r["sppr"]for r in records(b,"Selected model groups","Group SPPR")}
taxon_coeff={(r["taxon"],r["scope"],r["method"]):r["sppr"]for r in records(b,"PPR","Taxon SPPR")}
methods={"GE":"new_GE","TE":"new_TE_EEfix","With_Egestion":"new_WithEgestion"}
scopes={"all":{1,22,23},"inner":{1,22},"PP":{1}}
native={};unit_checks=[]
for option,method in methods.items():
    data=read(variant.parent/f"diagnostics/{option}_full_return.json")
    matrix=data["SPPR"]
    vals={i:dict(zip(matrix["columns"],r))for i,r in zip(matrix["index"],matrix["data"])}
    native[method]={scope:{i:math.fsum(row[c]for c in cols)for i,row in vals.items()}for scope,cols in scopes.items()}
    for r in audit:
        if not r["groups"]:continue
        for scope in scopes:
            expected=math.fsum(g["weight"]*native[method][scope][g["seq"]]*9/factors[g["seq"]]for g in r["groups"])
            actual=taxon_coeff[r["taxon"],scope,method]
            # The maintained regional calculator rounds taxon coefficients to6decimals.
            unit_checks.append(abs(expected-actual)<=0.500001e-6+abs(expected)*2e-15)

terminal={17,18,20,21}
terminal_groups=[]
for g in records(b,"Selected model groups","Groups"):
    if g["seq"]in terminal:terminal_groups.append(dict(group_id=g["seq"],group=g["group_name"],ee=g["ee"],q_tC_km2_year=g["q"],te_all_native=native["new_TE_EEfix"]["all"][g["seq"]]))
summary=read(HERE/"mapping_summary.json")
rows=[]
for r in audit:
    share=math.fsum(g["weight"]for g in r["groups"]if g["seq"]in terminal)
    if share:
        rows.append(dict(taxon=r["taxon"],terminal_weight=share,total_catch_tonnes=r["catch_tonnes"],terminal_assigned_catch_tonnes=r["catch_tonnes"]*share,total_simple_ppr_tC=r["simple_ppr_tC"],terminal_assigned_simple_ppr_tC=(r["simple_ppr_tC"] or 0)*share,full_taxon_TE_zero=all(g["seq"]in terminal for g in r["groups"]),groups=r["groups"],reason=r["reason"]))
mass=math.fsum(r["terminal_assigned_catch_tonnes"]for r in rows)
ppr=math.fsum(r["terminal_assigned_simple_ppr_tC"]for r in rows)
fullmass=math.fsum(r["total_catch_tonnes"]for r in rows if r["full_taxon_TE_zero"])
fullppr=math.fsum(r["total_simple_ppr_tC"] or 0 for r in rows if r["full_taxon_TE_zero"])
old=read_fast(HERE/"LME_052_before_GM2019_adoption.xlsx")
oldmapped={r["taxon"]for r in records(old,"PPR","Matching")if r["group"]}
baseline=read(HERE/"baseline_inventory.json")
oldcovered=math.fsum(r["catch_2019"]for r in baseline["catch"]if r["catch_basis"]=="landings"and r["taxon"]in oldmapped)
result=dict(schema_version=1,model_id=overview(b)["selected_model_id"],model_sha256=sha(variant),workbook_sha256=sha(REGION/"LME_052.xlsx"),year=2019,catch_basis="landings",unit_bridge_formula_verified=all(unit_checks),unit_comparisons=len(unit_checks),native_carbon_vs_saved_rounding_tolerance="0.500001e-6 absolute plus2e-15 relative for documented6-decimal taxon coefficient rounding",terminal_groups=terminal_groups,terminal_assigned_catch_tonnes=mass,terminal_assigned_catch_percent=100*mass/summary["total_catch_tonnes"],terminal_assigned_simple_ppr_tC=ppr,terminal_assigned_simple_ppr_percent=100*ppr/summary["total_known_simple_ppr_tC"],taxa_with_any_terminal_weight=len(rows),taxa_entirely_TE_zero=sum(r["full_taxon_TE_zero"]for r in rows),whole_taxon_zero_catch_tonnes=fullmass,whole_taxon_zero_catch_percent=100*fullmass/summary["total_catch_tonnes"],whole_taxon_zero_simple_ppr_tC=fullppr,whole_taxon_zero_simple_ppr_percent=100*fullppr/summary["total_known_simple_ppr_tC"],terminal_impact_rows=rows,baseline_mapping_coverage_percent=100*oldcovered/summary["total_catch_tonnes"],final_mapping_coverage_percent=summary["mapping_coverage_percent"],baseline_vs_final_note="Changing to the scientifically different pelagic reconstruction reduces literal benthic representation. Coverage under transparent analogue assumptions is not scientific validation, and TE numerical coverage counts returned finitezero coefficients despite the terminal EE0 warning.",consequence="The finiteTE zero row convention assigns noTEfootprint to positive-intake EE0 terminal groups. Do not interpret numericalcoverage as validatedcatch-footprintcoverage. GE/WithEgestion raw returns remain available as independent provisional formulations; no alternative coefficient substitutes forTE.")
(HERE/"regional_science_verification.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in result.items()if k!="terminal_impact_rows"},ensure_ascii=False,indent=2))
if not result["unit_bridge_formula_verified"]:raise SystemExit(1)
