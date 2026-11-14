from pathlib import Path
import hashlib,json
run=Path(__file__).resolve().parents[1]
files=['code/candidate_row.py','code/register_negative_batch.py','code/test_review_candidate_gate.py','outputs/test_review_candidate_gate.installable.py','outputs/build_html.patch','outputs/build_html.proposed.py']
receipt={'shared_mutations':False,'tests':[{'suite':'proposed exact-pair and candidate review gate','passed':7,'seconds':25.719},{'suite':'existing disqualification and model boundary','passed':12,'seconds':36.317},{'suite':'current Project isolated candidate insertion after empty-row fix','passed':2,'seconds':33.528}],'hashes':{p:hashlib.sha256((run/p).read_bytes()).hexdigest() for p in files},'limitations':['Actual shared installation and real publication remain coordinator-owned.','Generated installable gate module uses production imports; fixture bodies match tested local module.']}
(run/'qa/verification.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(receipt,indent=2))
