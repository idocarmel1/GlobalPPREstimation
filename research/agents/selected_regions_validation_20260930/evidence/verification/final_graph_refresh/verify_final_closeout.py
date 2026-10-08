"""Final current-byte acceptance, run after publication and before commit."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess
from urllib.parse import unquote

R=Path.cwd()
B=R/'original_research_archive/research/selected_regions_validation_20260930'
V=B/'verification'


def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.run(['git',*args],capture_output=True,check=True).stdout


def main():
    assert git('branch','--show-current').decode().strip()=='codex/validate-all-23-regions'
    git('merge-base','--is-ancestor','d14c71a9','HEAD')
    d=read(B/'final_23_region_status.json')
    assert len(d['regions'])==23 and len({r['unit_id'] for r in d['regions']})==23
    checked=[]
    for row in d['regions']:
        assert row['scientific_approval_claimed'] is False
        assert row['accepted_manual_researcher_fields_preserved'] is True
        for evidence in list(row['artifacts'].values())+[row['protected_canonical_model']]:
            p=R/evidence['path'];assert sha(p)==evidence['sha256'],p
            checked.append(evidence)
    assert sha(R/'Project.xlsx')==d['project_sha256']
    for evidence in d['verification']:
        assert sha(R/evidence['path'])==evidence['sha256'],evidence
    protected=read(V/'final_all23_protected_inputs_and_serialization.json')
    assert protected['status']=='PASS' and len(protected['checks'])==23
    for x in protected['checks']:assert sha(R/x['workbook'])==x['sha256'],x
    generated=read(V/'final_generated_outputs.json')
    for x in generated['files']:assert sha(R/x['path'])==x['sha256'],x
    tests=read(V/'final_workflow_test_acceptance.json')
    assert tests['tests']==56 and tests['status']=='PASS'
    for p,h in tests['current_source_hashes'].items():assert sha(R/p)==h,p
    assert sha(R/tests['evidence']['path'])==tests['evidence']['sha256']
    office=read(V/'final_all23_office_confidence_checkpoint.json')
    assert office['status']=='PASS' and len(office['regions'])==23
    for row in office['regions']:
        regional=next(r for r in d['regions'] if r['unit_id']==row['unit_id'])
        for k in ['report','appendix']:
            assert row[k]['file_sha256']==regional['artifacts'][k]['sha256'],(row['unit_id'],k)
    graph=R/'tools/knowledge_graph'
    hashes=read(graph/'source_hashes.json')
    for p,h in hashes.items():assert sha(R/p)==h,p
    publication=read(graph/'publication_manifest.json')
    for p,h in publication['files'].items():assert sha(graph/p)==h,p
    assert read(graph/'completion_verification.json')['status']=='PASS'
    link_count=0
    for target in re.findall(r'\]\(<([^>]+)>\)',(B/'final_validation_status.md').read_text(encoding='utf-8')):
        p=(B/unquote(target)).resolve();assert p.is_relative_to(R) and p.is_file(),target
        link_count+=1
    assert link_count==46,link_count
    tracked=set(p.decode() for p in git('ls-files','-z').split(b'\0') if p)
    untracked=set(p.decode() for p in git('ls-files','--others','--exclude-standard','-z').split(b'\0') if p)
    changed=set(p.decode() for p in git('diff','--name-only','-z').split(b'\0') if p)
    staged=set(p.decode() for p in git('diff','--cached','--name-only','-z').split(b'\0') if p)
    files=sorted(untracked|changed|staged)
    assert all((R/f).is_file() for f in files)
    assert not [f for f in files if (R/f).stat().st_size>=100*1024*1024], 'GitHub file-size limit'
    assert not [f for f in untracked if '/work/' in f or '/node_modules/' in f or '/__pycache__/' in f]
    result={'status':'PASS_BEFORE_COMMIT','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':'codex/validate-all-23-regions','base_commit_ancestor_verified':'d14c71a9d2e9f168af8c12e2ccd04c2d861df1cc','selected_regions':23,'current_regional_artifact_identities_checked':len(checked),'protected_serialized_cells':protected['serialized_cells'],'current_office_artifacts':46,'workflow_tests':56,'graph_sources':len(hashes),'graph_output_hashes_checked':len(publication['files']),'master_portable_report_links':link_count,'current_generated_files':generated['files'],'reviewed_scientific_status_sha256':sha(B/'final_23_region_status.json'),'untracked_or_changed_file_count':len(files),'untracked_or_changed_bytes':sum((R/f).stat().st_size for f in files),'git_push':'Must still be performed and remotely verified; this receipt does not claim publication.'}
    (V/'final_closeout_acceptance.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))


if __name__=='__main__':main()
