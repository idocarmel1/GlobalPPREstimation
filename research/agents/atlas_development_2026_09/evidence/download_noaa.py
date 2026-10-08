"""Retrieve MHI model tables through NOAA's published public FTP archive."""
from pathlib import Path
from io import BytesIO
import ftplib,json
from atlas.files import save_material

root=Path(__file__).resolve().parent
destination=root/'research/downloads/MHI-2021.json'
result=json.loads(destination.read_text(encoding='utf-8')) if destination.exists() else {'article_id':'MHI-2021','files':[],'attempts':[]}
host='ftp-oceans.ncei.noaa.gov';directory='/nodc/archive/arc0186/0240824/1.1/data/0-data'
with ftplib.FTP(host,timeout=30) as ftp:
    ftp.login();ftp.cwd(directory)
    for filename in ftp.nlst():
        if not filename.lower().endswith('.csv'):continue
        url=f'ftp://{host}{directory}/{filename}'
        if any(f['source_url']==url for f in result['files']):continue
        role='model_files' if filename.startswith('Table') else 'supplements'
        attempt={'article_id':'MHI-2021','url':url,'role':role,'attempted_on':'2026-09-04'}
        try:
            stream=BytesIO();ftp.retrbinary('RETR '+filename,stream.write)
            record=save_material(root,stream.getvalue(),'.csv')
            record.update(article_id='MHI-2021',role=role,source_url=url,filename=filename,retrieval_origin='NOAA public FTP')
            result['files'].append(record);attempt.update(result='downloaded_verified',size_bytes=len(stream.getvalue()))
        except Exception as exc:attempt.update(result='failed',error=str(exc))
        result['attempts'].append(attempt)
        destination.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
        print(filename,attempt['result'],flush=True)
