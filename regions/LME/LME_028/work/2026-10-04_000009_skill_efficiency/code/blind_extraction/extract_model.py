from pathlib import Path
from decimal import Decimal
import json, re, sys, datetime, hashlib

ROOT=Path(__file__).resolve().parents[7]
RUN=ROOT/'regions/LME/LME_028/work/2026-10-04_000009_skill_efficiency'
OUT=RUN/'outputs/blind_extraction'
E=OUT/'evidence'
def coords(p):
    source=json.loads((E/f'page_{p}_coordinates.json').read_text(encoding='utf-8'));rows=[]
    for line in source:
        if rows and 0<=line['y']-rows[-1]['y']<3 and all(w['bbox'][0]>=270 for w in line['cells']):
            rows[-1]['cells']=sorted(rows[-1]['cells']+line['cells'],key=lambda w:w['bbox'][0])
        else:rows.append(line)
    return rows
def text(cells):return ' '.join(w['text'] for w in cells)
def clean(v):return v.strip('()') if re.fullmatch(r'\(?\d+(?:\.\d+)?\)?',v) else None
def norm(s):
    s=s.casefold().replace('≤','<').replace('threadfm','threadfin')
    s=re.sub(r'\bjuv\.?\b','juvenile',s);s=re.sub(r'\bad\.?\b','adult',s)
    s=s.replace('dem.','demersal').replace('demesral','demersal');s=re.sub(r'\binverts\b','invertebrates',s)
    s=s.replace('phytoplanktons','phytoplankton').replace('zooplanktons','zooplankton').replace('benthic producers','benthic producer')
    s=re.sub(r'\([^<>]*?ids\)','',s)
    return re.sub(r'[^a-z0-9<>]','',s)
groups=[];cells=[['group_seq','group_name','field','source_literal','adopted_literal','status','pdf_page','printed_page','table','bbox_pdf_points','note']]
for line in coords(191)[2:40]:
    words=line['cells'];n=int(words[0]['text']);name=text([w for w in words[1:] if w['bbox'][2]<325])
    # The scanned page shows ≤; ABBYY's hidden layer reads < for these symbols.
    if n in [21,24,29]:name=name.replace('<','≤')
    g={'n':n,'name':name,'parameter_roles':{},'source_status':{'B/PB/QB/EE':'Table 6.1(b), PDF191 printed176; parenthesised model estimates retained'}}
    for field,x in [('biomass',365),('pb',411),('qb',457),('ee',502)]:
        candidates=[w for w in words if w['bbox'][0]>325 and abs(w['bbox'][2]-x)<12]
        assert len(candidates)<=1,(n,field,candidates)
        w=candidates[0] if candidates else None;literal=w['text'] if w else '';value=clean(literal)
        g[field]=value
        role='model_estimated' if literal.startswith('(') else 'tabulated' if value is not None else 'not_applicable_or_unreported'
        g['parameter_roles'][field]=role
        cells.append([str(n),name,field,literal,value,role,191,176,'Table6.1(b)',json.dumps(w['bbox']) if w else '', 'Caption on PDF190 printed175 defines parentheses as estimated by model'])
    groups.append(g)
assert [g['n'] for g in groups]==list(range(1,39))
lookup={norm(g['name']):g['n'] for g in groups}
aliases={'threadfinbream':13,'bigeyes':14,'lizardfish':15,'juvenilehairtail':16,'adulthairtail':17,'pomfret':18,'demfish<30cm':24,'juveniledemfish>30cm':25,'adultdemfish>30cm':26,'demsharksandrays':32}
lookup.update(aliases)
def identify(name):
    k=norm(name)
    if k not in lookup:raise ValueError(('unmatched source group',name,k))
    return lookup[k]

fleets=['PSt','ShT','PS','H&L','GN','Others']
landings={};catch_cells=[['group_seq','group_name','source_group_name','field','source_literal','pdf_page','printed_page','table','bbox_pdf_points','status']]
catch_totals=[['group_seq','group_name','printed_2000s_total_t_km2_year','computed_six_fleet_sum_t_km2_year','difference','pdf_page','printed_page','table','status']]
for p,ymin,ymax in [(193,510,658),(194,158,399)]:
    for line in coords(p):
        if not ymin<=line['y']<=ymax:continue
        label=text([w for w in line['cells'] if w['bbox'][0]<197])
        if not label:continue
        if label=='Total':
            numbers=[w for w in line['cells'] if w['bbox'][0]>=197 and clean(w['text']) is not None]
            for f,w in zip(fleets+['printed_total'],numbers[1:]):
                catch_cells.append(['Total','All groups',label,f,w['text'],p,p-15,'Table6.2',json.dumps(w['bbox']),'published_footer_total_not_import_group'])
            continue
        n=identify(label)
        numbers=[w for w in line['cells'] if w['bbox'][0]>=197 and clean(w['text']) is not None]
        assert len(numbers)==8,(p,label,numbers)
        landings[str(n)]={f:w['text'] for f,w in zip(fleets,numbers[1:7])}
        for f,w in zip(fleets+['printed_total'],numbers[1:]):
            catch_cells.append([n,groups[n-1]['name'],label,f,w['text'],p,p-15,'Table6.2',json.dumps(w['bbox']),'tabulated_landings_no_discard_separation'])
        subtotal=sum(Decimal(w['text']) for w in numbers[1:7]);printed=Decimal(numbers[7]['text'])
        catch_totals.append([n,groups[n-1]['name'],str(printed),str(subtotal),str(subtotal-printed),p,p-15,'Table6.2','printed totals retained separately; importer Total is exact fleet sum'])
assert len(landings)==38,sorted(set(range(1,39))-set(map(int,landings)))

# Blocks keyed by explicitly verified predator labels; numeric columns use right-edge anchors.
blocks=[(357,129,205.8,[3,4],[302,354],200),(357,287,431,[5,6,7,8,9],[250,317,384,438,510],195),(357,514,659,[10,11],[241,284],195),
        (358,117,351,[12],[297],240),(358,413,684,[13,14,15],[307,375,443],220),
        (359,129,439,[16,17,18],[308,377,445],240),
        (360,129,452,[19,20,21,22,23],[290,344,400,448,500],235),
        (361,129,480,[24,25,26,27],[299,372,444,517],235),
        (362,140,438,[28,29,30,31],[290,362,444,508],230),
        (363,136,663,[32,33,34,35,36,37],[249,303,352,413,467,522],205)]
diet={str(n):{'import':None} for n in range(3,38)}
diet_cells=[['consumer_seq','consumer_name','prey_seq','prey_name','source_row_name','source_literal','adopted_literal','status','pdf_page','printed_page','table','bbox_pdf_points','note']]
observed=set();printed_sums=[]
for p,ymin,ymax,cons,anchors,split in blocks:
    pending='';rows_seen=set()
    for line in coords(p):
        if not ymin<=line['y']<=ymax:continue
        labels=[w for w in line['cells'] if w['bbox'][0]<split]
        numbers=[w for w in line['cells'] if w['bbox'][0]>=split and re.fullmatch(r'\d+\.\d+',w['text'])]
        label=text(labels).strip(' .-')
        if pending:label=(pending+' '+label).strip();pending=''
        # Wrapped labels precede a continuation with numbers.
        if label and ('Sessile/other'==label or label in ['Threadfin bream','Lizard fish','Adult hairtail','Juvenile large pelagic','Juv demersal fish','Adult demersal fish','Demersal sharks and']):
            pending=label;continue
        if not label:continue
        if label=='Sum':
            printed_sums.append({'consumers':cons,'source_values':[w['text'] for w in numbers],'pdf_page':p});continue
        prey=identify(label);rows_seen.add(prey)
        row_numbers={}
        for w in numbers:
            j=min(range(len(anchors)),key=lambda j:abs(w['bbox'][2]-anchors[j]))
            assert abs(w['bbox'][2]-anchors[j])<8,(p,label,w)
            assert j not in row_numbers,(p,label,j)
            row_numbers[j]=w
        for j,c in enumerate(cons):
            key=(c,prey);assert key not in observed,(p,key);observed.add(key)
            w=row_numbers.get(j);lit=w['text'] if w else ''
            if w:diet[str(c)][str(prey)]=lit
            diet_cells.append([c,groups[c-1]['name'],prey,groups[prey-1]['name'],label,lit,lit,'tabulated' if w else 'source_blank_structural_absence',p,p-15,'Appendix6.2',json.dumps(w['bbox']) if w else '', 'blank retained in standard import; runtime interprets absent prey as zero'])
    assert not pending,(p,pending)
    for c in cons:
        for prey in range(1,39):
            if (c,prey) not in observed:
                diet_cells.append([c,groups[c-1]['name'],prey,groups[prey-1]['name'],'','','','source_row_omitted_structural_absence',p,p-15,'Appendix6.2','','not listed in sparse source block; standard import left blank'])
        diet_cells.append([c,groups[c-1]['name'],'import','outside modeled area','','',None,'not_reported_unknown',p,p-15,'Appendix6.2','','no import row; unknown never replaced with stated zero'])

published={}
for p,title,xleft,count,start,end in [(197,'Pedigree_categories',270,5,118,550),(199,'Pedigree_indices',270,5,118,550),(205,'Mortality_outputs',290,6,140,562)]:
    rows=[['group_seq','group_name','source_group_name',*(['B','PB','QB','Diet','Catch'] if count==5 else ['F_2000s_per_year','M_2000s_per_year','M0_2000s_per_year']),'pdf_page','printed_page','table','status']]
    for line in coords(p):
        if not start<=line['y']<=end:continue
        label=text([w for w in line['cells'] if w['bbox'][0]<xleft])
        n=identify(label)
        nums=[w for w in line['cells'] if w['bbox'][0]>=xleft and (clean(w['text']) is not None or w['text']=='N/A')]
        assert len(nums)==count,(p,label,nums)
        vals=[w['text'] for w in nums][-3:] if count==6 else [w['text'] for w in nums]
        rows.append([n,groups[n-1]['name'],label,*vals,p,p-15,'Table6.5' if count==6 else 'Table6.3(b)' if p==197 else 'Table6.4(b)','published_model_output' if count==6 else 'published_uncertainty_metadata'])
    assert len(rows)==38,(p,len(rows))
    published[title+'.csv']={'description':title+' of 2000s model; source evidence outside eight EwE imports','rows':rows}

# Author-stated numeric fields outside the final table remain separately identified.
prose=[['group_seq','field','source_literal','units','pdf_page','printed_page','section','status','adoption','note']]
def note(n,field,value,units,p,section,why='',adopt=False):
    prose.append([n,field,value,units,p,p-15,section,'published_prose', 'standard import' if adopt else 'companion only',why])
    if adopt:
        groups[n-1][field]=value;groups[n-1]['parameter_roles'][field]='author_stated_or_derived'
for n,v,p in [(10,'7.60',341),(13,'3.08',342),(14,'3.33',342),(19,'1.75',346),(20,'1.75',347),(21,'3.3',348),(23,'1.43',349),(24,'4.7',350),(25,'3.5',351),(26,'2.1',351),(27,'3.08',352),(28,'2.41',347),(29,'4.26',353),(31,'1.31',354),(32,'2.2',355),(33,'0.68',355)]:note(n,'z',v,'year^-1',p,'Appendix6.1','Total mortality stated in prose; may differ from final PB',True)
for n,v,p in [(5,'0.3',339),(18,'0.2',346),(27,'0.2',352),(32,'0.2',355),(33,'0.2',355)]:note(n,'pq',v,'dimensionless',p,'Appendix6.1','Assumed P/Q reported explicitly; retained despite rounding or final parameter conflicts',True)
alternatives=[(1,'pb','399',337),(1,'annual_production_carbon','14290',337),(1,'annual_production_wet_weight','128608',337),(1,'chlorophyll_to_wet_weight','100',337),(1,'wet_weight_to_C','9',337),(2,'pb','11.9',338),(2,'catch','0.045',338),(4,'ee','0.95',339),(4,'biomass_survey','1.529',339),(8,'pb','3',339),(8,'qb','7',340),(8,'catch','0.763',340),(10,'biomass_survey','0.013',340),(11,'biomass_survey','0.0045',341),(11,'pb','4',341),(12,'biomass_acoustic','1.24',341),(12,'biomass_trawl','0.13',341),(12,'biomass_mean','0.68',341),(14,'biomass','0.127',342),(14,'catch','0.207',343),(15,'biomass','0.0318',343),(15,'catch','0.086',344),(18,'catch','0.230',346),(18,'pb_role','model_estimated',346),(20,'catch','0.089',347),(22,'biomass','0.072',350),(22,'qb','16.47',350),(26,'biomass','0.015',351),(27,'ee','0.95',352),(27,'catch','0.643',352),(30,'biomass','0.242',354),(30,'qb','16.08',354),(32,'ee','0.95',355)]
for n,f,v,p in alternatives:note(n,f,v,'source field units (B/catch t km^-2; PB/QB year^-1; efficiencies fractions)',p,'Appendix6.1','Earlier/source-estimation description differs in places from final Table6.1(b)/6.2; preserved without overwrite')
for n,f,v,u,p,why in [
(3,'biomass_regional_survey_values','10.4; 9.8; 6.9','t km^-2',338,'Pearl River Estuary, western Guangdong, eastern Hainan; reported average9 used'),
(3,'catch_prose_2000','0.095','t km^-2 year^-1',338,'Acetes spp reported as Mo shrimp; source landings year2000'),
(4,'catch_proxy_1993','0.044','t km^-2 year^-1',339,'No2000report;1993closestavailableproxy'),
(5,'biomass_survey','2.24','t km^-2',340,'TableA6.2'),(6,'biomass_survey','1.98','t km^-2',340,'TableA6.2'),(7,'biomass_survey','1.43','t km^-2',340,'TableA6.2'),(8,'biomass_survey','2.68','t km^-2',340,'TableA6.2'),(9,'biomass_survey','2.61','t km^-2',340,'TableA6.2'),
(6,'catch_prose','0.0019','t km^-2 year^-1',340,'SAUPestimate; Table6.2differentroundedfleet sum'),(7,'catch_prose','0.039','t km^-2 year^-1',340,'Nationalcrustaceansminusshrimpandcrab'),
(10,'total_mortality_range','7.1-8.1','year^-1',341,'Metapenaeopsis palmensis and M.barbata; mean7.60'),
(12,'catch_prose','0.273','t km^-2 year^-1',342,'SAUPestimate'),
(14,'biomass_acoustic','0.245','t km^-2',342,'Originalacousticestimate'),(14,'biomass_trawl','0.009','t km^-2',342,'Originaltrawlestimate'),(14,'catch_composition_fraction','2.31','percent',343,'Late1990ssurvey'),
(15,'total_mortality_by_subregion','1.42; 1.78','year^-1',343,'NSCScontinental shelf;GulfTonkin; author usesaverageasPB'),
(18,'biomass_pooled_before_allocation','0.43','t km^-2',346,'Stromateids, ariommids, nomeis, formionids; even four-way allocation stated'),
(19,'exploitation_F_Z','0.62','dimensionless',346,'Assumedaverageforotherdemersal groups'),(19,'catch_prose','0.001','t km^-2 year^-1',347,'SAUPestimate'),
(20,'natural_mortality','0.67','year^-1',347,'Paulyempirical equation'),(20,'exploitation_F_Z','0.62','dimensionless',347,'NSCSdemersalaverage'),
(28,'biomass_survey_range','0.00091-0.11','t km^-2',347,'Trawl/acoustic mean deemedtoolow; authoradjusted0.07'),
(21,'biomass_acoustic_commercial','0.0368','t km^-2',348,'Commercialsmallcroakers'),(21,'biomass_trawl_Pennahia','0.392','t km^-2',348,'Surveyalternative'),(21,'commercial_noncommercial_demersal_ratio','1:0.9','ratio',348,'Scaling authoruses'),(21,'catch_prose','0.035','t km^-2 year^-1',349,'CalculatedB andF'),
(23,'bottom_trawl_adult_croaker_share','1.5','percent',349,'HongKongcatchcompositionproxy'),(23,'total_demersal_resource','0.64','t km^-2',349,'Late1990sresourceestimate'),(23,'fishing_mortality','0.67','year^-1',349,'Adults'),(23,'natural_mortality','0.76','year^-1',349,'Adults'),
(22,'catch_juvenile_share','90','percent',350,'Larimichthys crocea totalreported catch0.079; authorfraction, not usedtooverwritefleets'),(22,'catch_stock','0.079','t km^-2 year^-1',350,'Nationalyellowcroakerlandings2000'),
(24,'natural_mortality','1.8','year^-1',350,'Averagedmemberestimates'),(24,'exploitation_F_Z','0.62','dimensionless',350,'Assumedaverage'),(24,'catch_prose','0.179','t km^-2 year^-1',350,'SAUPestimate'),
(25,'large_demersal_catch_share','25','percent',351,'Bottomtrawls'),(25,'total_resource_as_written','0.64','t km^-2',351,'Prosedescribeslargedemersalresource;0.143at90percentnotarithmeticallyequal; preserve'),(25,'juvenile_biomass_share','90','percent',351,'Authorbelowage2wordingconflicts18monthtransition'),(25,'fishing_mortality','1.68','year^-1',351,'Juveniles'),(26,'natural_mortality','0.8','year^-1',351,'Adults'),(25,'catch_juvenile_share','90','percent',352,'Largedemersalstock'),(25,'catch_stock','0.351','t km^-2 year^-1',352,'SAUPestimate'),
(27,'natural_mortality','1.54','year^-1',352,'Membermean'),(27,'exploitation_F_Z','0.55','dimensionless',352,'SourceZ3.08doesnotfollowexactlyfromthisfraction;preserve'),
(29,'biomass_commercial','1.47','t km^-2',353,'Commercialsardine,thryssa,anchovyetc'),(29,'commercial_noncommercial_ratio','4.9:1','ratio',353,'Authorestimation'),(29,'biomass_prose','1.77','t km^-2',353,'Finaltable1.772 retained'),(29,'natural_mortality','1.91','year^-1',353,'Paulyempirical'),(29,'exploitation_F_Z','0.55','dimensionless',353,'Decapterus maruadsi proxy'),(29,'catch_prose','2.344','t km^-2 year^-1',354,'Nationalanchovy/sardine'),
(31,'biomass_commercial','0.079','t km^-2',354,'Acousticscombrids'),(31,'natural_mortality','0.59','year^-1',354,'Paulyempirical'),(31,'exploitation_F_Z','0.55','dimensionless',354,'Proxy'),(30,'catch_juvenile_share','90','percent',354,'Largepelagicstock'),
(32,'demersal_trawl_share','0.1','percent',355,'Late1980ssurveys; authorbiomassestimate'),(32,'natural_mortality','0.84','year^-1',355,'Demersal'),(33,'natural_mortality','0.26','year^-1',355,'Pelagic'),(32,'exploitation_F_Z','0.62','dimensionless',355,'NSCSaveragerate')]:note(n,f,v,u,p,'Appendix6.1',why)

membership=[['group_seq','group_name','source_membership','type','exhaustive','pdf_page','printed_page','section','notes']]
definitions={1:('Phytoplankton','guild',337,''),2:('Benthic algae','guild',338,''),3:('Zooplankton; catches include Acetes spp (Mo shrimp)','guild',338,'Unassimilated-food convention cannot be assigned from this mixed group'),4:('Medusae of phylum Cnidaria','taxon/guild',339,''),5:('Polychaetes','guild',339,''),6:('Echinoderms','guild',339,''),7:('Benthic crustaceans excluding shrimps and crabs; Oratosquilla spp proxy','guild',339,'Representativeproxy not exhaustive membership'),8:('Non-cephalopod molluscs','guild',339,''),9:('Sessile/other invertebrates','guild',339,''),10:('Penaeid shrimps; Metapenaeopsis palmensis; M. barbata','representative',341,''),11:('Crabs','guild',341,''),12:('Dominant Loligo squid; Loligo edulis; L. chinensis','representative',341,'Source also spells Logilo'),13:('Family Nemipteridae; Nemipterus virgatus; N. bathybius; N. japonicus','family plus representative',342,''),14:('Family Priacanthidae','family',342,''),15:('Family Synodontidae; Saurida tumbil; S. undosquamis','family plus representative',343,'OCR secondgenus5.; sourceidentityfromfirstSaurida'),16:('Family Trichiuridae; dominant Trichiurus lepturus; juvenile below18months','family and stage',344,''),17:('Family Trichiuridae; adult18months and older','family and stage',344,''),18:('Family Stromateidae','family',346,'Biomass pooled withariommids,nomeis,formionids then allocated evenly'),19:('Family Lutjanidae','family',346,''),20:('Family Serranidae','family',347,''),21:('Family Sciaenidae; total length≤30cm; Agyrosomus spp; Pennahia spp; Pennahia (Agyrosomus) argentatus','family plus representative and size',348,'Preserve source Agyrosomus spelling; chapterusesmaximumTL, appendixsaysTL'),22:('Sciaenids maximumTL>30cm; sexuallyimmature below24months; Larimichthys crocea representative','family,size and stage',349,''),23:('Sciaenids maximumTL>30cm; olderthan24months','family,size and stage',349,''),24:('Demersal fish maximumTL≤30cm excluding separately modeled groups','guild and size',350,'FinaltableDemesral source spellingretained'),25:('Demersal fish maximumTL>30cm excluding separate groups; juvenile','guild,size and stage',351,'Juvenilebelowage2 wording vs18monthadulttransition unresolved'),26:('Demersal fish maximumTL>30cm; adultolderthan18months','guild,size and stage',351,''),27:('Benthopelagic fish maximumTL≤30cm; living/feedingbottom,mid-water or surface','guild and size',352,'FinaltablehasoneBenthopelagicfishgroup; extraAppendix6.1.22largesizegroup unmapped'),28:('Psenopsis anomala; melon seed; Centrolophidae','named species',347,'ChapterfamilyatPDF189'),29:('Pelagic fish maximumTL≤30cm; sardine, thryssa, anchovy etc','guild,size and representative',353,''),30:('Largepelagic maximumTL>30cm; juvenile; scombrids representative','guild,size and stage',354,'Sourceheadinglargepelagicbutdefinitionmistakenlydemersal; retainedconflict'),31:('Largepelagic maximumTL>30cm; adultolderthan18months','guild,size and stage',354,''),32:('Demersal sharks and rays; elasmobranchs','guild',355,''),33:('Pelagic sharks and rays; elasmobranchs','guild',355,''),34:('Seabirds','guild',356,'HongKongmodelparameterproxy'),35:('Pinnipeds','guild',356,'HongKongmodelparameterproxy'),36:('Other mammals','guild',356,'HongKongmodelparameterproxy'),37:('Marine turtles','guild',356,'HongKongmodelparameterproxy'),38:('Detritus','pool',356,'Biomassassumed100')}
for n,(definition,kind,p,why) in definitions.items():membership.append([n,groups[n-1]['name'],definition,kind,'not asserted exhaustive unless family/guild definition',p,p-15,'Appendix6.1; chapter6.2.1',why])
unmapped=[['source_heading','source_field','source_literal','units','pdf_page','printed_page','status','reason'],['6.1.22 Large benthopelagic fish','max_total_length','>30','cm',352,337,'source_available_unmapped','No separate exact group in final38-rowTable6.1(b); no inventedpooling'],['6.1.22 Large benthopelagic fish','natural_mortality','0.86','year^-1',352,337,'source_available_unmapped','Same'],['6.1.22 Large benthopelagic fish','exploitation_F_Z','0.55','dimensionless',353,338,'source_available_unmapped','Same'],['6.1.22 Large benthopelagic fish','total_mortality','1.91','year^-1',353,338,'source_available_unmapped','Same'],['6.1.22 Large benthopelagic fish','catch','0.0079','t km^-2 year^-1',353,338,'source_available_unmapped','Same'],['6.1.22 Large benthopelagic fish','EE_assumption','0.95','dimensionless',352,337,'source_available_unmapped','Same']]
context=[['field','source_value','pdf_page','printed_page','locator','status','note'],['model_period','2000s; chapter says early2000s',188,173,'6.2.1','published','Distinctfrompublication2007 andmostlylandings2000'],['spatial_extent','Continental shelf<200m;106°53′–119°48′E;17°10′–25°52′N;mainlyChineseEEZ',185,170,'6.1/Figure6.1','published','Noareaormetricoverlap inferred'],['diet_source','Xu et al1994 local surveys;FishBase Froese&Pauly2004',192,177,'6.2.1','published','Appendix6.2 explicitlyappliesbothperiods'],['catch_source','PRCgovernmentlandings plusSAUPdownwardadjustedestimates',192,177,'6.2.1','published','Notallfleetcatchisfromsamecollectionyear'],['fleet_species_allocation','HongKongrelativefleetcatchcomposition prorated;Pitcher etal1998',193,178,'6.2.1','published','Geographicproxy, notnationalfleetcompositionmeasurement'],['source_parameter_adjustments','Authoriterativelyadjusteddiet thenPB,QB,B untilEE<1',193,178,'6.2.1','published','Reasonfinaltablespreferredoverinitialappendixvariants'],['final_basic_roles','ParenthesesindicateparametersestimatedbyEcopath',190,175,'Table6.1caption','published','Estimatednumericoutputsretained;not treatedas sourceblank'],['mortality_outputs','F,M,M0 published peryear',205,190,'Table6.5','published','M0 notGS orfraction; output retainedcompaniononly'],['pedigree_definitions','See verbatimfootnote source_text PDF197',197,182,'Table6.3footnote','published','Categoryindex pairing retainedexact; definitions notcorrectedto externalEwE'],['published_total_catch_text','7.35',205,190,'6.3.3','published_conflict','DiffersfromTable6.2footer7.736; notusedtooverwritefleetvalues']]

stanzas=[['stock','juvenile_group','adult_group','number_stanzas','transition_age_months','K_per_year','recruitment_power','Wmaturity_Winf','pdf_page','printed_page','table_or_section','status','note'],
['Hairtails (trichiurids)',16,17,'2','18','0.41','1','0.0007',345,330,'TableA6.3; age PDF344 printed329','published','K and maturity from FishBase; recruitment power explicit default; adult biomass/QB native multistanza equations not reproduced'],
['Croakers (> 30 cm)',22,23,'2','24','0.36','1','0.15',345,330,'TableA6.3; age PDF349 printed334','published','K 26 stocks; maturity 59 stocks; recruitment power explicit default'],
['Demersal fish (> 30 cm)',25,26,'2','18','0.31','1','0.13',345,330,'TableA6.3; age PDF351 printed336','published','33 species; same section also describes juveniles below age2: unresolved18-vs24 month wording conflict'],
['Pelagic fish (> 30 cm)',30,31,'2','18','0.59','1','0.13',345,330,'TableA6.3; age PDF354 printed339','published','23 species; prose mistakenly calls this demersal fish: source wording retained as conflict']]
missing=[['group_seq','group_name','field','status','searched_source','consequence']]
for g in groups:
    for f in ['hab_area','unassim','detritus_import','tl','ba','ba_rate','other_mort','immigration','emigration','emigration_rate']:
        if g.get(f) is None:missing.append([g['n'],g['name'],f,'not_reported_as_import_field' if f=='other_mort' else 'not_reported','Original publication chapter6 PDF185-225; Appendix6.1-6.2 PDF337-363; full369page keyword sweep','Source blank; M0 rate is available separately in Mortality_outputs.csv, not an other_mort fraction. EwE defaults may differ; see REPORT' if f=='other_mort' else 'Source blank; no biological zero. EwE defaults may differ; see REPORT'])
    missing.append([g['n'],g['name'],'discards','not_separated_or_reported','Table6.2; Appendix6.1','Published catch is retained as Landings; total removals including unknown discards unavailable'])
    missing.append([g['n'],g['name'],'detritus_fate','not_reported','Chapter6; Appendix6.1-6.2; full369page detritus sweep','Single pool existence does not prove routing fraction; leave blank'])

system=[['field','estimate_2000s','standard_error','printed_units_or_definition','pdf_page','printed_page','locator','status'],
['Sum of all consumption','1994','32','t km^-2 as printed',207,192,'Table6.6','published_output'],['Sum of all exports','129132','916','t km^-2 as printed',207,192,'Table6.6','published_output'],['Sum of all respiratory flows','1242','20','t km^-2 as printed',207,192,'Table6.6','published_output'],['Sum of all flows into detritus','129751','906','t km^-2 as printed',207,192,'Table6.6','published_output'],['Total system throughput','262118','1800','t km^-2 as printed',207,192,'Table6.6','published_output'],['Sum of all production','130725','906','t km^-2 as printed',207,192,'Table6.6','published_output'],['Mean trophic level of catch','2.85','0.003','dimensionless',207,192,'Table6.6','published_output'],['Gross efficiency','0.000056','0.00000043','catch/net primary production; source5.6x10^-5,4.3x10^-7',207,192,'Table6.6','published_output'],['Total primary production/total respiration','104.99','2.17','ratio',207,192,'Table6.6','published_output'],['Total primary production/total biomass','259.2','1.61','ratio',207,192,'Table6.6','published_output'],['Connectance index','0.303','0.000077','source7.7x10^-5 s.e.',207,192,'Table6.6','published_output'],['System omnivory index','0.181','0.00091','source9.1x10^-4 s.e.',207,192,'Table6.6','published_output'],['Pedigree index','0.417','','dimensionless',207,192,'Table6.6','published_output'],['PPR for animal consumption','5090','130','t km^-2; exceptprimaryproducers/detritus',207,192,'Text belowTable6.6;Figure6.6a','published_output'],['PPR for fisheries','769','37','t km^-2',208,193,'Text startsPDF207 ends208;Figure6.6b','published_output'],['PPR per unit of catch','99','4.7','PP biomasspercatchbiomass',208,193,'Text;Figure6.6d','published_output'],['PPR fisheries/animal consumption','1:6.6','','ratio',208,193,'Text;Figure6.6c','published_output'],['Geometric mean trophic transfer efficiency','10.2','','percent',206,191,'6.3.3','published_output'],['Catch at trophic levels<3','71','','percent',206,191,'6.3.3','published_output']]
published.update({'Basic_source_cells.csv':{'description':'Final basic-table cells with exact locators and parenthesised output roles','rows':cells},'Diet_source_cells.csv':{'description':'All consumer/prey cell statuses plus unknown diet imports; no source normalization','rows':diet_cells},'Catch_source_cells.csv':{'description':'Six fleet landings and independent printed totals with bounding boxes','rows':catch_cells},'Published_catch_totals.csv':{'description':'Printed totals distinguished from importer decimal fleet sums','rows':catch_totals},'Source_stanzas.csv':{'description':'Native growth/recruitment/maturity/transition fields unsupported by flat calculator','rows':stanzas},'Published_parameter_notes.csv':{'description':'Author prose fields and competing parameter versions; final table retained','rows':prose},'Missing_fields.csv':{'description':'Unknown/not-reported fields and their default implications','rows':missing},'Source_membership.csv':{'description':'Source guild/family/representative membership; noexternaltaxonomy', 'rows':membership},'Unmapped_source_groups.csv':{'description':'SourceAppendixgroupnotpresentasseparatefinalmodelrow; cannotinventcrosswalk','rows':unmapped},'Source_context.csv':{'description':'Area,period,sourceconventionsandconflicts','rows':context},'Published_system_outputs.csv':{'description':'SourcewholeecosystemoutputsandPPRbenchmark;notrecalculated', 'rows':system}})
model={'metadata':{'LME':'28 South China Sea','model_number':'NSCS_2000s_blind','model_name':'Northern South China Sea','model_year':'2000s','biomass_basis':'whole_model_area','export_basis':'reported_landings','source':'Cheung, Wai Lung. 2007. Vulnerability of marine fishes to fishing: from global overview to the northern South China Sea. PhD thesis, University of British Columbia. Chapter6/Table6.1(b)/Appendices6.1-6.2','identifier_status':'NSCS_2000s_blind is local isolated trial ID; no source EcoBase accession supplied'},'groups':groups,'consumers':list(range(3,38)),'fleets':fleets,'landings':landings,'discards':{},'detritus_groups':['Detritus'],'detritus_fate':{},'diet':diet,'diet_rows':38,'landings_rows':38,'discards_rows':38,'companions':published,'extraction_notes':{'no_repair':True,'no_normalization':True,'no_live_integration':True,'basis_evidence':'Equation6.1 defines B as total biomass PDF187 printed172; Appendix6.1 reports NSCS biomass per km2; habitat fractions not reported','source_blanks':'Sparse matrix blank prey cells left blank; source sums and interpreted zero convention separate from unknown import row'}}
(OUT/'extraction.json').write_text(json.dumps(model,ensure_ascii=False,indent=2),encoding='utf-8')
summary={'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'groups':len(groups),'consumers':len(diet),'positive_diet_cells':sum(len(x)-1 for x in diet.values()),'catch_group_rows':len(landings),'diet_prey_only_sums':{n:str(sum(Decimal(v) for k,v in x.items() if k!='import')) for n,x in diet.items()},'printed_diet_sums':printed_sums,'companions':list(published),'source_names_visually_verified':True}
(E/'extraction_checks.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
