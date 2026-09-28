"""Coordinate-based transcription of the local Allain et al. (2007) PDF.

Coordinates are display points (after the PDF page rotation). No diet normalization.
"""
from pathlib import Path
import json, re, hashlib, csv
from decimal import Decimal
import pymupdf

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'download-0adcf55e.pdf'
DOC = pymupdf.open(SOURCE)
UNION = ['Swordfish','Other Billfish','Blue Shark','Other Sharks','BET','YFT','SKJ','Piscivorous fish','Small Billfish','Small Sharks','Small BET','Small YFT','Small SKJ','baby SKJ','Epi forage','Epi crust','Epi fish','Epi small fish','Epi mollusc','Epi small mollusc','M Meso forage','M Meso fish+other','M meso mollusc','Meso forage','Meso fish + other','Meso mollusc','HM Bathy forage','M Bathy forage','Bathy forage','Mesozpk','Microzpk','Large phyto','Small phyto','Detritus']
FINAL = [x for x in UNION if x not in ['Epi forage','M Meso forage','Meso forage']]
INITIAL = [x for x in UNION if x not in ['baby SKJ','Epi crust','Epi fish','Epi small fish','Epi mollusc','Epi small mollusc','M Meso fish+other','M meso mollusc','Meso fish + other','Meso mollusc']]

def words(page):
    p=DOC[page-1]
    return [{'text': w[4], 'bbox': list(pymupdf.Rect(w[:4])*p.rotation_matrix)} for w in p.get_text('words')]

def center(w,dim):
    b=w['bbox']; return (b[dim]+b[dim+2])/2

def rows_at(page,xmax,ymin,ymax):
    selected=[w for w in words(page) if center(w,0)<xmax and ymin<center(w,1)<ymax]
    ys=[]
    for w in sorted(selected,key=lambda w:center(w,1)):
        y=center(w,1)
        if not ys or abs(ys[-1]-y)>2: ys.append(y)
    return ys

EVIDENCE=[]
def grid(page,row_names,row_y,col_names,col_x):
    cells={r:{} for r in row_names}
    for w in words(page):
        if not re.fullmatch(r'(?:\d+(?:\.\d+)?|-)',w['text']): continue
        x,y=center(w,0),center(w,1)
        ri=min(range(len(row_y)),key=lambda i:abs(y-row_y[i]))
        ci=min(range(len(col_x)),key=lambda i:abs(x-col_x[i]))
        if abs(y-row_y[ri])>3 or x<min(col_x)-20 or x>max(col_x)+20: continue
        key=col_names[ci]; row=row_names[ri]
        assert key not in cells[row],(page,row,key,w)
        cells[row][key]=w['text']
        EVIDENCE.append({'page':page,'table':{11:3,12:4,13:4,14:5,19:6}[page], 'row':row,'column':key,**w})
    return cells

# Table 6: all final estimates; exact printed values and printed dash retained.
y6=rows_at(19,165,382,651)
assert len(y6)==31,len(y6)
t6=grid(19,FINAL,y6,['tl','biomass','pb','qb','ee','pq'],[177,227,288,351,426,505])
# Table 3: paired initial/final input columns, 34 union rows.
y3=rows_at(11,125,96,481)
assert len(y3)==34,len(y3)
h3=sorted([w for w in words(11) if w['text'] in ['Initial','Final'] and 84<center(w,1)<96],key=lambda w:center(w,0))
t3=grid(11,UNION,y3,[f'{v}_{period}' for v in ['biomass','pb','qb','ee','unassim'] for period in ['Initial','Final']],[center(w,0) for w in h3])
# Table 4, first panel: 13 paired top consumers plus final-only baby SKJ.
y12=rows_at(12,135,115,388)
assert len(y12)==34,len(y12)
h12=sorted([w for w in words(12) if w['text'] in ['Initial','Final'] and 106<center(w,1)<115],key=lambda w:center(w,0))
cols12=[f'{g}|{p}' for g in UNION[:13] for p in ['Initial','Final']]+['baby SKJ|Final']
assert len(h12)==len(cols12)
d12=grid(12,UNION,y12,cols12,[center(w,0) for w in h12])
# Table 4 continuation: blue initial-only, red final-only, then paired forage/zpk.
y13=rows_at(13,133,116,405)
assert len(y13)==34,len(y13)
h13=sorted([w for w in words(13) if w['text'] in ['Initial','Final'] and 106<center(w,1)<116],key=lambda w:center(w,0))
cols13=[]
for g in UNION[14:31]:
    periods=['Initial'] if g in ['Epi forage','M Meso forage','Meso forage'] else ['Initial','Final'] if g in UNION[26:31] else ['Final']
    cols13.extend(f'{g}|{p}' for p in periods)
assert len(h13)==len(cols13),(len(h13),len(cols13))
d13=grid(13,UNION,y13,cols13,[center(w,0) for w in h13])
# Table 5: four fleet columns and rounded printed totals. Retain totals separately.
y5=rows_at(14,223,103,336)
assert len(y5)==24,len(y5)
t5=grid(14,INITIAL,y5,['Longline','PS Unass','PS FAD','Domestic ID PHL','printed_Total'],[248,291,332,384,435])
t5sum=grid(14,['Sum'],[340.9217],['Longline','PS Unass','PS FAD','Domestic ID PHL','printed_Total'],[248,291,332,384,435])
raw={'table3':t3,'table4_panel1':d12,'table4_panel2':d13,'table5':t5,'table5_printed_sums':t5sum,'table6':t6}
(HERE/'source_tables.json').write_text(json.dumps(raw,indent=2),encoding='utf-8')
(HERE/'cell_evidence.json').write_text(json.dumps(EVIDENCE,indent=2),encoding='utf-8')
(HERE/'source_words.json').write_text(json.dumps({str(p):words(p) for p in [9,11,12,13,14,19]},indent=2),encoding='utf-8')

for period,names,number in [('Final',FINAL,200701),('Initial',INITIAL,200702)]:
    seq={g:str(i+1) for i,g in enumerate(names)}
    groups=[]
    for g in names:
        r={'n':int(seq[g]),'name':g}
        if period=='Final':
            r.update({k:(None if v=='-' else v) for k,v in t6[g].items()})
        else:
            r.update({k:t3[g].get(k+'_Initial') for k in ['biomass','pb','qb','ee']})
        r['unassim']=t3[g].get('unassim_'+period)
        # Explicit multi-stanza BA/B=0 (p15) applies to final tuna stanzas only.
        if period=='Final' and g in ['BET','YFT','SKJ','Small BET','Small YFT','Small SKJ','baby SKJ']: r['ba_rate']='0'
        if g=='Detritus': r['detritus_import']='0' # p7: no import considered
        groups.append(r)
    diet={}
    for g in names[:-3]:
        key=f'{g}|{period}'
        diet[seq[g]]={'import':'0'} # p7
        for prey in names:
            v=d12[prey].get(key,d13[prey].get(key))
            if v is not None: diet[seq[g]][seq[prey]]=v
    landings={}
    for g in names:
        vals={k:v for k,v in t5.get(g,{}).items() if k!='printed_Total'}
        if vals: landings[seq[g]]=vals
        # Printed total zero for rows with no fleet figures is known aggregate zero,
        # retained separately. No fleet-specific zero is fabricated.
    model_id=f'941_{number}_WCPO_Warm_Pool_{period}_(mixed_periods)'
    model={'metadata':{'LME':'941 EEZ Kiribati Gilbert Islands proxy','model_number':number,'model_name':'WCPO Warm Pool '+period,'model_year':'mixed_periods'},
           'groups':groups,'consumers':list(range(1,len(names)-2)),
           'fleets':['Longline','PS Unass','PS FAD','Domestic ID PHL'],
           'landings':landings,'discards':{},'detritus_groups':['Detritus'],
           'detritus_fate':{seq[g]:{'Detritus':'1'} for g in names if g!='Detritus'},
           'diet':diet,'diet_rows':len(names),'landings_rows':len(names),'discards_rows':len(names),
           'source_identity':{'publication_year':2007,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'parameter_set':period,'period_note':'Mixed temporal inputs: YFT/BET and bycatch catches 1995-2004; SKJ catches and original forage biomass 1993-2002. 2005/2006 are assessment releases, not model periods.','model_id':model_id}}
    out=HERE/(period.lower()+'_extraction.json')
    out.write_text(json.dumps(model,indent=2),encoding='utf-8')
    sums={g:str(sum((Decimal(v) for v in diet[seq[g]].values()),Decimal(0))) for g in names[:-3]}
    print(period,len(names),'groups; diet totals:',sums)

