from pathlib import Path
import re, json, hashlib
from pypdf import PdfReader
from PIL import Image
from support import TABLE1,TABLE2,TABLE3,FIG9_NODES

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'gorbatenko_melnikov_2019.pdf'
OUTPUT=HERE.parent/'gorbatenko_melnikov_2019_English_translation.pdf'
source=PdfReader(SOURCE);output=PdfReader(OUTPUT)
checks=json.loads((HERE/'verification.json').read_text(encoding='utf8'))
numeric=re.compile(r'(?<![\w])\d+(?:[,.]\d+)?')
def rownums(line):return [s.replace(',','.') for s in numeric.findall(line)]
def verify_table(page,begin,end,expected,count):
    txt=source.pages[page-143].extract_text()
    txt=txt[txt.index(begin):txt.index(end)]
    rows=[]
    for line in txt.splitlines():
        vals=rownums(line)
        if len(vals)>=count:rows.append(vals[-count:])
    want=[r[-count:] for r in expected]
    assert rows==want,(page,rows,want)
    return {'numeric_cells':count*len(rows),'rows':len(rows),'exact_decimal_strings_match':True}
checks['numeric_table_verification']={
    'Table 1':verify_table(148,'Эвфаузииды','Примечание',TABLE1,12),
    'Table 2':verify_table(149,'Весь зоопланктон','По потреблению',TABLE2,3),
    'Table 3':verify_table(154,'Фитопланктон','* Прочие',TABLE3,8),
}
original=source.pages[14].images[0].image.convert('RGB')
preserved=Image.open(HERE/'figure_9_original.png').convert('RGB')
checks['figure9_image_identical_decoded_rgb']=original.size==preserved.size and original.tobytes()==preserved.tobytes()
assert checks['figure9_image_identical_decoded_rgb']
checks['figure9_decoded_size']=list(original.size)
checks['figure9_node_key']=FIG9_NODES
checks['source_sha256']=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
assert checks['source_sha256']==json.loads((HERE/'source_inventory.json').read_text(encoding='utf8'))['sha256']
checks['output_size_bytes']=OUTPUT.stat().st_size
checks['source_page_provenance_in_output']=all(f'Original page {n} (source PDF page {n-142})' in '\n'.join(p.extract_text() for p in output.pages) for n in range(143,164))
checks['figure9_english_page']=next(i+1 for i,p in enumerate(output.pages) if 'Figure 9. Energy flows' in p.extract_text())
checks['table3_english_page']=next(i+1 for i,p in enumerate(output.pages) if 'Table 3. Principal production' in p.extract_text())
checks['visual_review']='Every final page rendered and reviewed in contact sheets; full-page inspection of Table 3, Figure 8 key, Figure 9 and node key. No clipped table cells, missing source graphs, overlaid text or unreadable glyphs found.'
checks['translation_scope']='All main text, Russian and published English abstracts, 3 tables, 10 figures with captions and English keys, author footnote, 52 translated Russian bibliography entries and 52 published English references, funding/ethics/author statements and submission dates.'
checks['caveats']=['Unofficial AI-assisted translation, not author-approved.','Original figure graphics retain Russian labels; adjacent English keys translate them.','Original scientific and numerical inconsistencies are preserved, not corrected.','Carbon biomass header in Table 3 includes /year as printed.','Figure 9 ambiguous or overprinted arrow labels are preserved graphically without supplied interpretations.']
(HERE/'verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(checks,ensure_ascii=False,indent=2))
