from pathlib import Path
import sys
import pypdfium2 as pdfium
pdf_path=Path(sys.argv[1])
pdf=pdfium.PdfDocument(pdf_path)
for i in range(len(pdf)):
    page=pdf[i]
    bitmap=page.render(scale=1.5)
    bitmap.to_pil().save(pdf_path.parent/f'{pdf_path.stem}_page_{i+1:02d}.png')
    bitmap.close()
    page.close()
print('Rendered',len(pdf),'pages',flush=True)
pdf.close()
