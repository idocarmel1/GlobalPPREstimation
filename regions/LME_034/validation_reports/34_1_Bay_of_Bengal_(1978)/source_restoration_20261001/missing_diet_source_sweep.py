"""Read-only diet-prose and original-matrix sweep; propose no canonical changes."""
import json,re,sys
from decimal import Decimal
from pathlib import Path
from pypdf import PdfReader
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4]
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import sha

def main():
    pdf=ROOT/'regions/LME_034/papers/LME034-Guenette-2013/009031359-84f3dc3d.pdf'
    reader=PdfReader(pdf);texts=[p.extract_text() for p in reader.pages]
    diet_hits=[i for i,t in enumerate(texts,1) if re.search(r'diet|feeding|food|detriti',t,re.I)]
    for page in [11,19,20,21,22,50,51,52,53,55,56]:
        (OUT/f'diet_source_page_{page}.txt').write_text(texts[page-1],encoding='utf-8')
    ledger=json.loads((OUT/'table17_source_ledger.json').read_text(encoding='utf-8'))
    known={(c['predator_seq'],c['prey_seq']):Decimal(c['printed_value']) for c in ledger['printed_cells']}
    appendix=json.loads((OUT/'initial_diet_appendix_sweep.json').read_text(encoding='utf-8'))
    groups=[]
    for seq,analog in [(30,None),(32,19),(33,20),(36,23),(38,25),(39,26),(40,27),(41,28)]:
        total=Decimal(ledger['source_sums_exact_decimal_including_import'][str(seq)])
        groups.append({'group_seq':seq,'balanced_table17_sum':str(total),'residual_to_one':str(1-total),
            'balanced_detritus':str(known[seq,49]),'original_appendix_sum':appendix['56']['sums'][str(seq)],
            'original_appendix_detritus':appendix['56']['detritus'][str(seq)],'regional2_analogue_seq':analog,
            'regional2_printed_detritus':str(known[analog,49]) if analog else None,
            'analogue_detritus_exactly_equals_residual':known[analog,49]==1-total if analog else False,
            'author_explicitly_assigns_group_residual':False})
    result={'source_sha256':sha(pdf),'pages_scanned':len(texts),'diet_term_pages':diet_hits,
        'quantitative_missing_diet_recovery_found':False,'canonical_changes_performed':False,
        'group_evidence':groups,
        'prose_evidence':[
            {'page':11,'section':'Diets','finding':'Fish diets mainly use FishBase; undefined bony-fish/finfish items are allocated by habitat and size; the author emphasizes uncertainty. Coastal prey of widespread predators use shelf-area shares; hilsa and mackerel use regional catch shares. No residual percentages or missing cell assignments are specified.'},
            {'page':19,'section':'Benthic invertebrates','finding':'Animal grouping, biomass estimates and PB/PQ assumptions; 25/75 crustaceans/macrobenthos split refers to biomass, not diet. No missing diet proportions.'},
            {'page':20,'section':'Zooplankton','finding':'Contains herbivorous and carnivorous taxa; biomass/PB/QB origins stated. No diet deficit completion.'},
            {'page':21,'section':'Balancing the model','finding':'AppendixA3.2 is initial diet; manual balancing changes unreliable biomass, PB and diets. No residual allocations.'},
            {'page':22,'section':'Balancing the model','finding':'Describes diet changes/biomass adjustments for carangid predation, benthos and cephalopod cannibalism. No quantitative repair of the deficient regional3 diets.'},
            {'pages':[50,51,52,53],'section':'A3.1','finding':'Lists diet source studies/species and FishBase references, not pooled missing percentages.'},
            {'pages':[55,56],'section':'A3.2','finding':'Repeats regional3 Detritus zeros and deficits. Regional2 analogues have nonzero detritus proportions.'}],
        'scenario_constraints':[
            'Preserve raw source matrix and authorized group40 override as current canonical input.',
            'Exact regional-analogy detritus completion38=.40,39=.55,41=.10 (and retained40=1) is a strong reconstruction scenario, not direct author group38–41 evidence.',
            'Fish32/33/36 detritus analogues are .0092/.0084/.0327; their residuals .0095/.0088/.0336 differ. Assigning exact residuals to detritus is additional inference.',
            'Indian mackerel30 residual .0548 has no region-specific paired predator analogue and no stated prey allocation.',
            'Any residual split among prey, or external Import assignment, needs a declared hypothesis; no source inference from row absence or mass balance alone.',
            'Completion scenarios should use separate identified inputs and compare results before normalization; do not overwrite raw source or change non-diet parameters silently.']}
    (OUT/'missing_diet_source_sweep.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'groups':groups,'quantitative_missing_diet_recovery_found':False}))

if __name__=='__main__':main()
