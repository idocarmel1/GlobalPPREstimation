"""Source-faithful transcription. No regional production workbook mutations."""
from pathlib import Path
import json,csv,re,hashlib,subprocess,sys
import pymupdf as fitz
from openpyxl import Workbook
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
REG=ROOT/'regions/LME_038'; REVIEW=Path(__file__).parent
SKILL=Path('C:/Users/idoca/.agents/skills/ecopath-extraction/scripts')
def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf8')
def csvout(p,head,rows):
 with p.open('w',encoding='utf8',newline='') as f: w=csv.writer(f);w.writerow(head);w.writerows(rows)
def num(s):return None if s in ['-','–',''] or '<' in s or '>' in s else s.strip('()')

# Manual transcription from visually reviewed 200 dpi source page 80/printed 71.
# Columns: B PB QB EE GE harvest TL. Parentheses retained in cell evidence.
BASIC='''Benthic producers|153.000|11.885|-|(0.003)|-|0|(1.000)
Phytoplankton|(4.154)|135.000|-|0.950|-|0|(1.000)
Small herb. zoopl.|2.430|60.225|220.000|(0.470)|(0.274)|0|(2.000)
Lg. herb. zoopl.|0.560|20.000|70.000|(0.912)|(0.286)|0.008|(2.000)
Carn. zoopl.|0.310|42.580|135.050|(0.238)|(0.315)|0|(3.000)
Jelly fishes|0.100|5.011|25.050|(0.414)|(0.200)|0.003|(3.000)
Benthic infauna|18.940|6.570|27.400|(0.537)|(0.240)|0|(2.087)
SAF|0.377|(1.188)|9.280|0.750|(0.128)|0.010|(3.483)
Macrozoobenthos|(2.455)|3.000|12.500|0.750|(0.240)|0.001|(2.291)
LBS|20.000|0.100|0.500|(0.989)|(0.200)|0.100|(2.070)
Juv. pen. shrimps|(0.556)|13.000|70.000|0.950|0.186|0.008|(2.000)
Lg. pel. pred. (J)|(0.190)|3.350|(11.167)|0.500|0.300|0.116|(3.189)
Ad. pen. shrimps|(1.224)|5.000|28.945|0.950|0.173|0.014|(2.214)
Misc. pelagics|(0.221)|(2.174)|10.870|0.950|0.200|0.117|(3.524)
Leiognathids|0.193|(3.674)|18.370|(0.510)|0.200|0.019|(2.912)
Crabs + Lobsters|(0.765)|4.000|21.900|0.950|(0.183)|0.001|(2.460)
Cephalopods|(0.950)|3.100|20.318|0.950|(0.153)|0.005|(3.161)
Decapterus spp.|(0.087)|(2.810)|14.050|0.950|0.200|0.071|(3.152)
Rastrelliger spp.|(0.044)|(4.248)|14.160|0.950|0.300|0.035|(2.630)
Clupeoids|(0.899)|3.350|17.620|0.950|(0.190)|0.116|(2.940)
Small demersals|1.687|(2.568)|12.840|(0.553)|0.200|0.066|(3.120)
Med. demersals|0.046|(1.828)|9.140|(0.575)|0.200|0.015|(3.701)
Lg. dem. pred. (J)|(0.434)|(3.852)|12.840|0.500|0.300|0.066|(3.091)
Demersal rays|(0.009)|1.300|8.200|0.600|(0.159)|0.006|(3.395)
Lg. pel. pred (A)|(0.104)|1.200|8.650|0.500|(0.139)|0.051|(3.990)
Lg. dem. pred (A)|0.130|(0.920)|6.130|(0.174)|0.150|0.020|(3.885)
Marine mammals|0.138|0.045|15.355|(0.289)|(0.003)|0.001|(4.088)
Detritus|120.000|-|-|(0.264)|-|0|(1.000)'''
# Table 3.10 PDF81/printed72, prey rows -> predator:value; dashes stay blank.
DIET='''1|8:.010 9:.150 10:.100 13:.001 20:.002 21:.020 22:.030
2|3:.700 4:.700 7:.170 9:.290 10:.040 11:.800 14:.060 15:.010 18:.233 19:.370 20:.080 23:.072
3|5:.800 6:.600 8:.010 9:.139 10:.040 12:.769 13:.019 14:.110 15:.010 17:.540 18:.315 19:.579 20:.847 21:.050 23:.138
4|5:.200 6:.400 8:.010 9:.001 10:.010 12:.001 13:.001 14:.040 15:.010 17:.010 18:.028 19:.001 20:.001 21:.010 23:.006 27:.001
5|9:.070 10:.010 12:.020 14:.030 15:.010 20:.020 21:.020
6|14:.040 21:.005
7|7:.080 8:.060 13:.169 14:.050 15:.448 16:.150 17:.020 20:.020 21:.509 22:.110 23:.563 24:.150 26:.001
8|8:.001 14:.030 22:.010 23:.020 25:.040 26:.124
9|8:.111 14:.070 15:.100 16:.050 17:.060 21:.100 22:.050 23:.050 24:.501 26:.142
10|8:.200 9:.010 13:.010 15:.001 16:.010 21:.016 24:.001
11|8:.060 12:.030 14:.030 15:.010 16:.100 17:.140 18:.014 19:.050 20:.030 21:.060 23:.050
12|14:.009 21:.005 25:.030 26:.003 27:.020
13|8:.070 14:.100 15:.200 16:.100 17:.030 21:.080 22:.130 23:.050 24:.100 25:.130 26:.149 27:.020
14|14:.005 21:.004 25:.150 27:.050
15|8:.010 14:.083 17:.001 18:.010 21:.001 22:.001 23:.001 24:.001 25:.020 26:.012 27:.010
16|8:.110 14:.005 17:.100 21:.022 22:.130 24:.098 25:.001 26:.050
17|8:.020 14:.082 17:.040 21:.020 22:.080 23:.050 24:.050 25:.100 26:.085 27:.400
18|14:.030 25:.004 27:.040
19|21:.003 25:.005 27:.035
20|12:.180 14:.122 17:.020 18:.400 21:.015 22:.010 25:.470 26:.002 27:.209
21|8:.170 14:.088 15:.001 17:.027 21:.010 22:.400 24:.099 26:.204 27:.209
22|17:.001 26:.015 27:.001
23|8:.148 17:.001 22:.049 25:.050 26:.209
24|26:.001
25|26:.001 27:.005
26|26:.001
27|26:.001
28|3:.300 4:.300 7:.750 8:.010 10:.800 11:.200 13:.800 14:.016 15:.200 16:.590 17:.010 21:.050'''

def extract_buchary():
 groups=[];land={};evidence=[]
 for i,line in enumerate(BASIC.splitlines(),1):
  name,*vals=line.split('|'); keys=['biomass','pb','qb','ee','pq','harvest','tl']
  g={'n':i,'name':name,**{k:num(v) for k,v in zip(keys,vals) if k!='harvest'}}
  if 3<=i<=27:g['unassim']='0.4' if i in [3,4] else '0.2'
  groups.append(g);land[str(i)]={'Harvest':num(vals[5])}
  evidence += [[80,71,'Table 3.9',i,name,k,v,'manual from rendered page'] for k,v in zip(keys,vals)]
 diet={str(n):{} for n in range(3,28)}
 for line in DIET.splitlines():
  prey,items=line.split('|')
  for item in items.split():
   pred,value=item.split(':');value='0'+value;diet[pred][prey]=value;evidence.append([81,72,'Table 3.10',prey,groups[int(prey)-1]['name'],f'predator_{pred}',value,'manual from rendered page'])
 return groups,land,diet,evidence,[]

def extract_nurhakim(doc):
 words=doc[6].get_text('words'); rows=sorted(set(round(w[1],2) for w in words if 148<w[0]<180 and 165<w[1]<655))
 # Biomass values fix the row anchors; label continuation lines don't create rows.
 rows=[y for y in rows if any(abs(w[1]-y)<.1 and 148<w[0]<180 and re.search(r'\d',w[4]) for w in words)]
 assert len(rows)==27,rows
 bounds=[(85,145),(148,180),(182,214),(217,248),(250,281),(285,306),(309,347),(350,386),(389,420)]
 groups=[];land={};evidence=[];censored=[]
 for i,y in enumerate(rows,1):
  vals=[]
  end=rows[i]-1 if i<27 else y+12
  for j,(a,b) in enumerate(bounds):
   ws=[w for w in words if a<=w[0]<b and y-.5<=w[1]<(end if j==0 else y+2)]
   vals.append(' '.join(w[4] for w in sorted(ws,key=lambda w:(round(w[1]),w[0]))))
  name=vals[0];keys=['biomass','pb','qb','ee','printed_GE','landings','flow_to_detritus','tl']
  g={'n':i,'name':name,**{k:num(v) for k,v in zip(keys,vals[1:]) if k in ['biomass','pb','qb','ee','tl']}}
  groups.append(g);land[str(i)]={'Landings':num(vals[6])}
  evidence += [[7,305,'Table 2',i,name,k,v,'PDF coordinates'] for k,v in zip(keys,vals[1:])]
  for k,v in zip(keys,vals[1:]):
   if '<' in v or '>' in v:censored.append({'table':'Table 2','group':i,'field':k,'printed':v,'value':None})
 words=doc[7].get_text('words');anchors={int(w[4]):(w[1]+w[3])/2 for w in words if 102<w[0]<105 and w[4].isdigit()};assert len(anchors)==24
 preyanchors={int(w[4][:-1]):w[0] for w in words if w[4].endswith('.') and w[4][:-1].isdigit() and w[1]>660 and w[0]>115};assert len(preyanchors)==27
 diet={str(n):{} for n in range(3,27)}
 for prey,x in preyanchors.items():
  for pred,y in anchors.items():
   ws=[w for w in words if abs(w[0]-x)<1 and abs((w[1]+w[3])/2-y)<12 and w[1]<630]
   raw=''.join(w[4] for w in sorted(ws,key=lambda w:-w[1]))
   raw=raw.replace('0.001','0.001')
   evidence.append([8,306,'Table 3',prey,groups[prey-1]['name'],f'predator_{pred}',raw,'PDF coordinate cell; visually verified printed 217'])
   if '<' in raw or '>' in raw:
    censored.append({'table':'Table 3','prey':prey,'predator':pred,'printed':raw,'value':None});continue
   value=num(raw)
   if value is not None:
    try:float(value)
    except ValueError:raise ValueError((prey,pred,raw,ws))
    diet[str(pred)][str(prey)]=value
 return groups,land,diet,evidence,censored

def taxonomy(doc,kind):
 result={}
 if kind=='buchary':
  for pg in [57,58]:
   words=doc[pg].get_text('words');anchors=sorted([(int(w[4][:-1]),w[1]) for w in words if w[0]<105 and re.fullmatch(r'\d+\.',w[4])])
   for j,(n,y) in enumerate(anchors):
    end=anchors[j+1][1]-1 if j+1<len(anchors) else (713 if pg==57 else 650)
    ws=[w for w in words if w[0]>=275 and y-1<=w[1]<end];result[n]=' '.join(w[4] for w in ws)
 else:
  # Each leftmost word marks a new table group, except wrapped labels.
  for pg,first in [(3,1),(4,21)]:
   words=doc[pg].get_text('words'); lines=[l for b in doc[pg].get_text('dict')['blocks'] if 'lines' in b for l in b['lines']]
   left=[l for l in lines if 90<l['bbox'][0]<95 and 133<l['bbox'][1]<680 and not ''.join(s['text'] for s in l['spans']).startswith(('Zoopl.)','(Lg.'))]
   ys=sorted(l['bbox'][1] for l in left)
   for j,y in enumerate(ys):
    end=ys[j+1]-1 if j+1<len(ys) else (686 if pg==3 else 370)
    right=[l for l in lines if 254<l['bbox'][0]<258 and y-.5<=l['bbox'][1]<end]
    result[first+j]=' '.join(s['text'] for l in right for s in l['spans'])
 return result

def main():
 for folder,kind,mid,number,year in [('BUCHARY-1991','buchary','38_38001_Java_Sea_(mid1970s)',38001,'mid1970s'),('LME038-Nurhakim-2003','nurhakim','38_38002_North_Coast_Central_Java_(1979)',38002,1979)]:
  pdf=next((REG/'papers'/folder).glob('*.pdf'));doc=fitz.open(pdf);dest=REG/'models'/mid;ev=dest/'evidence';ev.mkdir(parents=True,exist_ok=True)
  groups,land,diet,cell,censored=extract_buchary() if kind=='buchary' else extract_nurhakim(doc)
  tax=taxonomy(doc,kind);assert len(tax)==len(groups),(kind,len(tax),len(groups))
  source={'metadata':{'LME':'38 Indonesian Sea','model_number':number,'model_name':'Java Sea' if kind=='buchary' else 'North Coast Central Java','model_year':year},'groups':groups,'consumers':list(range(3,len(groups))),'fleets':['Harvest' if kind=='buchary' else 'Landings'],'landings':land,'discards':{},'detritus_groups':['Detritus'],'detritus_fate':{},'diet':diet,'diet_rows':len(groups)}
  if kind=='buchary':
   source['detritus_fate']={str(i):{'Detritus':'1'} for i in range(1,29)}
   cell.extend([[61,52,'section 3.3.2',i,g['name'],'detritus_fate','1','all functional groups sent to single detritus group; prose'] for i,g in enumerate(groups,1)])
  save(dest/'extraction.json',source);save(ev/'censored_values.json',censored)
  csvout(ev/'source_cells.csv',['pdf_page','printed_page','table','group_or_prey_seq','group_name','field_or_predator','source_text','method'],cell)
  pages=[1,15,16,17,29,58,59,60,61,65,67,68,69,80,81,92] if kind=='buchary' else list(range(1,15))
  for pg in pages:
   page=doc[pg-1];save(ev/f'page_{pg}_words.json',page.get_text('words'));(ev/f'page_{pg}.txt').write_text(page.get_text(),encoding='utf8')
   if pg in ([29,58,59,60,65,80,81] if kind=='buchary' else [2,4,5,7,8]):page.get_pixmap(matrix=fitz.Matrix(2,2).prerotate(90 if (kind=='buchary' and pg in [80,81]) or(kind=='nurhakim' and pg==8) else 0)).save(str(ev/f'page_{pg}.png'))
  save(ev/'source_manifest.json',{'file':pdf.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'size_bytes':pdf.stat().st_size,'pages':len(doc),'publication_year':1999 if kind=='buchary' else 2003,'model_period':year,'local_model_number':number,'number_note':'Project-local diagnostic identifier; not EcoBase accession','role':'preferred spatial candidate per user' if kind=='buchary' else 'test/comparison candidate only; later comparative experiments not run'})
  r=subprocess.run([sys.executable,'-X','utf8',str(SKILL/'write_outputs.py'),str(dest/'extraction.json'),'--outdir',str(dest),'--dir-name','extracted_tables'],capture_output=True,text=True,encoding='utf8');print(r.stdout,r.stderr);r.check_returncode()
  wb=Workbook();ws=wb.active;ws.title='Taxonomy';ws.append(['seq','group_name','taxon_descr'])
  for g in groups:ws.append([g['n'],g['name'],tax[g['n']]])
  wb.save(dest/'extracted_tables/Taxonomy.xlsx')
  csvout(ev/'taxonomy_evidence.csv',['seq','group_name','taxon_descr','source'],[[g['n'],g['name'],tax[g['n']],f'Table 3.1 PDF58-59 printed49-50' if kind=='buchary' else 'Table 1 PDF4-5 printed302-303'] for g in groups])
  sums={k:sum(float(v) for v in d.values()) for k,d in diet.items()};save(ev/'source_diet_sums.json',sums);print(mid,'groups',len(groups),'diet sums',sums,'censored',len(censored))
if __name__=='__main__':main()
