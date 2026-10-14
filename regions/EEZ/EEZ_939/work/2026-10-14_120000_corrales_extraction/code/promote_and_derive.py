from pathlib import Path
import json,csv,subprocess,sys,shutil,hashlib
ROOT=Path(__file__).resolve().parents[6];WORK=Path(__file__).resolve().parents[1]
PAPER=ROOT/'regions/EEZ/EEZ_939/papers/Corrales-2010';RES=ROOT/'tools/skills/paper-to-ppr/resources/extraction'
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def promote(stage,model_id,derived=False):
 dest=PAPER/'models'/model_id;tables=dest/'extracted_tables';ev=tables/'evidence';ev.mkdir(parents=True,exist_ok=True)
 canonical=next(p for p in stage.glob('*.json') if isinstance(json.loads(p.read_text(encoding='utf-8')).get('group'),list))
 shutil.copy2(canonical,dest/'model.json')
 for p in stage.iterdir():
  if p.name=='model.json' or p==canonical:continue
  target=(ev/p.name) if p.suffix in ['.md','.log','.json'] or 'reconstructed' in p.name else tables/p.name
  if p.is_dir():shutil.copytree(p,target,dirs_exist_ok=True)
  else:shutil.copy2(p,target)
 dump(dest/'inputs/provenance.json',{'schema_version':1,'model_id':model_id,'source_files':['../../../sources/1-s2.0-S0924796316302329-main.pdf','../../../sources/supplements/1-s2.0-S0924796316302329-mmc1.docx'],'derivation':'Researcher authorized fate reconstruction on 2026-10-14' if derived else 'Published source literals and unknown markers; no normalization','model_sha256':hashlib.sha256((dest/'model.json').read_bytes()).hexdigest()})
 return dest
for period in ['1990_1994','2008_2012']:
 stage=Path(json.loads((WORK/f'outputs/stage_{period}.json').read_text(encoding='utf-8'))['path'])
 source_id=f'Corrales_2017_ICS_{period}';source=promote(stage,source_id)
 m=json.loads((WORK/f'inputs/extraction_{period}.json').read_text(encoding='utf-8'))
 m['metadata']['model_number']+= '_derived_fate';m['metadata']['variant']='researcher_authorized_derived_fate';m['metadata']['parent_model_id']=source_id
 dets={g['name']:g['n'] for g in m['groups'] if g['name'] in ['Detritus','Discards']}
 m['detritus_fate']={str(g['n']):{'Detritus':'0' if g['name']=='Discards' else '1','Discards':'1' if g['name']=='Discards' else '0','Export':'0'} for g in m['groups']}
 fate_rows=[['import_seq','group_name','natural_Detritus_fraction','Discards_fraction','Export_fraction','status','reason']]+[[str(g['n']),g['name'],m['detritus_fate'][str(g['n'])]['Detritus'],m['detritus_fate'][str(g['n'])]['Discards'],'0','researcher_authorized_assumption','Natural mortality and egestion enter natural Detritus; detritus pools retain identity; fishery returns are separate'] for g in m['groups']]
 m['companions']['Derived_natural_fate.csv']={'description':'Researcher-authorized natural mortality/egestion routing assumption; not a published fate matrix','rows':fate_rows}
 total='0.14' if period=='1990_1994' else '0.29'
 m['companions']['Fishery_discard_return.csv']={'description':'Separate fishery discard-return ledger. Pool destination is inferred from Discards group; the current calculator omits explicit fleet returns. Never blend this with natural mortality/egestion fractions.','rows':[['donor_seq','group_name','reported_discard_t_per_km2_year','recipient_seq','recipient_name','return_fraction','status','source']]+[[str(g['n']),g['name'],m['discards'][str(g['n'])]['Reported aggregate fisheries'] or '',str(dets['Discards']),'Discards','1','destination_assumed; source amount unchanged','Article Table1 PDF4 printed91'] for g in m['groups']]+[['aggregate','Published all-fleet discards',total,str(dets['Discards']),'Discards','1','published_total; assumed_destination','Article Table3 PDF8 printed95']]}
 inputfile=WORK/f'inputs/derived_fate_{period}.json';dump(inputfile,m);parent=WORK/f'outputs/derived_{period}'
 r=subprocess.run([sys.executable,'-X','utf8',str(RES/'scripts/write_outputs.py'),str(inputfile),'--outdir',str(parent)],capture_output=True,text=True,encoding='utf-8');assert r.returncode==0,r.stderr
 variant_stage=next(p for p in parent.iterdir() if p.is_dir());shutil.copy2(stage/'Taxonomy.xlsx',variant_stage/'Taxonomy.xlsx')
 for name,args in [('validate',['validate.py',str(variant_stage)]),('massbalance',['massbalance_check.py',str(variant_stage)]),('conversion',['database_json.py','-d',str(variant_stage),'--update-report'])]:
  rr=subprocess.run([sys.executable,'-X','utf8',str(RES/'scripts'/args[0])]+args[1:],capture_output=True,text=True,encoding='utf-8');(WORK/f'qa/{period}_derived_{name}.log').write_text(rr.stdout+'\n'+rr.stderr,encoding='utf-8');print(period,name,rr.returncode,flush=True)
 derived_id=source_id+'_derived_fate';derived=promote(variant_stage,derived_id,True)
 dump(WORK/f'outputs/derived_{period}.json',{'path':str(derived),'model_id':derived_id,'source_path':str(source)})
 print('promoted',source_id,derived_id,flush=True)
