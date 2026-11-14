import hashlib, json, sys, zipfile
from pathlib import Path
from lxml import etree as E

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
RUN = Path(__file__).resolve().parents[1]
VAL = RUN.parents[1]
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert (ROOT/'Project.xlsx').exists(), ROOT
protected = [ROOT/'Project.xlsx', ROOT/'regions/LME/LME_014/LME_014.xlsx', VAL.parent/'model.json', VAL.parent/'model_notes.md', ROOT/'tools/templates/validation.docx']
protected += [ROOT/'interactive_map'/n for n in ['index.html','trends.html','sources.html']]
protected += [p for p in (VAL.parent/'results').rglob('*') if p.is_file()]
(RUN/'qa/protected_before.json').write_text(json.dumps({p.relative_to(ROOT).as_posix():sha(p) for p in protected if p.exists()},indent=2),encoding='utf-8')
def inventory(p):
    with zipfile.ZipFile(p) as z:
        return {n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()}
(RUN/'qa/package_before.json').write_text(json.dumps(inventory(RUN/'inputs/validation_before.docx'),indent=2),encoding='utf-8')
with zipfile.ZipFile(RUN/'inputs/validation_before.docx') as z:
    doc=E.fromstring(z.read('word/document.xml'))
    manual={}
    for row in doc.findall('.//w:tbl/w:tr',NS):
        cells=row.findall('w:tc',NS)
        if len(cells)==2:
            label=''.join(cells[0].itertext())
            if label in ['SPPR calculation','Open issues and next action','Review and reproducibility']:
                manual[label]=E.tostring(row).decode()
(RUN/'qa/manual_before.json').write_text(json.dumps(manual,indent=2),encoding='utf-8')
(RUN/'artifact.md').write_text(f'''# Validation report template contract

Reference: {ROOT/'tools/templates/validation.docx'}
SHA256: {sha(ROOT/'tools/templates/validation.docx')}
Rendered with isolated hidden read-only Word after bundled LibreOffice was found unavailable; 3 pages inspected at full readable resolution in qa/template_render.

A4 portrait 8.27014 x 11.69028 inches, 0.65 inch margins. Calibri 11 normal with 5pt after; Title 23 with 8pt after; Heading1 17 and Heading2 12, both 8pt after. Restrained pale-blue table header, fixed grid, repeat headers. Main two columns 1.52986 and 5.44028 inches. Main table flows with full field order from Region through Review and reproducibility; SPPR follows GE/TE. Separate coverage, rule tables and Very low decisions follow; figures conclude. All new table percentages use two significant digits. Long Very low taxon lists may be split into contiguous groups with identical reasons to retain readable non-splitting rows.

Update existing report in place with current template structure. Preserve all existing package parts except word/document.xml and its hyperlink relationships. Preserve all three manual rows as exact XML, images, geometry, styles, authored content not superseded by verified findings, and useful links. Existing manual placeholders remain unsigned. Slots changed: title, article alternatives/rationale, source/version wording, GE/TE to independently identified ON diagnostics, Other configuration qualifier, concise coverage wording, exact current table headers/percentage displays, Very low reasons, geography captions and missing/broken portable links. All 250 appendix taxa and scientific data remain unchanged.

Report-only review: no registration or Project/regional/map/trends mutation. Final page and link QA plus manual XML preservation and protected hash checks are required. Unsigned parser rejection remains expected before and after; no researcher identity/date/verdict is introduced.
''',encoding='utf-8')
print('Captured protected hashes, manual rows, package baseline and template contract')
