"""Package completed document QA and portable evidence; no science or selection writes."""
from pathlib import Path
import hashlib
import json
import os

E = Path(__file__).resolve().parent
R = E.parents[3]
REGION = E.parents[1]
C = REGION / "models/52_GM2019_Fig9_Pelagic_(2000-2014)"
A = C / "assumption_variants/adopted_balanced_20261003"
I = C / "research_20261003/integration"


def read(p):
    return json.loads(p.read_text(encoding="utf-8"))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rel(p):
    return Path(os.path.relpath(p,E)).as_posix()


def main():
    spec = read(E / "report_inputs.json")
    content = read(E / "report_content_verification.json")
    structural = read(E / "document_structural_verification.json")
    qa = read(E / "visual_inspection.json")
    map_gate = read(E / "map_alignment_confirmed.json")
    assert not spec["provenance"]["pending_map_alignment"]
    assert not content["pending_map_alignment"]
    assert map_gate["alignment_passed"] is True
    assert qa["all_pages_inspected"] is True
    model_hash = sha(A / "model.json")
    assert model_hash == spec["provenance"]["model_sha256"] == content["exact_model_sha256"]
    for report in qa["reports"]:
        doc = R / report["docx_path"]
        pdf = E / report["pdf_path"]
        assert sha(doc) == report["docx_sha256"] == content["report_hashes"][doc.name]
        assert sha(pdf) == report["pdf_sha256"]
        assert [p["page"] for p in report["pages"]] == list(range(1,report["page_count"]+1))
        assert all(sha(E/p["image_path"]) == p["sha256"] and p["reviewed"] is True for p in report["pages"])
    artifacts = []
    def add(role,path):
        assert path.is_file(),path
        artifacts.append({"role":role,"availability":"present","path":rel(path),"sha256":sha(path)})
    pairs = [
        ("validation_docx",REGION/spec["validation_filename"]),("article_departures_docx",REGION/spec["departures_filename"]),
        ("taxon_appendix",REGION/"52_GM2019_Fig9_Pelagic_balanced_(2000-2014)_taxon_mapping_appendix.xlsx"),
        ("original_researcher_validation",REGION/"Model_validation_52_1_Sea_of_Okhotsk_NE_(1980).docx"),
        ("current_template",R/"tools/templates/Model_validation_template.docx"),
        ("native_input",A/"model.json"),("runtime_settings",A/"runtime_settings.json"),
        ("source_to_final_ledger",A/"source_to_final_ledger.json"),("food_components",A/"food_component_ledger.json"),
        ("final_carbon_flows",A/"carbon_food_flows.json"),("native_reload",A/"native_reload_result.json"),
        ("native_evidence_index",A/"evidence_index.json"),("native_reload_consistency",A/"reload_consistency.json"),
        ("all_arrow_decisions",A/"all_arrow_decisions.json"),("alternative_hypotheses",A/"alternative_hypotheses.json"),
        ("mandatory_cases",A/"case_coverage.json"),("microbial_consistency",A/"microbial_split_consistency.json"),
        ("F62_sensitivity_summary",A/"sensitivity/F62_summary.json"),("F62_all_group_comparisons",A/"sensitivity/F62_scoped_SPPR_comparison.csv"),
        ("constructor_roundtrip",A/"ewe_roundtrip_verification.json"),("actual_import_returns",A/"export_tool_results.json"),
        ("source_fidelity",A/"ewe_imports/SOURCE_FIDELITY_CHECK.json"),
        ("independent_native_gate",C/"research_20261003/completion_integration/independent_final_gate.json"),
        ("taxon_audit",I/"taxon_audit.json"),("mapping_summary",I/"mapping_summary.json"),
        ("allocation_ledger",I/"allocation_ledger.json"),("carbon_unit_bridge",I/"carbon_unit_bridge.json"),
        ("regional_science_verification",I/"regional_science_verification.json"),
        ("regional_adoption_verification",I/"regional_adoption_verification.json"),
        ("map_alignment",E/"map_alignment_confirmed.json"),("report_inputs",E/"report_inputs.json"),
        ("manual_field_inheritance",E/"inherited_manual_fields.json"),("report_content_verification",E/"report_content_verification.json"),
        ("document_structure_and_relative_links",E/"document_structural_verification.json"),
        ("full_matrix_inspection",E/"diagnostic_matrix_inspection.json"),("all_page_visual_review",E/"visual_inspection.json"),
        ("geography_assessment",E/"geography/geography_assessment.json"),
        ("target_geography_figure",E/"geography/target_LME052_intended_whole_sea.png"),
        ("source_sampling_figure",E/"geography/GM2019_Figure1_original_sampling.png"),
    ]
    for method in ("GE","TE","With_Egestion"):
        pairs.append((method+"_actual_full_return",A/"diagnostics"/(method+"_full_return.json")))
    for pair in pairs:
        add(*pair)
    for report in qa["reports"]:
        add(report["short_name"]+"_rendered_pdf",E/report["pdf_path"])
        for page in report["pages"]:
            add(report["short_name"]+"_reviewed_page_"+str(page["page"]),E/page["image_path"])
    required = [a["role"] for a in artifacts]
    index = {
        "schema_version":1,"run_id":"LME052_GM2019_adopted_reports_20261003","region_id":"LME_052",
        "model_id":spec["model_id"],"variant_id":"adopted_balanced_20261003",
        "source_identity":{"paper_id":"OKH-GM2019__LME_052","source_groups":22,"period":"2000–2014"},
        "computational_input_identity":{"sha256":model_hash,"settings":read(A/"runtime_settings.json")},
        "methods":["GE","TE","With Egestion"],"required_roles":required,"artifacts":artifacts,
        "reconciliation":{
            "exact_frozen_input":True,"every_native_input_change_in_report":True,"every_food_component_in_report":True,
            "all_very_low_taxa_once":True,"same_input_full_matrix_checks":True,
            "original_researcher_report_and_template_preserved":True,"manual_sppr_preserved":True,
            "all_final_rendered_pages_inspected":True,"relative_links_resolve_after_relocation":True,
            "map_alignment_confirmed_by_root":True,
        },
        "scientific_limits":{"human_validated":False,"production_eligible":False,"actual_methods":"all WARN",
            "annual_and_map_use":"provisional","Monte_Carlo":"NOT_RUN","global":"NOT_RUN",
            "detritus":"large nonsteady routing residual; not measured storage/burial","geography":"approximate whole-Sea envelope, not measured author polygon"},
        "purpose":"Document handoff and evidence integrity. This index is not model-selection authority or researcher approval."
    }
    (E/"evidence_index.json").write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding="utf-8")
    target_src = REGION/"validation_reports/52_1_Sea_of_Okhotsk_NE_(1980)/geography/target_and_intended_domain.png"
    sample_src = REGION/"papers/OKH-GM2019/English_translation_work/figure_1_original.png"
    assert sha(target_src) == sha(E/"geography/target_LME052_intended_whole_sea.png")
    assert sha(sample_src) == sha(E/"geography/GM2019_Figure1_original_sampling.png")
    lines = [
        "# Adopted GM2019 report evidence", "", "Model: `"+spec["model_id"]+"`. Native SHA256: `"+model_hash+"`.", "",
        "Created from the current validation template for researcher review. Decision, researcher name and review date remain unfilled. All three direct methods are WARN; annual/map values remain provisional.", "",
    ]
    for label,path in (("Validation report",REGION/spec["validation_filename"]),("Every article departure",REGION/spec["departures_filename"]),("Taxon appendix with Sources",REGION/"52_GM2019_Fig9_Pelagic_balanced_(2000-2014)_taxon_mapping_appendix.xlsx")):
        lines.append("- ["+label+"]("+rel(path)+") — SHA256 `"+sha(path)+"`.")
    lines += ["", "Both DOCX files were rendered through an independent hidden Word instance, opened read-only with macros disabled, and exported without saving. The packaged LibreOffice renderer was unavailable on this host. Every final page image was inspected; page counts and hashes are in [visual inspection](visual_inspection.json).", "",
        "[Content reconciliation](report_content_verification.json) checks all 448 changed native inputs, all 74 food components and all 115 Very low labels. [Structure and portability](document_structural_verification.json) preserves the original researcher report, template and exact manual SPPR cell, checks blue underlined relative links and relocates their targets under a different repository root. [Manual field inheritance](inherited_manual_fields.json) retains the old model's manual entries; its SD-sensitivity note is not a GM2019 result.", "",
        "Geographic assets preserve source pixels: the generic LME target figure is copied from [the prior target figure]("+rel(target_src)+"), SHA256 `"+sha(target_src)+"`; the sampling figure is copied from [primary Figure 1 pixels]("+rel(sample_src)+"), SHA256 `"+sha(sample_src)+"`. New interpretations are this review's explicitly approximate [geographic assessment](geography/geography_assessment.json). They do not claim measured overlap or an author GIS boundary.", "",
        "[Map alignment evidence](map_alignment_confirmed.json) records the independently verified final integration. [Portable artifact inventory](evidence_index.json) and [inventory check](evidence_index_check.json) provide the complete report handoff. These supporting records do not grant scientific approval or alter selection.", "",
    ]
    (E/"reports_index.md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps({"artifact_count":len(artifacts),"model_sha256":model_hash,"reports_pages":{r["short_name"]:r["page_count"] for r in qa["reports"]}}))


if __name__ == "__main__":
    main()
