from pathlib import Path
import json

root=Path.cwd()
out=root/'regions/LME_034/validation_reports/34_1_Bay_of_Bengal_(1978)/geography_sources'
central=json.loads((out/'central_context.json').read_text(encoding='utf8'))
geography=json.loads((out/'geographic_evidence.json').read_text(encoding='utf8'))
paper=next(p for p in central['Papers'] if p['article_id']=='LME034-Guenette-2013__LME_034')
model=central['Models & coverage'][0]

alternatives=[]
for p in central['Papers']:
    if p['article_id']==paper['article_id']:continue
    alternatives.append({k:p.get(k) for k in ['article_id','authors','publication_year','title','doi','landing_page','article_dir','model_years','functional_groups','coverage_note','download_status']})
for p in alternatives:
    if p['article_id']=='BOB-2019__LME_034':
        p['review_note']='Unverified legacy bibliographic entry; do not conflate it with the distinct Karim2018 article. Neither its reported2015–2016 model years nor legacy8% footprint is independently verified in this review.'
    if p['article_id']=='BOB-2014__LME_034':
        p['review_note']='Related BOBLME user guide, not established here as a distinct independently reconstructed alternative model. No verified local guide/main model file.'
    if p['article_id']=='LME034-Dutta-2023__LME_034':
        p['authors']='Sachinandan Dutta, Sourav Paul and Sumit Homechaudhuri'
        p['local_pdf']='regions/LME_034/papers/LME034-Dutta-2023/1-s2.0-S2352485523000506-main-10820fa3.pdf'
        p['review_note']='First PDF page independently confirms authors/title/year,29 functional groups. Domain is northern Bay off West Bengal, not whole LME; central inventory scope retained.'
    if p['article_id']=='LME034-Karim-2018__LME_034':
        p['authors']='Ehsanul Karim, Q. Liu, Y. Xue, B. Liao, S. J. Hasan, M. E. Hoq and Yahia Mahmud'
        p['local_pdf']='regions/LME_034/papers/LME034-Karim-2018/1603_31713196-9756a34b.pdf'
        p['functional_groups']=19
        p['model_area_km2_note']='over90,000 km² (abstract), subregional resettled Bangladesh maritime zone'
        p['review_note']='First PDF page independently confirms citation,19 functional groups and >90,000km² domain. Preserve as separate from unverified legacyBOB2019.'

context={
 'unit_id':'LME_034','region_name':'Bay of Bengal','selected_model_id':'34_1_Bay_of_Bengal_(1978)',
 'article':{'article_id':paper['article_id'],'authors':'Sylvie Guénette','year':2013,'date':'December2013','title':paper['title'],'doi':'? (not recorded)','local_pdf':'regions/LME_034/papers/LME034-Guenette-2013/009031359-84f3dc3d.pdf','paper_folder':'regions/LME_034/papers/LME034-Guenette-2013','pdf_pages':62,'publication_note':'Actual local report title page dates December2013. Central metadata records later distribution as BOBLME2014 Ecology09; its69-page edition is distinct from the62-page original inspected here. The archived local PDF is the source for these findings.'},
 'model':{'model_id':'34_1_Bay_of_Bengal_(1978)','baseline_year':1978,'simulation_years':'1978–2010','domain':'Bay of Bengal LME extended to northern Sumatra, Maldives and adjacent high seas; three geographic regions','local_json':'regions/LME_034/models/34_1_Bay_of_Bengal_(1978)/model.json','local_model_folder':'regions/LME_034/models/34_1_Bay_of_Bengal_(1978)','canonical_json_group_count_at_review':49,'group_count_note':'Source/runtime structure and current adopted group count are to be reconciled by the separate reconstruction review.'},
 'selection_rationale':{'Article':'?','Model':'?','recorded_selection_note':model['selection_rationale'],'review_note':'The recorded pilot designation identifies the selected model but gives no comparative reason for choosing this article among articles or this model among model alternatives; do not invent either reason.'},
 'other_known_articles':alternatives,
 'other_models_from_same_article':{'distinct_static_alternatives_established':[],'report_text':'No other distinct static model identified in the reviewed source. The initial inputs and balanced1978 parameters are states of the same baseline;1978–2010 Ecosim runs and AppendixA6 industrial-effort changes are simulations/scenarios of that baseline.','source_evidence':[{'pages':[6,7],'finding':'Source defines the1978 static model and1978–2010 dynamic simulation.'},{'pages':[23,24],'finding':'Initial input and balanced Ecopath tables refer to the same baseline; reconstruction audit owns their exact differences.'},{'pages':[28,29,60,61,62],'finding':'Alternative Indian industrial effort (industrial vessels alone versus large vessels with trawlers) changes vulnerability fits and simulated trends; it is an effort scenario, not another geographic or historical Ecopath baseline.'}]},
 'geographic_fit':geography,
 'geographic_compartments':{'region1':'Maldives and open waters/high seas','region2':'Sri Lanka, Indian coast and Bay of Bengal/Bangladesh','region3':'Myanmar, Thailand, western peninsular Malaysia, western Sumatra, Andaman and Nicobar','cross_region_groups':'Unprefixed oceanic/migratory groups span broader parts of S;2–3 Hilsa and2–3 Indian mackerel straddle shelf regions2 and3. Prefixes are geography, not stages/depth strata.','material_caveat':'Maldives shelf pools are outside R; the entire region1 domain is not. Its open-water/high-seas portion overlaps the southern target. R cannot be equated to the region2+3 EEZ subtotal. Do not extend the valid shelf-pool exclusion to every region1 compartment without habitat-specific evidence.'},
 'temporal_fit':{'reference_year':2019,'reference_basis':'landings','regional_catch_years':'1950–2019','baseline_to_reference_years':41,'text':'The1978 Ecopath baseline is41 years before the2019 landings reference. Fixed group coefficients and spatial/stage allocation assumptions are extrapolated across1950–2019 (28 years before and41 years after the baseline). The1978–2010 Ecosim exercise does not establish annual recalibration or a2019 static food web. The source baseline input combines landings and discards (p9), while this report uses2019 landings.'},
 'scope':'Read-only source/workbook review and report geography arithmetic. Files written only in this geography_sources supporting folder; no source model/workbook/map changes.'
}
(out/'context_and_geography.json').write_text(json.dumps(context,ensure_ascii=False,indent=2),encoding='utf8')
print(out/'context_and_geography.json')
