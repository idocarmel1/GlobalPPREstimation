from pathlib import Path
from decimal import Decimal
import csv, json, hashlib, pdfplumber

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT.parents[1]/'papers'/'LME027-Villanueva-2004'/'010056023-adc18d15.pdf'
OUT=ROOT/'extracted_tables'; OUT.mkdir(parents=True,exist_ok=True)
EVID=ROOT/'evidence'/'source'

# Literal transcription checked against rendered Table I, not OCR spelling.
data='''Scomberomorus tritor|3.4 .50 .009 .004 2.520 12.60 .950 .200
Elops spp.|3.3 .50 .021 .010 1.990 9.95 .950 .200
Sphyraena spp.|3.3 .25 8.688 2.172 1.700 8.50 .176 .200
Arius spp.|3.2 .50 2.544 1.272 2.655 17.70 .312 .150
Polydactylus quadrifilis|3.5 1.00 1.272 1.272 1.540 7.70 .079 .200
Pseudotolithus elongatus|3.3 1.00 1.800 1.800 1.680 8.40 .026 .200
Other Sciaenidae|3.3 1.00 .089 .089 1.650 8.25 .950 .200
Psettodes/Citharichthys|3.3 .50 .166 .0166 1.980 11.00 .950 .329
Galeoides decadactylus|3.2 .50 2.150 2.150 1.515 10.10 .950 .150
Dasyatis spp.|3.1 .50 .075 .037 1.650 8.25 .950 .100
Brachydeuterus auritus|2.7 .50 .019 .010 2.870 28.70 .950 .150
Plectorhinchus/Pomadasys|3.2 .75 1.558 1.168 1.270 8.47 .950 .150
Ilisha africana|2.9 .50 2.444 1.222 2.445 16.30 .950 .150
Cynoglossus spp.|3.1 .50 9.224 4.612 1.200 8.00 .950 .180
Chloroscombrus/Hemicaranx|3.3 .25 .066 .016 3.312 17.40 .935 .150
Carangidae (bentho-pelagic)|3.3 .50 .718 .359 1.335 8.90 .950 .150
Gerreidae|2.9 .50 .128 .064 3.075 20.50 .950 .180
Other Carangidae|3.2 .50 .224 .112 2.407 13.37 .440 .150
Ephippidae|3.0 .75 .013 .010 2.130 14.20 .950 .150
Ethmalosa fimbriata|2.7 .75 23.543 17.657 2.685 17.90 .543 .100
Sardinella maderensis|2.8 .50 .203 .102 3.390 33.90 .950 .050
Mugilidae|2.4 .50 2.750 1.375 1.386 27.72 .692 .051
Sarotherodon melanotheron|2.3 .60 2.100 1.260 1.275 25.20 .856 .050
Tilapia guineensis|2.3 .50 1.800 .900 1.030 20.60 .613 .250
Pelagic Shrimps|2.3 .75 4.674 3.505 4.500 18.00 .950 .250
Littoral shrimps|2.3 .25 26.853 6.713 4.500 18.00 .950 .312
Pelagic crabs|2.7 .75 7.409 5.557 2.500 8.00 .950 .312
Littoral crabs|2.1 .25 3.576 .894 2.500 8.00 .950 .312
Cephalopods|3.0 .50 29.892 14.946 2.500 8.00 .950 .333
Bivalves and Gastropods|2.0 .50 21.320 10.600 3.000 9.00 .950 .320
Annelids and Polychaets|2.0 .25 26.530 6.633 8.000 25.00 .950 .314
Zoobenthos|2.1 .25 32.853 8.213 22.000 70.00 .950 .333
Pelagic zooplankton|2.1 .50 7.221 3.611 50.000 150.00 .950 .333
Littoral zooplankton|2.1 .50 4.104 2.052 50.000 150.00 .950 .333
Benthic algae|1.0 .25 50.000 12.500 36.798 - .950 -
Pelagic phytoplankton|1.0 .50 6.810 3.405 200.000 - .950 -
Littoral phytoplankton|1.0 .50 1.968 .984 365.000 - .950 -
Detritus|1.0 1.000 1.000 - - - .863 -'''
fields=['TL','habitat_area_fraction','biomass_A_t_km2_habitat','biomass_B_t_km2_whole_area','PB_per_year','QB_per_year','EE','GE']
pdf=pdfplumber.open(SRC)
page=pdf.pages[4]
words=page.extract_words()
idwords=sorted([w for w in words if w['x0']<94 and w['top']>260 and w['top']<700],key=lambda w:w['top'])
# The visible row-1 numeral has no extracted text; row11 OCR is Il.
idwords.insert(0,next(w for w in words if w['text'].startswith('Scomberomorus')))
assert len(idwords)==38
xregions=[(199,220),(233,264),(280,312),(326,355),(355,385),(389,418),(418,442),(442,469)]
cells=[]; groups=[]
def literal(s): return '0'+s if s.startswith('.') else s
for idx,line in enumerate(data.splitlines(),1):
    name,nums=line.split('|'); nums=[literal(s) for s in nums.split()]
    idw=idwords[idx-1]; cy=(idw['top']+idw['bottom'])/2
    g={'group_id':idx,'group_name':name,'pdf_page':5,'printed_page':409,'table':'I'}
    for field,s,(xl,xr) in zip(fields,nums,xregions):
        chars=[c for c in page.chars if xl<= (c['x0']+c['x1'])/2 <xr and abs((c['top']+c['bottom'])/2-cy)<5.5]
        isitalic=bool(chars) and all('Italic' in c['fontname'] for c in chars if c['text'].strip())
        c={'group_id':idx,'group_name':name,'field':field,'literal':s,'numeric_value':None if s=='-' else float(s),'missingness':'printed_dash' if s=='-' else 'printed_number','pdf_page':5,'printed_page':409,'table':'I','cell_id':f'I/r{idx}/{field}','bbox_pt':[xl,round(cy-6,3),xr,round(cy+6,3)],'text_layer_literal':''.join(c['text'] for c in sorted(chars,key=lambda x:x['x0'])),'font_names':sorted(set(c['fontname'] for c in chars)),'model_estimated_italic':isitalic if s!='-' else None,'verification':'manual transcription checked against source_page-05.png; geometry/typography from pdfplumber'}
        cells.append(c);g[field]=None if s=='-' else s
    g['group_type']='detritus' if idx==38 else ('primary_producer' if idx>=35 else 'consumer')
    groups.append(g)

fleets=['Dugout','Beach seine','Encircling gillnets','Cast nets','Fixed gill nets','Derived gill nets','Trawl lines','Shrimp nets','Traps','Other gears']
catch_entries={1:{2:'.005',5:'.005'},2:{9:'.010'},3:{1:'.200',2:'.100',4:'.070',5:'.260'},4:{0:'.110',1:'.120',2:'.010',4:'.140',5:'.140',6:'.040'},5:{1:'.060',2:'.015',4:'.010',5:'.050',7:'.005'},6:{1:'.010',4:'.010',5:'.050'},7:{1:'.030',4:'.025',5:'.070',7:'.005'},8:{9:'.010'},9:{4:'.009',7:'.001'},10:{9:'.010'},11:{9:'.010'},12:{3:'.005',4:'.003',7:'.002'},13:{7:'.010'},14:{1:'.005',4:'.003',7:'.001',8:'.001'},15:{2:'.020'},16:{2:'.010',5:'.060'},17:{1:'.010'},18:{1:'.015',2:'.005'},19:{1:'.010'},20:{1:'.560',2:'22.250',3:'.015',4:'.300',5:'.050',7:'.005',8:'.010'},21:{1:'.006',2:'.002',3:'.002'},22:{1:'.375',2:'.010',3:'.150',5:'.040',7:'.005',8:'.010'},23:{1:'.180',3:'.030',4:'.030',5:'.010',8:'.090'},24:{1:'.070',3:'.020',4:'.030',5:'.005',7:'.005',8:'.010'},25:{7:'1.050'},26:{7:'.350'},27:{9:'.010'},28:{8:'.100'},29:{9:'.010'},30:{8:'4.800'}}
totals='.01 .01 .63 .56 .14 .07 .13 .01 .01 .01 .01 .01 .01 .01 .02 .07 .01 .02 .01 23.19 .01 .59 .34 .14 1.05 .35 .01 .10 .01 4.80'.split()
source_names_II={1:'Scomberomorous tritor',7:'Other Sciaenidae spp.',15:'Chloroscombrus/Hemicaranx spp.',17:'Gerreidae spp.',18:'Other Carangidae spp.',19:'Ephippidae spp.'}
page6=pdf.pages[5]; ws6=page6.extract_words()
ids6=sorted([w for w in ws6 if 109<=w['x0']<120 and 194<=w['top']<475],key=lambda w:w['top'])
assert len(ids6)==32
anchor=[258,304,355,420,465,506,545,585,619,652,692]
regions6=[(240,272),(287,320),(340,374),(405,435),(450,480),(490,520),(531,559),(570,598),(604,634),(637,668),(680,703)]
catch=[];catch_cells=[]
for idx in range(1,31):
    g=groups[idx-1]; row={'group_id':idx,'group_name':g['group_name'],'table_II_source_name':source_names_II.get(idx,g['group_name'])}
    cy=(ids6[idx-1]['top']+ids6[idx-1]['bottom'])/2
    for k,fleet in enumerate(fleets+['Total catch']):
        s=literal(catch_entries[idx][k]) if k in catch_entries[idx] else ''
        if k==10:s=literal(totals[idx-1])
        row[fleet]=s
        xl,xr=regions6[k]
        chars=[c for c in page6.chars if xl<=(c['x0']+c['x1'])/2<xr and abs((c['top']+c['bottom'])/2-cy)<4.5]
        catch_cells.append({'group_id':idx,'group_name':g['group_name'],'field':fleet,'literal':s,'numeric_value':float(s) if s else None,'missingness':'printed_number' if s else 'blank_not_explicit_zero','pdf_page':6,'printed_page':410,'table':'II','cell_id':f'II/r{idx}/{fleet}','bbox_pt':[xl,round(cy-4.5,3),xr,round(cy+4.5,3)],'text_layer_literal':''.join(c['text'] for c in sorted(chars,key=lambda x:x['x0'])),'verification':'manual transcription checked against source_page-06.png; geometry from pdfplumber'})
    row['pdf_page']=6;row['printed_page']=410;row['table']='II';catch.append(row)

def writecsv(path,rows):
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def savejson(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
writecsv(OUT/'table_I_literal.csv',groups)
writecsv(OUT/'table_II_literal.csv',catch)
savejson(OUT/'table_I_cell_provenance.json',cells)
savejson(OUT/'table_II_cell_provenance.json',catch_cells)
savejson(EVID/'source_coordinate_words.json',{'pdf_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'pages':[{'pdf_page':i+1,'width_pt':p.width,'height_pt':p.height,'words':p.extract_words()} for i,p in enumerate(pdf.pages)]})
savejson(OUT/'literal_source_extraction.json',{'schema':'literal_source_evidence_v1_not_full_ecopath_import','source_pdf':'../../papers/LME027-Villanueva-2004/010056023-adc18d15.pdf','path_basis':'candidate_directory','sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'model_name':'Sine-Saloum Delta Biosphere Reserve','model_period':None,'year_evidence':'No explicit baseline year in chapter; catches refer to 2000 and 2001-source data. Publication year is not model year.','groups':groups,'catches':catch,'fleets':fleets,'published_totals':{'catch_density':'32.340','fleet_totals':['0.110','1.651','22.427','0.222','0.630','0.740','0.040','1.439','5.021','0.060'],'fleet_TL':['3.18','2.74','2.75','2.40','2.92','3.20','3.18','2.28','2.01','3.02'],'catch_TL':'2.63'},'diet_matrix':None,'diet_orientation':None,'not_importable_reason':'Quantitative diet matrix and several model fields unavailable in chapter. Blank catches preserved; no zeros, defaults, or diet completion introduced.','unknown_fields':['diet proportions and imports','unassimilated consumption','biomass accumulation','detritus routing/export','migration','discards separated from catches','native baseline year','exact membership of pooled groups']})

scenario='''0.004 0.000 0.00 0.011 0.000 0.00 0.006 0.000 0.00
0.010 0.002 0.22 0.011 0.004 0.36 0.002 0.001 0.36
2.150 1.683 0.78 0.714 0.916 1.28 0.750 0.961 1.28
1.256 1.131 0.90 0.633 0.934 1.47 0.253 0.373 1.47
1.268 1.341 1.06 0.160 0.277 1.73 0.271 0.470 1.73
1.797 1.681 0.94 0.080 0.123 1.53 0.015 0.023 1.53
0.085 0.001 0.01 0.142 0.002 0.02 0.027 0.000 0.02
0.083 0.102 1.23 0.011 0.023 2.01 0.002 0.004 2.01
1.076 1.584 1.47 0.011 0.028 2.41 0.002 0.005 2.41
0.037 0.022 0.60 0.011 0.011 0.99 0.002 0.002 0.99
0.009 0.021 2.22 0.011 0.041 3.63 0.002 0.008 3.63
1.167 1.010 0.87 0.011 0.016 1.42 0.002 0.003 1.42
1.222 1.356 1.11 0.011 0.021 1.82 0.002 0.004 1.82
4.614 4.973 1.08 0.011 0.020 1.76 0.002 0.004 1.76
0.016 0.012 0.73 0.022 0.026 1.19 0.004 0.005 1.19
0.357 0.531 1.49 0.080 0.194 2.24 0.015 0.037 2.44
0.064 0.067 1.05 0.011 0.020 1.72 0.002 0.004 1.72
0.112 0.148 1.33 0.023 0.050 2.17 2.068 0.009 2.17
0.010 0.011 1.12 0.011 0.020 1.84 0.002 0.004 1.84
17.021 10.685 0.63 25.580 26.314 1.03 2.068 2.127 1.03
0.102 0.150 1.48 0.011 0.028 2.42 0.002 0.005 2.42
1.356 0.740 0.55 0.666 0.595 0.89 0.173 0.155 0.89
1.249 1.062 0.85 0.386 0.537 1.39 0.145 0.202 1.39
0.896 0.809 0.90 0.160 0.236 1.48 0.060 0.089 1.48
3.481 3.511 1.01 1.194 1.972 1.65 1.492 2.465 1.65
6.710 6.984 1.04 0.401 0.683 1.70 0.501 0.854 1.70
5.593 11.210 2.00 0.012 0.038 3.28 0.002 0.007 3.28
0.892 0.909 1.02 0.114 0.191 1.67 0.022 0.036 1.67
15.047 23.919 1.59 0.012 0.030 2.60 0.002 0.006 2.60
10.528 8.532 0.81 5.427 7.205 1.33 1.031 1.369 1.33'''
scenario_fields=['biomass_start','biomass_end','biomass_S_E_printed','catch_start','catch_end','catch_S_E_printed','value_start','value_end','value_S_E_printed']
scenario_rows=[]
for idx,line in enumerate(scenario.splitlines(),1):
    row={'group_id':idx,'Table_I_identity':groups[idx-1]['group_name']}
    row.update(zip(scenario_fields,line.split()));row.update(pdf_page=7,printed_page=411,table='III',scenario='10-year doubling fishing effort all gears',input_status='Ecosim scenario output, not baseline substitution',verification='Manual rendered-page transcription; TableIII names linked by explicit taxon identity')
    scenario_rows.append(row)
writecsv(OUT/'table_III_scenario_literal.csv',scenario_rows)

# Arithmetic evidence only: no source value is replaced.
checks=[]
for g in groups:
    if g['biomass_B_t_km2_whole_area'] is not None:
        expected=Decimal(g['biomass_A_t_km2_habitat'])*Decimal(g['habitat_area_fraction'])
        observed=Decimal(g['biomass_B_t_km2_whole_area']); delta=observed-expected
        checks.append({'group_id':g['group_id'],'group_name':g['group_name'],'check':'B_B minus habitat*B_A','printed':str(observed),'arithmetic_expected':str(expected),'delta':str(delta),'material_discrepancy':abs(delta)>Decimal('.0009'),'source':'Table I PDF5 printed409; no correction applied'})
    if g['QB_per_year'] is not None and g['GE'] is not None:
        expected=Decimal(g['PB_per_year'])/Decimal(g['QB_per_year']); observed=Decimal(g['GE']);delta=observed-expected
        checks.append({'group_id':g['group_id'],'group_name':g['group_name'],'check':'GE minus PB/QB','printed':str(observed),'arithmetic_expected':str(expected),'delta':str(delta),'material_discrepancy':abs(delta)>Decimal('.001'),'source':'Table I PDF5 printed409; no correction applied'})
writecsv(OUT/'table_I_internal_arithmetic.csv',checks)
audit=[]
for row in catch:
    subtotal=sum(Decimal(row[f]) if row[f] else Decimal(0) for f in fleets)
    audit.append({'kind':'group_total','identity':row['group_name'],'literal_total':row['Total catch'],'sum_numeric_cells':str(subtotal),'delta':str(Decimal(row['Total catch'])-subtotal),'blank_cells_assumption':'Blanks excluded from arithmetic only; not source zeros'})
pub=['.110','1.651','22.427','.222','.630','.740','.040','1.439','5.021','.060']
for k,fleet in enumerate(fleets):
    subtotal=sum(Decimal(r[fleet]) if r[fleet] else Decimal(0) for r in catch)
    audit.append({'kind':'fleet_total','identity':fleet,'literal_total':literal(pub[k]),'sum_numeric_cells':str(subtotal),'delta':str(Decimal(pub[k])-subtotal),'blank_cells_assumption':'Blanks excluded from arithmetic only; not source zeros'})
subtotal=sum(Decimal(r['Total catch']) for r in catch)
audit.append({'kind':'grand_total','identity':'sum printed group catch totals','literal_total':'32.340','sum_numeric_cells':str(subtotal),'delta':str(Decimal('32.340')-subtotal),'blank_cells_assumption':'No blank group total for Table II 1-30; groups31-38 absent, not confirmed zero'})
writecsv(OUT/'table_II_arithmetic.csv',audit)
print('wrote literal groups, catches, provenance and arithmetic: '+str(OUT))
