import json, re, hashlib
from pathlib import Path
from decimal import Decimal
import pymupdf as fitz
import zipfile
from lxml import etree

out=Path(__file__).resolve().parent
region=out.parents[2]
project=region.parents[1]
source=region/'papers/GUI-2004/Palomares-et-al-west-africa-ecosystems-bd6604d6.pdf'
canonical=region/'models/28_646_Guinea_(1998)/model.json'
from functools import lru_cache
@lru_cache(None)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
model=json.loads(canonical.read_text(encoding='utf-8'))
groups={int(g['group_seq']):g for g in model['group']}
doc=fitz.open(source)
ledger=[]
for page_no in range(141,145):
    p=doc[page_no-1]
    p.set_rotation(90)
    words=[]
    for w in p.get_text('words'):
        box=list(fitz.Rect(w[:4])*p.rotation_matrix)
        words.append({'token':w[4],'bbox_original':list(w[:4]),'bbox_upright':box,'x':(box[0]+box[2])/2,'y':box[1]})
    headers=[w for w in words if w['token'].isdigit() and w['x']>170 and w['y']<115]
    # Header is the first complete 21-consumer row below the caption.
    byy={}
    for w in headers:byy.setdefault(round(w['y'],1),[]).append(w)
    candidates=[v for v in byy.values() if len(v)==21]
    assert len(candidates)==1,(page_no,byy)
    anchors={int(w['token']):w['x'] for w in candidates[0]}
    header_y=candidates[0][0]['y']
    rows=[w for w in words if w['token'].isdigit() and w['x']<100 and w['y']>header_y+5]
    print('page',page_no,'prey rows',[w['token'] for w in rows])
    for label in rows:
        prey=int(label['token']); assert 1<=prey<=45
        row_words=[w for w in words if abs(w['y']-label['y'])<0.7 and w['x']>170]
        assigned={}
        for w in row_words:
            consumer=min(anchors,key=lambda c:abs(anchors[c]-w['x']))
            assert abs(anchors[consumer]-w['x'])<12,(page_no,prey,w,consumer)
            assert consumer not in assigned,(page_no,prey,consumer,assigned.get(consumer),w)
            assert re.fullmatch(r'-|\d+(?:\.\d+)?',w['token']),w
            assigned[consumer]=w
        for c in sorted(anchors):
            w=assigned.get(c)
            token=w['token'] if w else ''
            value=Decimal(token) if token not in ['','-'] else Decimal(0)
            existing={int(d['prey_seq']):d['proportion'] for d in ((groups[c].get('diet_descr') or {}).get('diet') or []) if isinstance(d,dict)}
            old=groups[c]['diet_imp'] if prey==45 else existing.get(prey,'0')
            ledger.append({'consumer_seq':c,'consumer_name':groups[c]['group_name'],'prey_seq':prey,'prey_name':'Import' if prey==45 else groups[prey]['group_name'],
                           'source_file':str(source.relative_to(project)).replace('\\','/'),'source_sha256':sha(source),'table':'Tableau 8 balanced first line; italic second line is earlier original diet',
                           'pdf_page':page_no,'printed_page':page_no-4,'printed_token':token,'source_proportion':str(value),'source_absence':'dash' if token=='-' else 'blank' if token=='' else None,
                           'bbox_original':w['bbox_original'] if w else None,'bbox_upright':w['bbox_upright'] if w else None,'canonical_proportion':old,'exact_match':Decimal(old)==value,
                           'researcher_accepted_correction':None,'review_status':'pending_researcher_review'})
    p.get_pixmap(matrix=fitz.Matrix(2.5,2.5)).save(out/f'upright{page_no}.png')
assert len(ledger)==45*42,len(ledger)
by_consumer=[]
for c in range(1,43):
    cells=[x for x in ledger if x['consumer_seq']==c]
    source_total=sum((Decimal(x['source_proportion']) for x in cells),Decimal(0))
    old_total=sum((Decimal(x['canonical_proportion']) for x in cells),Decimal(0))
    deltas=[x for x in cells if not x['exact_match']]
    comparisons=[]
    for x in cells:
        s=Decimal(x['source_proportion']); o=Decimal(x['canonical_proportion'])
        if s: comparisons.append({'prey_seq':x['prey_seq'],'source':str(s),'canonical':str(o),'ratio_canonical_over_source':str(o/s)})
    by_consumer.append({'consumer_seq':c,'consumer_name':groups[c]['group_name'],'printed_total':str(source_total),'canonical_total':str(old_total),'different_cells':len(deltas),'nonzero_ratios':comparisons,
                        'printed_total_rounding_review':'unreviewed; total alone does not establish rounding','normalization_classification':'pending cell ratio/source revision assessment'})
(out/'native_diet_ledger.json').write_text(json.dumps({'source_sha256':sha(source),'canonical_sha256':sha(canonical),'cells':ledger,'per_consumer':by_consumer},indent=2,ensure_ascii=False),encoding='utf-8')
for c in by_consumer:
    print(c['consumer_seq'],c['consumer_name'],'printed',c['printed_total'],'canonical',c['canonical_total'],'diff',c['different_cells'])
    if c['consumer_seq'] in [1,5,9,21]: print(c['nonzero_ratios'])
z=zipfile.ZipFile(region/'Model_validation_28_646_Guinea_(1998).docx')
docx=etree.fromstring(z.read('word/document.xml'))
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
paras=[' '.join(p.xpath('.//w:t/text()',namespaces=ns)) for p in docx.xpath('.//w:p',namespaces=ns)]
(out/'researcher_edit_review.json').write_text(json.dumps({'docx_sha256':sha(region/'Model_validation_28_646_Guinea_(1998).docx'),'paragraphs_relevant':[p for p in paras if any(k in p.lower() for k in ['diet','manual','researcher','approval','extract'])], 'explicit_cell_corrections_found':[], 'reviewer_signoff':'not granted'},indent=2,ensure_ascii=False),encoding='utf-8')
