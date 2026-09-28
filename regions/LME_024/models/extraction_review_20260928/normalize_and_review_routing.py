from pathlib import Path
from decimal import Decimal, getcontext
import copy, hashlib, json, sys

getcontext().prec = 40
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
SOURCE = OUT.parent / 'Hernvann_2020_Celtic_Sea_1985' / 'model.json'
DEST = OUT / 'authorized_diet_normalization'
DEST.mkdir(exist_ok=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = sha(SOURCE)
original = json.loads(SOURCE.read_text(encoding='utf8'))
model = copy.deepcopy(original)
changes = []
for group in model['group']:
    if int(group['group_seq']) > 50:
        continue
    entries = group['diet_descr']['diet']
    known = [e for e in entries if Decimal(e['proportion']) >= 0]
    imp = Decimal(group['diet_imp'])
    total = sum((Decimal(e['proportion']) for e in known), Decimal(0)) + max(imp, Decimal(0))
    if total != 1:
        for e in known:
            e['proportion'] = str(Decimal(e['proportion']) / total)
        if imp >= 0:
            group['diet_imp'] = str(imp / total)
    after = sum((Decimal(e['proportion']) for e in known), Decimal(0)) + max(Decimal(group['diet_imp']), Decimal(0))
    assert abs(after - 1) < Decimal('1e-35')
    changes.append({'group': group['group_seq'], 'name': group['group_name'], 'source_sum': str(total), 'normalized_sum': str(after), 'factor': str(1/total)})

# Verify that only the authorized diet proportions and known diet imports changed.
restored = copy.deepcopy(model)
for a,b in zip(restored['group'], original['group']):
    a['diet_descr'] = b['diet_descr']
    a['diet_imp'] = b['diet_imp']
assert restored == original
path = DEST / '24_2402020_Celtic_Sea_Hernvann_Diet_Normalized_(1985).json'
path.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding='utf8')
removals = {53: Decimal(0), 54: Decimal(0)}
for g in model['group'][:50]:
    q = Decimal(g['biomass']) * Decimal(g['qb'])
    for entry in g['diet_descr']['diet']:
        prey = int(entry['prey_seq'])
        if prey in removals and Decimal(entry['proportion']) >= 0:
            removals[prey] += q * Decimal(entry['proportion'])
input_data = json.loads((OUT/'extraction_input.json').read_text(encoding='utf8'))
result = {'source_sha256':before, 'normalized_sha256':sha(path), 'authorization':'User authorized diet normalization only; no routing, pooling, or biological parameter changes.', 'columns':changes, 'detritus_consumer_removals':{str(k):str(v) for k,v in removals.items()}, 'published_B3_discard_sum':'0.2559104', 'published_discard_BA_rate_times_B':'0.1000', 'conditional_discard_budget_gap':str(removals[53]+Decimal('0.1')-Decimal('0.2559104'))}
sys.path.insert(0, str(ROOT/'tools/scientific_code/PPREstimation'))
from ModelData import ModelData
from PPRCalculator import PPRCalculator
try:
    calc = PPRCalculator.from_modeldata(ModelData(str(path)),zero_catch=True,zero_biomass_accum=True,default_gs=True,normalize_DC=False)
    result['constructor'] = {'status':'LOADED'}
except Exception as exc:
    result['constructor'] = {'status':'NOT_LOADED','exception_type':type(exc).__name__,'exception':str(exc)}
assert sha(SOURCE) == before
result['source_unchanged'] = True
result['only_authorized_fields_changed'] = True
(DEST/'NORMALIZATION_AND_ROUTING_CHECK.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k != 'columns'},indent=2))
