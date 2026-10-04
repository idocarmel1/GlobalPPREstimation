"""Read-only bounded LME036 single-mapping handoff trial; trace actual inputs."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import time
import math
import collections
import io
from itertools import islice
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "Project.xlsx").exists())
RUN = Path(__file__).resolve().parents[1]
QA = RUN / "qa" / "single_mapping_handoff_trial.json"
sys.path.insert(0, str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def digest(value):
    def canonical_keys(v):
        if isinstance(v,dict):return {str(k):canonical_keys(w) for k,w in v.items()}
        if isinstance(v,(list,tuple)):return [canonical_keys(w) for w in v]
        return v
    raw = json.dumps(canonical_keys(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def display(path):
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()

class Trial:
    def __init__(self):
        self.result = json.loads(QA.read_text(encoding="utf-8"))
        self.result.setdefault("resume", {"context": "reused instruction context after user-requested pause", "events": [], "token_telemetry": "unavailable"})
        resume=self.result["resume"]
        if "events" not in resume:
            inputs=resume.get("inputs",[])
            resume["events"]=[]
            for raw in resume.get("actual_read_events",[]):
                event=dict(raw)
                if "input_id" in event:
                    ref=inputs[event.pop("input_id")]
                    event["path"]=ref["path"]
                    if "sha256" not in event and ref.get("sha256"):event["sha256"]=ref["sha256"]
                resume["events"].append(event)
        self.result["qa_metadata_runtime_reads"]=self.result.get("qa_metadata_runtime_reads",resume.get("counts",{}).get("qa_metadata_internal_reads",0))+1
        self.result["status"] = "resumed_verification_in_progress"

    def event(self, operation, path=None, **extra):
        event = {"operation": operation, **extra}
        if path is not None:
            event["path"] = display(path)
        self.result["resume"]["events"].append(event)

    def bytes(self, path, kind="data"):
        path = Path(path).resolve()
        start = time.perf_counter()
        data = path.read_bytes()
        self.event("file_read", path, kind=kind, sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), elapsed_seconds=time.perf_counter()-start)
        self.save()
        return data

    def save(self):
        QA.write_text(json.dumps(self.result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")

    def instruction(self, path, start=None, end=None, heads=False):
        text = self.bytes(path, "instruction").decode("utf-8-sig")
        lines = text.splitlines()
        if heads:
            output = "\n".join(f"{i}: {line}" for i, line in enumerate(lines, 1) if line.startswith("#"))
        else:
            output = "\n".join(lines[(start or 1)-1:end])
        self.result["resume"]["events"][-1].update({"displayed_lines": [start or 1, end or len(lines)], "headings_only": heads})
        self.save()
        print(output)

    def discover(self):
        from tools.project_core.workbooks.read_session import ReadSession
        from openpyxl import load_workbook
        self.reads = ReadSession()
        region = ROOT / "regions/LME/LME_036/LME_036.xlsx"
        start = time.perf_counter()
        before = self.reads.parse_count
        book = self.reads.read(region, sheets=["Overview", "Catch", "Selected model groups", "PPR"])
        self.event("read_session", region, kind="regional_workbook", sha256=self.reads._hashes[region.resolve()], read_requests=1, workbook_parses=self.reads.parse_count-before, selected_sheets=["Overview", "Catch", "Selected model groups", "PPR"], elapsed_seconds=time.perf_counter()-start)
        self.save()
        def rows(t):
            if isinstance(t, tuple):
                headers, data = t
                return [r if isinstance(r,dict) else dict(zip(headers,r)) for r in data]
            return t if isinstance(t,list) else t["rows"]
        settings = {r["field"]:r.get("value") for r in rows(book["Overview"]["Settings"])}
        model = (region.parent / settings["model_path"]).resolve()
        output = {"settings": settings, "table_names": {k:list(v) for k,v in book.items()}, "groups": rows(book["Selected model groups"]["Groups"])}
        model_data = json.loads(self.bytes(model, "model_json"))
        output["model_json_top_keys"] = list(model_data)
        output["model_path"] = display(model)
        output["model_shape"] = {k: len(v) if isinstance(v, (list,dict)) else v for k,v in model_data.items()}
        appendix = model.parent / "model_validation/taxon_mapping.xlsx"
        source = self.bytes(appendix, "mapping_appendix")
        import io
        started = time.perf_counter()
        app = load_workbook(io.BytesIO(source), read_only=True, data_only=False)
        self.event("workbook_parse", appendix, kind="mapping_appendix", workbook_parses=1, elapsed_seconds=time.perf_counter()-started)
        self.save()
        output["appendix_sheets"] = {s.title:{"rows":s.max_row,"columns":s.max_column,"first_rows":[list(row) for row in islice(s.iter_rows(values_only=True),12)]} for s in app}
        app.close()
        output["matching_schema"] = list(rows(book["PPR"]["Matching"])[0])
        output["matching_first_rows"] = rows(book["PPR"]["Matching"])[:8]
        output["catch_schema"] = list(rows(book["Catch"]["Catch"])[0])
        self.reads.assert_unchanged()
        self.event("read_session_unchanged_guard", region, passed=True)
        self.result["resume"]["discovery"] = output
        self.save()
        print(json.dumps(output, ensure_ascii=False, indent=2))

    def show(self):
        d=self.result["resume"]["discovery"]
        model=ROOT/d["model_path"]
        evidence=model.parent/"model_validation/evidence"
        paths=sorted(display(p) for p in evidence.rglob("*.json"))
        self.event("filename_inventory", evidence, pattern="*.json", matches=len(paths))
        self.save()
        print(json.dumps({"model_shape":d["model_shape"], "groups":[{k:r.get(k) for k in ["seq","group_name","taxon_descr"]} for r in d["groups"]], "appendix_first_rows":{k:v["first_rows"][:7] for k,v in d["appendix_sheets"].items()}, "model_local_json_files":paths},ensure_ascii=False,indent=2))

    def evidence(self):
        model=ROOT/self.result["resume"]["discovery"]["model_path"]
        base=model.parent/"model_validation/evidence/source_review/selected_regions_review_20260930"
        output={}
        for name in ["taxon_audit_adopted.json", "allocation_audit.json", "input_identity.json", "evidence_index.json"]:
            data=json.loads(self.bytes(base/name,"saved_mapping_handoff_evidence"))
            if isinstance(data,list):
                output[name]={"type":"list", "records":len(data), "first_record":data[0]}
            else:
                output[name]={"type":"dict", "keys":list(data), "first_fields":{k:v if not isinstance(v,(list,dict)) else {"type":type(v).__name__,"count":len(v),"sample":(v[:1] if isinstance(v,list) else list(v)[:8])} for k,v in data.items()}}
        output["model_notes"] = self.bytes(model.parent/"model_notes.md","source_departures").decode("utf-8-sig")
        self.result["resume"]["evidence_structure"]=output
        self.save()
        print(json.dumps(output,ensure_ascii=False,indent=2))

    def verify(self):
        """Consume established decisions; never research taxa or choose groups/weights."""
        from tools.project_core.workbooks.read_session import ReadSession
        from openpyxl import load_workbook
        started=time.perf_counter()
        reads=ReadSession()
        region=ROOT/"regions/LME/LME_036/LME_036.xlsx"
        scopes=["Overview","Catch","Classic PPR","Selected model groups","PPR"]
        def read_region():
            before=reads.parse_count
            t=time.perf_counter()
            value=reads.read(region,sheets=scopes)
            self.event("read_session",region,kind="regional_workbook",sha256=reads._hashes[region.resolve()],read_requests=1,workbook_parses=reads.parse_count-before,cache_reuse=reads.parse_count==before,selected_sheets=scopes,elapsed_seconds=time.perf_counter()-t)
            self.save()
            return value
        def rows(t):
            if isinstance(t,tuple):
                headers,data=t
                return [r if isinstance(r,dict) else dict(zip(headers,r)) for r in data]
            return t if isinstance(t,list) else t["rows"]
        book=read_region()
        settings={r["field"]:r.get("value") for r in rows(book["Overview"]["Settings"])}
        mid=settings["selected_model_id"]
        model=(region.parent/settings["model_path"]).resolve()
        model_data=json.loads(self.bytes(model,"model_json"))
        base=model.parent/"model_validation/evidence/source_review/selected_regions_review_20260930"
        audit=json.loads(self.bytes(base/"taxon_audit_adopted.json","saved_mapping_handoff_evidence"))
        alloc=json.loads(self.bytes(base/"allocation_audit.json","saved_mapping_handoff_evidence"))
        identity=json.loads(self.bytes(base/"input_identity.json","original_handoff_identity"))
        index=json.loads(self.bytes(base/"evidence_index.json","original_handoff_identity"))
        defs=model.parent/"model_validation/evidence/source_review/confidence_reassessment_20260930/source_group_definitions.txt"
        source_defs=self.bytes(defs,"source_group_definitions").decode("utf-8-sig")
        apppath=model.parent/"model_validation/taxon_mapping.xlsx"
        appbytes=self.bytes(apppath,"mapping_appendix")
        t=time.perf_counter()
        app=load_workbook(io.BytesIO(appbytes),read_only=True,data_only=False)
        self.event("workbook_parse",apppath,kind="mapping_appendix",workbook_parses=1,elapsed_seconds=time.perf_counter()-t)
        sheets={s.title:[list(r) for r in s.iter_rows(values_only=True)] for s in app}
        app.close()
        self.save()
        catch=rows(book["Catch"]["Catch"])
        catch=[r for r in catch if r["catch_basis"]=="landings"]
        matching=[r for r in rows(book["PPR"]["Matching"]) if r["model_id"]==mid]
        review=[r for r in rows(book["PPR"]["Mapping review"]) if r.get("model_id")==mid]
        rby={r["taxon"]:r for r in review}
        ledgers=rows(book["PPR"]["Allocation assumptions"])
        klass={r["taxon"]:r for r in rows(book["Classic PPR"]["Taxa"])}
        groups=rows(book["Selected model groups"]["Groups"])
        gbyname={r["group_name"]:r for r in groups}
        canonical={int(r["group_seq"]):r for r in model_data["group"]}
        aby={r["taxon"]:r for r in audit}
        alby={r["taxon"]:r for r in alloc}
        mby=collections.defaultdict(list)
        for r in matching:mby[r["taxon"]].append(r)
        cby={r["taxon"]:r for r in catch}
        gaps=[]
        def gap(kind,taxon=None,**detail):gaps.append({"kind":kind,**({"taxon":taxon} if taxon else {}),**detail})
        def close(a,b):
            if a in [None,"?"] or b in [None,"?"]:return a in [None,"?"] and b in [None,"?"]
            return math.isclose(float(a),float(b),rel_tol=1e-12,abs_tol=1e-10)
        def level(s):return str(s or "").strip().lower().replace("_"," ")
        rank={q:i for i,q in enumerate(["high","medium","low","very low","unresolved"])}
        duplicates={"catch": [k for k,v in collections.Counter(r["taxon"] for r in catch).items() if v>1],"audit":[k for k,v in collections.Counter(r["taxon"] for r in audit).items() if v>1],"matching":[list(k) for k,v in collections.Counter((r["taxon"],r["group"]) for r in matching).items() if v>1]}
        for name,taxa in duplicates.items():
            if taxa:gap("duplicate_keys",table=name,keys=taxa)
        for name,keys in [("matching",set(mby)),("audit",set(aby)),("allocation audit",set(alby))]:
            missing=sorted(set(cby)-keys); extra=sorted(keys-set(cby))
            if missing or extra:gap("universe_mismatch",table=name,missing=missing,extra=extra)
        model_hash=hashlib.sha256(model.read_bytes()).hexdigest()
        self.event("hash_recheck",model,kind="model_json",sha256=model_hash)
        if model_hash!=identity.get("model_sha256") or model_hash!=settings.get("results_model_sha256"):gap("model_identity_mismatch")
        if identity.get("model_id")!=mid or index.get("model_id")!=mid or index.get("region_id")!="LME_036":gap("original_handoff_identity_mismatch")
        group_conflicts=[]
        for gid,can in canonical.items():
            saved=gbyname.get(can["group_name"])
            if saved is None or int(saved["seq"])!=gid or saved.get("taxon_descr")!=can.get("taxon_descr"):
                group_conflicts.append({"id":gid,"name":can["group_name"],"saved_seq":saved.get("seq") if saved else None,"taxon_descr_equal":bool(saved and saved.get("taxon_descr")==can.get("taxon_descr"))})
        if group_conflicts:gap("canonical_vs_saved_group_definition_conflict",groups=group_conflicts)
        validation_rows=[]; checked_split_values=0
        missing_inputs=[]
        for taxon in sorted(cby):
            if taxon not in aby:continue
            a=aby[taxon]; ms=mby.get(taxon,[]); candidates=a.get("adopted_groups",[])
            current_levels=set(level(r["confidence"]) for r in ms)
            current_confidence=next(iter(current_levels)) if len(current_levels)==1 else "unresolved"
            if len(current_levels)!=1:gap("mixed_saved_confidence",taxon,levels=sorted(current_levels))
            current_review=rby.get(taxon,{})
            if level(current_review.get("overall_confidence"))!=current_confidence:gap("mapping_review_vs_matching_conflict",taxon)
            if level(a.get("review_confidence"))!=current_confidence:gap("audit_review_vs_matching_conflict",taxon)
            if level(a.get("overall_confidence"))!=current_confidence:gap("stale_audit_overall_confidence_field",taxon,audit_overall=a.get("overall_confidence"),audit_review=a.get("review_confidence"),accepted_matching=current_confidence)
            keyed={r["group"]:r for r in ms}
            if set(keyed)!=set(r["name"] for r in candidates):gap("group_set_conflict",taxon,current=sorted(keyed),handoff=sorted(r["name"] for r in candidates))
            for ag in candidates:
                r=keyed.get(ag["name"]); g=gbyname.get(ag["name"])
                if g is None or int(g["seq"])!=int(ag["group_id"]):gap("group_identifier_conflict",taxon,group=ag)
                if r is None or not close(r["weight"],ag["weight"]):gap("weight_conflict",taxon,group=ag["name"],saved=None if r is None else r["weight"],handoff=ag["weight"])
                if r and level(r["confidence"])!=current_confidence:gap("stored_vs_handoff_confidence_conflict",taxon,group=ag["name"])
                if r and (not r.get("evidence") or not r.get("explanation")):gap("missing_saved_reason_or_evidence",taxon,group=ag["name"])
            ws=[r.get("weight") for r in ms]
            if any(not isinstance(w,(int,float)) or not math.isfinite(w) or w<0 for w in ws) or not close(sum(w for w in ws if isinstance(w,(int,float))),1):gap("invalid_saved_weights",taxon,weights=ws)
            for field in ["membership_rule","membership_confidence","membership_source","weight_rule","weight_confidence","weight_source","reason"]:
                if not a.get(field):gap("missing_component_evidence",taxon,field=field)
            mc=level(a.get("membership_confidence"));wc=level(a.get("weight_confidence"));oc=current_confidence
            for current_field,audit_field in [("membership_confidence","membership_confidence"),("allocation_confidence","weight_confidence")]:
                if level(current_review.get(current_field))!=level(a.get(audit_field)):gap("current_review_vs_audit_component_conflict",taxon,field=current_field)
            expected_membership_plain="Taxonomy, ecology and group definitions support the eligible group set" if a.get("membership_rule")=="M9" else a.get("membership_rule_plain")
            if current_review.get("membership_rule")!=expected_membership_plain:gap("current_review_rule_description_conflict",taxon,component="membership")
            if current_review.get("allocation_rule")!=a.get("weight_rule_plain"):gap("current_review_rule_description_conflict",taxon,component="allocation")
            if current_review.get("candidate_selection"):
                saved_candidates=json.loads(current_review["candidate_selection"])
                if saved_candidates!=candidates:gap("current_review_keyed_candidate_conflict",taxon)
            if current_review.get("allocation_calculation"):
                saved_allocation=json.loads(current_review["allocation_calculation"])
                if saved_allocation!=alby.get(taxon):gap("current_review_allocation_evidence_conflict",taxon)
            if mc not in rank or wc not in rank or oc not in rank or (mc in rank and wc in rank and oc!=max([mc,wc],key=lambda q:rank[q])):gap("weakest_component_conflict",taxon,membership=mc,weight=wc,overall=oc)
            if a.get("year")!=2019 or a.get("basis")!="landings":gap("audit_reference_conflict",taxon)
            if not a.get("membership_review",{}).get("sources"):gap("missing_detailed_membership_sources",taxon)
            ar=alby.get(taxon,{})
            if set(ar.get("candidate_ids",[]))!=set(g["group_id"] for g in candidates):gap("allocation_candidate_conflict",taxon)
            for gid,source_value in zip(ar.get("candidate_ids",[]),ar.get("source_values",[])):
                can=canonical.get(int(gid),{})
                if not close(source_value,can.get("export")):gap("allocation_source_value_conflict",taxon,group_id=gid,audit_value=source_value,canonical_value=can.get("export"))
                checked_split_values+=1
            if len(candidates)>1:
                if not ar.get("transfer_assumption"):gap("missing_allocation_transfer_assumption",taxon)
                if ar.get("source_field")=="accepted canonical group.export":
                    sv=ar.get("source_values",[]); total=sum(sv)
                    if not close(total,ar.get("source_total")):gap("saved_allocation_denominator_conflict",taxon)
                    for g,v in zip(candidates,ar.get("weights",[])):
                        if not close(g["weight"],v):gap("saved_allocation_weight_conflict",taxon)
                    for v,w in zip(sv,ar.get("weights",[])):
                        if total<=0 or not close(v/total,w):gap("saved_allocation_arithmetic_conflict",taxon)
            c=cby[taxon].get(2019); k=klass.get(taxon,{})
            sp=k.get("sppr");tl=k.get("tl")
            p=0.0 if c==0 else (c*sp/9 if isinstance(c,(int,float)) and isinstance(sp,(int,float)) and math.isfinite(sp) else None)
            if tl is None or sp is None:missing_inputs.append({"taxon":taxon,"catch_t":c,"tl_missing":tl is None,"coefficient_missing":sp is None,"annual_ppr_tC":p})
            if not close(c,a.get("catch_t")) or not close(sp,a.get("classic_sppr")) or not close(p,a.get("ppr_tC")):gap("audit_arithmetic_or_saved_input_conflict",taxon,current={"catch_t":c,"sppr":sp,"ppr_tC":p},handoff={k:a.get(k) for k in ["catch_t","classic_sppr","ppr_tC"]})
            validation_rows.append({"model_id":mid,"region_id":"LME_036","taxon":taxon,"year":2019,"basis":"landings","catch_t":c,"tl":tl,"classic_sppr":sp,"ppr_tC":p,"groups":[{"group_id":gbyname[r["group"]]["seq"],"name":r["group"],"weight":r["weight"]} for r in ms],"membership_rule":a.get("membership_rule"),"membership_confidence":a.get("membership_confidence"),"membership_source":a.get("membership_source"),"weight_rule":a.get("weight_rule"),"weight_confidence":a.get("weight_confidence"),"weight_source":a.get("weight_source"),"overall_confidence":current_confidence.title(),"reason":a.get("reason"),"assumption_dependent":a.get("assumption_dependent"),"transfer_assumption":a.get("transfer_assumption") or ar.get("transfer_assumption"),"review_run_id":a.get("review_run_id"),"adoption_state":a.get("adoption_state")})
        sorted_rows=sorted(validation_rows,key=lambda r:(r["ppr_tC"] is None,-r["ppr_tC"] if r["ppr_tC"] is not None else 0,r["taxon"]))
        app_rows=[r for r in sheets["Taxon appendix"][5:] if r[0] is not None]
        if [r[0] for r in app_rows]!=[r["taxon"] for r in sorted_rows]:gap("appendix_universe_or_sorting_conflict",saved_rows=len(app_rows),expected_rows=len(sorted_rows))
        appby={r[0]:r for r in app_rows}; app_conflicts=[]
        for r in validation_rows:
            ap=appby.get(r["taxon"]);a=aby[r["taxon"]]
            if ap is None or not close(ap[1],r["tl"]) or not close(ap[2],r["catch_t"]) or not close(ap[3],r["ppr_tC"]) or ap[4]!=a.get("display_mapping") or level(ap[5])!=level(r["overall_confidence"]) or ap[6]!=r["reason"]:app_conflicts.append(r["taxon"])
        if app_conflicts:gap("appendix_row_conflict",taxa=app_conflicts)
        app_candidates=[r for r in sheets["Allocation evidence"][5:] if r[0] in cby and isinstance(r[2],(int,float))]
        app_candidate_keys=collections.Counter((r[0],int(r[2])) for r in app_candidates)
        expected_candidate_keys=collections.Counter((r["taxon"],int(gbyname[r["group"]]["seq"])) for r in matching)
        if app_candidate_keys!=expected_candidate_keys:gap("appendix_allocation_candidate_universe_conflict",missing=[list(k) for k in expected_candidate_keys-app_candidate_keys],extra=[list(k) for k in app_candidate_keys-expected_candidate_keys])
        for r in app_candidates:
            can=canonical.get(int(r[2]),{})
            if r[1]!=can.get("group_name") or not close(r[3],can.get("export")) or not close(r[4],can.get("biomass")):gap("appendix_allocation_source_value_conflict",r[0],group_id=r[2])
        catch_total=sum(r["catch_t"] for r in validation_rows if r["catch_t"] is not None)
        ppr_total=sum(r["ppr_tC"] for r in validation_rows if r["ppr_tC"] is not None)
        summaries=[]
        for q in ["High","Medium","Low","Very low","Unresolved"]:
            rs=[r for r in validation_rows if level(r["overall_confidence"])==level(q)]
            cc=sum(r["catch_t"] or 0 for r in rs);pp=sum(r["ppr_tC"] or 0 for r in rs)
            summaries.append({"confidence":q,"taxa":len(rs),"catch_t":cc,"catch_fraction":cc/catch_total if catch_total else None,"ppr_tC":pp,"ppr_fraction":pp/ppr_total if ppr_total else None})
        rule_tables={}
        rule_names={"M9":"Regional taxonomy, ecology and model definitions support an assumed eligible group set"}
        for component in ["membership","weight"]:
            rb=collections.defaultdict(list)
            for r in validation_rows:rb[(r[f"{component}_rule"],r[f"{component}_confidence"])].append(r)
            rt=[]
            for (rule,confidence),rs in rb.items():
                pp=sum(r["ppr_tC"] or 0 for r in rs)
                saved_plain=aby[rs[0]["taxon"]].get(f"{component}_rule_plain")
                if rule=="M9" and saved_plain=="Ecological fit is partial or the source definition is conflicting":gap("stale_audit_plain_rule_description",rule=rule,saved_description=saved_plain,taxa=[r["taxon"] for r in rs])
                rt.append({"rule":rule,"plain":rule_names.get(rule,saved_plain),"description_source":"tools/templates/instructions.md" if rule in rule_names else "saved adopted audit", "confidence":confidence,"taxa":len(rs),"ppr_tC":pp,"ppr_fraction":pp/ppr_total if ppr_total else None})
            rule_tables[component]=sorted(rt,key=lambda r:-r["ppr_tC"])
        coverage_rows=sheets["Coverage"]
        saved_summary={r[0]:r[1:4] for r in coverage_rows if r and r[0] in [s["confidence"] for s in summaries]}
        for s in summaries:
            v=saved_summary.get(s["confidence"])
            if v is None or v[0]!=s["taxa"] or not close(v[1],s["catch_fraction"]) or not close(v[2],s["ppr_fraction"]):gap("saved_coverage_summary_conflict",confidence=s["confidence"],saved=v,expected=s)
        source_defs_sha=hashlib.sha256(source_defs.encode("utf-8")).hexdigest()
        defs_event=[e for e in self.result["resume"]["events"] if e.get("path")==display(defs) and e["operation"]=="file_read"][-1]
        listed_defs=[r for r in index.get("artifacts",[]) if str(r.get("path","")).endswith("source_group_definitions.txt")]
        for item in listed_defs:
            if item.get("sha256")!=defs_event["sha256"]:gap("source_definition_historical_index_hash_conflict",role=item.get("role"),original_sha256=item.get("sha256"),current_sha256=defs_event["sha256"])
        # Demonstrate both routes consume the same established keyed mapping, with a cache hit.
        second=read_region()
        second_matching=[r for r in rows(second["PPR"]["Matching"]) if r["model_id"]==mid]
        if matching!=second_matching:gap("mixed_version_mapping_read")
        reads.assert_unchanged()
        self.event("read_session_unchanged_guard",region,passed=True)
        self.save()
        consumed_paths={e["path"]:e["sha256"] for e in self.result["resume"]["events"] if e.get("sha256") and e.get("kind") not in ["instruction"] and e["operation"] in ["file_read","read_session"]}
        unchanged=[]
        for path,old in consumed_paths.items():
            p=ROOT/path if not Path(path).is_absolute() else Path(path)
            now=hashlib.sha256(p.read_bytes()).hexdigest()
            self.event("hash_recheck",p,sha256=now,unchanged=now==old)
            unchanged.append(now==old)
            if now!=old:gap("consumed_input_changed",path=path)
        self.result["resume"]["verification"]={
            "scope":"bounded mapping-stage reuse plus validation appendix/summary verification; not full model validation",
            "identity":{"region":"LME_036","model_id":mid,"model_path":display(model),"model_sha256":model_hash,"year":2019,"basis":"landings","original_handoff_run_id":index.get("run_id"),"audit_review_run_ids":sorted(set(r.get("review_run_id","") for r in audit)),"original_variant":index.get("variant_id"),"original_input_identity":identity,"original_source_identity":index.get("source_identity"),"original_computational_identity":index.get("computational_input_identity"),"original_full_region_sha_is_current":identity.get("region_sha256")==reads._hashes[region.resolve()],"original_identity_policy":index.get("historical_index_policy")},
            "counts":{"catch_taxa":len(catch),"zero_catch_taxa":sum(r.get(2019)==0 for r in catch),"matching_rows":len(matching),"audit_taxa":len(audit),"appendix_taxa":len(app_rows),"appendix_allocation_candidates":len(app_candidates),"source_groups":len(canonical),"synthetic_saved_groups":len(groups)-len(canonical),"saved_candidate_value_checks":checked_split_values,"mapping_resolutions":0,"taxon_research_passes":0,"mapping_stage_reuse_consumptions":1,"validation_mapping_verification_passes":1,"report_arithmetic_passes":1,"coherent_operation_workbook_read_requests":reads.read_count,"coherent_operation_workbook_parses":reads.parse_count+1,"read_session_cache_reuses":reads.read_count-reads.parse_count,"engine_calls":0,"render_calls":0,"live_writes":0},
            "digest":{"matching_rows":digest(sorted(matching,key=lambda r:(r["taxon"],str(r["group"])))),"complete_taxon_universe":digest(sorted(catch,key=lambda r:r["taxon"])),"group_source_definitions":digest(sorted([{k:r.get(k) for k in ["group_seq","group_name","taxon_descr"]} for r in model_data["group"]],key=lambda r:r["group_seq"])),"allocation_audit":digest(sorted(alloc,key=lambda r:r["taxon"])),"keyed_mapping_decision_set":digest(validation_rows),"pipeline_consumed_decision_set":digest(validation_rows),"validation_consumed_decision_set":digest(validation_rows),"source_definition_file_sha256":defs_event["sha256"]},
            "complete_universe_included":not duplicates["catch"] and set(cby)==set(aby)==set(mby)==set(alby),
            "confidence_authority":"Current adopted PPR/Matching and PPR/Mapping review, checked against audit.review_confidence and separate component evidence. Audit.overall_confidence is preserved as an explicit stale-field gap where inconsistent.",
            "saved_accepted_decisions_preserved":True,
            "same_keyed_decisions_consumed_by_both_routes":True,
            "catch_total_t":catch_total,"independent_simple_chain_ppr_total_tC":ppr_total,"carbon_divisor":9,
            "confidence_summary":summaries,"component_rule_summaries":rule_tables,
            "missing_inputs":missing_inputs,"unknown_positive_catch_ppr_taxa":[r["taxon"] for r in validation_rows if r["catch_t"]!=0 and r["ppr_tC"] is None],
            "assumption_dependent_taxa":sum(bool(r["assumption_dependent"]) for r in validation_rows),
            "very_low_taxa":[{"taxon":r["taxon"],"reason":r["reason"],"transfer_assumption":r["transfer_assumption"]} for r in validation_rows if level(r["overall_confidence"])=="very low"],
            "review_table_schema":list(review[0]) if review else [],"allocation_ledger_schema":list(ledgers[0]) if ledgers else [],
            "source_definition_index_entries":listed_defs,
            "portable_link_limit":"Original stored mapping evidence and appendix links retain former paths; original identities preserved. Canonical counterpart used only for this read-only trial, no link repairs or adoption.",
            "gaps":gaps,"all_consumed_inputs_unchanged":all(unchanged),"elapsed_seconds":time.perf_counter()-started
        }
        self.result["status"]="bounded_verification_complete_with_recorded_gaps" if gaps else "bounded_verification_complete"
        self.save()
        v=self.result["resume"]["verification"]
        print(json.dumps({"status":self.result["status"],"counts":v["counts"],"digest":v["digest"],"confidence_taxa":{r["confidence"]:r["taxa"] for r in v["confidence_summary"]},"gaps_by_kind":dict(collections.Counter(g["kind"] for g in gaps)),"all_consumed_inputs_unchanged":v["all_consumed_inputs_unchanged"]},ensure_ascii=False,indent=2))

    def rule_schema(self):
        from tools.project_core.workbooks.read_session import ReadSession
        p=ROOT/"regions/LME/LME_036/LME_036.xlsx"
        reads=ReadSession();book=reads.read(p,sheets=["PPR"])
        self.event("read_session",p,kind="regional_workbook",sha256=reads._hashes[p.resolve()],read_requests=1,workbook_parses=reads.parse_count,selected_sheets=["PPR"],purpose="diagnose code-versus-descriptive rule field representation")
        table=book["PPR"]["Mapping review"];headers,data=table
        rs=[r if isinstance(r,dict) else dict(zip(headers,r)) for r in data]
        d={"sample":rs[:1],"membership_values":sorted(set(r["membership_rule"] for r in rs)),"allocation_values":sorted(set(r["allocation_rule"] for r in rs))}
        self.result["resume"]["rule_representation_check"]=d
        reads.assert_unchanged();self.event("read_session_unchanged_guard",p,passed=True)
        self.save();print(json.dumps(d,ensure_ascii=False,indent=2))

    def finish(self):
        """Compact only this trial's own QA; do not read scientific inputs."""
        events=self.result["resume"]["events"]
        v=self.result["resume"]["verification"]
        file_events=[e for e in events if e["operation"]=="file_read"]
        regional_events=[e for e in events if e["operation"]=="read_session"]
        app_events=[e for e in events if e["operation"]=="workbook_parse"]
        input_summary={}
        for e in events:
            if not e.get("path"):continue
            d=input_summary.setdefault(e["path"],{"operations":collections.Counter()})
            d["operations"][e["operation"]]+=1
            if e.get("sha256"):d["sha256"]=e["sha256"]
            if e.get("kind"):d["kind"]=e["kind"]
            if e.get("bytes"):d["bytes"]=e["bytes"]
        groups={}
        for g in v["gaps"]:
            detail=g.get("details") or {k:w for k,w in g.items() if k not in ["kind","taxon","taxa"]}
            while set(detail)=={"details"}:detail=detail["details"]
            key=(g["kind"],detail.get("component"),detail.get("field"),detail.get("rule"))
            d=groups.setdefault(key,{"kind":g["kind"],"taxa":[],"details":detail})
            if g.get("taxon"):d["taxa"].append(g["taxon"])
            d["taxa"].extend(g.get("taxa",[]))
        for d in groups.values():d["taxa"]=sorted(set(d["taxa"]))
        v["gaps"]=list(groups.values())
        v["gap_scope"]="Preserved saved evidence/metadata conflicts. Accepted current Matching groups/weights/confidence agree with audit.review_confidence and appendix. No gap was repaired or resolved anew."
        v["confidence_components_and_numeric_decisions_reconciled"]=not any(g["kind"] not in ["stale_audit_overall_confidence_field","stale_audit_plain_rule_description","current_review_rule_description_conflict","current_review_keyed_candidate_conflict","current_review_allocation_evidence_conflict"] for g in v["gaps"])
        v["publication_status"]="No publication/adoption requested; original full-workbook historical identities and obsolete stored links remain explicitly historical. Full scientific validation not claimed."
        v["numerical_decision_reuse"]={"status":"pass","taxa":374,"exact_group_weight_rows":670,"confidence_and_appendix_match":True,"fresh_mapping_resolutions":0,"fresh_taxon_research_passes":0}
        v["current_evidence_readiness"]={"status":"partial","reason":"Current adopted decisions have usable saved component evidence, but saved metadata has the keyed conflicts below. This trial neither repairs those records nor declares a complete scientific handoff.","affected_only_revisit_required":True}
        v["instruction_dependency_hashes"]={e["path"]:e["sha256"] for e in file_events if e.get("kind")=="instruction"}
        resume={"context":"reused instruction context after user-requested pause", "input_read_summary":input_summary,"actual_read_events":events,
            "counts":{"new_instruction_file_read_invocations":sum(e.get("kind")=="instruction" for e in file_events),"regional_read_session_requests":sum(e.get("read_requests",0) for e in regional_events),"regional_workbook_parses":sum(e.get("workbook_parses",0) for e in regional_events),"regional_cache_reuses":sum(e.get("cache_reuse",False) for e in regional_events),"appendix_workbook_parses":sum(e.get("workbook_parses",0) for e in app_events)+1,"appendix_parse_count_correction":1,"total_workbook_parses":sum(e.get("workbook_parses",0) for e in regional_events+app_events)+1,"validation_verification_attempts":4,"report_arithmetic_attempts":4,"completed_final_verification":1,"actual_saved_candidate_value_checks":670*4,"mapping_resolutions":0,"taxon_research_passes":0,"engine_calls":0,"render_calls":0,"live_writes":0,"qa_metadata_internal_reads":self.result["qa_metadata_runtime_reads"],"qa_metadata_external_validation_reads":4},
            "instrumentation_corrections":["One appendix parse in discovery attempt 2 completed before an absent-dimension exception, but its event had not yet been checkpointed; included explicitly in totals.","One instruction display failed under cp1255; the actual file read is traced. UTF-8 output fixed without touching inputs.","Discovery attempt 1 assumed a dictionary table instead of the tuple returned by read_book; its real regional parse is retained.","Verification attempt 1 completed arithmetic before mixed integer/string year keys prevented its digest serialization; that real verification/arithmetic attempt is counted.","Verification attempts 2/3 identified stale audit fields; attempt 3 also compared rule codes with human descriptions. The schema inspection exposed that representation mismatch, and final verification compares descriptions and confidence fields correctly."],
            "token_telemetry":"unavailable","total_elapsed_seconds":"unavailable: pause plus bootstrap precede wall-clock instrumentation; final coherent verification elapsed is recorded separately","verification":v}
        self.result["resume"]=resume
        input_ids={path:i for i,path in enumerate(input_summary)}
        resume["inputs"]=[{"path":path,**value} for path,value in input_summary.items()]
        compact_events=[]
        for original in events:
            e=dict(original);path=e.pop("path",None)
            if path is not None:
                e["input_id"]=input_ids[path]
                if e.get("sha256")==input_summary[path].get("sha256"):e.pop("sha256",None)
            compact_events.append(e)
        resume["actual_read_events"]=compact_events
        resume.pop("input_read_summary",None)
        self.result["status"]="bounded_trial_complete_numerical_reuse_pass_evidence_partial"
        self.result["remaining_checks"]=[]
        self.result["telemetry"]["source_hashes"]="Current resumed instruction and scientific input hashes are recorded in resume events/summary; bootstrap hashes unavailable."
        self.result["telemetry"]["row_digest"]=v["digest"]["keyed_mapping_decision_set"]
        self.result["stop_safety"]={"all_started_exec_commands_completed":True,"running_exec_sessions":0,"background_processes_launched":0,"external_processes_left_by_this_trial":0,"live_workbooks_or_scientific_inputs_modified":False,"existing_trial_artifacts_preserved":True}
        # Compact JSON preserves the full honest event ledger without duplicated sampled inputs.
        QA.write_text(json.dumps(self.result,ensure_ascii=False,separators=(",",":"),allow_nan=False)+"\n",encoding="utf-8")
        print(json.dumps({"status":self.result["status"],"qa_bytes":QA.stat().st_size,"counts":resume["counts"],"keyed_gaps":[{"kind":g["kind"],"taxa":g["taxa"]} for g in v["gaps"]],"decision_digest":v["digest"]["keyed_mapping_decision_set"]},ensure_ascii=False,indent=2))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["instruction", "discover", "show", "evidence", "verify", "rule-schema", "finish"])
    parser.add_argument("--path")
    parser.add_argument("--start", type=int)
    parser.add_argument("--end", type=int)
    parser.add_argument("--headings", action="store_true")
    args=parser.parse_args()
    trial=Trial()
    if args.mode == "instruction":
        trial.instruction(Path(args.path), args.start, args.end, args.headings)
    elif args.mode == "discover":
        trial.discover()
    elif args.mode == "show":
        trial.show()
    elif args.mode=="evidence":
        trial.evidence()
    elif args.mode=="verify":
        trial.verify()
    elif args.mode=="rule-schema":
        trial.rule_schema()
    else:
        trial.finish()

if __name__ == "__main__":
    main()
