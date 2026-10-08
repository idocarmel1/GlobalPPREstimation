"""Standalone offline report with embedded verified gzip data and no remote assets."""
from pathlib import Path
import hashlib,gzip,base64,json
ROOT=Path(__file__).resolve().parents[1]
def run():
    data=(ROOT/'results/report_data.v2.json').read_bytes()
    template=(ROOT/'src/report_template.html').read_text(encoding='utf-8')
    payload=base64.b64encode(gzip.compress(data,compresslevel=9,mtime=0)).decode('ascii')
    html=template.replace('__PAYLOAD__',payload).replace('__DATA_HASH__',hashlib.sha256(data).hexdigest())
    (ROOT/'report.html').write_text(html,encoding='utf-8')
    print('REPORT',len(html.encode()),'bytes; embedded data',len(data),'bytes')
if __name__=='__main__':run()
