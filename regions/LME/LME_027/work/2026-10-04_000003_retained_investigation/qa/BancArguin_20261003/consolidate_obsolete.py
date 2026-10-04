"""Consolidate explicitly authorized obsolete Banc files after byte-exact archive checks."""
from pathlib import Path
import hashlib,json,shutil,zipfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];REGION=ROOT/'regions/LME_027'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
manifest=load(HERE/'baseline/manifest.json');archive=HERE/'baseline'/manifest['archive']
assert sha(archive)==manifest['archive_sha256']
cross=load(HERE/'extraction/old_to_canonical_mapping.json')
assert len(cross)==4 and {x['variant'] for x in cross}=={'Base','M30','P30'}
for rec in cross:
    model=ROOT/rec['canonical_directory']/'model.json'
    assert sha(model)==rec['new_sha256']
    assert load(model.parent/'extracted_tables/ROUNDTRIP_CHECK.json')
assert load(HERE/'extraction/completeness.json')['complete']
assert load(HERE/'mapping/completeness.json')['complete']
assert len(load(HERE/'qa/final_docx_acceptance.json'))==3
targets=[(ROOT/rec['old_directory']).resolve() for rec in cross]+[(REGION/'papers/CAN-2014/extracted').resolve()]
expected={p.resolve() for p in targets}
assert len(expected)==5
for target in targets:
    assert target.is_relative_to(REGION.resolve()) and target!=REGION.resolve()
    assert target.parent in {(REGION/'models').resolve(),(REGION/'papers/CAN-2014').resolve()}
    assert target.exists() and target.is_dir() and not target.is_symlink()
    assert not target.name.startswith('Guenette')
archive_rows={r['path']:r for r in manifest['archived_files']}
with zipfile.ZipFile(archive) as z:
    assert len(z.namelist())==len(archive_rows)
    for path,rec in archive_rows.items():
        assert hashlib.sha256(z.read(path)).hexdigest()==rec['sha256']
    actual=[]
    for target in targets:
        for path in target.rglob('*'):
            if path.is_file():
                rel=path.relative_to(ROOT).as_posix();assert rel in archive_rows
                assert sha(path)==archive_rows[rel]['sha256'],rel
                actual.append(rel)
    assert set(actual)==set(archive_rows),'Some archived files lie outside cleanup targets'
# All absolute target boundaries and every replacement/archive were verified above.
for target in targets:shutil.rmtree(target)
for target in targets:assert not target.exists()
paper_index=REGION/'papers/CAN-2014/extracted';paper_index.mkdir()
rows=['# Current Banc d’Arguin extraction and assessment\n','Guénette, Meissa and Gascuel (2014), DOI 10.1371/journal.pone.0094742. Three distinct 1991 parameterizations; candidate results are not adopted regional results.\n']
for v in ('Base','M30','P30'):
    mid=f'Guenette2014_BancArguin_{v}_1991'
    rows.append(f'- **{v}:** [canonical JSON](../../../models/{mid}/model.json), [extraction report and imports](../../../models/{mid}/extracted_tables/REPORT.md), [regional assessment](../../../models/{mid}/regional_assessment/assessment.json), [validation DOCX](../../../Model_validation_{mid}.docx), [Excel appendix](../../../LME027_Guenette2014_{v}_taxon_mapping_appendix.xlsx).')
rows+=['','Base source admission fails; a separately identified runtime experiment returns FAIL for all direct methods. M30/P30 have 114 unpublished variant diet components each and no independent model SPPR or PPR.','', '[Assessment evidence and results](../../../validation_reports/BancArguin_20261003/evidence_index.json) · [Superseded files, preserved byte-for-byte](../../../validation_reports/BancArguin_20261003/baseline/superseded_Banc_evidence.zip) · [Archive manifest](../../../validation_reports/BancArguin_20261003/baseline/manifest.json).','','The archive contains the two obsolete Base folders, former M30/P30 folders, and stale paper extraction outputs. Unique source evidence and provenance remain recoverable. Original publications, Northwest Africa 1987, the Morissette2009 candidate, and selected regional numerical outputs are preserved.']
(paper_index/'MASTER_INDEX.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
result={'cleanup_performed':True,'removed_directories':[p.relative_to(ROOT).as_posix() for p in targets],'archived_files_verified':len(archive_rows),'archive_sha256':sha(archive),'one_canonical_directory_per_variant':True,'new_index':(paper_index/'MASTER_INDEX.md').relative_to(ROOT).as_posix()}
(HERE/'cleanup.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
