"""Snapshot the two source projects without changing either one."""
from pathlib import Path
import csv, hashlib, json, shutil
import openpyxl

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent/'simple_PPR_global/Global_history_TE010_2026-09-04'

def main():
    target = ROOT/'inputs'
    target.mkdir(exist_ok=True)
    sources = {
        'PPR_global_summary.xlsx': SOURCE/'PPR_global_summary.xlsx',
        'selected_regions.geojson': SOURCE/'spatial/selected_regions.geojson',
        'selected_regions.csv': SOURCE/'tables/selected_regions.csv',
        'annual_regions.csv': SOURCE/'tables/annual_regions.csv',
        'original_map.html': Path.home()/'Downloads/ecopath_all84_interactive_map (3).html',
    }
    manifest = []
    for name, source in sources.items():
        dest = target/name
        if not dest.exists():
            shutil.copy2(source,dest)
        manifest.append({'file':name,'source':str(source),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
    (target/'provenance.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    text = (target/'original_map.html').read_text(encoding='utf-8')
    db = json.JSONDecoder().raw_decode(text.split('const DB=',1)[1])[0]
    (target/'original_catalog.json').write_text(json.dumps(db,ensure_ascii=False),encoding='utf-8')
    workbook = openpyxl.load_workbook(target/'PPR_global_summary.xlsx',read_only=True,data_only=True)
    sheet = workbook['Global Estimation']
    rows = list(sheet.values)
    headers = rows[9]
    selected = [dict(zip(headers,row)) for row in rows[10:] if row[0] and str(row[0]).startswith(('LME_','EEZ_','HS_'))]
    data = {'year':sheet['B3'].value,'total_ppr':sheet['B5'].value,'regions':selected}
    (target/'global_estimation.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    geometry = json.loads((target/'selected_regions.geojson').read_text(encoding='utf-8'))
    print('Selected',len(selected),'year',data['year'],'polygons',len(geometry['features']))
    print('Geometry properties', geometry['features'][0]['properties'])

if __name__=='__main__':
    main()
