"""Reopen the current diagnostic package; no calculator or workbook imports."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math
import os

SCRIPT = Path(__file__).resolve()
RUN = SCRIPT.parents[1]
MODEL = RUN.parents[2]
OUT = MODEL / "results/diagnostics/validation_20261114"
HIST = MODEL / "model_validation/evidence/source_review/direct_diagnostics"
ENGINE = HIST / "engine"
OLD_OUT = RUN / "outputs/current_diagnostics"

def read(name, base=OUT):
    return json.loads((base/name).read_text(encoding="utf-8-sig"))

def write(name, value, base=OUT):
    (base/name).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rel(path, base=OUT):
    return Path(os.path.relpath(path,base)).as_posix()

def numeric_equal(a,b):
    return math.isclose(a,b,abs_tol=1e-12,rel_tol=1e-12)

evidence = read("execution_evidence.json")
if not (OUT/"artifact_promotion.json").exists():
    old_sha = sha(OUT/"execution_evidence.json")
    evidence["canonical_input"] = rel(MODEL/"model.json")
    evidence["script_path"] = rel(RUN/"code/run_current_diagnostics.py")
    for item in evidence["engine_files"]:
        item["path"] = rel(ENGINE/Path(item["path"]).name)
    write("execution_evidence.json",evidence)
    write("artifact_promotion.json",dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),
        previous_location=rel(OLD_OUT,MODEL),current_location=rel(OUT,MODEL),
        reason="Promote the newly authorized current-input diagnostic evidence for persistent report links; preserve original execution identity.",
        moved_without_numerical_change=True,rebased_fields=["canonical_input","script_path","engine_files[].path"],
        execution_evidence_sha256_before_rebase=old_sha,execution_evidence_sha256_after_rebase=sha(OUT/"execution_evidence.json")))

reports, solutions, metadata, groups = read("direct_reports.json"),read("direct_solutions.json"),read("matrices_metadata.json"),read("loaded_groups.json")
coefficients, ledger = read("group_scope_coefficients.json"),read("runtime_transformation_ledger.json")
canonical = read("model.json",MODEL)
names={int(i):row[groups["columns"].index("group_name")] for i,row in zip(groups["index"],groups["data"])}
catch={int(i):row[groups["columns"].index("catch")] for i,row in zip(groups["index"],groups["data"])}
checks=dict(evidence["preservation_checks"])
checks["canonical_hash_current"] = sha(MODEL/"model.json") == evidence["canonical_sha256_before"] == evidence["canonical_sha256_after"]
checks["all_canonical_group_names_retained"] = all(names[int(g["group_seq"])] == g["group_name"] for g in canonical["group"])
checks["pinned_code_hashes_current"] = all(sha((OUT/i["path"]).resolve()) == i["sha256"] for i in evidence["engine_files"])
checks["executed_script_hash_current"] = sha((OUT/evidence["script_path"]).resolve()) == evidence["script_sha256"]
methods=[]
negative_entries=[]
for method,returns in solutions.items():
    for key,mat in returns.items():
        meta=next(x for x in metadata if x["method"]==method and x["matrix"]==key)
        assert len(mat["index"])==len(set(mat["index"]))
        assert len(mat["columns"])==len(set(mat["columns"]))
        assert len(mat["data"])==len(mat["index"])
        assert all(len(row)==len(mat["columns"]) for row in mat["data"])
        assert mat["index"]==meta["row_ids"] and mat["columns"]==meta["column_ids"]
        assert [names[i] for i in mat["index"]]==meta["row_names"]
        assert [names[i] for i in mat["columns"]]==meta["column_names"]
        assert meta["shape"]==[len(mat["index"]),len(mat["columns"])]
        assert all(isinstance(v,(int,float)) and math.isfinite(v) for row in mat["data"] for v in row)
        for mask in ["null_mask","nan_mask","positive_infinity_mask","negative_infinity_mask"]:
            assert len(meta[mask])==len(mat["data"])
            assert all(len(r)==len(mat["columns"]) and not any(r) for r in meta[mask])
    s=returns["SPPR"]
    meta=next(x for x in metadata if x["method"]==method and x["matrix"]=="SPPR")
    for gid,row in zip(s["index"],s["data"]):
        for sid,v in zip(s["columns"],row):
            if v<0:negative_entries.append(dict(method=method,matrix="SPPR",source_id=sid,source_name=names[sid],group_id=gid,group_name=names[gid],sppr_value=v))
        for scope,ids in meta["source_scope_definitions"].items():
            total=math.fsum(row[s["columns"].index(i)] for i in ids)
            stored=next(x["sppr"] for x in coefficients if x["method"]==method and x["scope"]==scope and x["group_id"]==gid)
            assert numeric_equal(total,stored)
    negcols={x["source_id"] for x in negative_entries if x["method"]==method}
    assert len(negcols)==reports[method]["divergence"]["n_negative_sources"]
    for scope,field in [("all","ppr_all"),("inner","ppr_inner"),("PP","ppr_pp_only")]:
        value=math.fsum(c["sppr"]*catch[c["group_id"]] for c in coefficients if c["method"]==method and c["scope"]==scope)
        assert numeric_equal(value,reports[method]["footprint"][field])
    methods.append(dict(method=method,status=reports[method]["status"],shape=meta["shape"],
        row_ids=s["index"],source_ids=s["columns"],source_names=meta["column_names"],
        finite_entries=sum(len(row) for row in s["data"]),negative_entries=[x for x in negative_entries if x["method"]==method],
        negative_source_columns=len(negcols),rho_living=reports[method]["divergence"]["rho_living"],
        b=reports[method]["divergence"]["b"],detritus_sppr=reports[method]["divergence"]["sppr_det"],
        warnings=reports[method]["warnings"],balance=reports[method]["balance"]))
assert negative_entries==read("negative_source_entries.json")["entries"]
checks["reopened_unique_axes_names_dimensions_and_masks"] = True
checks["reopened_coefficients_footprints_and_negative_pairings_reconciled"] = True
checks["all_requested_methods_returned"] = set(reports)=={"GE","TE","With Egestion"} and all(r["status"] in {"OK","WARN","FAIL"} for r in reports.values())
historical_comparison=read("historical_comparison.json")
serialization_diffs=[x for x in historical_comparison["state_differences"] if x == {
    "path":"/_groups_df/data/0/2","before":None,"after":{"__nonfinite__":"NaN"}}]
material_state_diffs=[x for x in historical_comparison["state_differences"] if x not in serialization_diffs]
checks["historical_numeric_runtime_matches_at_1e_12"] = not material_state_diffs
checks["historical_returned_matrices_match_at_1e_12"] = historical_comparison["matrices_equal_at_tolerance"]
checks["historical_diagnostic_returns_exactly_equal"] = reports==read("direct_reports.json",HIST)
assert all(checks.values()),checks
verification=dict(verified_utc=datetime.now(timezone.utc).isoformat(),checks=checks,methods=methods,
    historical_state_missing_representation_difference=serialization_diffs,
    historical_state_difference_explanation="Only synthetic diet_import taxon_descr is historical null versus explicitly serialized NaN. Numeric fields and all returned matrices match at absolute tolerance 1e-12, rtol=0; this does not convert the historical input into the current one.",
    no_adoption=True,coverage_scope="GE, TE, With Egestion; not full publication inventory")
write("verification.json",verification)

roles={"execution_provenance":"execution_evidence.json","full_direct_returns":"direct_reports.json",
    "full_returned_matrices":"direct_solutions.json","axes_masks_scopes":"matrices_metadata.json",
    "negative_source_pairings":"negative_source_entries.json","scope_coefficients":"group_scope_coefficients.json",
    "source_loaded_state":"source_loaded_state.json","runtime_before":"runtime_before_methods.json",
    "runtime_after":"runtime_after_methods.json","transformation_ledger":"runtime_transformation_ledger.json",
    "historical_comparison":"historical_comparison.json","independent_reopen_checks":"verification.json",
    "promotion_record":"artifact_promotion.json","canonical_input":rel(MODEL/"model.json"),
    "reproduction_script":rel(RUN/"code/run_current_diagnostics.py"),"verification_script":rel(SCRIPT)}
index=dict(schema_version=1,run_id=RUN.name,region_id="LME_038",model_id=MODEL.name,variant_id=MODEL.name,
    source_identity=dict(paper_id="INDO-1999__LME_038",canonical_model_sha256=sha(MODEL/"model.json"),source_review_scope="Retained canonical extraction; no fresh extraction"),
    computational_input_identity=dict(path=rel(MODEL/"model.json"),sha256=sha(MODEL/"model.json"),constructor_settings=evidence["constructor_settings"],ee_floor=evidence["ee_floor"]),
    methods=["GE","TE","With Egestion"],required_roles=list(roles),
    artifacts=[dict(role=role,path=path,sha256=sha((OUT/path).resolve()),availability="present") for role,path in roles.items()],
    reconciliation=checks)
write("evidence_index.json",index)
review=dict(schema_version=1,review_date="2026-11-14",unit_id="LME_038",model_id=MODEL.name,
    current_canonical_sha256=sha(MODEL/"model.json"),current_diagnostic_package=rel(OUT,RUN/"outputs"),
    current_methods=methods,historical_input_sha256="db0bc803ea5a068e346b82df8d8b4e4b13f8351bf61103c6507997cb6996ae35",
    historical_findings="Retained matrices independently inspected before the newly authorized current-input run; 29 recipients and 4 source columns per method, no nonfinite or negative contributions. Historical direct-engine hashes verified.",
    current_finding="Fresh current-input GE/TE/With Egestion diagnostics now establish this exact pinned baseline configuration; no reliance on the broken historical runtime certificate is needed for the report's diagnostic rows.",
    scientific_limits=["Macrozoobenthos raw diet sums to 0.660; runtime normalization scales its six nonzero cells by 1/0.660 without identifying the missing 0.340.",
        "The 28 prior accepted BA completions remain computational rather than measured stock changes.",
        "Detritus EE changes from source-loaded 0.264 to runtime 1.0 under the recorded loader convention.",
        "The pinned engine has no EE-floor transformation; these results do not describe the current engine's default floor-enabled configuration.",
        "TE reports near-zero transfer efficiency for Marine mammals (27), with all-source SPPR 269815.0941253361; b=0 is a TE formulation convention, not evidence of absent physical recycling.",
        "No fresh whole-matrix primary-source extraction audit was performed.",
        "The regional workbook remains pending because no numerical adoption, arithmetic, project registration or map refresh was performed."],
    report_ready=dict(GE="OK. No negative SPPR entries across the basal-source columns. rho_living = 0.402; recycling b = 0.245; Detritus (28) SPPR = 1.315. The saved balance check passes.",
        TE="WARN. No negative SPPR entries across the basal-source columns. rho_living = 0.621; Detritus (28) SPPR = 0.774. Marine mammals (27) has near-zero transfer efficiency and all-source SPPR about 269,815; the saved balance check passes. TE's reported b = 0 is a formulation convention.",
        timing_configuration="Fresh diagnostics of the current canonical input use the audited baseline engine with runtime diet normalization and no EE-floor transformation; regional results have not been adopted."),
    rerun_recommendation="No further GE/TE/With Egestion run is needed for this report. Publishing new regional results would require separately authorized compatible coefficient adoption and dependent arithmetic; full publication coverage is outside this report-only run.",
    checks=checks)
write("diagnostic_review.json",review,RUN/"outputs")
print(json.dumps({"package":str(OUT),"statuses":{m:r["status"] for m,r in reports.items()},"checks":checks},ensure_ascii=False))
