"""Read-only regional inputs; final-paper candidate membership and reference arithmetic."""
from __future__ import annotations
import collections, csv, hashlib, json, math, re, sys
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
MODEL = OUT.parent
REGION = MODEL.parents[1]
PRIOR = REGION / 'validation_reports/27_118_Northwest_Africa_(1987)'
PDF = REGION / 'papers/FCRR_2009_17-2.pdf.pdf'
sys.path.insert(0, str(ROOT / 'tools'))
from workbooks import read_book, records, overview, finite

def write(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')

def norm(s):
    return re.sub(r'\s+', ' ', s).strip().casefold()

pdf = PdfReader(PDF)
parts=[]
for page,first,end in [(18,'1. Minke whales',None),(19,'16. Rays',None),(20,'22. Crustaceans','Groups 1 - 10.')]:
    text=pdf.pages[page-1].extract_text()
    text=text[text.index(first):]
    if end: text=text[:text.index(end)]
    parts.append(text)
body=' '.join(parts)
segments=re.split(r'(?<![\w.])(\d{1,2})\. ',body)
headers=['Minke whales','Fin whales','Humpback whales','Bryde\u2019s whales','Sei whales','Blue whales','Sperm whales','Killer whales','Beaked whales','Small cetaceans','Seabirds','Large pelagics','Mesopelagics predators','Bathydemersal predators','Sharks','Rays','Costal tunas','Coastal demersals','Clupeids','Other coastal pelagics','Cephalopods','Crustaceans','Benthos','Benthic producers','Zooplankton','Phytoplankton','Detritus']
table3={int(segments[j]):re.sub(r'\s+',' ',segments[j+1][len(headers[int(segments[j])-1]):]).strip() for j in range(1,len(segments),2)}
assert len(table3)==27
table17=pdf.pages[40].extract_text()
table17=table17[table17.index('1. Minke whales'):]
rows=re.findall(r'(\d+)\.\s+([^\d]+?)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)',table17)
groups={int(r[0]):{'seq':int(r[0]),'group_name':r[1].strip(),'biomass':float(r[3]),'source_table':17,'pdf_page':41} for r in rows}
assert len(groups)==27
native=json.loads((MODEL/'evidence/identity/ecobase118_official_native.json').read_text(encoding='utf-8'))
native_catch_check=json.loads((MODEL/'evidence/identity/native_fleet_catch_comparison.json').read_text(encoding='utf-8'))
native_by_name={g['group_name']:g for g in native['group_descr']['group']}
assert all(r['within_1e-7'] for r in native_catch_check['rows'])
for g in groups.values():
    ng=native_by_name[g['group_name']]
    g['native_seq']=int(ng['group_seq'])
    g['native_export_catch']=float(ng['export'])
    g['native_catch_literal']=ng['export']
write('native_to_table17_group_crosswalk.json',list(groups.values()))
source_to_final={i:i for i in range(1,28)}
source_to_final.update({6:8,7:6,8:7})
source_rows=json.loads((PRIOR/'source_member_taxonomy_review.json').read_text(encoding='utf-8'))
authority_by_literal={norm(r['source_member']):r for r in source_rows}
source_members=[]
source_inventory=[]
for src,description in table3.items():
    gid=source_to_final[src]
    members=[s.strip() for s in description.split(',') if s.strip()]
    source_inventory.append({'table3_seq':src,'table3_group_name':headers[src-1],'seq':gid,'group_name':groups[gid]['group_name'],'taxon_descr':'; '.join(members) if members else 'not documented — Table 3 leaves the membership cell blank','pdf_page':18 if src<=15 else 19 if src<=21 else 20,'table':3,'scope':'Listed included taxa; bold denotes key species, not an exhaustive only-key-member inventory. Source spellings retained.','members':members})
    for m in members:
        a=authority_by_literal.get(norm(m),{}).get('authority')
        if m=='Balaenoptera musculus': a=authority_by_literal.get('b. musculus',{}).get('authority')
        if m=='Tursiops truncatus': a=authority_by_literal.get('tursiops truncates',{}).get('authority')
        source_members.append({'source_member':m,'table3_seq':src,'seq':gid,'group_name':groups[gid]['group_name'],'pdf_page':18 if src<=15 else 19 if src<=21 else 20,'authority':a,'authority_evidence':'retained source_member_taxonomy_review.json; WoRMS retrieved 2026-09-30' if a else None,'source_label_conflict':bool(authority_by_literal.get(norm(m),{}).get('source_label_conflict',False))})
source_inventory.sort(key=lambda r:r['seq'])
write('source_membership.json',source_inventory)
write('source_member_taxonomy_review.json',source_members)
write('table3_table17_crosswalk.json',[{k:v for k,v in r.items() if k in ['table3_seq','table3_group_name','seq','group_name','pdf_page']} for r in source_inventory])
with (OUT/'taxonomy.csv').open('w',encoding='utf-8-sig',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=['seq','group_name','taxon_descr']);w.writeheader();w.writerows({k:r[k] for k in w.fieldnames} for r in source_inventory)

book=read_book(REGION/'LME_027.xlsx')
settings=overview(book);year=int(settings['taxon_detail_year']);basis=settings['catch_basis']
catches=records(book,'Catch','Catch');catches=[r for r in catches if r['catch_basis']==basis]
classic=records(book,'Classic PPR','Taxa');classic_by={r['taxon']:r for r in classic}
prior=json.loads((PRIOR/'taxon_audit.json').read_text(encoding='utf-8'));prior_by={r['taxon']:r for r in prior}
assert len(catches)==len({r['taxon'] for r in catches})==512
assert {r['taxon'] for r in catches}==set(prior_by)
catch_snapshot=[{k:r.get(k) for k in ['taxon','common_name','functional_group','commercial_group','unidentified','catch_basis',year]} for r in catches]
(MODEL/'calculations/classic_inputs_2019.json').write_text(json.dumps({'year':year,'basis':basis,'workbook_sha256':hashlib.sha256((REGION/'LME_027.xlsx').read_bytes()).hexdigest(),'overview':settings,'catch':catch_snapshot,'classic_taxa':classic},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def direct_matches(taxon,authority):
    matches=[]
    target=authority.get('valid_AphiaID') or authority.get('AphiaID')
    for m in source_members:
        a=m['authority'] or {}
        if norm(taxon)==norm(m['source_member']): matches.append((m,'exact'))
        elif target and target==(a.get('valid_AphiaID') or a.get('AphiaID')): matches.append((m,'authority identity'))
    return matches

def genus_matches(taxon,authority):
    genus=authority.get('valid_name',taxon) if authority.get('rank')=='Genus' else None
    if not genus: return []
    return [m for m in source_members if ((m['authority'] or {}).get('genus')==genus or re.fullmatch(re.escape(genus)+r' sp\.?',m['source_member'])) and m['seq']>=12]

def modern_reason(text):
    return text.replace('precursor','final Table 3').replace('Precursor','Final Table 3').replace('source-version transfer','transfer from the listed representative composition').replace('Pool/species and source-version transfer is assumed.','Inclusion of unlisted related taxa remains assumed.').replace('source version/composition remains transferred.','unlisted species composition remains assumed.').replace('source-version','composition')

# Explicit receiving-candidate corrections following genus/order inspection of Table 3.
# Others retain the previously reviewed taxonomic/ecological set unless direct final evidence resolves it.
overrides={
 'Anguilliformes':([14,18],'M9','Medium','The catch order includes final Table 3 Muraena and Synaphobranchus in Bathydeersal predators and Conger/Congridae in Coastal demersal. Both named eel-bearing pools are required; unobserved order composition and their pooled fish catches are assumed.'),
 'Ophidiidae':([14],'M9','Medium','Final Table 3 explicitly lists Spectrunculus grandis in Bathydeersal predators. Brotula barbata in Coastal demersal belongs to Brotulidae under the retained authority, not Ophidiidae; the verified modern family extension is assumed.'),
 'Inermiidae':([18],'M4','Medium','Retained WoRMS identifies the historical Inermiidae label with Haemulinae, which the current WoRMS Haemulidae record places within Haemulidae. Final Table 3 names Haemulidae in Coastal demersal. This modern family bridge supports an unlisted taxonomic extension; the source-era family concept and bonnetmouth pelagic ecology remain transfer assumptions. Source: https://www.marinespecies.org/aphia.php?id=125538&p=taxdetails (retrieved 2026-10-03).'),
 'Miscellaneous marine crustaceans':([22],'M9','Medium','The provider explicitly names this residual category Marine crabs, shrimps, lobsters nei. Final Table 3 Crustaceans includes Brachyura, shrimp families and lobster genera, supporting the same decapod union. Copepod Zooplankton is excluded by that reporting scope. Extension to the unlisted residual constituents is assumed, but unknown proportions within one receiving group add no allocation uncertainty.'),
}
for flatfish in ['Citharus linguatula','Psettodes belcheri','Psettodes bennettii','Psettodidae']:
    overrides[flatfish]=([18],'M4','Medium','Retained authoritative taxonomy places this catch label within Pleuronectiformes; the provider reports flatfishes. Final Table 3 explicitly includes Pleuronectiformes and several flatfish families in Coastal demersal, with no competing flatfish source pool. Inclusion of this unlisted family/species is a supported extension rather than only a weak habitat analogue.')
weak_reasons={
 'Alepisaurus ferox':'The provider identifies a large bathypelagic fish; source Mesopelagic predators includes deep-pelagic Aphanopus and Myctophum, making it the closest represented feeding-habitat analogue. Alepisauridae is absent from the source list and the pool does not establish this large lancetfish’s depth or diet composition; Large pelagics is the competing, less specifically deep-water pool.',
 'Anguilla anguilla':'The diadromous European eel is unlisted and Anguillidae is absent. Coastal demersal contains Conger/Congridae and other marine bottom fishes, a meaningful eel/bottom-habitat analogue, but its marine mixed-guild ecology does not represent the eel’s freshwater-to-sea life cycle. Bathydeersal predators contains other deep-water eels and is a less appropriate proxy for the provider’s demersal catch category.',
 'Branchiostegus':'The reported tilefish genus belongs to unlisted Malacanthidae. The provider’s medium-demersal category connects it to Coastal demersal, whose listed sea breams and other coastal bottom fishes provide a habitat analogue; source membership, burrow-associated ecology and depth composition are not established for this catch genus. Bathydeersal predators remains a possible deeper-water alternative.',
 'Echelus myrus':'This unlisted ophichthid eel is reported as a large demersal fish. Coastal demersal contains Conger/Congridae, giving an eel and bottom-habitat analogue, but the source contains no Ophichthidae and does not establish equivalent ecology. The other eel-bearing pool, Bathydeersal predators, is retained as a reviewed alternative but is less consistent with the provider’s non-bathyal category.',
 'Epigonus telescopus':'The provider reports a medium bathydemersal fish. Source Bathydeersal predators includes Beryx, hake and other deep-bottom fishes, but no Epigonidae; transferring this mixed deep-bottom pool to black cardinalfish is an ecological analogue with unverified species composition. Coastal demersal provides a weaker depth match.',
 'Kyphosus sectatrix':'The provider reports a medium reef-associated fish. Coastal demersal includes Sarpa salpa, Acanthuridae and other reef/coastal fishes, a useful ecological analogue, but no Kyphosidae is listed and the mixed source pool does not establish sea-chub membership or equivalent feeding composition. Pelagic pools have a weaker documented reef connection.',
 'Megalops atlanticus':'The provider places tarpon among large pelagic fishes, linking it to source Large pelagics (Coryphaena and mobile tunas/billfishes). Megalopidae is unlisted; the tarpon’s coastal/estuarine ecology differs from that offshore-oriented mixed pool. Other coastal pelagics, containing Elops lacerta, is a meaningful alternative; current placement follows the provider’s size/habitat proxy with Very low confidence.',
 'Peristediidae':'The provider reports medium bathydemersal armored gurnards. Bathydeersal predators provides a deep-bottom analogue but lacks Peristediidae. Coastal demersal contains true gurnards (Triglidae) and is a competing taxonomic/habitat analogue; the provider’s bathydemersal category motivates the present weak deeper-pool assignment.',
 'Polymixia nobilis':'The provider reports a medium bathydemersal fish. Bathydeersal predators contains Beryx and other deep-bottom fishes, but no Polymixiidae, so a stout-beardfish catch uses a mixed habitat analogue without source membership confirmation. Coastal demersal is a less specific depth match.',
 'Sarotherodon melanotheron':'The blackchin tilapia is an unlisted cichlid associated with brackish/estuarine waters, while the source lacks a freshwater/estuarine cichlid compartment. Coastal demersal contains mullets and other coastal fishes and is the closest represented estuarine/coastal analogue; its marine mixed-guild coefficient is a substantial ecological transfer.',
}
for taxon in ['Heteropriacanthus cruentatus','Priacanthidae','Priacanthus','Priacanthus arenatus']:
    weak_reasons[taxon]='The provider identifies reef-associated bigeyes/catalufas in Priacanthidae. Coastal demersal lists Anthias, groupers and other reef/coastal fishes, giving a specific reef-fish analogue, but Priacanthidae is absent and the source does not establish an equivalent bigeye feeding or depth composition. Offshore pelagic and bathydemersal pools have weaker evidence for this provider category.'
for taxon in ['Uranoscopus','Uranoscopus scaber']:
    weak_reasons[taxon]='The provider reports demersal stargazers in unlisted Uranoscopidae. Coastal demersal contains benthic predatory fishes and flatfishes, giving a bottom-habitat analogue; no stargazer member or guild criterion verifies inclusion, and their benthic ambush ecology is not isolated in this mixed pool. Bathydeersal predators is a weaker match to the provider’s non-bathyal category.'
for taxon,reason in weak_reasons.items():
    prior_ids=[g['seq'] for g in prior_by[taxon]['groups']]
    overrides[taxon]=(prior_ids,'M11','Very low',reason)
confidence_order=['High','Medium','Low','Very low','Unresolved']
audit=[];allocation=[]
for catch in sorted(catches,key=lambda r:r['taxon']):
    taxon=catch['taxon'];old=prior_by[taxon];authority=old.get('authority_record') or {};ids=[g['seq'] for g in old['groups']]
    rule=old['membership_rule'];mc=old['membership_confidence'];mr=modern_reason(old['membership_reason'])
    matched=direct_matches(taxon,authority)
    gm=genus_matches(taxon,authority)
    # Printed or authority-resolved exact members take priority over unrelated family representatives.
    if matched and rule not in ['M10','M11','M6']:
        matched_ids=sorted({m['seq'] for m,k in matched})
        rank=authority.get('rank')
        if rank in ['Species','Subspecies'] or len(ids)==1:
            ids=matched_ids
            if len(ids)==1:
                rule='M1' if any(k=='exact' for m,k in matched) else 'M2';mc='High'
                listed='; '.join(dict.fromkeys(m['source_member'] for m,k in matched))
                mr=f'Final Table 3 explicitly includes {listed} in {groups[ids[0]]["group_name"]}.'
                if rule=='M2':mr+=f' Retained WoRMS accepted-name/AphiaID evidence identifies this with catch label {taxon}; source spelling is preserved.'
                if taxon=='Scaridae':mr+=' The fisheries family usage is WoRMS 125557 (accepted Scarinae), not the homonymous genus misspelling 398089.'
            else:
                rule='M9';mc='Medium';mr+=' Source membership overlaps more than one group; the combined receiving set remains an explicit interpretation.'
        else:
            rule='M9';mc='Medium';mr=modern_reason(old['membership_reason'])+' The final Table 3 broad label is reconciled with actual listed members in all retained pools, rather than treated as exclusive.'
    elif gm and rule in ['M9','M4']:
        ids=sorted({m['seq'] for m in gm})
        generic=any(re.fullmatch(re.escape(authority.get('valid_name',taxon))+r' sp\.?',m['source_member']) for m in gm)
        if generic and len(ids)==1:rule='M1';mc='High'
        else:rule='M4' if len(ids)==1 else 'M9';mc='Medium'
        listed='; '.join(dict.fromkeys(m['source_member'] for m in gm))
        mr=f'Final Table 3 genus evidence ({listed}) establishes the receiving '+('pool.' if len(ids)==1 else 'pool union.')
        if not generic:mr+=' Extension from those named representatives to the reported genus remains assumed.'
        if len(ids)>1:mr+=' Actual genus members span these groups; unknown composition requires a proxy split.'
    elif rule=='M12':
        # A precursor match that fails the final literal/authority check must never be blanket upgraded.
        rule='M4';mc='Medium';mr='The retained precursor taxonomic connection remains a representative-based extension; no exact final Table 3 literal or authority identity was verified for this catch label.'
    if taxon in overrides:ids,rule,mc,mr=overrides[taxon]
    if len(ids)==1:
        weights=[1.0];wr='W1';wc='High';ar='One reviewed group; no numerical split.';attempts=[]
    else:
        vals=[groups[g]['native_export_catch'] for g in ids];total=math.fsum(vals)
        assert all(finite(v) and v>=0 for v in vals) and total>0
        weights=[v/total for v in vals];wr='W4';wc='Medium'
        ar='Verified native EcoBase118 group landings proportions are assumed to represent this taxon’s mixture. The fixed 1987 model composition is transferred to 2019 landings; pooled species and catchability differ from the unobserved target mixture.'
        if 13 in ids or 23 in ids:ar+=' Native catches differ from printed 1987 fleet totals: local mesopelagic catch is about half the printed value; foreign Benthos catch is absent natively but 426 t in print. The proxy deliberately uses the coherent native model version.'
        if 25 in ids:ar+=' Zooplankton retains its explicit native zero model catch; this is not evidence of observed absence.'
        bvals=[groups[g]['biomass'] for g in ids];btotal=math.fsum(bvals)
        attempts=[{'field':'printed final-model catch','accepted':False,'reason':'Table 17 has no catch column; prose and Tables 1–2 do not identify a complete balanced-model vector. This print-only failure is resolved by verified official native fleet evidence.'},{'field':'official native group/export','accepted':True,'raw_values':vals,'total':total,'unit':'t wet weight/km2/year','source':'../evidence/identity/ecobase118_official_native.json','semantic_verification':'../evidence/identity/native_fleet_catch_comparison.json','period':1987,'basis':'total landings; two fleets; no discard quantity supplied'},{'field':'Table 17 biomass','accepted':False,'reason':'Complete alternative retained but unnecessary because verified native model landings take precedence.','raw_values':bvals,'total':btotal,'unit':'t/km2','alternative_weights':[v/btotal for v in bvals]}]
    gs=[{'seq':g,'group_name':groups[g]['group_name'],'weight':w} for g,w in zip(ids,weights)]
    coeff=classic_by.get(taxon,{})
    c=catch.get(year);s=coeff.get('sppr');tl=coeff.get('tl');ppr=0.0 if c==0 else c*s/9 if finite(c) and finite(s) else None
    overall=max([mc,wc],key=confidence_order.index)
    source_evidence=[{'source_member':m['source_member'],'seq':m['seq'],'pdf_page':m['pdf_page'],'match':k,'authority_url':(m['authority'] or {}).get('url')} for m,k in matched]
    if gm:source_evidence.extend({'source_member':m['source_member'],'seq':m['seq'],'pdf_page':m['pdf_page'],'match':'genus representative','authority_url':(m['authority'] or {}).get('url')} for m in gm)
    family=authority.get('family')
    family_evidence=[{'source_member':m['source_member'],'seq':m['seq'],'pdf_page':m['pdf_page'],'authority_url':(m['authority'] or {}).get('url')} for m in source_members if family and (m['authority'] or {}).get('family')==family and m['seq']>=12 and not m['source_label_conflict']]
    candidate_decisions=[]
    for inv in source_inventory:
        gid=inv['seq'];included=gid in ids
        candidate_decisions.append({'seq':gid,'group_name':inv['group_name'],'decision':'included' if included else 'excluded','reason':mr if included else 'Outside this independently reviewed taxon/group set. Explicit named membership takes precedence; competing source guilds assessed using exact identities, genus/family representatives, reporting scope and the stated analogue limitations.','source_definition':inv['taxon_descr'],'source_table3_seq':inv['table3_seq'],'source_pdf_page':inv['pdf_page']})
    rec={'taxon':taxon,'year':year,'catch_basis':basis,'catch_tonnes':c,'tl':tl,'classic_coefficient_wet':s,'simple_chain_ppr_tC':ppr,'groups':gs,'mapping_display':'; '.join(f'{g["group_name"]} ({100*g["weight"]:.6f}%)' for g in gs),'membership_rule':rule,'membership_confidence':mc,'membership_reason':mr,'allocation_rule':wr,'allocation_confidence':wc,'allocation_reason':ar,'overall_confidence':overall,'assumed_membership':mc!='High','assumed_allocation':wr!='W1','reason':mr+' '+ar,'sources':['final_table3','final_table17','native_catches','authority','reporting','classic','prior_review'],'authority_record':authority,'authority_url':old.get('authority_url'),'direct_final_source_evidence':source_evidence,'family_source_evidence':family_evidence,'provider_metadata':{k:catch.get(k) for k in ['common_name','functional_group','commercial_group','unidentified']},'candidate_decisions':candidate_decisions,'previous_mapping':{'model_id':'27_118_Northwest_Africa_(1987)','groups':old['groups'],'membership_rule':old['membership_rule'],'membership_confidence':old['membership_confidence'],'allocation_rule':old['allocation_rule'],'allocation_confidence':old['allocation_confidence'],'overall_confidence':old['overall_confidence']},'changes':{'group_set_changed':ids!=[g['seq'] for g in old['groups']],'weights_changed':gs!=old['groups'],'membership_confidence_changed':mc!=old['membership_confidence'],'allocation_confidence_changed':wc!=old['allocation_confidence']},'missing_inputs':{'catch':not finite(c),'tl':not finite(tl),'classic_coefficient':not finite(s),'annual_ppr':ppr is None},'input_locations':{'catch':'LME_027.xlsx / Catch / Catch / landings / 2019','tl_coefficient':'LME_027.xlsx / Classic PPR / Taxa / tl, sppr'},'adoption':'candidate only; not adopted; selected EcoBase118 and shared workbooks unchanged'}
    audit.append(rec)
    allocation.append({'taxon':taxon,'candidates':[{'seq':g,'group_name':groups[g]['group_name'],'native_seq':groups[g]['native_seq'],'source_catch_raw':groups[g]['native_export_catch'],'source_catch_literal':groups[g]['native_catch_literal'],'source_catch_status':'explicit native group/export; reconciles with fleet total-landings records; zero denotes no catch in model','source_biomass':groups[g]['biomass'],'weight':w} for g,w in zip(ids,weights)],'attempts':attempts,'allocation_rule':wr,'allocation_confidence':wc,'reason':ar,'units':'native model catch t wet weight/km2/year; final Table17 biomass t/km2','source_period':'1987 native model; late-1980s printed baseline with heterogeneous input periods','source_location':'Verified official EcoBase118 native group/export and fleet catch_descr; Table17 name crosswalk; final Table17 PDF41 biomass alternative','applied_years':[year],'applied_bases':[basis]})

write('taxon_audit.json',audit);write('allocation_evidence.json',allocation)
totalcatch=math.fsum(r['catch_tonnes'] for r in audit if finite(r['catch_tonnes']));totalppr=math.fsum(r['simple_chain_ppr_tC'] for r in audit if finite(r['simple_chain_ppr_tC']))
summary={'year':year,'catch_basis':basis,'taxa':len(audit),'source_ecological_groups':27,'synthetic_import_groups':0,'total_catch_tonnes':totalcatch,'total_simple_chain_ppr_tC':totalppr,'missing_classic_coefficients':[r['taxon'] for r in audit if r['missing_inputs']['classic_coefficient']],'positive_catch_unknown_ppr':[r['taxon'] for r in audit if r['catch_tonnes']>0 and r['simple_chain_ppr_tC'] is None],'unresolved_taxa':[r['taxon'] for r in audit if r['overall_confidence']=='Unresolved'],'confidence_summary':[],'membership_summary':[],'allocation_summary':[],'adoption':'candidate only; not adopted'}
for label in confidence_order:
    rs=[r for r in audit if r['overall_confidence']==label];c=math.fsum(r['catch_tonnes'] for r in rs);p=math.fsum(r['simple_chain_ppr_tC'] or 0 for r in rs)
    summary['confidence_summary'].append({'label':label,'taxa':len(rs),'catch_tonnes':c,'ppr_tC':p,'catch_percentage':100*c/totalcatch,'ppr_percentage':100*p/totalppr})
rule_names={'M1':'Explicit membership in the final source group list','M2':'Verified taxonomic identity or synonym of a final source member','M4':'Supported extension from final source representatives','M9':'Assumed eligible group set from final source members and reporting scope','M6':'Conflicting final source labels with a supported but uncertain assignment','M10':'Broad reporting category approximated across compatible source pools','M11':'Closest represented taxonomic or ecological analogue','W1':'One receiving group; no allocation split required','W4':'Verified native source-model landings proportions transferred to reference-year catch'}
for component in ['membership','allocation']:
    for rule,conf in sorted({(r[component+'_rule'],r[component+'_confidence']) for r in audit}):
        rs=[r for r in audit if r[component+'_rule']==rule and r[component+'_confidence']==conf];p=math.fsum(r['simple_chain_ppr_tC'] or 0 for r in rs)
        summary[component+'_summary'].append({'rule':rule,'plain_language_rule':rule_names[rule],'confidence':conf,'taxa':len(rs),'ppr_tC':p,'ppr_percentage':100*p/totalppr})
    summary[component+'_summary'].sort(key=lambda r:-r['ppr_percentage'])
write('coverage_summary.json',summary)
verylow=collections.defaultdict(list)
for r in audit:
    if r['overall_confidence']=='Very low':verylow[r['reason']].append(r['taxon'])
write('very_low_decisions.json',[{'taxa':taxa,'affected_taxa':'; '.join(taxa),'reason':reason} for reason,taxa in verylow.items()])
ordered=sorted(audit,key=lambda r:(r['simple_chain_ppr_tC'] is None,-(r['simple_chain_ppr_tC'] or 0),r['taxon']))
write('appendix_rows.json',[{'Taxon name':r['taxon'],'TL':r['tl'],'Catch (t)':r['catch_tonnes'],'Simple-chain PPR (t C)':r['simple_chain_ppr_tC'],'Mapped group names and weights':r['mapping_display'],'Confidence level':r['overall_confidence'],'Reason':r['reason']+' Sources: final_table3, native_catches, authority, reporting, classic.'} for r in ordered])
write('mapping_changes.json',[{'taxon':r['taxon'],'previous':r['previous_mapping'],'candidate_groups':r['groups'],'membership_rule':r['membership_rule'],'membership_confidence':r['membership_confidence'],'allocation_rule':r['allocation_rule'],'allocation_confidence':r['allocation_confidence'],'overall_confidence':r['overall_confidence'],'changes':r['changes'],'reason':r['reason']} for r in audit])
write('matching.json',[{'taxon':r['taxon'],'group_seq':g['seq'],'group_name':g['group_name'],'weight':g['weight'],'confidence':r['overall_confidence'],'membership_confidence':r['membership_confidence'],'allocation_confidence':r['allocation_confidence'],'reason':r['reason']} for r in audit for g in r['groups']])
verify={'taxon_count':len(audit),'unique_taxa':len({r['taxon'] for r in audit}),'candidate_group_count':len(groups),'source_table3_count':len(source_inventory),'source_members':len(source_members),'catch_total_tonnes':totalcatch,'simple_chain_ppr_tC':totalppr,'coefficient_missing':sum(r['missing_inputs']['classic_coefficient'] for r in audit),'missing_coefficient_positive_catch':len(summary['positive_catch_unknown_ppr']),'weights_sum_max_error':max(abs(math.fsum(g['weight'] for g in r['groups'])-1) for r in audit),'confidence_taxa_sum':sum(x['taxa'] for x in summary['confidence_summary']),'confidence_catch_percentage_sum':math.fsum(x['catch_percentage'] for x in summary['confidence_summary']),'confidence_ppr_percentage_sum':math.fsum(x['ppr_percentage'] for x in summary['confidence_summary']),'membership_rule_percentage_sum':math.fsum(x['ppr_percentage'] for x in summary['membership_summary']),'allocation_rule_percentage_sum':math.fsum(x['ppr_percentage'] for x in summary['allocation_summary']),'group_set_changes':[r['taxon'] for r in audit if r['changes']['group_set_changed']],'all_prior_reference_arithmetic_reconciles':all(math.isclose(r['catch_tonnes'],prior_by[r['taxon']]['catch_tonnes'],abs_tol=1e-8) and math.isclose(r['simple_chain_ppr_tC'] or 0,prior_by[r['taxon']]['simple_chain_ppr_tC'] or 0,abs_tol=1e-8) for r in audit),'method':'saved classic wet coefficient times recorded 2019 landings divided by 9, once; no Ecopath mapping or SPPR used','transfer_efficiency':settings['transfer_efficiency'],'workbook_modified':False,'adopted':False}
(MODEL/'calculations/classic_verification.json').write_text(json.dumps(verify,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(MODEL/'calculations/classic_taxon_2019.json').write_text(json.dumps([{k:r[k] for k in ['taxon','year','catch_basis','catch_tonnes','tl','classic_coefficient_wet','simple_chain_ppr_tC','missing_inputs','input_locations']} for r in ordered],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(verify,ensure_ascii=False,indent=2))
print(json.dumps(summary['confidence_summary'],ensure_ascii=False,indent=2))
write('appendix_sources.json',[
 {'id':'final_table3','title':'Morissette et al. (2009), final Northwest Africa group membership, Table 3','supports':'PDF18–20, printed14–16: literal source members; bold marks key taxa. Table3 whale6/7/8 map to Table17 group8/6/7. Typos and the Centrolophidae-in-Sharks anomaly remain source facts.','target':'../../../papers/FCRR_2009_17-2.pdf.pdf#page=18','date':'2026-10-03'},
 {'id':'final_table17','title':'Morissette et al. (2009), balanced Northwest Africa model, Table 17','supports':'PDF41, printed37: exact final group names, order and biomass. Complete biomass alternative retained in allocation evidence, not used when verified native model catch is available.','target':'../../../papers/FCRR_2009_17-2.pdf.pdf#page=41','date':'2026-10-03'},
 {'id':'native_catches','title':'Official EcoBase118 native group exports reconciled to fleet total landings','supports':'Complete native model catch vector, exact name crosswalk and all raw values retained. Fixed1987 mixture is a Medium assumption; native local-mesopelagic and foreign-Benthos catches disagree with printed1987 totals, so these are native-model rather than exact printed-table weights.','target':'../evidence/identity/native_fleet_catch_comparison.json','date':'2026-10-03'},
 {'id':'native_original','title':'Official EcoBase118 original native XML','supports':'Full source model and native catch literals; group export quantities reproduce the selected canonical values.','target':'../evidence/identity/ecobase118_official_input.xml','date':'2026-10-03'},
 {'id':'authority','title':'Retained WoRMS scientific-name, synonym and taxonomic-rank evidence','supports':'Primary records retrieved2026-09-30; each source member and catch label is joined by accepted identity, rank, genus and family. These records support taxonomy, not an exhaustive ecological boundary.','target':'../../../validation_reports/27_118_Northwest_Africa_(1987)/taxonomy_api_evidence.json','date':'2026-09-30'},
 {'id':'inermiidae','title':'WoRMS Haemulidae classification and Haemulinae','supports':'Historical Inermiidae resolves in retained authority to Haemulinae; live Haemulidae entry confirms its parent family. Candidate assignment is a Medium historical-family extension to final source18.','target':'https://www.marinespecies.org/aphia.php?id=125538&p=taxdetails','date':'2026-10-03'},
 {'id':'reporting','title':'Sea Around Us residual-fish reporting and FAO ISSCAAP39 evidence','supports':'Bony-fish reporting scope for marine/finfish/groundfish/pelagic residual labels; mixed source guild members remain eligible while dedicated cartilage pools are excluded.','target':'../../../validation_reports/27_118_Northwest_Africa_(1987)/reporting_scope_sources/source_manifest.json','date':'2026-09-30'},
 {'id':'classic','title':'Regional Catch and Classic PPR / Taxa inputs','supports':'All512 landings labels and saved taxon TL/coefficients; independent2019 PPR = landings × saved wet coefficient /9. Transfer efficiency0.1.100 missing coefficients have zero2019 landings and therefore zero annual PPR.','target':'../../../LME_027.xlsx','date':'2026-10-03'},
 {'id':'prior_review','title':'Prior all-taxon review retained as evidence and comparison','supports':'Provider scope, positive analogues, taxonomic records and old decisions, independently reassessed against final Table3. Prior allocation quantities are not assumed solely because previously used.','target':'../../../validation_reports/27_118_Northwest_Africa_(1987)/taxon_audit.json','date':'2026-09-30'},
 {'id':'candidate_decisions','title':'Every candidate mapping and source-group inclusion/exclusion decision','supports':'512 taxon records with separate membership/weight evidence and confidence, old/new decisions, 27 receiving-group decisions per taxon and candidate-only status.','target':'taxon_audit.json','date':'2026-10-03'},
 {'id':'candidate_weights','title':'Candidate allocation calculations and alternative biomass weights','supports':'All group/raw native catch values and normalized weights; rejected print-only catch attempt, complete Table17 biomass alternative, source-period and reference-year assumptions.','target':'allocation_evidence.json','date':'2026-10-03'},
 {'id':'groundfish','title':'FAO Mora moro species sheet1183, PDF9','supports':'Demersal-slope habitat supports inclusion of source Mesopelagic predators in groundfish candidates, because that mixed guild explicitly contains Mora moro.','target':'../../../validation_reports/27_118_Northwest_Africa_(1987)/reporting_scope_sources/FAO_Mora_moro_demersal.pdf#page=9','date':'2026-09-30'}
])
