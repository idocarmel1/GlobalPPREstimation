"""Retain publication receipts and remove only proved redundant task scratch."""
from pathlib import Path
import hashlib, importlib.util, json

RUN=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('combined_publication',RUN/'code/combined_publication.py')
publication=importlib.util.module_from_spec(spec);spec.loader.exec_module(publication)
ROOT=publication.ROOT
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text('utf-8'))
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

result=read(RUN/'qa/combined_publication.json')
controls=read(RUN/'qa/published_controls.json')
ui=read(RUN/'qa/ui_verification.json')
assert result['passed'] and controls['passed'] and ui['passed']
assert ui['project_sha256']==result['project_sha256']
assert sha(ROOT/'Project.xlsx')==result['project_sha256']
assert not (ROOT/'.project-write.lock').exists(),'Publication is still active'
for filename in ['index.html','trends.html']:
    assert sha(ROOT/'interactive_map'/filename)==result[filename+'_sha256']
for unit,evidence in result['units'].items():
    model=publication.MODELS[unit]
    assert sha(model/'model_validation/validation.docx')==evidence['report_sha256']
    receipt={
        'schema_version':1,'unit_id':unit,**evidence,
        'project_sha256':result['project_sha256'],
        'pages':{name:result[name+'_sha256'] for name in ['index.html','trends.html']},
        'publication_timestamp_utc':result['timestamp_utc'],
        'scientific_runs':0,'new_monte_carlo_draws':0,
        'scope':'Signed decision publication and explicitly authorized retained-package adoption; no renewed scientific approval.',
        'combined_evidence':(RUN/'qa/combined_publication.json').relative_to(ROOT).as_posix(),
        'controls_evidence':(RUN/'qa/published_controls.json').relative_to(ROOT).as_posix(),
        'browser_evidence':(RUN/'qa/ui_verification.json').relative_to(ROOT).as_posix(),
        'retained_numeric_adoption':unit in publication.ADOPT,
    }
    write(model/'model_validation/evidence/source_review/coordinator_publication_20261114.json',receipt)

model598=publication.MODELS['EEZ_598'];model38=publication.MODELS['LME_038'];model49=publication.MODELS['LME_049']
work598=model598/'model_validation/work';work38=model38/'model_validation/work';work49=model49/'model_validation/work'
caches=[
    work598/'2026-11-14_160800_floor_adoption/code/__pycache__/stage_floor_adoption.cpython-313.pyc',
    work598/'2026-11-14_160800_floor_adoption/code/__pycache__/verified_floor_packages.cpython-313.pyc',
    RUN/'code/__pycache__/retained_packages.cpython-313.pyc',
    RUN/'code/__pycache__/combined_publication.cpython-313.pyc',
    work38/'2026-11-14_152558_signoff/code/__pycache__/adopt_current_diagnostics.cpython-313.pyc',
    work49/'2026-11-14_183000_map_adoption/code/__pycache__/stage_lme049_adoption.cpython-313.pyc',
    work49/'2026-11-14_183000_map_adoption/code/__pycache__/verified_lme049_package.cpython-313.pyc',
    work49/'2026-11-14_183000_map_adoption/code/guard_patch/__pycache__/ee_floor_layout_candidate.cpython-312.pyc',
]
removals=[(p,'Rebuildable Python bytecode; source retained',None) for p in caches if p.is_file()]
render=work598/'2026-11-14_173000_eez598_validation/qa'
for number in [1,3,4,5]:
    old,final=render/f'page-{number}.png',render/f'final-page-{number}.png'
    if old.is_file():
        assert final.is_file() and sha(old)==sha(final),'Render duplicate is no longer identical'
        removals.append((old,'Byte-identical duplicate of retained final render',final))
ledger=[]
for candidate,reason,retained in removals:
    resolved=candidate.resolve()
    assert resolved.is_relative_to(ROOT) and not candidate.is_symlink()
    ledger.append({'path':candidate.relative_to(ROOT).as_posix(),'sha256':sha(candidate),'bytes':candidate.stat().st_size,
                   'reason':reason,'retained_equivalent':retained.relative_to(ROOT).as_posix() if retained else None})
write(RUN/'qa/cleanup.json',{'removed':ledger,'kept':'All provenance-linked original packages, importers, snapshots, ledgers, source records and referenced QA.'})
for candidate,_,_ in removals:candidate.unlink()
assert all(not candidate.exists() for candidate,_,_ in removals)
print(json.dumps({'publication_receipts':len(result['units']),'redundant_files_removed':len(ledger),'bytes_removed':sum(x['bytes'] for x in ledger)}))
