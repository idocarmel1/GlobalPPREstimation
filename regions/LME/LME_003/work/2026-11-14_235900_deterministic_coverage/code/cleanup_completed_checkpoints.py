"""Retire only hash-inventoried package duplicates after final acceptance."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path

WORK = Path(__file__).resolve().parents[1]
ROOT = next(p for p in WORK.parents if (p/'Project.xlsx').is_file())
CACHE = WORK/'outputs/completion_checkpoints'
PLAN = WORK/'qa/checkpoint_cleanup_plan.json'
LEDGER = ROOT/'common_reference_data/provenance/source_paths.csv'

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_bytes())
def rel(path): return Path(path).relative_to(ROOT).as_posix()

def safe(path):
    path = Path(path)
    if not path.resolve().is_relative_to(ROOT): raise ValueError('Path escaped workspace')
    current = path
    while current != ROOT:
        if current.exists() and (current.is_symlink() or current.stat(follow_symlinks=False).st_file_attributes & 1024):
            raise ValueError('Reparse point rejected: '+str(current))
        current = current.parent
    return path

def acceptance():
    for path in (ROOT/'.project-write.lock', WORK/'tmp/adoption_supervisor.lock'):
        if path.exists(): raise ValueError('Writer lock exists')
    cleanup = read(WORK/'qa/cleanup_after_acceptance_result.json')
    if cleanup['status'] != 'COMPLETED': raise ValueError('Original bounded cleanup has not passed')
    publication = read(WORK/'outputs/adoption_publication.json')
    if sha(ROOT/'Project.xlsx') != publication['project_sha256']: raise ValueError('Accepted Project changed')
    original_plan = read(WORK/'qa/prepared_cleanup_plan.json')
    for name, expected in original_plan['acceptance']['files'].items():
        if sha(safe(ROOT/name)) != expected: raise ValueError('Acceptance source changed: '+name)
    return original_plan['acceptance']['files']

def prepare():
    accepted = acceptance(); items=[]; directories=[]; seals=[]
    inventory = read(WORK/'inputs/validated_inventory.json')
    pairs = {(x['unit_id'], x['model_id']) for x in inventory['pairs']}
    for unit in CACHE.iterdir():
        safe(unit)
        for model in unit.iterdir():
            safe(model)
            if (unit.name, model.name) not in pairs: raise ValueError('Unexpected cache identity')
            for folder in model.iterdir():
                safe(folder)
                manifest = folder/'COMPLETE.json'; fingerprint = folder/'manifest.sha256'
                if sha(manifest) != fingerprint.read_text(encoding='ascii'): raise ValueError('Unsealed or corrupt package')
                data = read(manifest)
                if data['state'] != 'COMPLETE' or data['identity'] != [unit.name, model.name]: raise ValueError('Wrong package')
                allowed = {manifest, fingerprint}
                for entry in data['files']:
                    obj = folder/'objects'/entry['after_sha256'];safe(obj)
                    if sha(obj) != entry['after_sha256'] or sha(safe(ROOT/entry['path'])) != entry['after_sha256']:
                        raise ValueError('Accepted canonical package differs from cache')
                    allowed.add(obj)
                found=set()
                for base, dirs, files in os.walk(folder, followlinks=False):
                    safe(base); directories.append(rel(Path(base)))
                    for name in dirs:safe(Path(base)/name)
                    for name in files:found.add(safe(Path(base)/name))
                if found != allowed: raise ValueError('Unexpected files in checkpoint package')
                target = WORK/'qa/retired_checkpoints'/unit.name/(folder.name+'.json')
                seals.append({'source':rel(manifest),'destination':rel(target),'sha256':sha(manifest)})
                for path in sorted(allowed):items.append({'path':rel(path),'sha256':sha(path),'bytes':path.stat().st_size})
            directories.append(rel(model))
        directories.append(rel(unit))
    directories.append(rel(CACHE))
    plan={'schema_version':1,'accepted_files':accepted,'helper_sha256':sha(__file__),
          'ledger_before_sha256':sha(LEDGER),'items':items,'seals':seals,
          'empty_directories':sorted(set(directories),key=lambda x:len(x),reverse=True)}
    PLAN.write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'prepared':True,'files':len(items),'bytes':sum(x['bytes'] for x in items),'packages':len(seals),'plan_sha256':sha(PLAN)}))

def apply():
    plan=read(PLAN)
    if plan['helper_sha256'] != sha(__file__) or plan['accepted_files'] != acceptance():raise ValueError('Cleanup plan changed')
    if sha(LEDGER) != plan['ledger_before_sha256']:raise ValueError('Ledger changed')
    for item in plan['items']:
        path=safe(ROOT/item['path'])
        if not path.is_relative_to(CACHE) or sha(path)!=item['sha256']:raise ValueError('Deletion precondition changed')
    for item in plan['seals']:
        target=safe(ROOT/item['destination']);target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and sha(target)!=item['sha256']:raise ValueError('Retired seal collision')
        target.write_bytes((ROOT/item['source']).read_bytes())
        if sha(target)!=item['sha256']:raise ValueError('Retired seal copy failed')
    retired={x['source']:x['destination'] for x in plan['seals']}
    removed=[]; removed_dirs=[]; error=None
    try:
        for item in plan['items']:
            path=safe(ROOT/item['path'])
            if sha(path)!=item['sha256']:raise ValueError('Deletion target changed')
            with (WORK/'qa/checkpoint_cleanup_events.jsonl').open('a',encoding='utf-8') as f:
                f.write(json.dumps({'event':'unlink_intent',**item})+'\n');f.flush();os.fsync(f.fileno())
            path.unlink();removed.append(item)
        for name in plan['empty_directories']:
            path=safe(ROOT/name)
            if not path.is_relative_to(CACHE):raise ValueError('Directory outside cache')
            if path.exists() and not any(path.iterdir()):path.rmdir();removed_dirs.append(name)
    except Exception as exc:
        error=repr(exc)
        raise
    finally:
        if sha(LEDGER)!=plan['ledger_before_sha256']:raise ValueError('Concurrent ledger edit preserved')
        with LEDGER.open('a',encoding='utf-8',newline='') as f:
            writer=csv.writer(f)
            for item in removed:
                destination=retired.get(item['path'],'')
                writer.writerow([item['path'],destination,item['sha256'],item['sha256'] if destination else '',
                                 'checkpoint_retired','Verified duplicate complete-model recovery package retired after final acceptance; canonical results and compact seal retained',
                                 '', '', '2026-11-14_235900_deterministic_coverage'])
            for name in removed_dirs:writer.writerow([name,'','','','empty_directory_removed','Empty checkpoint directory after exact accepted cleanup','','','2026-11-14_235900_deterministic_coverage'])
        result={'status':'COMPLETED' if not error else 'PARTIAL_FAILURE','plan_sha256':sha(PLAN),'removed_files':len(removed),
                'removed_directories':len(removed_dirs),'retired_seals':plan['seals'],'ledger_sha256':sha(LEDGER),'error':error}
        (WORK/'qa/checkpoint_cleanup_result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    acceptance()
    print(json.dumps(result))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','apply']);args=parser.parse_args()
    prepare() if args.mode=='prepare' else apply()
