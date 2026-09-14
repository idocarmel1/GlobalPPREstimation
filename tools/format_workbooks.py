"""Apply readable Overview row heights without changing any workbook values."""
import argparse,math,os,tempfile,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

def format_overview(path):
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(path) as source:
        xml=ET.fromstring(source.read('xl/worksheets/sheet1.xml'))
        for row in xml.findall('m:sheetData/m:row',ns):
            cell=next((c for c in row if c.get('r','').startswith('B')),None)
            if cell is None or int(row.get('r'))<3:continue
            text=''.join(cell.itertext());row.set('ht',str(max(24,16*math.ceil(len(text)/95))));row.set('customHeight','1')
        fd,tmp=tempfile.mkstemp(suffix='.xlsx',dir=path.parent);os.close(fd)
        try:
            with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as out:
                for item in source.infolist():out.writestr(item,ET.tostring(xml,encoding='utf-8') if item.filename=='xl/worksheets/sheet1.xml' else source.read(item.filename))
            os.replace(tmp,path)
        finally:
            if os.path.exists(tmp):os.unlink(tmp)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);a=ap.parse_args()
    paths=sorted((a.root/'regions').glob('*/*.xlsx'))
    for p in paths:format_overview(p)
    print(f'Formatted {len(paths)} regional Overview sheets')
