from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());r=ROOT/'regions/LME_049'
pairs={'KUR-2019_Western_North_Pacific_2013':'49_20192013_Western_North_Pacific_Watari_(2013)','KUR-2025_Kuroshio_Oyashio_Extension_2023':'49_20252023_Kuroshio_Oyashio_Extension_Chen_(2023)'}
files=[p for p in (r/'models').rglob('*') if p.suffix in ['.json','.csv','.md','.txt','.log','.py'] and 'diagnostic_code' not in p.parts and p.name not in ['model.json','update_candidate_ids.py']]+[r/'papers'/k/'metadata.json' for k in ['KUR-2019','KUR-2025']]
for p in files:
    original=p.read_text(encoding='utf-8');changed=original
    for old,new in pairs.items():changed=changed.replace(old,new)
    if p.suffix=='.py':changed=changed.replace("REG.glob('models/KUR-*')","REG.glob('models/49_*')")
    if original!=changed:p.write_text(changed,encoding='utf-8')
