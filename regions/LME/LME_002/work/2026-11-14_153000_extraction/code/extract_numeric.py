from pathlib import Path
import json, re, csv, hashlib
import pdfplumber
import pypdfium2
from decimal import Decimal, localcontext

ROOT=Path(__file__).resolve().parents[6]
WORK=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'regions/LME/LME_002/papers/GOA-2007/sources/noaa_22894_DS1-9dadd884.pdf'
for child in ('outputs','qa'):
    (WORK/child).mkdir(parents=True,exist_ok=True)

def cache(pages=range(239,310)):
    with pdfplumber.open(SOURCE) as pdf:
        for pno in pages:
            page=pdf.pages[pno-1]
            out={'pdf_page':pno,'width':page.width,'height':page.height,'words':page.extract_words(x_tolerance=0.4,y_tolerance=2),'text':page.extract_text(x_tolerance=0.4,y_tolerance=2)}
            (WORK/'qa'/f'page_{pno}.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf-8')
            print(pno, out['text'].splitlines()[:3],flush=True)

def render(pages):
    pdf=pypdfium2.PdfDocument(SOURCE)
    for pno in pages:
        img=pdf[pno-1].render(scale=3).to_pil()
        img.save(WORK/'qa'/f'page_{pno}.png')
        print('rendered',pno,flush=True)

def loadpage(pno):
    d=json.loads((WORK/'qa'/f'page_{pno}.json').read_text(encoding='utf-8'))
    if sum(not w['upright'] for w in d['words'])>len(d['words'])/2:
        h=d['height']
        d['words']=[dict(w,text=w['text'][::-1],x0=h-w['bottom'],x1=h-w['top'],top=w['x0'],bottom=w['x1'],source_bbox=bbox([w])) for w in d['words'] if not w['upright']]
        d['rotation_applied']=90
    return d

def lines(words):
    result=[]
    for w in sorted(words,key=lambda w:(round(w['top'],1),w['x0'])):
        if not result or abs(w['top']-result[-1][0]['top'])>2:
            result.append([w])
        else: result[-1].append(w)
    return [sorted(x,key=lambda w:w['x0']) for x in result]

def bbox(ws):
    return [round(min(w['x0'] for w in ws),3),round(min(w['top'] for w in ws),3),round(max(w['x1'] for w in ws),3),round(max(w['bottom'] for w in ws),3)] if ws else None

def table(pages,count):
    rows=[]
    for pno in pages:
        ls=lines(loadpage(pno)['words'])
        start=next(i for i,r in enumerate(ls) if r[0]['text']=='Group')+1
        first=ls[start]
        vals=[w for w in first if re.fullmatch(r'[-0-9,.]+|#N/A',w['text'])]
        assert len(vals)==count,(pno,vals)
        anchors=[(w['x0']+w['x1'])/2 for w in vals]
        for r in ls[start:]:
            if r[0]['x0']>100: continue
            split=next((i for i,w in enumerate(r) if w['x0']>170 and re.fullmatch(r'[-0-9,.]+|#N/A',w['text'])),None)
            if split is None: continue
            name=' '.join(w['text'] for w in r[:split])
            cells=[[] for _ in anchors]
            for w in r[split:]:
                k=min(range(count),key=lambda j:abs((w['x0']+w['x1'])/2-anchors[j]))
                cells[k].append(w)
            literals=[''.join(w['text'] for w in c) for c in cells]
            assert all(re.fullmatch(r'[-0-9,.]+|#N/A',v) for v in literals),(pno,name,literals)
            rows.append({'name':name,'values':literals,'bboxes':[bbox(c) for c in cells],'pdf_page':pno,'name_bbox':bbox(r[:split])})
    return rows

def basic():
    c1=table(range(239,242),6)
    groups=[]; crosswalk=[]; evidence=[]
    for i,row in enumerate(c1,1):
        row['raw_name']=row['name']
        row['name']=row['name'].replace('W ', 'W').replace('W .', 'W.')
        v=row['values']; included=v[4]!='#N/A'
        n=len(groups)+1 if included else None
        crosswalk.append({'union_order':i,'n':n,'name':row['name'],'raw_pdf_label':row['raw_name'],'included_in_GOA':included,'pdf_page':row['pdf_page'],'GOA_B':v[4],'GOA_EE':v[5]})
        if included:
            groups.append({'n':n,'name':row['name'],'biomass':v[4],'ee':v[5]})
        for j,field in [(4,'biomass'),(5,'ee')]:
            evidence.append({'table':'C1','pdf_page':row['pdf_page'],'printed_page':row['pdf_page']-10,'group':row['name'],'n':n,'field':field,'source_literal':v[j],'adopted_literal':v[j] if included else None,'bbox':row['bboxes'][j],'status':'published' if included else 'absent_from_GOA'})
    (WORK/'outputs'/'canonical_groups.json').write_text(json.dumps(groups,indent=2,ensure_ascii=False),encoding='utf-8')
    (WORK/'outputs'/'union_group_crosswalk.json').write_text(json.dumps(crosswalk,indent=2,ensure_ascii=False),encoding='utf-8')
    aliases={'Sperm and beaked whales':'Sperm and beaked whale','Urchins dollars cucumbers':'Urchins dollars cucumber'}
    byname={g['name']:g for g in groups}
    allnames={x['name'] for x in crosswalk}
    norm=lambda s:re.sub('[^a-z0-9]','',s.lower())
    name_norm={norm(n):n for n in allnames}
    def canonical(s):
        s=aliases.get(s,s)
        return name_norm.get(norm(s),s)
    for row in table(range(242,245),9):
        name=canonical(row['name']);assert name in allnames,name
        g=byname.get(name)
        for j,field in [(6,'pb'),(7,'qb'),(8,'tl')]:
            v=row['values'][j]
            if g is not None:g[field]=v
            else:assert v=='#N/A',(name,field,v)
            evidence.append({'table':'C2','pdf_page':row['pdf_page'],'printed_page':row['pdf_page']-10,'group':name,'source_group':row['name'],'n':g['n'] if g else None,'field':field,'source_literal':v,'adopted_literal':v if g else None,'bbox':row['bboxes'][j],'status':'published' if g else 'absent_from_GOA'})
    landings={};discards={}; catchrows=[]
    for row in table(range(245,248),6):
        name=canonical(row['name']);assert name in allnames,name
        g=byname.get(name)
        for j,field,dest in [(4,'retained_catch_tonnes',landings),(5,'discards_including_offal_tonnes',discards)]:
            v=row['values'][j]
            with localcontext() as ctx:
                ctx.prec=34
                derived=str(Decimal(v.replace(',',''))/Decimal(291840)) if g and v!='#N/A' else None
            if g:dest[str(g['n'])]={'All fisheries (including processing offal)':derived}
            else:assert v=='#N/A',(name,field,v)
            evidence.append({'table':'C3','pdf_page':row['pdf_page'],'printed_page':row['pdf_page']-10,'group':name,'n':g['n'] if g else None,'field':field,'source_literal':v,'adopted_literal':derived,'bbox':row['bboxes'][j],'status':('missing_or_inapplicable_source_NA' if v=='#N/A' else 'derived_tonnes_divided_by_291840_km2') if g else 'absent_from_GOA'})
            catchrows.append([name,field,v,derived or '',str(row['pdf_page']),json.dumps(row['bboxes'][j]),'source tonnes / 291840 km2' if g else 'absent from GOA'])
    assert all('qb' in g for g in groups)
    model={'metadata':{'LME':'2 Gulf of Alaska','model_number':'Aydin2007','model_name':'Gulf of Alaska','model_year':'1990-1994','biomass_basis':'whole_model_area'},'groups':groups,'consumers':[g['n'] for g in groups if Decimal(g['qb'])>0],'fleets':['All fisheries (including processing offal)'],'landings':landings,'discards':discards,'diet':{},'diet_rows':len(groups),'landings_rows':len(groups),'discards_rows':len(groups),'detritus_groups':['Discards','Offal','Pelagic Detritus','Benthic Detritus','Outside Detritus'],'detritus_fate':{},'companions':{'Published_catch_tonnes.csv':{'description':'Source Table C3 tonnes, retained catch after processing and discards inclusive of offal; density derived using published 291840 km2 model area.','rows':[['group','field','source_tonnes','derived_tonnes_per_km2','pdf_page','bbox','status']]+catchrows}}}
    (WORK/'outputs'/'numeric_writer_input.json').write_text(json.dumps(model,indent=2,ensure_ascii=False),encoding='utf-8')
    (WORK/'outputs'/'numeric_cell_evidence.json').write_text(json.dumps(evidence,indent=2,ensure_ascii=False),encoding='utf-8')
    print('groups',len(groups),'consumers',len(model['consumers']),'union',len(c1),flush=True)

DIET_PAGES=[260,261,262,264,265,266,267,268,269,270,271,272,273,274]
def matrix_grids():
    out=[]
    for pno in DIET_PAGES:
        d=loadpage(pno);ws=d['words']
        preyword=next(w for w in ws if w['text']=='Prey')
        nums=[w for w in ws if re.fullmatch(r'\d+\.\d+%',w['text']) and w['top']>preyword['bottom']-1]
        anchors=[]
        for w in sorted(nums,key=lambda w:w['x1']):
            if not anchors or w['x1']-anchors[-1][-1]>3: anchors.append([w['x1']])
            else: anchors[-1].append(w['x1'])
        anchors=[sum(a)/len(a) for a in anchors]
        rowlines=lines(ws)
        firsty=min(w['top'] for w in nums)
        lasty=max(w['bottom'] for w in nums)
        labelmax=min(w['x0'] for w in nums)-5
        headerws=[w for w in ws if w['bottom']<firsty and w['x0']>labelmax and w['top']>preyword['top']-32]
        headcols=[[] for _ in anchors]
        centers=[x-8 for x in anchors]
        for w in headerws:
            k=min(range(len(centers)),key=lambda j:abs((w['x0']+w['x1'])/2-centers[j]))
            headcols[k].append(w)
        headers=[' '.join(w['text'] for r in lines(col) for w in r) for col in headcols]
        rows=[]
        for rr in rowlines:
            if not(firsty-1<=rr[0]['top']<=lasty):continue
            name=' '.join(w['text'] for w in rr if w['x0']<labelmax)
            if not name: continue
            cells=[None]*len(anchors);bbs=[None]*len(anchors)
            for w in rr:
                if not re.fullmatch(r'\d+\.\d+%',w['text']): continue
                k=min(range(len(anchors)),key=lambda j:abs(w['x1']-anchors[j]))
                assert cells[k] is None,(pno,name,k,cells[k],w)
                cells[k]=w['text'];bbs[k]=w.get('source_bbox',bbox([w]))
            rows.append({'source_prey':name,'values':cells,'bboxes':bbs})
        entry={'pdf_page':pno,'table':f'C{pno-248}','anchors':anchors,'headers':headers,'rows':rows,'blank_semantics':'not in diet (structural absence); printed 0.00% trace in diet','rotation_applied':d.get('rotation_applied',0)}
        out.append(entry)
        print(pno,list(enumerate(headers)),flush=True)
    (WORK/'outputs'/'direct_diet_source_grids.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
    print('PREY NAMES',sorted({r['source_prey'] for p in out for r in p['rows']}),flush=True)

def matrix_headers():
    from PIL import Image,ImageDraw
    pdf=pypdfium2.PdfDocument(SOURCE)
    strips=[]
    for pno in DIET_PAGES:
        d=loadpage(pno)
        prey=next(w for w in d['words'] if w['text']=='Prey')
        im=pdf[pno-1].render(scale=3,rotation=d.get('rotation_applied',0)).to_pil()
        im.save(WORK/'qa'/f'page_{pno}_upright.png')
        im=im.crop((0,max(0,(prey['top']-40)*3),im.width,(prey['bottom']+18)*3))
        draw=ImageDraw.Draw(im);draw.text((5,3),str(pno),fill='red')
        strips.append(im)
    for start in range(0,len(strips),5):
        batch=strips[start:start+5]
        montage=Image.new('RGB',(max(x.width for x in batch),sum(x.height for x in batch)+20*len(batch)),'#cccccc')
        y=0
        for im in batch:montage.paste(im,(0,y));y+=im.height+20
        montage.save(WORK/'qa'/f'diet_headers_{start}.png')

MATRIX_TARGETS={
260:{8:['W. Pollock_Juv'],9:['W. Pollock'],10:['P. Cod_Juv'],11:['P. Cod']},
261:{4:['Herring_Juv'],5:['Herring']},
262:{8:['Arrowtooth_Juv'],9:['Arrowtooth'],10:['P. Halibut_Juv'],11:['P. Halibut']},
264:{14:['YF. Sole'],15:['FH. Sole_Juv'],16:['FH. Sole'],17:['N. Rock sole'],18:['S. Rock sole'],19:['AK Plaice']},
265:{6:['Dover Sole'],7:['Rex Sole'],8:['Misc. Flatfish']},
266:{10:['Sablefish_Juv'],11:['Sablefish'],12:['Eelpouts'],13:['Giant Grenadier','Pacific Grenadier','Other Macruids'],14:['Misc. fish deep']},
267:{8:['POP_Juv'],9:['POP'],10:['Sharpchin Rock'],11:['Northern Rock'],12:['Dusky Rock']},
268:{8:['Shortraker Rock'],9:['Rougheye Rock'],10:['Shortspine Thorns_Juv'],11:['Shortspine Thorns'],12:['Other Sebastes']},
269:{6:['Atka mackerel_Juv'],7:['Atka mackerel'],8:['Greenlings']},
270:{6:['Lg. Sculpins'],7:['Other sculpins'],8:['Misc. fish shallow']},
271:{0:['Squids'],1:['Salmon returning'],2:['Salmon outgoing'],3:['Bathylagidae'],4:['Capelin'],5:['Sandlance'],6:['Eulachon'],7:['Oth. managed forage'],8:['Oth. pelagic smelt'],12:['Myctophidae'],13:['Octopi']},
272:{9:['Bairdi'],10:['King Crab'],12:['Pandalidae']},
273:{0:['NP shrimp'],1:['Brittle stars'],2:['Urchins dollars cucumber'],3:['Snails'],4:['Hermit crabs'],5:['Misc. crabs'],6:['Misc. Crustacean'],7:['Sea stars'],8:['Anemones'],9:['Corals'],10:['Hydroids'],11:['Urochordata'],12:['Sea Pens'],13:['Sponges'],14:['Bivalves'],15:['Benthic Amphipods'],16:['Polychaetes','Misc. worms']},
274:{0:['Scyphozoid Jellies'],1:['Fish Larvae'],2:['Chaetognaths'],3:['Euphausiids'],4:['Mysids'],5:['Pelagic Amphipods'],6:['Gelatinous filter feeders'],7:['Pteropods'],8:['Copepods'],9:['Pelagic microbes'],10:['Benthic microbes']},
}

# Exact column labels independently read from the upright source-page renders.
SOURCE_HEADERS={
260:{8:'GOA W. pollock juv',9:'GOA W. pollock',10:'GOA P. cod juv',11:'GOA P. cod'},
261:{4:'GOA Herring juv',5:'GOA Herring'},
262:{8:'GOA Arrow. juv',9:'GOA Arrow. fl.',10:'GOA P. halibut juv',11:'GOA P. halibut'},
264:{14:'GOA Yellowfin sole',15:'GOA Flathead sole juv',16:'GOA Flathead sole',17:'GOA N. rock sole',18:'GOA S. rock sole',19:'GOA Alaska plaice'},
265:{6:'GOA Dover sole',7:'GOA Rex sole',8:'GOA Misc. flatfish'},
266:{10:'GOA Sablefish juv',11:'GOA Sablefish',12:'GOA Eelpouts',13:'GOA Macrourids',14:'GOA Misc. deep fish'},
267:{8:'GOA Pacific ocean perch juv',9:'GOA Pacific ocean perch adu',10:'GOA Sharpchin rockfish',11:'GOA Northern rockfish',12:'GOA Dusky rockfish'},
268:{8:'GOA Shortraker rockfish',9:'GOA Rougheye rockfish',10:'GOA Shortspine thornyhead juv',11:'GOA Shortspine thornyhead adu',12:'GOA Other Sebastes'},
269:{6:'GOA Atka mackerel juv',7:'GOA Atka mackerel',8:'GOA Greenlings'},
270:{6:'GOA Large sculpins',7:'GOA Other sculpins',8:'GOA Misc. shallow fish'},
271:{0:'All Squids',1:'All Salmon returning',2:'All Salmon outgoing',3:'All Bathylagidae',4:'All Capelin',5:'All Sand lance',6:'All Eulachon',7:'All Managed forage',8:'All Oth pel. smelt',12:'EBS/GOA Myctophidae',13:'GOA Octopus'},
272:{9:'GOA Tanner crab',10:'GOA King crab',12:'All Pandalid shrimp'},
273:{0:'All Non-Pandalid shrimp',1:'All Brittle star',2:'All Urchins dollars and cucumbers',3:'All Snails',4:'All Hermit crabs',5:'All Misc crabs',6:'All Misc. Crustacean',7:'All Sea star',8:'All Anemones',9:'All Corals',10:'All Benth. Hydroid',11:'All Benth. Urochordata',12:'All Sea pens',13:'All Sponge',14:'All Bivalves',15:'All Benth. Amphipods',16:'All Polychates and Misc. worms'},
274:{0:'Scyphozoid jellies',1:'Fish larvae',2:'Chaetognaths etc.',3:'Euphausiids',4:'Mysids',5:'Pelagic amphipods',6:'Pel. gel. filter feeder',7:'Pteropods',8:'Copepods',9:'Microzooplankton',10:'Benthic bacteria'},
}

PREY_ALIASES={
'W . pollock':'W. Pollock','W . pollock juv':'W. Pollock_Juv','W. pollock':'W. Pollock','W. pollock juv':'W. Pollock_Juv',
'P. cod':'P. Cod','P. cod juv':'P. Cod_Juv','Herring juv':'Herring_Juv','Arrowtooth fl.':'Arrowtooth','Arrowtooth juv':'Arrowtooth_Juv',
'P. halibut':'P. Halibut','P. halibut juv':'P. Halibut_Juv','Yellowfin sole':'YF. Sole','Flathead sole':'FH. Sole','Flathead sole juv':'FH. Sole_Juv',
'N. rock sole':'N. Rock sole','S. rock sole':'S. Rock sole','Alaska plaice':'AK Plaice','Dover sole':'Dover Sole','Rex sole':'Rex Sole','Misc. flatfish':'Misc. Flatfish',
'Sablefish juv':'Sablefish_Juv','Other Macrourids':'Other Macruids','Misc. deep fish':'Misc. fish deep','Pacific ocean perch':'POP','Pacific ocean perch juv':'POP_Juv',
'Northern rockfish':'Northern Rock','Shortspine thornyhead':'Shortspine Thorns','Shortspine thornyhead juv':'Shortspine Thorns_Juv','Atka mackerel juv':'Atka mackerel_Juv',
'Large sculpins':'Lg. Sculpins','Misc. shallow fish':'Misc. fish shallow','Octopus':'Octopi','Sand lance':'Sandlance','Managed forage':'Oth. managed forage','Oth pel. smelt':'Oth. pelagic smelt',
'Tanner crab*':'Bairdi','Tanner crab adu':'Bairdi','King crab*':'King Crab','King crab adu':'King Crab','Pandalid shrimp':'Pandalidae','Non-Pandalid shrimp':'NP shrimp',
'Sea star':'Sea stars','Brittle star':'Brittle stars','Urchins dollars and':'Urchins dollars cucumber','Urchins dollars and cucumbers':'Urchins dollars cucumber',
'Misc crabs':'Misc. crabs','Benthic amphipods':'Benthic Amphipods','Benth. Hydroid':'Hydroids','Benth. Urochordata':'Urochordata','Sea pens':'Sea Pens','Sponge':'Sponges',
'Polychates':'Polychaetes','Misc. worm etc.':'Misc. worms','Scyphozoid jellies':'Scyphozoid Jellies','Fish larvae':'Fish Larvae','Chaetognaths etc.':'Chaetognaths',
'Pelagic amphipods':'Pelagic Amphipods','Pel. gel. filter feeder':'Gelatinous filter feeders','Microzooplankton':'Pelagic microbes','Benthic bacteria':'Benthic microbes',
'Algae':'Macroalgae','Large phytoplankton':'Lg Phytoplankton','Small phytoplankton':'Sm Phytoplankton','Pelagic detritus':'Pelagic Detritus','Benth detritus':'Benthic Detritus',
}

def diets():
    model=json.loads((WORK/'outputs'/'numeric_writer_input.json').read_text(encoding='utf-8'))
    grids=json.loads((WORK/'outputs'/'direct_diet_source_grids.json').read_text(encoding='utf-8'))
    byname={g['name']:g for g in model['groups']}
    evidence=[];sums=[];issues=[]
    for p in grids:
        pno=p['pdf_page']
        for col,targets in MATRIX_TARGETS[pno].items():
            for target in targets:
                predator=byname[target];diet={};total=Decimal(0)
                for r in p['rows']:
                    raw=r['source_prey'];prey=PREY_ALIASES.get(raw,raw);v=r['values'][col]
                    g=byname.get(prey)
                    adopted=None if v is None else format(Decimal(v.rstrip('%')).scaleb(-2),'f')
                    if adopted is not None:
                        total+=Decimal(adopted)
                        if g:
                            key=str(g['n'])
                            assert key not in diet,(target,raw,prey)
                            diet[key]=adopted
                        else:issues.append({'predator':target,'prey':raw,'value':v,'page':pno})
                    evidence.append({'table':p['table'],'pdf_page':pno,'printed_page':pno-10,'consumer':target,'consumer_n':predator['n'],'source_column_index':col,'source_header':SOURCE_HEADERS[pno][col],'source_prey':raw,'prey':prey,'prey_n':g['n'] if g else None,'source_literal':v,'adopted_literal':adopted,'bbox':r['bboxes'][col],'status':'source_blank_not_in_diet' if v is None else ('printed_trace_zero' if Decimal(adopted)==0 else 'published_percent_divided_by_100')})
                diet['import']=None
                model['diet'][str(predator['n'])]=diet
                sums.append({'consumer':target,'n':predator['n'],'pdf_page':pno,'sum_proportions':str(total),'source_percent_sum':str(total*100),'import_status':'not_published','source_status':'direct_published_matrix; no normalization; source blanks not in diet'})
    (WORK/'outputs'/'direct_diet_cell_evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
    (WORK/'outputs'/'direct_diet_sums.json').write_text(json.dumps(sums,ensure_ascii=False,indent=2),encoding='utf-8')
    (WORK/'outputs'/'direct_diet_issues.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2),encoding='utf-8')
    (WORK/'outputs'/'numeric_writer_input.json').write_text(json.dumps(model,ensure_ascii=False,indent=2),encoding='utf-8')
    print('direct diets',len(sums),'issues',issues,flush=True)
    print('sum range',min(Decimal(x['sum_proportions']) for x in sums),max(Decimal(x['sum_proportions']) for x in sums),flush=True)

def companions():
    model=json.loads((WORK/'outputs'/'numeric_writer_input.json').read_text(encoding='utf-8'))
    canon=json.loads((WORK/'outputs'/'union_group_crosswalk.json').read_text(encoding='utf-8'))
    norm=lambda s:re.sub('[^a-z0-9]','',s.lower())
    names={norm(g['name']):g for g in canon}
    anchors=[199.4,239.4,274.8,310.2,360.7,413.8,454.4,507.2]
    headers=['group','n','biomass_rating','pb_rating','qb_rating','diet_rating','catch_federal_rating','catch_halibut_rating','catch_state_rating','catch_subsistence_rating','pdf_page','source_status']
    rows=[];ev=[]
    for pno in [278,279,280]:
        d=loadpage(pno);ls=lines(d['words']); start=next(i for i,r in enumerate(ls) if r[0]['text']=='GOA')+1
        for r in ls[start:]:
            if r[0]['x0']>100: continue
            label=' '.join(w['text'] for w in r if w['x0']<185)
            g=names.get(norm(label));assert g,(pno,label)
            cells=[[] for _ in anchors]
            for w in r:
                if w['x0']<185:continue
                if w['text']=='---':
                    for i in range(3):
                        ww=dict(w,text='-',x0=w['x0']+i*(w['x1']-w['x0'])/3,x1=w['x0']+(i+1)*(w['x1']-w['x0'])/3)
                        k=min(range(8),key=lambda j:abs((ww['x0']+ww['x1'])/2-anchors[j]));cells[k].append(ww)
                else:
                    k=min(range(8),key=lambda j:abs((w['x0']+w['x1'])/2-anchors[j]));cells[k].append(w)
            values=[''.join(w['text'] for w in cell) for cell in cells]
            assert all(v=='' or re.fullmatch('[0-8-]+',v) for v in values),(label,values)
            rows.append([g['name'],str(g['n'] or ''),*values,str(pno),'published; blank preserved; dash denotes absent group'])
            ev.extend({'table':'C28','group':g['name'],'n':g['n'],'field':headers[i+2],'source_literal':v,'pdf_page':pno,'bbox':bbox(cells[i]),'status':'source_blank' if v=='' else 'published'} for i,v in enumerate(values))
    assert len(rows)==147,len(rows)
    model['companions']['Published_pedigree.csv']={'description':'Table C28 GOA data quality ratings, scale 1 highest to 8 lowest; source blanks and absent-group dashes preserved. Not biological model parameters.','rows':[headers]+rows}
    # Preserve all tabulated source cells and unresolved crosswalks as companions.
    for fname,desc in [('numeric_cell_evidence.json','C1-C3 exact source values and field coordinate evidence'),('direct_diet_cell_evidence.json','C12-C26 exact source percentages, blank/trace distinctions and unresolved source prey')]:
        records=json.loads((WORK/'outputs'/fname).read_text(encoding='utf-8'))
        keys=list(dict.fromkeys(k for r in records for k in r))
        data=[[json.dumps(r[k],ensure_ascii=False) if isinstance(r.get(k),(list,dict)) else r.get(k) for k in keys] for r in records]
        model['companions'][fname.replace('.json','.csv')]={'description':desc,'rows':[keys]+data}
    cwheaders=list(canon[0])
    model['companions']['Source_group_crosswalk.csv']={'description':'Complete 147-row three-model union Table C1 crosswalk; only 133 rows have numerical GOA B and EE. Printed #N/A excludes a group in C1; zero biomass skate groups retained.','rows':[cwheaders]+[[r.get(k) for k in cwheaders] for r in canon]}
    (WORK/'outputs'/'pedigree_cell_evidence.json').write_text(json.dumps(ev,indent=2,ensure_ascii=False),encoding='utf-8')
    (WORK/'outputs'/'numeric_writer_input.json').write_text(json.dumps(model,indent=2,ensure_ascii=False),encoding='utf-8')
    for name,c in model['companions'].items():
        with (WORK/'outputs'/name).open('w',encoding='utf-8',newline='') as f:csv.writer(f).writerows(c['rows'])
    print('pedigree rows',len(rows),'companions',len(model['companions']),flush=True)

def bird_source():
    d=loadpage(224);ls=lines([w for w in d['words'] if w['upright']])
    firstsum=next(r for r in ls if r[0]['text']=='Sum')
    vals=[w for w in firstsum if re.fullmatch(r'[0-9.]+',w['text'])]
    assert len(vals)==11,vals
    anchors=[(w['x0']+w['x1'])/2 for w in vals]
    fields=['miscellaneous_invertebrates','gelatinous_zooplankton','crustacean_zooplankton','small_cephalopods','large_cephalopods','fish_low_energy','fish_medium_energy','fish_high_energy','birds_and_mammals','carrion_offal_and_discards','unknown']
    section=None;records=[];grid=[]
    sections={'Murres','Kittiwakes','Puffins','Auklets','Storm-Petrel','Fulmars','Gulls','Cormorants*'}
    for rr in ls:
        txt=' '.join(w['text'] for w in rr)
        if txt in sections:section=txt;continue
        if section is None:continue
        if txt.startswith('*Diet') or txt=='214':break
        prop=' '.join(w['text'] for w in rr if w['x0']<100)
        label=' '.join(w['text'] for w in rr if 100<=w['x0']<165)
        preferred=' '.join(w['text'] for w in rr if w['x0']>=478)
        cells=[[] for _ in anchors]
        for w in rr:
            if not(165<=w['x0']<478):continue
            k=min(range(11),key=lambda j:abs((w['x0']+w['x1'])/2-anchors[j]))
            cells[k].append(w)
        literals=[' '.join(w['text'] for w in c) for c in cells]
        # Source footnotes remain verbatim in a dedicated notes field rather than false numeric cells.
        numeric=all(v=='' or re.fullmatch(r'[0-9.+]+',v) for v in literals)
        grid.append([section,prop,label,*(literals if numeric else ['']*11),preferred,'224',txt if not numeric else ''])
        for field,c in zip(fields,cells):
            records.append({'table':'B8','pdf_page':224,'printed_page':214,'group':section,'row_label':label,'proportion_or_weighted_marker':prop,'field':field,'source_literal':' '.join(w['text'] for w in c),'bbox':bbox(c),'row_text':txt,'interpretation':'published source categories; not resolved Ecopath prey proportions'})
    model=json.loads((WORK/'outputs'/'numeric_writer_input.json').read_text(encoding='utf-8'))
    header=['source_bird_group','proportion_or_weighted_marker','source_row_label',*fields,'preferred_prey','pdf_page','source_note']
    comp={'description':'Table B8 source seabird diet categories and weighted summaries. Source percentages, blanks and trace + kept; these categories are not fully resolved Ecopath prey allocations. Values retain source provenance and energy-category meaning.','rows':[header]+grid}
    model['companions']['Published_seabird_diet_inputs.csv']=comp
    (WORK/'outputs'/'numeric_writer_input.json').write_text(json.dumps(model,ensure_ascii=False,indent=2),encoding='utf-8')
    with (WORK/'outputs'/'Published_seabird_diet_inputs.csv').open('w',encoding='utf-8',newline='') as f:csv.writer(f).writerows(comp['rows'])
    (WORK/'outputs'/'seabird_source_cells.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    print('bird source rows',len(grid),'anchors',anchors,flush=True)

def finalize():
    source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    model=json.loads((WORK/'outputs'/'numeric_writer_input.json').read_text(encoding='utf-8'))
    receipts=[]
    for name in ['numeric_cell_evidence.json','direct_diet_cell_evidence.json','pedigree_cell_evidence.json','seabird_source_cells.json']:
        path=WORK/'outputs'/name
        records=json.loads(path.read_text(encoding='utf-8'))
        for r in records:
            r['source_file']='regions/LME/LME_002/papers/GOA-2007/sources/noaa_22894_DS1-9dadd884.pdf'
            r['source_sha256']=source_hash
        path.write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
        keys=list(dict.fromkeys(k for r in records for k in r))
        rows=[[json.dumps(r[k],ensure_ascii=False) if isinstance(r.get(k),(list,dict)) else r.get(k) for k in keys] for r in records]
        cname=name.replace('.json','.csv')
        model['companions'][cname]={'description':f'Exact source-cell provenance for {name}; no normalization or scientific parameter repair.','rows':[keys]+rows}
        with (WORK/'outputs'/cname).open('w',encoding='utf-8',newline='') as f:csv.writer(f).writerows([keys]+rows)
        receipts.append({'path':name,'rows':len(records),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    (WORK/'outputs'/'numeric_writer_input.json').write_text(json.dumps(model,ensure_ascii=False,indent=2),encoding='utf-8')
    ds=json.loads((WORK/'outputs'/'direct_diet_sums.json').read_text(encoding='utf-8'))
    for s in ds:
        mapped=sum(Decimal(v) for k,v in model['diet'][str(s['n'])].items() if k!='import' and v is not None)
        s['mapped_prey_sum']=str(mapped)
        s['unresolved_source_prey_sum']=str(Decimal(s['sum_proportions'])-mapped)
    (WORK/'outputs'/'direct_diet_sums.json').write_text(json.dumps(ds,ensure_ascii=False,indent=2),encoding='utf-8')
    qa={'source_sha256':source_hash,'model_identity':'Aydin2007_Gulf_of_Alaska_1990-1994','groups':len(model['groups']),'consumers':len(model['consumers']),'direct_diets':len(ds),'basic_values':len(model['groups'])*5,'numerical_source_fields':'C1 B/EE; C2 PB/QB/TL; C3 retained/discard tonnes; C12-C26 applicable GOA and All diet columns; C28 quality; B8 bird source categories','group_order':'C1 union order filtered only on GOA B != #N/A; 147 union rows, 133 retained','visual_inspection':'C1 first two pages, C2 first page, C3 first page; all 14 diet table headers and C16/C22 full tables; B8 full table; C28 first page at 216 DPI (3x72)','conflicts':['C1/C2 numerical Mud/Black skate rows vs C3 #N/A catches','C16 FH.Sole 105.46%, S.Rock sole 106.93% exact printed sums; retained','C22 Lg.Sculpins 2.61% Yellowfin sole juv and 0.48% N.rock sole juv with no GOA C1/C2 groups; cells retained as unresolved companion, mapped sum 96.92%','C28 caption 1-8 scale but producers/detritus diet rating 0 published'], 'no_fabrication':'No input zero completion, diet normalization, preference allocation, biomass reconstruction or missing-parameter default applied. Percentage /100 and tonnes /291840 are explicit unit conversions.','evidence':receipts}
    (WORK/'qa'/'numeric_extraction_audit.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in qa.items() if k in ('groups','consumers','direct_diets','source_sha256','conflicts')}),flush=True)

if __name__=='__main__':
    import sys
    if sys.argv[1]=='cache': cache([int(x) for x in sys.argv[2:]] if sys.argv[2:] else range(239,310))
    elif sys.argv[1]=='render': render([int(x) for x in sys.argv[2:]])
    elif sys.argv[1]=='basic': basic()
    elif sys.argv[1]=='grids': matrix_grids()
    elif sys.argv[1]=='headers': matrix_headers()
    elif sys.argv[1]=='diets': diets()
    elif sys.argv[1]=='companions': companions()
    elif sys.argv[1]=='birds': bird_source()
    elif sys.argv[1]=='finalize': finalize()
    elif sys.argv[1]=='finish': diets(); bird_source(); finalize()
