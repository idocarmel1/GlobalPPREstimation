"""Final cross-package identity, consumed-source and local-link closure checks."""
import hashlib,json,re,sys,zipfile
from pathlib import Path
from urllib.parse import unquote
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
RUN=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.project_core.validation.researcher_review import table_rows,read_report
STUDIES=[ROOT/'research/human'/name for name in [
    'sppr_trophic_level_20261018_validated7',
    'ppr_taxonomic_resolution_20261018_validated7',
    'ppr_taxonomic_resolution_GE_20261018_validated7']]
AGG=ROOT/'regions/LME/LME_028/work/2026-10-18_121535_trophic_aggregation_validated7'
cache={}
def sha(p):
    if p not in cache:
        h=hashlib.sha256()
        with p.open('rb') as stream:
            for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
        cache[p]=h.hexdigest()
    return cache[p]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
registration=read(RUN/'qa/registration_verification.json')
assert sha(ROOT/'Project.xlsx')==registration['project_sha256']
target=('LME_028','28_646_Guinea_(1998)')
report=ROOT/'regions/LME/LME_028/papers/GUI-2004/models/28_646_Guinea_(1998)/model_validation/validation.docx'
assert sha(report)==registration['report_sha256']
name,date,review=read_report(ROOT,report,target[1])
assert (name,date,review['status'])==('Ido Carmel','2026-10-18','Disqualified by researcher')
assert review['sections']==[] and review['reason']==registration['reason']
with zipfile.ZipFile(ROOT/'Project.xlsx') as z:
    rows=[r for _,r in table_rows(z,'Models & coverage','Models')[3]]
positive={(r['unit_id'],r['model_id']) for r in rows if r.get('researcher_review_status')=='Validated by researcher'}
assert positive=={tuple(p) for p in registration['positive_pairs']} and len(positive)==7
cohort_bytes=(STUDIES[0]/'inputs/cohort.json').read_bytes()
cohort=read(STUDIES[0]/'inputs/cohort.json')
assert {(r['unit_id'],r['model_id']) for r in cohort['pairs']}==positive
assert cohort['project_sha256']==sha(ROOT/'Project.xlsx')
for row in cohort['pairs']+cohort['excluded_pairs']:
    assert sha(ROOT/row['validation_report_path'])==row['validation_report_sha256']
packages=[]
for study in STUDIES:
    assert (study/'inputs/cohort.json').read_bytes()==cohort_bytes
    ledger=read(study/'inputs/source_hashes.json')
    for rel,item in ledger.items():
        expected=item if isinstance(item,str) else item['sha256']
        assert sha(ROOT/rel)==expected,('Stale study source',str(study),rel)
    packages.append({'path':study.relative_to(ROOT).as_posix(),'source_hashes_verified':len(ledger)})
assert (AGG/'inputs/cohort.json').read_bytes()==cohort_bytes
links=0
for folder in [*STUDIES,AGG]:
    for document in folder.glob('*.md'):
        for reference in re.findall(r'\]\(([^\n]+?)\)',document.read_text(encoding='utf-8')):
            if reference.startswith(('https:','http:','#','mailto:')):continue
            destination=unquote(reference.split('#',1)[0].strip('<>'))
            assert (document.parent/destination).exists(),('Broken link',document,reference)
            links+=1
for page,item in registration['pages'].items():
    assert sha(ROOT/'interactive_map'/page)==item['sha256']
result={'signed_review_current':True,'exact_current_validated_pairs':sorted(positive),
        'identical_cohort_manifests':4,'packages':packages,'local_document_links_verified':links,
        'published_views_unchanged_since_registration_verification':True,
        'unique_consumed_files_rehashed':len(cache)}
(RUN/'qa/current_research_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
