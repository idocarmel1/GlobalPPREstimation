"""Create the user's assumed-GS/detritus variant without changing source data."""
from pathlib import Path
from datetime import datetime,timezone
from decimal import Decimal
import copy,json,hashlib

HERE=Path(__file__).resolve().parent
OUT=HERE/'assumption_variants/user_defaults_20261003'
OUT.mkdir(parents=True,exist_ok=True)
source=HERE/'model.json'
before=hashlib.sha256(source.read_bytes()).hexdigest()
model=json.loads(source.read_text(encoding='utf-8'))
ext=json.loads((HERE/'extracted_tables/extraction.json').read_text(encoding='utf-8'))
for g in model['group']:
 n=int(g['group_seq'])
 if 2<=n<=21:g['gs']='0.2'
 if n==22:
  g['detritus_import']='0';g['export']='0'
 elif n==1:
  g['diet_descr']={'diet':[{'prey_seq':'22','proportion':'0','detritus_fate':'1'}]}
 if n in range(2,22):
  for cell in g['diet_descr']['diet']:cell['detritus_fate']='1' if cell['prey_seq']=='22' else '0'
for g in ext['groups']:
 if 2<=g['n']<=21:g['unassim']='0.2'
 if g['n']==22:g['detritus_import']='0'
ext['detritus_fate']={str(n):{'Detritus':'1'} for n in range(1,22)}
assumptions=dict(schema_version=1,authorized_date='2026-10-03',recorded_utc=datetime.now(timezone.utc).isoformat(),basis='Direct user instruction in LME_052 chat',baseline_model_sha256=before,GS={'value':'0.2','consumer_ids':list(range(2,22)),'basis':'EwE ordinary default; not applied to producer or detritus'},detritus_routing={'unassimilated_consumption_fraction':'1','other_mortality_flow_fraction':'1','destination_group_id':22,'origin_living_group_ids':list(range(1,22))},detritus_import='0',detritus_export='0',detritus_biomass_accumulation={'status':'derive residual when complete inputs exist','equation':'BA_det = sum(unassimilated_consumption + other_mortality_flows + any actual discards) - detritus_consumption','positive':'net stock accumulation','negative':'stock drawdown; feasibility requires sufficient initial detritus stock','not_assumed_zero':True},catch_living_BA_and_migration_export={'status':'still unknown; user requested source targets to test possible values, not numerical defaults'},diet_and_conversion_changes='none; waiting for researcher readings of F62/F67 and microbial conversion decision',scope='separate assumptions variant; baseline source model, selected model, DOCX and map unchanged',ready=False)
model['_reconstruction'].update(variant='user_defaults_20261003',user_assumptions_file='assumptions.json',status='BLOCKED_USER_ASSUMPTIONS_VARIANT',GS_is_user_default=True,detritus_fate_is_user_assumption=True,detritus_import_export_is_user_zero_assumption=True,detritus_BA_is_uncomputed_residual=True)
ext.update(variant='user_defaults_20261003',user_assumptions=assumptions,reconstruction_status='INCOMPLETE_RESEARCH_CANDIDATE')
for name,obj in [('model.json',model),('extraction.json',ext),('assumptions.json',assumptions)]:
 (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
assert len(model['group'])==22
assert sum(g['gs']=='0.2' for g in model['group'])==20
assert all(sum(Decimal(v) for v in fate.values())==1 for fate in ext['detritus_fate'].values())
for base,current in zip(json.loads(source.read_text(encoding='utf-8'))['group'],model['group']):
 assert all(base[k]==current[k] for k in ['biomass','pb','qb','ee','biomass_accum','biomass_accum_rate'])
 if base['pp']=='0':assert [r['proportion'] for r in base['diet_descr']['diet']]==[r['proportion'] for r in current['diet_descr']['diet']]
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
verification=dict(passed=True,groups=22,GS_assigned_consumers=20,detritus_routing_assigned_living_groups=21,baseline_sha256_unchanged=True,basic_source_inputs_unchanged=True,feeding_diet_cells_unchanged=True,detritus_BA_not_fabricated=True,ready=False)
(OUT/'verification.json').write_text(json.dumps(verification,indent=2),encoding='utf-8')
print(json.dumps(dict(output=str(OUT),**verification),ensure_ascii=False,indent=2))
