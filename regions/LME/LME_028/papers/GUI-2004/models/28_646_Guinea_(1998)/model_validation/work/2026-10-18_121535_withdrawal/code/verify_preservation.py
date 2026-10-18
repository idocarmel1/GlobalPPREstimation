"""Compare the initial byte baseline with the completed administrative changes."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
RUN=Path(__file__).resolve().parents[1]
BASE=json.loads((RUN/'qa/baseline.json').read_text(encoding='utf-8'))
MODEL='regions/LME/LME_028/papers/GUI-2004/models/28_646_Guinea_(1998)'
ALLOWED={'Project.xlsx','interactive_map/index.html','interactive_map/trends.html',
         'research/README.md','tools/knowledge_graph/REFRESH_SCOPE.md',
         MODEL+'/model_notes.md',MODEL+'/model_validation/validation.docx'}
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
changed={};unchanged=[]
for rel,before in BASE['protected_sha256'].items():
    path=ROOT/rel
    after=sha(path) if path.is_file() else None
    if after==before:unchanged.append(rel)
    else:changed[rel]={'before':before,'after':after}
assert set(changed)==ALLOWED,{'unexpected':sorted(set(changed)-ALLOWED),'missing':sorted(ALLOWED-set(changed))}
historical=[]
for prefix in BASE['historical_packages']:
    before={p for p in BASE['protected_sha256'] if p.startswith(prefix+'/')}
    after={p.relative_to(ROOT).as_posix() for p in (ROOT/prefix).rglob('*') if p.is_file()}
    assert before==after,('Historical file membership changed',prefix,before^after)
    assert not before.intersection(changed),prefix
    historical.append({'path':prefix,'files_unchanged':len(before)})
prior_readme=Path(BASE['temporary_rollback'])/'README.md'
if prior_readme.is_file():
    # Original researcher additions must remain; only new current-cohort lines
    # are appended/inserted by this task.
    current=iter((ROOT/'research/README.md').read_text(encoding='utf-8').splitlines())
    for line in prior_readme.read_text(encoding='utf-8').splitlines():
        assert any(candidate==line for candidate in current),'Original research-index line altered: '+line
result={'protected_files':len(BASE['protected_sha256']),'unchanged_files':len(unchanged),
        'changed_authorities_and_generated_views':changed,'historical_packages':historical,
        'all_regional_workbooks_and_saved_science_unchanged':True,
        'mapping_workbook_unchanged':MODEL+'/model_validation/taxon_mapping.xlsx' in unchanged,
        'sources_page_and_generated_data_unchanged':all(p in unchanged for p in BASE['protected_sha256'] if p=='interactive_map/sources.html' or p.startswith('interactive_map/data/')),
        'preexisting_source_ledger_edits_unchanged':'common_reference_data/provenance/source_paths.csv' in unchanged,
        'temporary_rollback_removed':not Path(BASE['temporary_rollback']).exists(),
        'git_status':subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True)}
assert result['mapping_workbook_unchanged']
(RUN/'qa/preservation_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['changed_authorities_and_generated_views','git_status']},indent=2))
