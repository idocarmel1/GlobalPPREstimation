"""Read-only targeted evidence collection; no scientific files are changed."""
import csv, io, json, math, hashlib, sys, zipfile
from pathlib import Path
from collections import defaultdict
ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').exists())
REG = ROOT / 'regions/LME_032'
REP = REG / 'validation_reports/32_1_Arabian_Sea_off_Karnataka_(2000)'
WORK = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))
from workbooks import read_book, records, overview, sha
def load(p): return json.loads(p.read_text(encoding='utf-8'))
audit = load(REP/'mapping/adopted_taxon_audit.json')
recon = load(REP/'mapping/retained_weight_reconstruction.json')
w5 = {r['taxon']:r for r in recon}
donors = {t:{s['taxon']:s['group_id'] for s in r['support']} for t,r in w5.items()}
lookup = defaultdict(list)
for t, names in donors.items():
    lookup[t].append((t,'target',None))
    for name, gid in names.items(): lookup[name].append((t,'donor',gid))
agg = {t:{role:{dim:defaultdict(float) for dim in ['fishing_entity','fishing_sector','gear_type','reporting_status','catch_type','decade','year']} for role in ['target','donor']} for t in w5}
bygroup = {t:defaultdict(float) for t in w5}
counts = defaultdict(int)
with zipfile.ZipFile(REG/'raw/LME_032-catch.zip') as z:
    member=z.getinfo('SAU LME 32 v50-1.csv')
    mh=hashlib.sha256()
    with z.open(member) as binary:
        for block in iter(lambda:binary.read(1024*1024),b''):mh.update(block)
    member_info={'name':member.filename,'sha256':mh.hexdigest(),'uncompressed_bytes':member.file_size,'crc32':format(member.CRC,'08x')}
    with io.TextIOWrapper(z.open('SAU LME 32 v50-1.csv'),encoding='utf-8-sig',newline='') as handle:
        for row in csv.DictReader(handle):
            if row['scientific_name'] not in lookup: continue
            year=int(row['year'])
            if not 1950<=year<=2019: continue
            value=float(row['tonnes'])
            for target, role, gid in lookup[row['scientific_name']]:
                counts[(target,role)]+=1
                for dim in agg[target][role]:
                    key = str(year//10*10) if dim=='decade' else str(year) if dim=='year' else row[dim]
                    agg[target][role][dim][key]+=value
                if role=='donor':bygroup[target][gid]+=value
out={'schema_version':1,'scope':'Original SAU v50.1 LME032 1950–2019 raw catch; read-only donor/target reporting-applicability comparison. Distribution differences are warnings about transfer, not observed coarse-label species shares.','raw_sha256':sha(REG/'raw/LME_032-catch.zip'),'raw_member':member_info,'selection':{'years':[1950,2019],'target':'exact scientific_name equals each W5 taxon label','donors':'exact scientific_name names in retained_weight_reconstruction support; all original strata, landings and discards, reported and unreported','donor_selection_sha256':sha(REP/'mapping/retained_weight_reconstruction.json')},'items':[]}
for t,r in w5.items():
    target_total=math.fsum(agg[t]['target']['year'].values()); donor_total=math.fsum(agg[t]['donor']['year'].values())
    item={'taxon':t,'target_total_catch_t':target_total,'donor_total_catch_t':donor_total,'donor_count':len(donors[t]),'original_record_counts':{role:counts[(t,role)] for role in ['target','donor']},'source_group_totals_t':dict(bygroup[t]),'dimensions':{}}
    for dim in agg[t]['target']:
        av,bv=agg[t]['target'][dim],agg[t]['donor'][dim]
        ak={k:v/target_total for k,v in av.items()};bk={k:v/donor_total for k,v in bv.items()}
        keys=set(ak)|set(bk)
        tv=0.5*math.fsum(abs(ak.get(k,0)-bk.get(k,0)) for k in keys)
        target_supported=math.fsum(v for k,v in ak.items() if bv.get(k,0)>0)
        item['dimensions'][dim]={'total_variation':tv,'target_catch_share_with_positive_donor':target_supported,'target_distribution':dict(sorted(ak.items(),key=lambda kv:-kv[1])),'donor_distribution':dict(sorted(bk.items(),key=lambda kv:-kv[1]))}
    out['items'].append(item)
WORK.mkdir(parents=True,exist_ok=True)
(WORK/'raw_reporting_applicability.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{ 'taxon':i['taxon'],'target_catch_t':i['target_total_catch_t'],'donor_catch_t':i['donor_total_catch_t'],'checks':{d:{'TV':round(i['dimensions'][d]['total_variation'],4),'supported_target_share':round(i['dimensions'][d]['target_catch_share_with_positive_donor'],4),'target_top3':list(i['dimensions'][d]['target_distribution'].items())[:3],'donor_top3':list(i['dimensions'][d]['donor_distribution'].items())[:3]} for d in ['fishing_entity','fishing_sector','gear_type','catch_type','decade']}} for i in out['items']],ensure_ascii=False,indent=2))
