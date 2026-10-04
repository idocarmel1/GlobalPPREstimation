from pathlib import Path
import json
from baseline import ROOT
from summarize import saved_checks
for p in sorted((ROOT/'results/models').glob('*/study.json')):
    s=saved_checks(json.loads(p.read_text(encoding='utf-8')))
    failed=[x for x in s['baseline_checks'] if x.get('passed') is False]
    print(p.parent.name,len(s['baseline_checks']), 'FAILED',failed,flush=True)
