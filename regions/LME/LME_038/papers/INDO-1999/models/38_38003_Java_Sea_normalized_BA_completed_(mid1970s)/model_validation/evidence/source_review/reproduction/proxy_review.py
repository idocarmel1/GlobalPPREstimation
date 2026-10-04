from pathlib import Path
import json,sys,pickle,csv,gzip,zipfile,io,math,collections,hashlib
Q=Path(__file__).parent;ROOT=Q.parents[4];sys.path.insert(0,str(ROOT/'tools'));import workbooks as W
R=ROOT/'regions/LME_038';MID='38_38003_Java_Sea_normalized_BA_completed_(mid1970s)';E=R/'validation_reports'/MID;b=pickle.load((Q/'book.pkl').open('rb'))
hist=R/'models/extraction_review_20260928/complete_selected_mapping.py';ds=json.loads((R/'models'/MID/'evidence/MAPPING_DECISIONS.json').read_text(encoding='utf-8'));inv={r['taxon']:r for r in json.loads((R/'models'/MID/'evidence/catch_taxa_inventory.json').read_text(encoding='utf-8'))};donors=[];composition=collections.defaultdict(float)
for t,d in ds['taxa'].items():
 if d['basis']!='catch_composition' and not inv[t]['unidentified']:
  for s,w in zip(d['ids'],d['weights']):
   composition[s]+=inv[t]['all_years_tonnes']*w;donors.append(dict(taxon=t,seq=s,weight=w,all1950_2019_total_catch=inv[t]['all_years_tonnes'],allocated_tonnes=inv[t]['all_years_tonnes']*w,basis=d['basis']))
assert all(math.isclose(composition[int(s)],v,rel_tol=1e-12,abs_tol=1e-7)for s,v in ds['fixed_composition_tonnes_by_seq'].items())
reviews=[]
for t,d in ds['taxa'].items():
 if d['basis']=='catch_composition':
  vals=[composition[s]for s in d['ids']];ws=[v/math.fsum(vals)for v in vals];assert all(math.isclose(x,y,abs_tol=1e-14)for x,y in zip(ws,d['weights']))
  reviews.append(dict(taxon=t,candidates=d['ids'],weights=d['weights'],donors=[x for x in donors if x['seq']in d['ids']],membership_query='Every source-reviewed direct/model-catch assignment whose taxon is not unidentified; source-stage fractions first; all1950–2019 total catch; no family/genus restriction and no coarse-pool recursion.',basis='all catch = landings + discards',period='1950–2019'))
with zipfile.ZipFile(R/'raw/LME_038-catch.zip')as z:
 print('zipfiles',z.namelist())
 n=next(x for x in z.namelist()if x.endswith('.csv'));txt=io.TextIOWrapper(z.open(n),encoding='utf-8-sig');reader=csv.DictReader(txt)
 fields=['fishing_entity','fishing_sector','catch_type','reporting_status','gear_type','end_use_type','year']
 strata={t:{k:collections.defaultdict(float)for k in fields}for t in inv}
 for row in reader:
  t=row['scientific_name'];v=float(row['tonnes'])
  for k in fields:strata[t][k][row[k]]+=v
 for review in reviews:
  t=review['taxon'];dw=collections.defaultdict(float)
  for donor in review['donors']:dw[donor['taxon']]+=donor['weight']
  comparisons={}
  for field in fields:
   target=dict(strata[t][field]);donor=collections.defaultdict(float)
   for tx,wt in dw.items():
    for key,v in strata[tx][field].items():donor[key]+=wt*v
   tt=math.fsum(target.values());dt=math.fsum(donor.values());tp={k:v/tt for k,v in target.items()}if tt else{};dp={k:v/dt for k,v in donor.items()}if dt else{}
   tv=.5*math.fsum(abs(tp.get(k,0)-dp.get(k,0))for k in set(tp)|set(dp))if tt and dt else None
   comparisons[field]=dict(target_raw_tonnes=target,donor_raw_allocated_tonnes=dict(donor),target_fractions=tp,donor_fractions=dp,total_variation=tv)
  review['strata']=comparisons;review['donor_taxon_weights']=dict(dw)
(E/'identified_catch_proxy_review.json').write_text(json.dumps(dict(builder_path='../../models/extraction_review_20260928/complete_selected_mapping.py',builder_sha256=W.sha(hist),raw_zip_sha256=W.sha(R/'raw/LME_038-catch.zip'),inventory_sha256=W.sha(R/'models'/MID/'evidence/catch_taxa_inventory.json'),reproduced_composition={str(k):v for k,v in composition.items()},reviews=reviews,all_saved_fractions_reproduced=True,raw_strata_review_pending=False,limitations='Donors span source guilds and taxa, with stage weights applied. They are not same-lineage observations. Reporting/fleet/gear/basis/year differences and unknown residual species composition limit allocation confidence to Low when these fractions are retained.'),ensure_ascii=False,indent=2),encoding='utf-8')
print('proxy taxa',len(reviews),'donors',len(set(x['taxon']for x in donors)))
