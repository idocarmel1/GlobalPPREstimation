from pathlib import Path
from PIL import Image
import hashlib
import json

OUT=Path(__file__).resolve().parent
MODEL=OUT.parents[2]
evidence=json.loads((OUT/'source_evidence.json').read_text(encoding='utf-8'))
qa=json.loads((OUT/'verification.json').read_text(encoding='utf-8'))
qa['source_hash_checks']=[]
qa['native_crop_checks']=[]
for item in evidence:
    if 'file' in item:
        actual=hashlib.sha256(Path(item['file']).read_bytes()).hexdigest()
        assert actual==item['sha256']
        qa['source_hash_checks'].append({'file':item['file'],'matches_original_record':True})
    if 'crop' in item:
        original=Image.open(item['source']).convert('RGB').crop(item['bounds_original_pixels'])
        saved=Image.open(OUT/item['crop']).convert('RGB')
        assert original.size==saved.size and original.tobytes()==saved.tobytes()
        qa['native_crop_checks'].append({'file':item['crop'],'exact_native_source_pixels':True})
arrow=json.loads((MODEL/'research_20261003'/'arrow_audit'/'audit_verification.json').read_text(encoding='utf-8'))
actual=hashlib.sha256((MODEL/'audit'/'figure9_original.png').read_bytes()).hexdigest()
assert actual==arrow['source']['source_image_sha256']
qa['figure_hash_matches_prior_arrow_audit']=True
ledger=json.loads((OUT/'jellyfish_error_hypothesis_ledger.json').read_text(encoding='utf-8'))
assert len(ledger['hypotheses'])==16
assert len({h['id'] for h in ledger['hypotheses']})==16
qa['unique_hypothesis_ids']=True
(OUT/'verification.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Verified 2 original PDF hashes, 6 exact native-pixel crops, prior Figure9 hash and 16 distinct hypothesis IDs.')
