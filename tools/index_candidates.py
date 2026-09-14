"""Index archived regional EwE candidates and their original extraction evidence."""
import argparse,json,shutil
from pathlib import Path
from workbooks import *

def index(root):
    p=read_book(root/'Project.xlsx');models=records(p,'Models & coverage','Models');added=0
    papers=records(p,'Papers','Papers')
    for region in sorted((root/'regions').iterdir()):
        if not region.is_dir():continue
        known={sha(f):f.parent.name for f in (region/'models').glob('*/model.json')}
        for source in sorted((region/'papers').rglob('*.json')):
            if any(part in ['work','raw_converter'] for part in source.relative_to(region/'papers').parts):continue
            try:d=json.loads(source.read_text(encoding='utf-8-sig'))
            except (ValueError,UnicodeError):continue
            if not isinstance(d,dict) or not isinstance(d.get('group'),list):continue
            h=sha(source);model=known.get(h);paper_id=source.relative_to(region/'papers').parts[0]
            paper=next((r for r in papers if r.get('unit_id')==region.name and r.get('source_article_id')==paper_id),{})
            if not model:
                model=source.stem if source.stem!='model' else source.parent.name
                dest=region/'models'/model/'model.json'
                if dest.exists() and sha(dest)!=h:model+='_'+h[:8];dest=region/'models'/model/'model.json'
                dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest);known[h]=model
                if not any(r['unit_id']==region.name and r['model_id']==model for r in models):
                    metadata={}
                    neutral=source.parent/'model.json'
                    if neutral.exists():
                        try:metadata=json.loads(neutral.read_text()).get('metadata',{})
                        except (ValueError,AttributeError):pass
                    models.append({'unit_id':region.name,'model_id':model,'model_path':dest.relative_to(root).as_posix(),'source_filename':source.name,'selected':False,'selection_rationale':None,'paper_ids':paper.get('article_id',paper_id),'model_year':metadata.get('model_year'),'variant':metadata.get('variant'),'model_area_km2':metadata.get('model_area_km2'),'availability':'archived candidate; not adopted by migration'})
                    added+=1
            record=next((r for r in models if r['unit_id']==region.name and r['model_id']==model),None)
            if record is not None:
                for k in ['publication_year','model_years','target_coverage_ratio','coverage_class','coverage_note','doi']:
                    if not record.get(k) and paper.get(k) is not None:record[k]=paper[k]
                if not record.get('paper_ids'):record['paper_ids']=paper.get('article_id',paper_id)
            if 'extracted' in source.parts:
                target=region/'models'/model/'extracted_tables';target.mkdir(exist_ok=True)
                for f in source.parent.iterdir():
                    if f.is_file() and f.suffix.lower() in ['.csv','.xlsx','.xls','.md','.txt','.json']:
                        to=target/f.name
                        if not to.exists():shutil.copy2(f,to)
    p['Models & coverage']['Models']=table_dict(models);write_book(root/'Project.xlsx',p)
    print(f'Indexed {len(models)} model/region candidates ({added} additional archived candidates); selections unchanged')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);a=ap.parse_args();index(a.root)
