"""Finalize only report-related entries after the root supplies the final DOCX/QA.

Prepared but not executed. Default invocation is a model-local preview; --apply
updates evidence/evidence_index.json and its completeness.json only after the
candidate passes the maintained evidence checker. No scientific engine imports.
Scientific artifacts, source/configuration/status metadata, reports, workbooks,
mapping decisions and regional/central publication files are never edited.
"""
from __future__ import annotations
import argparse
import copy
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
sys.dont_write_bytecode=True

RUN=Path(__file__).resolve().parents[1]
VALIDATION=RUN.parents[1]
MODEL=VALIDATION.parent
ROOT=next(p for p in MODEL.parents if (p/'Project.xlsx').exists())
INDEX=VALIDATION/'evidence/evidence_index.json'
COMPLETENESS=INDEX.with_name('completeness.json')
CHECKER=ROOT/'tools/skills/paper-to-ppr/scripts/check_evidence.py'
OLD_QA=VALIDATION/'work/2026-11-14_200000_ices_full_review/qa'
NEW_ROLES=('report_comparison_handoff','primary_model_decision_qa','local_selection_qa',
           'report_verification','report_visual_verification','report_evidence_finalization_code')
REPLACE_ROLES={'report','report_verification','report_visual_verification'}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def dumps(value):return json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
def relative(path,base):return os.path.relpath(path,base).replace('\\','/')

def allowed(path):
    """Accept only explicit workspace files, honoring excluded basenames first."""
    if path.name.casefold()=='notes for ai.txt':raise ValueError('Excluded basename')
    path=(path if path.is_absolute() else ROOT/path).resolve()
    if not path.is_relative_to(ROOT.resolve()):raise ValueError(f'Path outside workspace: {path}')
    if not path.is_file():raise FileNotFoundError(path)
    return path

def artifact(role,path):
    return {'role':role,'path':relative(path,INDEX.parent),'sha256':sha(path),'availability':'present'}

def append_distinct(artifacts,record):
    matches=[r for r in artifacts if r.get('role')==record['role'] and r.get('path')==record['path']]
    if matches:
        if any(r!=record for r in matches):raise ValueError(f'Existing evidence changed: {record["role"]} {record["path"]}')
        return
    artifacts.append(record)

def verify_present(records,except_roles=()):
    failures=[]
    for record in records:
        if record.get('availability')!='present' or record.get('role') in except_roles:continue
        path=allowed((INDEX.parent/record['path']).resolve())
        if sha(path)!=record.get('sha256'):
            failures.append({'role':record.get('role'),'path':record['path'],'reason':'Existing artifact SHA-256 mismatch'})
    if failures:raise ValueError('Unrelated stale evidence must be resolved explicitly; no blanket rehash: '+json.dumps(failures))

def collect_strings(value):
    if isinstance(value,str):yield value
    elif isinstance(value,dict):
        for v in value.values():yield from collect_strings(v)
    elif isinstance(value,list):
        for v in value:yield from collect_strings(v)

def bind_report_qa(path,report_hash):
    """Require the current report and visual QA to identify the actual final bytes."""
    value=read(path)
    if report_hash.casefold() not in {x.casefold() for x in collect_strings(value)}:
        raise ValueError(f'{path.name} does not record the supplied final report SHA-256')
    return value

def prepare(args):
    report=allowed(args.report)
    if report.suffix.casefold()!='.docx' or report.parent!=VALIDATION.resolve():
        raise ValueError('Final DOCX must be directly under this model_validation directory, not a staged inputs/outputs copy')
    expected=args.expected_report_sha256.casefold()
    if sha(report)!=expected:raise ValueError('Final DOCX SHA-256 does not match the supplied expected hash')
    index_before=INDEX.read_bytes();index_before_hash=hashlib.sha256(index_before).hexdigest()
    if args.expected_index_sha256 and index_before_hash!=args.expected_index_sha256.casefold():
        raise ValueError('Evidence index changed since the expected checkpoint')
    original=json.loads(index_before)
    if original.get('schema_version')!=1 or original.get('model_id')!=MODEL.name:
        raise ValueError('Wrong evidence schema/model identity')
    current_reports=[r for r in original['artifacts'] if r.get('role')=='report']
    if len(current_reports)!=1:raise ValueError('Expected exactly one current report artifact')
    # Only the report bytes themselves may already have been replaced by authoring.
    verify_present(original['artifacts'],except_roles={'report'})
    paths={
        'report_comparison_handoff':allowed(args.comparison_handoff),
        'primary_model_decision_qa':allowed(args.primary_decision_qa),
        'local_selection_qa':allowed(args.selection_qa),
        'report_verification':allowed(args.report_verification),
        'report_visual_verification':allowed(args.render_verification),
        'report_evidence_finalization_code':Path(__file__).resolve()}
    # Read JSON as evidence, without inventing scientific checks or approval flags.
    for role,path in paths.items():
        if role!='report_evidence_finalization_code':read(path)
    bind_report_qa(paths['report_verification'],expected)
    bind_report_qa(paths['report_visual_verification'],expected)
    candidate=copy.deepcopy(original);updated=[]
    for record in original['artifacts']:
        role=record.get('role')
        if role=='report':
            updated.append(artifact('report',report))
        elif role in ('report_verification','report_visual_verification'):
            # Preserve the earlier review evidence, but do not label it current.
            old=copy.deepcopy(record);old['role']='historical_'+role
            append_distinct(updated,old)
        else:updated.append(copy.deepcopy(record))
    # Authenticate an already-retained prior report snapshot if available.
    old=current_reports[0];old_path=(INDEX.parent/old['path']).resolve()
    prior_candidates=[RUN/'inputs'/old_path.name]
    if old_path!=report:prior_candidates.append(old_path)
    for prior in prior_candidates:
        if prior.is_file() and sha(prior)==old['sha256']:
            append_distinct(updated,artifact('historical_report',prior));break
    for role,path in paths.items():append_distinct(updated,artifact(role,path))
    candidate['artifacts']=updated
    candidate['required_roles']=list(dict.fromkeys(original['required_roles']+list(NEW_ROLES)))
    # All source/configuration/adoption/approval/reconciliation metadata stays literal.
    assert {k:v for k,v in candidate.items() if k not in ('artifacts','required_roles')}=={
        k:v for k,v in original.items() if k not in ('artifacts','required_roles')}
    for record in original['artifacts']:
        if record.get('role') not in REPLACE_ROLES:assert record in updated
    verify_present(candidate['artifacts'])
    qa=RUN/'qa';qa.mkdir(parents=True,exist_ok=True)
    # Preview has its own relative-link base; the actual candidate retains the
    # evidence-directory base. No current evidence-directory write occurs here.
    preview=copy.deepcopy(candidate)
    for record in preview['artifacts']:
        if record.get('availability')=='present':
            record['path']=relative((INDEX.parent/record['path']).resolve(),qa)
    preview_path=qa/'evidence_index_proposed.json'
    preview_path.write_text(dumps(preview),encoding='utf-8')
    spec=importlib.util.spec_from_file_location('maintained_evidence_checker',CHECKER)
    checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    result=checker.check(preview_path)
    (qa/'evidence_index_proposed_completeness.json').write_text(dumps(result),encoding='utf-8')
    if not result['complete']:raise ValueError('Proposed evidence is incomplete: '+json.dumps(result))
    log={'operation':'Report artifact/evidence finalization only','run_id':RUN.name,
        'timestamp_utc':datetime.now(timezone.utc).isoformat(),'apply_requested':args.apply,
        'index_path':relative(INDEX,RUN),'index_before_sha256':index_before_hash,
        'final_report_path':relative(report,RUN),'final_report_sha256':expected,
        'current_report_roles_replaced':sorted(REPLACE_ROLES),'new_roles':list(NEW_ROLES),
        'scientific_artifact_records_preserved':True,'source_configuration_approval_metadata_preserved':True,
        'project_map_trends_workbooks_untouched':True,'candidate_complete':True,
        'paths':{role:relative(p,RUN) for role,p in paths.items()}}
    if args.apply:
        if INDEX.read_bytes()!=index_before:raise ValueError('Concurrent index change; aborting before write')
        if sha(report)!=expected:raise ValueError('Report changed during finalization')
        verify_present(candidate['artifacts'])
        backup=qa/('evidence_index_before_'+index_before_hash[:12]+'.json')
        if backup.exists():
            if backup.read_bytes()!=index_before:raise ValueError('Backup identity conflict')
        else:backup.write_bytes(index_before)
        temporary=INDEX.with_name('evidence_index.'+RUN.name+'.tmp')
        temporary.write_text(dumps(candidate),encoding='utf-8');os.replace(temporary,INDEX)
        final=checker.check(INDEX)
        if not final['complete']:
            INDEX.write_bytes(index_before)
            raise ValueError('Final check failed; index restored: '+json.dumps(final))
        COMPLETENESS.write_text(dumps(final),encoding='utf-8')
        log.update(index_after_sha256=sha(INDEX),completeness_sha256=sha(COMPLETENESS),
            index_applied=True,final_complete=True)
    else:log['index_applied']=False
    (qa/'report_evidence_finalization.json').write_text(dumps(log),encoding='utf-8')
    print(dumps(log))

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--report',required=True,type=Path)
    ap.add_argument('--expected-report-sha256',required=True)
    ap.add_argument('--expected-index-sha256')
    ap.add_argument('--comparison-handoff',type=Path,default=OLD_QA/'report_comparison_handoff.json')
    ap.add_argument('--primary-decision-qa',type=Path,default=RUN/'qa/report_patch_verification.json')
    ap.add_argument('--selection-qa',type=Path,default=OLD_QA/'selection_status_before_primary_update.json')
    ap.add_argument('--report-verification',type=Path,default=RUN/'qa/report_patch_verification.json')
    ap.add_argument('--render-verification',type=Path,default=RUN/'qa/report_visual_verification.json')
    ap.add_argument('--apply',action='store_true',help='Write the verified current evidence index/completeness; omit for model-local preview only')
    prepare(ap.parse_args())

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');main()
