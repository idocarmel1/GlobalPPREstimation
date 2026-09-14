"""Render a genuinely offline SVG map and graphs using Project.xlsx alone."""
import argparse, base64, json, zlib, os, tempfile
from pathlib import Path
from workbooks import *

def payload(path):
    b=read_book(path)
    # Compact transport contains regional values only, never taxon data.
    p={
      'regions':records(b,'Regions & status','Regions'),
      'papers':records(b,'Papers','Papers'),
      'models':records(b,'Models & coverage','Models'),
      'annual':rows(b,'Regional PPR','Annual'),
      'npp':rows(b,'Regional NPP','NPP'),
      'nppProvenance':rows(b,'Regional NPP','Provenance'),
      'pairs':rows(b,'Method comparisons','Pairs'),
      'common':rows(b,'Method comparisons','Common catch totals'),
      'diagnostics':records(b,'Diagnostics & sensitivity','Diagnostics'),
      'geometry':unchunks(rows(b,'Map geography','Geometry')),
      'meta':unchunks(rows(b,'Definitions & build','Metadata')),
      'workbook_sha256':sha(path)}
    if len({r['unit_id'] for r in p['regions']})!=len(p['regions']):raise ValueError('Duplicate project region')
    return p

def build(path,out):
    p=payload(path);template=Path(__file__).with_name('atlas_template.html').read_text()
    encoded=base64.b64encode(zlib.compress(json.dumps(p,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode(),9)).decode()
    html=template.replace('__PAYLOAD__',encoded)
    out.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=out.parent,suffix='.html');os.close(fd)
    try:Path(tmp).write_text(html,encoding='utf-8');os.replace(tmp,out)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    print(f'Offline atlas: {len(p["regions"])} regions; {out.stat().st_size/1e6:.1f} MB')
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--workbook',type=Path,default=Path(__file__).resolve().parents[1]/'Project.xlsx');ap.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'interactive_map/atlas.html');a=ap.parse_args();build(a.workbook,a.output)
