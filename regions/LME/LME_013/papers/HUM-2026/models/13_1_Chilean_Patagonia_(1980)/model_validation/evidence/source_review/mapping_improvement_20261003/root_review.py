from pathlib import Path
from copy import deepcopy
import json,sys
sys.stdout.reconfigure(encoding='utf-8');OUT=Path(__file__).parent
inputs={r['taxon']:r for r in json.loads((OUT/'review_inputs.json').read_text(encoding='utf-8'))}
source=json.loads((OUT/'baseline_tables.json').read_text(encoding='utf-8'));h,rows=source['Selected model groups']['Groups'];groups=[dict(zip(h,r)) for r in rows]
reasons={
 'Pyura chilensis':('IMARPE identifies piure/cochiza as a sessile benthic ascidian harvested by diving in Chile. Its chordate phylum does not make it a fish. Retain Benthos under the source’s explicit seabed definition; no size or age subdivision is defined. One group, no allocation split.','M3','High',5),
 'Chrysaora plocamia':('IMARPE documents a large pelagic jellyfish from Peru to southern Chile. Retain Macrozooplankton as a Very low macroscopic plankton analogue: the source defines euphausiids, whereas jellyfish differ in size, gelatinous composition and diet. Benthic polyps do not establish a caught-mass stage split. One group, no split.','M11','Very low',4)}
reviews={}
for taxon,(reason,rule,confidence,seq) in reasons.items():
    old=inputs[taxon];r={**old['old_review'],'taxon':taxon,'new_mappings':[{'group':g['group_name'],'seq':seq,'weight':1} for g in groups if g['seq']==seq],'membership_rule':rule,'membership_confidence':confidence,'allocation_rule':'W1','allocation_confidence':'High','overall_confidence':confidence,'reason':reason,'appendix_reason':reason,'provider_meaning':old['provider'],'synonyms_and_rank':'Exact provider species key retained; IMARPE regional account and preserved authority snapshot reviewed.','included_candidates':[],'excluded_candidates':[],'evidence':[],'stage_criteria':'No focal size/stage division for this group; no observed caught-mass stage split inferred.','allocation_reason':'One reviewed source group/analogue; no numerical split.'}
    for g in groups:
        candidate={'seq':g['seq'],'group':g['group_name'],'included':g['seq']==seq}
        candidate['reason']=reason if g['seq']==seq else ('Species-specific fish/skate/mammal definitions or synthetic/nonliving roles do not contain this taxon. Habitat or prey overlap alone does not establish source membership.' if g['seq'] not in [1,2,3,4,5,6] else 'Source plankton/taxonomic and habitat criteria differ; alternative life-phase or prey overlap is insufficient for an observed caught-mass allocation. See the included analogue/definition rationale.')
        r['included_candidates' if candidate['included'] else 'excluded_candidates'].append(candidate)
    url='https://biodiversidadacuatica.imarpe.gob.pe/Files/ExportarEspeciePdf?taxonId='+('832' if seq==5 else '465')
    r['evidence'].append({'title':'IMARPE regional species account: '+taxon,'url':url,'locator':'PDF pages 1–3, taxonomy, ecology and fishery sections','supports':reason,'material_read':'Full primary institutional PDF text read','date':'2026-10-03'})
    r['evidence'].append({'title':'Neira et al. focal model definitions','url':'https://doi.org/10.1016/j.pocean.2025.103631','locator':'Table 1 PDF4','supports':'Benthos is the explicit seabed category; Macrozooplankton is specifically euphausiids. No gelatinous compartment or ascidian stage boundary supplied.'})
    reviews[taxon]=r
(OUT/'root_additional_review.json').write_text(json.dumps({'decisions':reviews,'scope':'Independent root checks of a chordate invertebrate and a zero-catch gelatinous label; catch-label coverage checked by keys, not phylum alone.','scientific_execution':False},ensure_ascii=False,indent=2),encoding='utf-8')
print('Independent root species checks saved',list(reviews))
