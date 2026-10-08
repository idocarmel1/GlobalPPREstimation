"""Bounded current-audit inventory for the regional cephalopod scope lesson."""
from pathlib import Path
import hashlib,json,re
from verify_review_confidence import AUDITS

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
progress=json.loads((BASE/'verification/review_package_progress.json').read_text(encoding='utf-8'))
out=[]
fields=['taxon','common_name','membership_confidence','membership_reason','reason','rationale',
        'mapping_display','candidate_ids','group_ids','mapped_groups','group_names','groups',
        'review_confidence','overall_confidence','confidence']
for unit in progress['regions']:
    if 'handoff' not in unit:continue
    path=ROOT/Path(unit['handoff']['path']).parent/AUDITS.get(unit['unit_id'],'taxon_audit.json')
    data=json.loads(path.read_text(encoding='utf-8'))
    rows=data.get('rows',data.get('records')) if isinstance(data,dict) else data
    relevant=[{k:r[k] for k in fields if k in r} for r in rows
              if re.match(r'^(Octopus|Octopoda|Octopodidae|Sepiida|Sepiidae|Sepia|Sepiella)(?:\s|$)',r['taxon'])]
    out.append({'unit_id':unit['unit_id'],'audit':path.relative_to(ROOT).as_posix(),
                'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rows':relevant})
record={'scope':'Current authoritative audit rows, including narrower species; historical embedded mappings excluded.',
        'regions':out,'source_applicability_review':'Pending coordinator source-based disposition; inventory alone is not a source membership check.'}
(BASE/'verification/cephalopod_label_scope_inventory.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for item in out:
    print(item['unit_id'],len(item['rows']))
    for row in item['rows']:
        reason=row.get('membership_reason',row.get('reason',row.get('rationale','')))
        if re.search('pelagic|argonaut|bathy',str(reason),re.I):
            print('CHECK',row['taxon'],str(reason)[:1100])
