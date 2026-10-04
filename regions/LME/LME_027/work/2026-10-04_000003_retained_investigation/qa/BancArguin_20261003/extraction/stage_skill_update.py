from pathlib import Path
import json,hashlib,shutil
here=Path(__file__).resolve().parent;installed=Path('C:/Users/idoca/.agents/skills/ecopath-extraction');staged=here/'skill_update';staged.mkdir(exist_ok=True)
targets=['scripts/write_outputs.py','scripts/database_json.py','SKILL.md','references/output-formats.md','references/workflow.md','references/diet-source-runtime.md']
checks={}
for rel in targets:
    p=installed/rel;q=staged/rel;q.parent.mkdir(exist_ok=True);q.write_bytes(p.read_bytes());checks[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
(here/'skill_update_original_hashes.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
shutil.copyfile(here/'source_fidelity.py',staged/'scripts/source_fidelity.py')
p=staged/'scripts/write_outputs.py';s=p.read_text(encoding='utf-8')
s=s.replace('    write_xlsx(model, outdir)\n','    write_xlsx(model, outdir)\n    from source_fidelity import write_companions\n    write_companions(model, outdir)\n    (outdir / "model.json").write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")\n')
# Unknown prey cells are never silently summed into a known total. Explicit source blanks can be reviewed in a separate known-cell sum ledger.
s=s.replace('        sums.append("" if import_unknown else dec_str(total))','        prey_unknown = any(v is None or str(v).strip() in ("", "-9999") for k, v in col.items() if k != "import")\n        sums.append("" if import_unknown or prey_unknown else dec_str(total))')
p.write_text(s,encoding='utf-8')
p=staged/'scripts/database_json.py';s=p.read_text(encoding='utf-8')
s=s.replace('        final_json = {"group": groups_json}','        from source_fidelity import preserve_source\n        final_json = preserve_source(input_dir, {"group": groups_json})\n        groups_json = final_json["group"]\n        diet_source_sums = final_json["source_fidelity"]["diet_sums"]')
s=s.replace('f"    - Detritus fate sum is not 1 ({total_fate:.5f}). Normalizing to 1.0")\n                    det_norm_factor = 1.0 / total_fate\n                    for p_seq in group_diet_map:\n                        group_diet_map[p_seq]["detritus_fate"] *= det_norm_factor','f"    - Detritus fate sum is not 1 ({total_fate:.5f}); preserving source values")')
s=s.replace("with open(output_json, 'w') as f:","with open(output_json, 'w', encoding='utf-8') as f:")
s=s.replace("with open(json_path, 'r') as f:","with open(json_path, 'r', encoding='utf-8') as f:")
s=s.replace("        groups = data.get('group', [])\n        if not groups:","        if data.get('extraction_source_tables'):\n            from source_fidelity import reconstruct_source_workbook\n            return reconstruct_source_workbook(data, output_excel)\n\n        groups = data.get('group', [])\n        if not groups:")
p.write_text(s,encoding='utf-8')
print(staged)
