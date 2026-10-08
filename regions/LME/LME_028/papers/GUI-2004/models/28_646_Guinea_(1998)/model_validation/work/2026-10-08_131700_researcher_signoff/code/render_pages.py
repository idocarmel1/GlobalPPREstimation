from pathlib import Path
import pypdfium2 as pdfium
run=Path(__file__).resolve().parent.parent
pdf=pdfium.PdfDocument(run/'qa/report.pdf')
for i,page in enumerate(pdf):
    page.render(scale=1.5).to_pil().save(run/f'qa/page-{i+1}.png')
    (run/f'qa/page-{i+1}.txt').write_text(page.get_textpage().get_text_range(),encoding='utf-8')
print(f'Rendered {len(pdf)} pages')
