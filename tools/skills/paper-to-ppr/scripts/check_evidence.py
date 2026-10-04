"""Check a portable evidence index without executing scientific code.

This verifies inventory integrity, not scientific validity. Producers must supply
required_roles for the actual stages and perform matrix/summary reconciliation.
"""
import argparse
import hashlib
import json
from pathlib import Path, PureWindowsPath

REQUIRED=('schema_version','run_id','region_id','model_id','variant_id',
          'source_identity','computational_input_identity','methods','required_roles','artifacts')

def check(path):
    path=Path(path)
    if path.name.casefold()=='notes for ai.txt':raise ValueError('excluded basename')
    data=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data,dict):
        return {'complete':False,'missing_roles':[],'errors':['index must be a JSON object'],
                'verified_artifacts':[],'unavailable':[]}
    errors=[f'missing field: {key}' for key in REQUIRED if key not in data]
    present=set();unavailable=[];verified=[]
    if data.get('schema_version')!=1:errors.append('unsupported schema_version')
    for key in ('run_id','region_id','model_id','variant_id'):
        value=data.get(key)
        if not isinstance(value,str) or not value.strip():errors.append(f'{key} needs a nonempty identity')
    for key in ('source_identity','computational_input_identity'):
        value=data.get(key)
        if not isinstance(value,(str,dict)) or not value or isinstance(value,str) and not value.strip():
            errors.append(f'{key} needs a nonempty identity')
    methods=data.get('methods')
    if not isinstance(methods,list) or any(not isinstance(m,str) or not m.strip() for m in methods):
        errors.append('methods must be a list of named methods (empty for non-computational stages)')
    required_roles=data.get('required_roles')
    if not isinstance(required_roles,list) or not required_roles or any(not isinstance(r,str) or not r for r in required_roles):
        errors.append('required_roles must name applicable handoff roles')
        required_roles=[]
    artifacts=data.get('artifacts',[])
    if not isinstance(artifacts,list):artifacts=[];errors.append('artifacts must be a list')
    for artifact in artifacts:
        if not isinstance(artifact,dict):errors.append('invalid artifact record');continue
        role=artifact.get('role');status=artifact.get('availability')
        if not isinstance(role,str) or not role:errors.append('artifact missing valid role');continue
        if status not in ('present','missing','failed','inapplicable'):
            errors.append(f'{role}: invalid availability');continue
        if status!='present':
            if not artifact.get('reason') or not artifact.get('acquisition_status'):
                errors.append(f'{role}: unavailable artifact needs reason and acquisition_status')
            unavailable.append({'role':role,'availability':status,'reason':artifact.get('reason')})
            continue
        value=artifact.get('path')
        if not isinstance(value,str) or not value:
            errors.append(f'{role}: present artifact needs path');continue
        candidate=Path(value)
        if candidate.name.casefold()=='notes for ai.txt' or PureWindowsPath(value).name.casefold()=='notes for ai.txt':
            errors.append(f'{role}: excluded basename');continue
        windows_path=PureWindowsPath(value)
        if candidate.is_absolute() or windows_path.drive or windows_path.root or '://' in value:
            errors.append(f'{role}: nonportable absolute path');continue
        target=(path.parent/candidate).resolve()
        if target.name.casefold()=='notes for ai.txt':errors.append(f'{role}: excluded basename');continue
        if not target.is_file():errors.append(f'{role}: file missing: {value}');continue
        expected=artifact.get('sha256')
        actual=hashlib.sha256(target.read_bytes()).hexdigest()
        if expected!=actual:errors.append(f'{role}: SHA-256 mismatch: {value}');continue
        present.add(role);verified.append(value)
    missing=sorted(set(required_roles)-present)
    reconciliation=data.get('reconciliation',{})
    if not isinstance(reconciliation,dict):
        errors.append('reconciliation must be an object');reconciliation={}
    for name,passed in reconciliation.items():
        if passed is not True:errors.append(f'reconciliation not passed: {name}')
    return {'complete':not errors and not missing,'missing_roles':missing,'errors':errors,
            'verified_artifacts':verified,'unavailable':unavailable,
            'limits':'Checks inventory/hashes and declared reconciliation; does not validate scientific interpretation.'}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('index',type=Path);ap.add_argument('--output',type=Path)
    args=ap.parse_args();result=check(args.index);text=json.dumps(result,ensure_ascii=False,indent=2)
    if args.output:
        if args.output.name.casefold()=='notes for ai.txt':raise ValueError('excluded basename')
        args.output.write_text(text,encoding='utf-8')
    print(text)
    raise SystemExit(0 if result['complete'] else 1)

if __name__=='__main__':main()
