"""Scientific calculation identity used for safe completed-run reuse."""
from pathlib import Path
import hashlib,json
from baseline import ROOT,FRACTIONS,SETTINGS,METHODS,SCOPES
def fingerprint(input_path):
    files=list((ROOT/'src/experimental_engine').glob('*.py'))+[ROOT/'src'/x for x in ['baseline.py','scenarios.py','ledger.py','metrics.py','run_study.py']]
    data=dict(source_json_sha256=hashlib.sha256(Path(input_path).read_bytes()).hexdigest(),fractions=FRACTIONS,settings=SETTINGS,methods=METHODS,scopes=SCOPES,
        code_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    data['calculation_sha256']=hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
    return data
