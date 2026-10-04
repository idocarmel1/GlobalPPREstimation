"""Native Word PDF pagination/format comparison and affected-page PNGs only."""
from pathlib import Path
import hashlib, json, subprocess
import pdfplumber
from PIL import Image
from lxml import etree
from patch_and_prove import CHANGES, ROOT, EVIDENCE, NS

POPPLER = Path(r'C:\Users\idoca\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe')
def sha_bytes(data): return hashlib.sha256(data).hexdigest()
def sha_file(path): return sha_bytes(path.read_bytes())
def norm(text): return ' '.join(text.split())
def character_proof(page):
    keys = ('text','x0','x1','top','bottom','fontname','size','non_stroking_color')
    return [{k:round(c[k],4) if isinstance(c[k],float) else c.get(k) for k in keys} for c in page.chars]
def blue_text(page):
    return ''.join(c['text'] for c in page.chars if isinstance(c.get('non_stroking_color'),(list,tuple)) and len(c['non_stroking_color'])==3 and c['non_stroking_color'][2] > c['non_stroking_color'][0]+0.25)

proof = json.loads((EVIDENCE/'patch_proof.json').read_text())
output = {'renderer': 'Retained LME038 native Word owned hidden read-only export helper; bundled Poppler PNG rasterization and bundled pdfplumber layout extraction',
          'helper_path': 'regions/LME_038/validation_reports/38_38003_Java_Sea_normalized_BA_completed_(mid1970s)/reproduction/render_word.ps1',
          'poppler_path':str(POPPLER),'raster_dpi': 144, 'requested_visual_scope': 'Page 1 for five documents; page 2 for LME038', 'files': []}
for item in proof['files']:
    unit = item['unit']
    before_pdf = EVIDENCE/'render'/unit/'before'/'report.pdf'
    after_pdf = EVIDENCE/'render'/unit/'after'/'report.pdf'
    before, after = pdfplumber.open(before_pdf), pdfplumber.open(after_pdf)
    assert len(before.pages) == len(after.pages), f'Page count regression: {unit}'
    old, new = CHANGES[unit]
    selected = 2 if unit == 'LME_038' else 1
    pages = []
    replacements = 0
    for i,(bp,ap) in enumerate(zip(before.pages,after.pages)):
        btext, atext = norm(bp.extract_text() or ''), norm(ap.extract_text() or '')
        n = btext.count(old)
        replacements += n
        assert btext.replace(old,new) == atext, f'Page content or pagination changed: {unit} page {i+1}'
        assert (bp.width,bp.height) == (ap.width,ap.height)
        bl,al = bp.hyperlinks,ap.hyperlinks
        links_before = sorted(x.get('uri') or '' for x in bl)
        links_after = sorted(x.get('uri') or '' for x in al)
        assert links_before == links_after, f'Exported PDF hyperlink targets changed: {unit} {i+1}'
        blue_before,blue_after = blue_text(bp),blue_text(ap)
        assert norm(blue_before) == norm(blue_after), f'Blue link text changed: {unit} {i+1}'
        bchars,achars = character_proof(bp),character_proof(ap)
        char_exact = bchars == achars
        assert n or char_exact, f'Unchanged page character geometry changed: {unit} {i+1}'
        page_info = {'page': i+1, 'text_content_exact_except_authorized_wording': True, 'authorized_replacement_on_page': n,
                     'same_page_dimensions': True, 'character_text_geometry_and_color_exact': char_exact,
                     'before_character_sha256':sha_bytes(json.dumps(bchars,sort_keys=True).encode()),
                     'after_character_sha256':sha_bytes(json.dumps(achars,sort_keys=True).encode()),
                     'exported_hyperlink_targets_exact': True, 'exported_hyperlink_count':len(bl),
                     'blue_link_text_exact': True, 'blue_link_char_count_before':len(blue_before), 'blue_link_char_count_after':len(blue_after)}
        if i+1 == selected:
            for phase,pdf in [('before',before_pdf),('after',after_pdf)]:
                p = EVIDENCE/'render'/unit/phase/f'page-{selected}.png'
                subprocess.run([str(POPPLER),'-png','-r','144','-f',str(selected),'-l',str(selected),'-singlefile',str(pdf),str(p.with_suffix(''))],check=True,capture_output=True)
                assert p.exists()
                page_info[f'{phase}_png'] = str(p.relative_to(ROOT))
                page_info[f'{phase}_png_sha256'] = sha_file(p)
        pages.append(page_info)
    assert replacements == 1, f'Expected one rendered wording occurrence: {unit}, got {replacements}'
    final_docx = ROOT/item['path']
    assert sha_file(final_docx) == item['after_sha256']
    before_tree = etree.fromstring((EVIDENCE/'xml'/f'{unit}.before.document.xml').read_bytes())
    after_tree = etree.fromstring((EVIDENCE/'xml'/f'{unit}.after.document.xml').read_bytes())
    hyperlinks = []
    for b,a in zip(before_tree.findall('.//w:hyperlink',NS),after_tree.findall('.//w:hyperlink',NS)):
        assert etree.tostring(b) == etree.tostring(a)
        texts = ''.join(t.text or '' for t in b.findall('.//w:t',NS))
        styles = [p.get('{'+NS['w']+'}val') for p in b.findall('.//w:rStyle',NS)]
        colors = [p.get('{'+NS['w']+'}val') for p in b.findall('.//w:color',NS)]
        underlines = [p.get('{'+NS['w']+'}val') for p in b.findall('.//w:u',NS)]
        hyperlinks.append({'text':texts,'run_styles':styles,'direct_colors':colors,'direct_underlines':underlines,'xml_exact':True})
    output['files'].append({'unit':unit,'path':item['path'],'final_sha256':item['after_sha256'],
        'before_page_count':len(before.pages),'after_page_count':len(after.pages),'pagination_preserved':True,
        'each_page_text_exact_except_authorized_wording':True,
        'inspected_page':selected,'visual_inspection_pending':True,'pages':pages,
        'hyperlink_appearance_xml_exact':hyperlinks,
        'before_pdf_sha256':sha_file(before_pdf),'after_pdf_sha256':sha_file(after_pdf)})
    print(unit,'pages',len(after.pages),'changed character geometry pages',[x['page'] for x in pages if not x['character_text_geometry_and_color_exact']],flush=True)
    before.close(); after.close()
(EVIDENCE/'render_comparison.json').write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
