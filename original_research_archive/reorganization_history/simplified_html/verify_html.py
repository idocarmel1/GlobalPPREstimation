"""Check the standalone payload and source-workbook identity without a browser."""
import argparse,base64,json,re,zlib
from pathlib import Path
from workbooks import sha,read_book,rows

def verify(workbook,html):
    text=html.read_text();match=re.search(r"const EMBEDDED='([A-Za-z0-9+/=]+)';",text)
    if not match:raise ValueError('Embedded payload absent')
    data=json.loads(zlib.decompress(base64.b64decode(match[1])))
    if data['workbook_sha256']!=sha(workbook):raise ValueError('HTML belongs to an older project workbook')
    project=read_book(workbook)
    assert data['annual']==rows(project,'Regional PPR','Annual')
    assert data['npp']==rows(project,'Regional NPP','NPP')
    assert data['common']==rows(project,'Method comparisons','Common catch totals')
    assert len(data['regions'])==len(rows(project,'Regions & status','Regions'))
    assert not re.search(r'<(?:script|img|iframe)[^>]+src\s*=|<link[^>]+href\s*=',text,re.I)
    print(f'HTML payload verified: {len(data["regions"])} regions; current workbook hash; no external script/style/image resources')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--workbook',type=Path,required=True);ap.add_argument('--html',type=Path,required=True);a=ap.parse_args();verify(a.workbook,a.html)
