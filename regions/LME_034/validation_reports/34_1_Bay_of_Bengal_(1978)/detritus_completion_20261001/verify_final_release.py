"""Verify the final generated pages and record their adopted workbook identity."""
import hashlib,json,subprocess,sys
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    integration=json.loads((OUT/'central_integration.json').read_text(encoding='utf-8'))
    assert sha(ROOT/'Project.xlsx')==integration['project_sha256'],'Central workbook changed during final HTML release'
    result=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'tools/verify_html.py'),
        '--workbook',str(ROOT/'Project.xlsx'),'--html',str(ROOT/'interactive_map/index.html')],
        cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    (OUT/'html_verification.txt').write_text(result.stdout+result.stderr,encoding='utf-8')
    print(result.stdout,end='',flush=True)
    if result.stderr: print(result.stderr,end='',flush=True)
    assert result.returncode==0,('Final HTML verification failed',result.returncode)
    assert sha(ROOT/'Project.xlsx')==integration['project_sha256'],'Central workbook changed during verification'
    integration['central_build_status']='final HTML built and verified'
    integration['html_project_fingerprint_verified']=True
    integration['generated_page_sha256']={name:sha(ROOT/'interactive_map'/name)
        for name in ['index.html','trends.html','archive/index.html']}
    (OUT/'central_integration.json').write_text(json.dumps(integration,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'final_release_verified':True,'project_sha256':integration['project_sha256'],
        'all_other_regional_records_exactly_unchanged':integration['all_other_regional_records_exactly_unchanged']}),flush=True)

if __name__=='__main__':main()
