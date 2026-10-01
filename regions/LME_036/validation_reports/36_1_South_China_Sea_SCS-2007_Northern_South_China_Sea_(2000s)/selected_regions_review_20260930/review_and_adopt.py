"""Explicit regional proposal decisions and guarded dependent adoption."""
import copy,json,math,pathlib,sys,hashlib,shutil,datetime
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[4]
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book,records,rows,overview,sha,digest_tables,table_dict,write_book,input_hash,validate_region
from regional import recalculate,set_setting,set_result_hash
MID='36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s)'
REGION=ROOT/'regions/LME_036';BOOK=REGION/'LME_036.xlsx'
OLD=HERE.parent/'confidence_reassessment_20260930'
RUN='selected_regions_review_20260930'

def save(n,v): (HERE/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')

# Each correction is an independent reviewed biological decision. The broad
# demersal sets are explicit representative-based regional assumptions, not
# assertions that a global family is uniformly demersal or fully enumerated.
DECISIONS={
 'Ariidae':([24,25,26],'M9','Medium','Regional demersal Arius venosus (30 cm TL) and Netuma thalassina (>30 cm TL) establish both species-size classes. The eligible regional marine set is inferred from these representative taxa; the provider label does not document exclusion of the small member.'),
 'Mullidae':([24,25,26],'M9','Medium','Bottom-foraging Upeneus moluccensis (22.5 cm TL) and Parupeneus barberinus (60 cm TL) support both residual demersal size classes. Extension to the regional family reporting category is an explicit assumption.'),
 'Lethrinidae':([24,25,26],'M9','Medium','Regional bottom-associated Lethrinus variegatus (20 cm TL) and L. miniatus (90 cm TL) require small plus large demersal pools. Emperors are excluded from source-era Lutjanidae snappers; species composition remains assumed.'),
 'Upeneus':([24,25,26],'M9','Medium','Small demersal U. moluccensis and the genus inventory member U. taeniopterus (33 cm TL) span the source species-maximum threshold. Regional genus composition and the extension to both demersal classes are assumed; 28 cm SL is not treated as 28 cm TL.'),
 'Platycephalidae':([24,25,26],'M9','Medium','Regional demersal Sorsogona tuberculata (14.5 cm TL) and Platycephalus indicus (100 cm TL) span both species-size classes. The family reporting category is assumed to contain these bottom-associated components.'),
 'Terapon':([24,25,26],'M9','Medium','Terapon puta has maximum 30 cm TL, on the inclusive small side; T. jarbua reaches 36 cm TL and T. theraps 30 cm SL excludes a secure small assignment. Both demersal size classes are retained under a regional genus-composition assumption.'),
 'Plotosus':([24,25,26],'M9','Medium','Western Pacific demersal P. nhatrangensis (24.3 cm TL), P. lineatus (35.2 cm TL) and P. canius (111.1 cm TL) support both size classes. Inclusion of relevant marine/estuarine genus components is assumed.'),
 'Scorpaenidae':([24,25,26],'M9','Medium','Small regional bottom-associated Sebastapistes cyanostigma (10 cm TL) complements the documented larger scorpionfishes. Residual demersal membership across both size classes is a regional family inference; reef association alone is not the size criterion.'),
 'Sillaginidae':([24,25,26],'M9','Medium','FAO bottom-dwelling regional sillaginids include small Sillago argentifasciata and S. japonica and large S. sihama. Both species-size classes are necessary; actual family mixture is not measured.'),
 'Sillago':([24,25,26],'M9','Medium','Regional bottom-associated S. argentifasciata (14.9 cm TL), S. japonica (30 cm TL), and S. sihama (31 cm SL) span the inclusive small and large species classes. Genus proportions remain assumed.'),
 'Terapontidae':([24,25,26],'M9','Medium','The relevant marine/estuarine Terapon components include T. puta (30 cm TL) and larger T. jarbua. Their two species-size classes are inferred for marine family catch; unrelated freshwater family components are not asserted to occur in this marine catch category.'),
 'Balistidae':([24,25,26],'M9','Medium','Regional bottom-associated Rhinecanthus verrucosus (23 cm TL) and larger triggerfishes require small plus large demersal species pools. Composition and ecological extension to the marine reporting family remain assumed.'),
 'Lethrinus':([24,25,26],'M9','Medium','Regional bottom-associated L. variegatus (20 cm TL) and L. miniatus (90 cm TL) establish both species-size classes. The genus-level reporting mixture is represented by both residual demersal classes as an assumption.'),
 'Plotosidae':([24,25,26],'M9','Medium','Marine Western Pacific Plotosus components range from P. nhatrangensis (24.3 cm TL) to P. lineatus/P. canius (>30 cm TL). Their small/large demersal set is assumed representative of marine family catch; freshwater global family members are not automatically included.'),
 'Labridae':([24,25,26],'M9','Medium','Regional bottom-foraging Halichoeres trimaculatus (27 cm TL) complements larger wrasses. Both demersal species-size classes are retained; the catch reporting concept is not silently expanded to every member of a modern broader family classification.'),
 'Scarus':([24,25,26],'M9','Medium','Regional benthic-grazing Scarus fuscocaudalis (25 cm TL) and larger Scarus support both demersal species-size classes. Genus catch composition remains a representative-based inference.'),
 'Scaridae':([24,25,26],'M9','Medium','Regional Scarus fuscocaudalis (25 cm TL) and larger bottom-associated parrotfishes span both species-size classes. The source-era parrotfish reporting concept is retained despite modern family nomenclature.'),
 'Muraenidae':([24,25,26],'M9','Medium','Taiwan-referenced benthic Gymnothorax melatremus has maximum 30 cm TL and complements larger regional morays. Both residual demersal size classes are assumed to represent marine family catch; length is species maximum, not landed individual size.'),
 'Congridae':([24,25,26],'M9','Medium','Regional demersal Ariosoma megalops (20.8 cm TL) and bottom-associated Conger myriaster (100 cm TL) support both species-size classes. Family composition is inferred; bathydemersal depth does not alone imply pelagic residence.'),
 'Gerreidae':([24,25,26],'M9','Medium','Regional demersal Gerres limbatus (15 cm TL) and G. filamentosus (39 cm TL) on mud/sand bottoms establish both size classes. These directly supported pools replace exclusive group 27; family mixture remains inferred.'),
 'Gerres':([24,25,26],'M9','Medium','Regional demersal G. limbatus (15 cm TL) and G. filamentosus (39 cm TL) support both size classes and replace the unsupported exclusive benthopelagic placement. Genus composition is assumed.'),
 'Drepane':([25,26],'M9','Medium','FAO regional D. punctata and D. longimana are large coastal bottom-associated sicklefishes (50 cm TL). The large demersal pair resolves the genus/species inconsistency; extension to the reported regional genus remains explicit.'),
 'Exocoetidae':([29,30,31],'M9','Medium','The regional flyingfish reporting family contains small pelagic species and separately reported Cheilopogon unicolor (38 cm TL). Both pelagic size classes are retained; the provider small-pelagic classifier is not evidence excluding the large member.'),
 'Engraulidae':([29,30,31],'M9','Medium','Small anchovies and larger regional Coilia support both pelagic species-size classes. The reported Anchovies, round herrings label does not establish a species-level exclusion of Coilia; within-family composition is assumed.'),
 'Dasyatidae':([32,33],'M9','Medium','Demersal stingrays and pelagic Pteroplatytrygon violacea, whose published range includes the South China Sea, span both source elasmobranch habitat pools. The reported family mixture is inferred, not a measured pelagic fraction.'),
 'Sphyrnidae':([32,33],'M9','Medium','Pelagic hammerheads and regional benthopelagic winghead Eusphyra blochii support both elasmobranch habitat pools. Treating the near-bottom winghead component as the demersal source guild is an explicit regional interpretation.'),
 'Psettodidae':([25,26],'M3','High','FAO identifies only Psettodes erumei in the Western Central Pacific family, a demersal species reaching about 60 cm TL. Group 24 is pruned: common 20-40 cm individuals do not qualify as a species with maximum TL at or below 30 cm.'),
 'Chirocentrus dorab':([30,31],'M3','High','FAO identifies a coastal pelagic wolf-herring with maximum 100 cm SL, securely above 30 cm TL. The large pelagic pair replaces group 27; neither a reef tag nor common-name herring makes this a benthopelagic or small species.'),
 'Hilsa kelee':([30,31],'M3','High','The authoritative species record gives pelagic-neritic ecology and maximum 35 cm TL. The small-pelagic group 29 is contradicted; the complete large-pelagic pair is eligible independently of landed fish sizes.'),
 'Siganus canaliculatus':([25,26],'M5','Medium','Maximum 40 cm TL contradicts small group 24. Coastal seagrass/algal and substrate-associated biology supports an assumed large-demersal interpretation of the reef-associated species; group eligibility is an ecological extension, not a direct source enumeration.'),
 'Decapterus maruadsi':([30,31],'M5','Medium','Uehara et al. (2021), Table 3 p.160, gives D. maruadsi observed maximum 35.4 cm from the fork-length study Ohshimo et al. (2006); its 34.2 cm FL asymptote is separately retained. A reported observed FL above 30 excludes the small TL class. Large-pelagic membership uses the documented pelagic ecology; the original observed maximum is cited through the primary comparison table.'),
 'Decapterus russelli':([27],'M6','Low','Explicit benthopelagic ecology and maximum 45 cm TL support final group 27 more closely than the exclusively pelagic pair. Inclusion of the appendix large component in final 27 is an explicit unresolved extension; no source merger is asserted.'),
 'Megalops cyprinoides':([27],'M6','Low','Explicit benthopelagic ecology and maximum 150 cm TL support group 27 as an assumed ecological placement. Its large-species scope remains unresolved against the appendix; this correction does not claim that the two appendix pools were merged.'),
 'Planiliza haematocheilus':([30,31],'M5','Medium','The species account explicitly describes pelagic-neritic coastal/estuarine residence and maximum 80 cm TL. The large pelagic pair replaces an unsupported exclusive demersal assignment; translation of the habitat tag to this source guild remains an ecological assumption.'),
 'Caesionidae':([27,29,30,31],'M6','Low','FAO regional fusiliers are reef-associated midwater planktivores with small Pterocaesio and large Caesio. Benthopelagic and both pelagic size classes replace the exclusive large-demersal pair as a disclosed habitat approximation. Group 27 size scope is unresolved; modern Lutjanidae classification does not authorize dedicated source-era snapper group 19.'),
 'Caesio':([27,30,31],'M6','Low','Large regional Caesio, including C. cuning (60 cm TL), are reef-associated midwater planktivores. Group 27 and the large-pelagic pair form an explicit habitat approximation replacing demersal-only membership. Final group 27 scope and source-era Caesionidae versus Lutjanidae remain unresolved; no snapper membership or merger is asserted.'),
}

def main():
 reviewed_sha=sha(BOOK); model=REGION/'models'/MID/'model.json'; model_sha=sha(model)
 book=read_book(BOOK); baseline=copy.deepcopy(book)
 assert overview(book)['selected_model_id']==MID and overview(book)['taxon_detail_year']==2019 and overview(book)['catch_basis']=='landings'
 audit=json.loads((OLD/'taxon_audit_adopted.json').read_text(encoding='utf-8'));by={r['taxon']:r for r in audit}
 proposals=json.loads((OLD/'nonadopted_group_proposals.json').read_text(encoding='utf-8'))
 canonical={int(g['group_seq']):g for g in json.loads(model.read_text(encoding='utf-8'))['group']}
 runtime={int(g['seq']):g for g in records(book,'Selected model groups','Groups')}
 catch_source={int(g['group']):g for g in json.loads((HERE.parent/'source/reconstruction_2000s/SOURCE_CATCH_TOTALS.json').read_text(encoding='utf-8'))}
 current=records(book,'PPR','Matching');curby={t:[r for r in current if r['taxon']==t] for t in by}
 for t,r in by.items():
  assert len(curby[t])==len(r['adopted_groups'])
  assert {(z['group'],round(z['weight'],12)) for z in curby[t]}=={(z['name'],round(z['weight'],12)) for z in r['adopted_groups']},t
 for p in proposals:
  assert {(z['group_id'],round(z['weight'],12)) for z in p['current_groups']}=={(z['group_id'],round(z['weight'],12)) for z in by[p['taxon']]['adopted_groups']},p['taxon']
 # Freeze the assessed accepted input, including the current coordinator styling.
 for p in [BOOK,REGION/f'Model_validation_{MID}.docx',REGION/'LME036_taxon_mapping_appendix.xlsx']:
  shutil.copy2(p,HERE/('baseline_'+p.name))
 protected=lambda b:{'Catch':digest_tables(b['Catch']['Catch']),'Classic Taxa':digest_tables(b['Classic PPR']['Taxa']),'Groups':digest_tables(b['Selected model groups']['Groups']),'Group SPPR':digest_tables(b['Selected model groups']['Group SPPR']),'NPP':digest_tables(b['NPP']),'Diagnostics model_health':digest_tables(b['Diagnostics']['model_health'])}
 save('input_identity.json',{'region_sha256':reviewed_sha,'model_sha256':model_sha,'model_id':MID,'reviewed_input_sha256':input_hash(book),'protected_tables':protected(book),'reference':{'year':2019,'basis':'landings','taxa':374,'carbon_divisor':9}})
 disposition=[];changes=[];allocation=[]
 for p in proposals:
  t=p['taxon'];old=copy.deepcopy(by[t]);r=by[t]
  if t in DECISIONS:
   ids,mrule,mconf,reason=DECISIONS[t]
   source_values=[float(canonical[i]['export']) for i in ids]
   provenance=[]
   for i,x in zip(ids,source_values):
    src=catch_source[i];v=float(src['2000s_fleet_sum']);assert math.isclose(x,v,rel_tol=0,abs_tol=1e-12),(t,i,x,v)
    assert math.isclose(x,runtime[i]['catch'],rel_tol=0,abs_tol=1e-12)
    provenance.append({'group_id':i,'canonical_group_name':canonical[i]['group_name'],'source_table_name':src['name'],'canonical_export':x,'loaded_catch':runtime[i]['catch'],'source_fleet_values':src['2000s_fleets'],'source_fleet_sum':v,'printed_total':src['2000s_printed_total'],'pdf_page':src['pdf_page'],'table':'6.2','units':'t wet weight/km2/year','basis':'reported fishery catches written to Landings; no discard split','is_loader_default':False,'explicit_source_zero':v==0})
   assert all(math.isfinite(x) and x>=0 for x in source_values) and math.fsum(source_values)>0
   weights=[1.] if len(ids)==1 else [x/math.fsum(source_values) for x in source_values]
   r['adopted_groups']=[{'group_id':i,'name':canonical[i]['group_name'],'weight':w} for i,w in zip(ids,weights)]
   r.update({'membership_rule':mrule,'membership_confidence':mconf,'weight_rule':'W1' if len(ids)==1 else 'W4','weight_confidence':'High' if len(ids)==1 else 'Medium','review_confidence':min([mconf,'High' if len(ids)==1 else 'Medium'],key=['Unresolved','Very low','Low','Medium','High'].index),'reason':reason+(' Source-model catch proportions supply an assumed fixed 1950–2019/all-bases mixture; they are not observed taxon-specific catches.' if len(ids)>1 else ''),'adoption_run_id':RUN,'membership_sources':p['sources'],'source_membership_reuse':'Retained authoritative source locators re-evaluated for this explicit correction; no new exhaustive global taxonomy claim.','weight_source':'Cheung Table 6.2 PDF pp.193–194: exact complete six-fleet sums match accepted canonical group.export and loaded catch.','allocation_provenance':provenance,'assumption_dependent':len(ids)>1 or mconf!='High'})
   r['membership_source']='; '.join(s.get('title','')+' — '+s.get('url',s.get('path',s.get('repo_path','')))+' ('+s.get('section',s.get('page/section',s.get('page_or_section','')))+')' for s in p['sources'])
   r['display_mapping']='; '.join(g['name']+f" ({100*g['weight']:.6f}%)" for g in r['adopted_groups'])
   change={'taxon':t,'old_groups':old['adopted_groups'],'new_groups':r['adopted_groups'],'old_membership_rule':old['membership_rule'],'new_membership_rule':mrule,'old_membership_confidence':old['membership_confidence'],'new_membership_confidence':mconf,'old_weight_rule':old['weight_rule'],'new_weight_rule':r['weight_rule'],'old_weight_confidence':old['weight_confidence'],'new_weight_confidence':r['weight_confidence'],'old_overall_confidence':old['review_confidence'],'new_overall_confidence':r['review_confidence'],'catch_2019_landings_t':r['catch_t'],'independent_ppr_2019_tC_exposure':r['ppr_tC'],'reason':r['reason'],'source_locators':p['sources']}
   changes.append(change)
   disposition.append({'taxon':t,'decision':'adopted','adopted':True,'proposal':p['proposal'],**change})
  else:
   reason='Retain current mapping with its reviewed '+r['review_confidence']+' confidence. '+p['rationale']+' The retained evidence does not establish a complete replacement candidate set or close this habitat/reporting/length-metric boundary. No numerical reallocation is justified by the proposal alone.'
   disposition.append({'taxon':t,'decision':'rejected_as_insufficiently_supported','adopted':False,'proposal':p['proposal'],'old_groups':old['adopted_groups'],'new_groups':old['adopted_groups'],'reason':reason,'source_locators':p['sources'],'scientific_limitation_retained':True})
   r['proposal_disposition']=reason
  r['reassessment_20260930_scope']='Proposal re-evaluated; complete prior taxon review reused where unaffected.'
 # Verify and retain complete source provenance for every split, including any
 # genuinely zero candidate. A rounded printed total is not a default zero.
 for r in audit:
  ids=[g['group_id'] for g in r['adopted_groups']]
  vals=[float(canonical[i]['export']) for i in ids]
  if len(ids)>1:
   for i,x in zip(ids,vals):assert i in catch_source and math.isclose(x,float(catch_source[i]['2000s_fleet_sum']),rel_tol=0,abs_tol=1e-12)
   expect=[v/math.fsum(vals) for v in vals]
   assert all(math.isclose(w,g['weight'],rel_tol=1e-12,abs_tol=1e-12) for w,g in zip(expect,r['adopted_groups'])),r['taxon']
  allocation.append({'taxon':r['taxon'],'candidate_ids':ids,'weights':[g['weight'] for g in r['adopted_groups']],'rule':r['weight_rule'],'confidence':r['weight_confidence'],'source_field':'accepted canonical group.export','source_values':vals,'source_total':math.fsum(vals),'usable_complete_catch':len(ids)>1,'source_zero_ids':[i for i,v in zip(ids,vals) if v==0],'default_or_missing_ids':[],'biomass_fallback_needed':False,'source_provenance':'Cheung Table6.2 PDF193–194 complete fleet sums checked against canonical export and loaded catch; original source differences remain documented.','transfer_assumption':'Fixed northern-shelf 2000s guild proportions across whole-LME 1950–2019 landings/catch/discards, not observed species mixtures.'})
  if 'assumption_dependent' not in r:r['assumption_dependent']=len(ids)>1 or r['membership_confidence']!='High'
 # Patch authoritative rows by exact taxon/group keys.
 evidence=str((HERE/'taxon_audit_adopted.json').relative_to(ROOT)).replace('\\','/')
 matching=[]
 for r in audit:
  for g in r['adopted_groups']:
   matching.append({'model_id':MID,'taxon':r['taxon'],'group':g['name'],'weight':g['weight'],'confidence':r['review_confidence'].lower().replace(' ','_'),'evidence':evidence,'explanation':r['reason']})
 book['PPR']['Matching']=table_dict(matching)
 reviews={r['taxon']:r for r in records(book,'PPR','Mapping review')}
 labels={'M1':'The source explicitly assigns the taxon to the model group','M3':'Documented taxonomy and ecology unambiguously meet the group definition','M5':'Documented size and habitat support an ecological assignment','M6':'Ecological fit is partial or the source definition is conflicting','M9':'Taxonomy, ecology and group definitions support the eligible group set','M10':'A broad catch label is approximated by compatible model groups','M11':'The closest represented ecological analogue substitutes for an absent group','W1':'The taxon is assigned to one group and needs no split','W4':'Model catch proportions supply an assumed allocation across eligible groups'}
 for r in audit:
  rv=reviews[r['taxon']];rv.update({'membership_rule':labels[r['membership_rule']],'membership_confidence':r['membership_confidence'],'allocation_rule':labels[r['weight_rule']],'allocation_confidence':r['weight_confidence'],'overall_confidence':r['review_confidence'],'membership_evidence':r['membership_source'],'allocation_evidence':r['weight_source'],'candidate_selection':json.dumps(r['adopted_groups'],ensure_ascii=False),'allocation_calculation':json.dumps(next(x for x in allocation if x['taxon']==r['taxon']),ensure_ascii=False),'reason':r['reason'],'adoption_date':'2026-09-30','review_run_id':RUN,'assumption_dependent':r['assumption_dependent']})
 book['PPR']['Mapping review']=table_dict(reviews.values())
 ledger=[r for r in records(book,'PPR','Allocation assumptions') if r['taxon'] not in DECISIONS]
 for t in DECISIONS:
  r=by[t]
  r['transfer_assumption']=r.get('transfer_assumption') or 'Fixed northern-shelf 2000s guild proportions across whole-LME 1950–2019 and catch bases; actual taxon composition is unmeasured.'
  if len(r['adopted_groups'])<=1:continue
  for g in r['adopted_groups']:
   i=g['group_id'];ledger.append({'unit_id':'LME_036','model_id':MID,'taxon':t,'rule':'model_catch_proxy','confidence':'assumed','weight_evidence':'model_catch_proxy','definition':r['reason'],'evidence':evidence,'limitations':r['transfer_assumption']+' Complete six-fleet source catches are model proxies, not observed taxon composition.','source_period':'2000s','online_search':'Prior retained stage-composition search plus current regional catch-composition source search: no applicable whole-LME taxon wet-mass shares at model boundaries recovered.','previous_mapping':json.dumps(curby[t],ensure_ascii=False),'years_applied':'1950-2019','catch_bases_applied':'landings;catch;discards','rule_details':'complete_source_model_catch_proportions','source_catch_basis':'Table6.2 reported fishery catches; no discard split','temporal_and_basis_assumption':'Fixed northern-shelf 2000s proxy across whole-LME years and catch bases.','group':g['name'],'seq':i,'source_catch':float(canonical[i]['export']),'weight':g['weight'],'source_definition':canonical[i]['taxon_descr'],'numeric_sppr_exists':any(x['group']==g['name'] and isinstance(x['sppr'],(int,float)) for x in records(book,'Selected model groups','Group SPPR')),'review_confidence':r['review_confidence'],'membership_review_confidence':r['membership_confidence'],'weight_review_confidence':r['weight_confidence'],'assumption_dependent':True,'confidence_review_evidence':evidence,'confidence_review_reason':r['reason']})
 book['PPR']['Allocation assumptions']=table_dict(ledger)
 # Preserve historical calculation evidence with an explicit historical title.
 if 'Size allocation impact' in book['Diagnostics']:
  book['Diagnostics']['Historical size allocation impact']=book['Diagnostics'].pop('Size allocation impact')
 # The standard calculator only rebuilds dependent arithmetic from accepted
 # group SPPR. Restore independent classic results whose inputs are identical.
 recalculate(book,BOOK)
 book['Classic PPR']=copy.deepcopy(baseline['Classic PPR'])
 ratio_header,ratio_rows=book['PPR–NPP']['Ratios'];new_model=[r for r in ratio_rows if r[0]]
 old_independent=[r for r in baseline['PPR–NPP']['Ratios'][1] if not r[0]]
 book['PPR–NPP']['Ratios']=(ratio_header,old_independent+new_model)
 categories=[];totalcatch=math.fsum(r['catch_t'] for r in audit);totalppr=math.fsum(r['ppr_tC'] for r in audit)
 for q in ['High','Medium','Low','Very low','Unresolved']:
  rr=[r for r in audit if r['review_confidence']==q]
  categories.append({'confidence':q,'taxa':len(rr),'catch_t':math.fsum(r['catch_t'] for r in rr),'ppr_tC':math.fsum(r['ppr_tC'] for r in rr),'catch_pct':100*math.fsum(r['catch_t'] for r in rr)/totalcatch,'ppr_pct':100*math.fsum(r['ppr_tC'] for r in rr)/totalppr})
 rule_tables={}
 for component,rf,cf in [('membership_rules','membership_rule','membership_confidence'),('weight_rules','weight_rule','weight_confidence')]:
  combos=set((r[rf],r[cf]) for r in audit);rule_tables[component]=sorted([{'Plain-language rule':labels[code],'Confidence':conf,'PPR percentage':100*math.fsum(r['ppr_tC'] for r in audit if (r[rf],r[cf])==(code,conf))/totalppr} for code,conf in combos],key=lambda x:-x['PPR percentage'])
 assumed=sum(r['assumption_dependent'] for r in audit);very=next(r for r in categories if r['confidence']=='Very low')
 set_setting(book,'source_note',f'PROVISIONAL: all 374 taxa reviewed; {len(changes)} evidence-supported group-set corrections adopted after individual review of 78 proposals; {assumed} assumption-dependent taxa, including {very["taxa"]} Very low assignments; 0 unresolved. Very low mappings cover {very["catch_pct"]:.4f}% of 2019 landings. Accepted parameters, raw catch, classic TL/coefficient, NPP and group SPPR preserved. See PPR / Mapping review and Allocation assumptions; regional scope and diagnostic limitations remain.')
 set_setting(book,'calculation_status','provisional: supported mapping corrections adopted and dependent arithmetic recalculated from unchanged group SPPR; classic results preserved; historical model sensitivity bounds invalidated')
 set_setting(book,'calculation_input_sha256',input_hash(book));set_result_hash(book)
 assert protected(book)==protected(baseline)
 assert sha(model)==model_sha
 summary={'taxa':len(audit),'catch_t':totalcatch,'ppr_tC':totalppr,'categories':categories,**rule_tables,'proposals':len(proposals),'adopted_group_corrections':len(changes),'rejected_proposals':len(proposals)-len(changes),'assumption_dependent_taxa':assumed,'single_group_taxa':sum(len(r['adopted_groups'])==1 for r in audit),'split_taxa':sum(len(r['adopted_groups'])>1 for r in audit),'missing_tl_coefficient_taxa':sum(r['tl'] is None for r in audit),'unknown_annual_ppr_taxa':sum(r['ppr_tC'] is None for r in audit)}
 save('proposal_dispositions.json',disposition);save('mapping_changes.json',changes);save('taxon_audit_adopted.json',audit);save('allocation_audit.json',allocation);save('summary.json',summary)
 def annual_key(r):return tuple('' if x is None else x for x in r[:6])
 oldannual={annual_key(r):r for r in baseline['PPR']['Annual'][1]};effect=[]
 for r in book['PPR']['Annual'][1]:
  key=annual_key(r);oldrow=oldannual.get(key)
  if r[5]!='ppr' or oldrow is None:continue
  i=book['PPR']['Annual'][0].index(2019);x,y=oldrow[i],r[i]
  if isinstance(x,(int,float)) and isinstance(y,(int,float)):
   effect.append({'model_id':r[0],'scope':r[1],'method':r[2],'basis':r[3],'unidentified':r[4],'old_2019_ppr_tC':x/9,'new_2019_ppr_tC':y/9,'change_tC':(y-x)/9,'change_pct':100*(y-x)/x if x else None})
 save('dependent_result_changes.json',effect)
 # Freshness guard checks the originally reviewed file immediately before save.
 if sha(BOOK)!=reviewed_sha:raise RuntimeError('Regional workbook changed since review; re-read and reconcile before saving.')
 write_book(BOOK,book)
 reopened=read_book(BOOK);assert protected(reopened)==protected(baseline)
 validate_region(reopened,BOOK)
 save('adoption_checks.json',{'protected_tables_preserved':True,'model_preserved':sha(model)==model_sha,'classic_ppr_all_tables_preserved':digest_tables(reopened['Classic PPR'])==digest_tables(baseline['Classic PPR']),'independent_ratios_preserved':digest_tables([r for r in reopened['PPR–NPP']['Ratios'][1] if not r[0]])==digest_tables(old_independent),'freshness_guard_expected_sha256':reviewed_sha,'freshness_guard_checked_immediately_before_save':True,'final_region_sha256':sha(BOOK),'final_input_sha256':overview(reopened)['calculation_input_sha256'],'final_result_sha256':overview(reopened)['calculation_result_sha256'],'region_validation_passed':True,'proposal_dispositions':len(disposition),'adopted_corrections':len(changes),'protected_baseline':protected(baseline),'protected_final':protected(reopened),'historical_size_allocation_impact':'Retained and explicitly renamed Historical size allocation impact; predates current mappings and not used for current arithmetic.'})
 print(json.dumps(summary,ensure_ascii=True))

if __name__=='__main__':main()
