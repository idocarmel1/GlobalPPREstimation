"""Verify original layouts and current workbook data in the generated atlas pages."""
import argparse,json,math,re
from pathlib import Path
from workbooks import sha,read_book,records
from original_atlas_data import embedded,branch
from build_html import linked_layout

def verify(workbook,html):
    directory=html.parent if html.suffix=='.html' else html
    templates=Path(__file__).with_name('original_html_layout');fingerprint=sha(workbook)
    pages={}
    for filename,variable in [('index.html','DB'),('trends.html','SERIES_DB')]:
        path=directory/filename;data,layout=embedded(path,variable)
        marker=f'<meta name="ppr-project-sha256" content="{fingerprint}">'
        assert marker in layout,f'{filename}: stale project-workbook fingerprint'
        assert layout.replace(marker,'')==linked_layout((templates/filename).read_text()),f'{filename}: layout or JavaScript differs from original template beyond allowed file-link updates'
        pages[filename]=data
    b=read_book(workbook);ts=pages['trends.html'];checks=0
    for r in records(b,'Regional PPR','Annual'):
        u=ts['units'][r['unit_id']]
        if not r['model_id']:record=u['simple']
        else:
            model=next(m for m in u['models'] if m['id']==r['model_id'])
            record=model['scopes'][r['scope']]['methods'][r['method']]
        target=branch(record,r['unidentified'],r['catch_basis']);metric=r['metric']
        values=[target.get('sensitivity',[{}]*70)[i].get(metric) for i in range(70)] if metric in ['min_tC','max_tC'] else target[metric]
        for y,v in zip(range(1950,2020),values):
            assert v==r[y],(r['unit_id'],r['method'],metric,y,v,r[y]);checks+=1
    for r in records(b,'Regional NPP','NPP'):
        values=ts['units'][r['unit_id']]['npp'][r['method']]
        assert values==[r[y] for y in range(1950,2020)]
        assert pages['index.html']['network']['npp'][r['unit_id']][r['method']]==values
    for r in records(b,'Regions & status','Regions'):
        assert ts['units'][r['unit_id']]['default_model']==r['selected_model_id']
    assert (directory/'archive/index.html').is_file()
    for a in pages['index.html']['articles']:
        for f in a.get('material_files',[]):
            assert (directory/f['relative_path']).is_file(),f['relative_path']
    assert (directory/'data/unidentified_taxa.json').is_file()
    print(f'Original map/time-series layouts and JavaScript match (only file links updated); {checks} annual cells and NPP match Project.xlsx; selected models, source files and archive page verified')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--workbook',type=Path,required=True);ap.add_argument('--html',type=Path,required=True);a=ap.parse_args();verify(a.workbook.resolve(),a.html.resolve())
