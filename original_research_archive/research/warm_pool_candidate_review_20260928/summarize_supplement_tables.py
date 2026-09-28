import json,re
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
review=ROOT/'regions/EEZ_941/models/941_201901_Warm_Pool_(2005)/source_review'
data=json.loads((review/'SUPPLEMENT_XML_EVIDENCE.json').read_text(encoding='utf-8'))
for ti in (0,3,4,5):
    print('TABLE',ti+1)
    for ri,row in enumerate(data['tables'][ti],1):
        if ti==0:
            if row[0]['text'].strip():print('MEMBERSHIP',ri,row[0]['text'])
            for c in row:
                if re.search('assimil|egest|detrit|accumul|migrat|import|export|discard',c['text'],re.I):print('PROSE',ri,c['text'])
        elif ti in (3,4) and ri<46:continue
        else:print(ri,' | '.join(f"{c['grid_start']}:{c['text'].strip()}" for c in row))
