from pathlib import Path
from copy import deepcopy
import json,sys,math,re,hashlib
sys.stdout.reconfigure(encoding='utf-8');OUT=Path(__file__).parent
def load(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
inputs={r['taxon']:r for r in load('review_inputs.json')};base=load('baseline_tables.json');gh,gr=base['Selected model groups']['Groups'];groups=[dict(zip(gh,r)) for r in gr];byname={r['group_name']:r for r in groups}
decisions={};ownership={}
fish_path=OUT/'fish_squid_review.json';fish_text=fish_path.read_text(encoding='utf-8')
fish_raw=json.loads(fish_text)
if 'Prose >3 conflicts at age3.' in fish_text:
    (OUT/'baseline/fish_squid_review_before_root_correction.json').write_text(fish_text,encoding='utf-8')
    fish_text=fish_text.replace('Prose >3 conflicts at age3.','Original Table 1 and prose use adults ≥3 years; >3 is a secondary transcription discrepancy.').replace('Hoki table <3/>=3 conflicts with prose>3 at age3.','Original Hoki Table 1 and prose use juveniles <3 and adults ≥3 years; a secondary >3 transcription is not the operative boundary.')
    fish_raw=json.loads(fish_text);fish_raw['_meta']['parent_evidence_correction']={'reason':'Direct source prose and Table 1 were visually checked alongside allocation review; both use adults ≥3 years.','review_before_correction_sha256':hashlib.sha256((OUT/'baseline/fish_squid_review_before_root_correction.json').read_bytes()).hexdigest()}
    fish_path.write_text(json.dumps(fish_raw,ensure_ascii=False,indent=2),encoding='utf-8')
def readable(s):
    replacements={'source6':'the Small pelagic fish group','source7':'the Seriolella-defined Other demersal fish group','source12':'the named Skates group','group6':'Small pelagic fish','group7':'Other demersal fish','sourcecatch':'source catch','nativeY':'native source catch','nativeB':'native source biomass','caughtMASS':'caught mass','caught-MASS':'caught mass','smallpelagic':'small pelagic','catchstage':'caught stage','catchbasis':'catch basis','familymixture':'family mixture','sourceage':'source age','caughtstage':'caught stage','nearbottom':'near-bottom','nearcoastal':'near-coastal','wholelabel':'whole label'}
    for a,b in replacements.items():s=s.replace(a,b)
    s=re.sub(r'(?<=\d)(?=cm|mm|years|m\b|km\b|tonnes\b)', ' ',s)
    s=re.sub(r'(\b(?:establishes|describes|around|to|beyond|usuallymax|at|up to))(?=\d)',r'\1 ',s)
    s=re.sub(r'weak7\b','a weak Seriolella-pool',s)
    return s
for filename in ['fish_squid_review.json','elasm_invertebrate_review.json','allocation_residual_review.json','root_additional_review.json']:
    d=load(filename)
    rows=d.get('decisions',d.get('reviews',d.get('taxa',d.get('taxon_records',[])))) if isinstance(d,dict) else d
    if isinstance(rows,dict):rows=[r|{'taxon':t} for t,r in rows.items()]
    for row in rows:
        t=row['taxon'];assert t in inputs,t
        r=deepcopy(row)
        r['reason']=r.get('reason',r.get('retained_or_change_reason',r.get('membership_reason','')))
        assert isinstance(r['reason'],str) and r['reason'],(filename,t,'missing reason')
        r['allocation_reason']=r.get('allocation_reason',r.get('allocation_calculation',{}).get('reason','One reviewed group; no numerical split.'))
        if filename=='allocation_residual_review.json':r['reason']+=' '+r['allocation_reason']
        r['review_record']=deepcopy(row);r['review_evidence_file']=filename
        if t in decisions:r['additional_membership_review']=decisions[t]['review_record']
        decisions[t]=r;ownership[t]=filename
assert set(decisions)==set(inputs),(len(decisions),sorted(set(inputs)-set(decisions)),sorted(set(decisions)-set(inputs)))
# Concrete parent adjudication, after comparing primary habitat/morphology and
# reporting evidence with the operative focal definitions. No coefficients
# participate in eligibility decisions.
clarifications={
 'Gadiformes':('The historical cod-like reporting category is approximated by the represented Hoki, Southern blue whiting and Southern hake pools. The Seriolella-defined pool is excluded as non-gadiform. Complete source catches (0.006, 0.056, 0.011, 0.125) supply transferred proportions; regional composition remains unknown.','Unknown cod-like species composition and unrepresented grenadiers require a broad-category approximation. Complete 1980 source catches supply proxy weights, without establishing regional composition.'),
 'Malacostraca':('Every positive exact-label provider record is Chilean artisanal landings with hand/tools. This supports an assumed bottom-associated reporting scope and Benthos at 100%. Reconstructed gear information limits membership to Medium; pelagic class members are not declared biologically absent.',''),
 'Coelorinchus chilensis':('FAO regional range/depth and grenadier morphology support the Hoki union as a weak benthopelagic cod-like analogue. Hoki and grenadier share an elongate tapering body and extended fins, but ecology and taxonomy differ. Complete Hoki source catches provide 9.677419% juvenile-pool and 90.322581% adult-pool coefficients; these are not grenadier ages.','A grenadier has no named focal group. The Hoki union is a weak morphology/habitat analogue with different biology. Historical Hoki catch proportions divide surrogate coefficients and do not measure grenadier stage composition.'),
 'Macrouridae':('Regional grenadiers require a broad, weak Hoki-union analogue based on cod-like taxonomy, tapering morphology and shelf/slope habitat. Family composition is unknown. Complete Hoki source catches provide 9.677419% juvenile-pool and 90.322581% adult-pool coefficients; the source age-three boundary is not transferred to grenadiers.','Unknown grenadier composition has no named source pool. Hoki morphology/habitat provides only a weak broad-category analogue; transferred Hoki catch weights are not observed grenadier ages.'),
 'Carangidae':('The regional jack family includes schooling pelagic Decapterus and bottom/reef-associated Selene and adult Seriola. Small pelagic fish and the Seriolella bottom-fish analogue cover this unknown mixture only approximately. Both source catches are missing, so complete biomass proportions supply 91.587871% and 8.412129%; catchability and composition are assumed.','Unknown family composition spans pelagic and bottom/reef-associated fish. The Seriolella-defined pool is an analogue, and model biomass proportions are an unobserved regional composition proxy.'),
 'Sciaenidae':('Retain the Seriolella-defined Other demersal fish pool as a Very low bottom-fish analogue for the unknown drum-family mixture. The proposed pelagic split was rejected: primary IMARPE regional bottom-fishery evidence for Larimus outweighs the generic provider pelagic tag. One reviewed group; no split.','Drum-family composition is unknown and the focal Other demersal fish definition lists Seriolella only. Bottom-fish habitat supplies a weak analogue, without literal source membership.'),
 'Macruronus magellanicus':('Exact source Hoki union: juveniles <3 years and adults ≥3 years. Retain 0.006/(0.006+0.056) and 0.056/(0.006+0.056) from complete static source catches. Regional age counts and corrected supplementary catches do not establish observed caught-mass stage composition; the historical split remains a Medium-confidence proxy.','')}
for taxon,(reason,vlreason) in clarifications.items():
    decisions[taxon]['reason']=reason;decisions[taxon]['appendix_reason']=reason
    if vlreason:decisions[taxon]['very_low_reason']=vlreason
    decisions[taxon]['parent_adjudication']='Adopted after focal-definition and regional evidence comparison; allocation proposals reconciled independently of saved coefficient values.'
rank={'High':4,'Medium':3,'Low':2,'Very low':1,'Unresolved':0}
for taxon,r in decisions.items():
    m=r['new_mappings']
    for x in m:
        if 'group' not in x:x['group']=x['group_name']
        x['seq']=byname[x['group']]['seq']
    # Keep the exact saved floats whenever the reviewed numerical decision is retained.
    old=inputs[taxon]['matching'];nm={x['group']:x for x in m};om={x['group']:x for x in old}
    if set(nm)==set(om) and all(math.isclose(nm[g]['weight'],om[g]['weight'],rel_tol=0,abs_tol=1e-14) for g in nm):
        for x in m:x['weight']=om[x['group']]['weight']
    assert r['overall_confidence']==min([r['membership_confidence'],r['allocation_confidence']],key=rank.get)
    assert math.isclose(math.fsum(x['weight'] for x in m),1,abs_tol=1e-9,rel_tol=0)
    if 'allocation_candidates' not in r:r['allocation_candidates']=r.get('candidates',[])
    # Preserve the review's precise candidate rationales in its record; the final
    # statuses are separately reconciled against the adopted eligible group set.
    r['final_candidate_status']=[{'seq':g['seq'],'group':g['group_name'],'included':g['group_name'] in nm,'weight':nm[g['group_name']]['weight'] if g['group_name'] in nm else 0,'zero_meaning':'candidate excluded by eligibility, not observed source zero' if g['group_name'] not in nm else 'adopted allocation'} for g in groups]
    r['method_priority_evidence']={'landings_2019_tonnes':inputs[taxon]['catch_tonnes'],'independent_simple_chain_tC':inputs[taxon]['simple_chain_ppr_tC'],'saved_method_source_exposures_tC':inputs[taxon]['method_exposure_tC']}
    r['model_applicability_separate_from_membership']='Fixed 1980 Chilean Patagonia coefficient transfer across the Humboldt LME remains provisional with saved WARN diagnostics; group eligibility does not validate this transfer.'
    r['appendix_reason']=readable(r.get('appendix_reason',r['reason']))
    if r['allocation_rule']=='W1' and not any(w in r['appendix_reason'].lower() for w in ['no split','no numerical split','no allocation split','one group']):r['appendix_reason']+=' One group; no numerical split.'
(OUT/'reconciled_decisions.json').write_text(json.dumps(decisions,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
(OUT/'review_completeness.json').write_text(json.dumps({'taxa':218,'all_exact_labels_including_zero':True,'review_ownership':ownership,'root_adjudication_taxa':list(clarifications),'membership_allocation_separate':True,'numerical_retention_uses_exact_baseline_weights':True},ensure_ascii=False,indent=2),encoding='utf-8')
print('Reconciled exact labels',len(decisions))
