"""Rasterize independent Word QA exports with the bundled PDFium runtime."""
from pathlib import Path
import json
import pypdfium2 as pdfium

root = Path(__file__).resolve().parent
outputs = []
for pdf_path in sorted((root / "qa").glob("*/*.pdf")):
    pdf = pdfium.PdfDocument(str(pdf_path))
    pages = []
    for i in range(len(pdf)):
        page = pdf[i]
        bitmap = page.render(scale=1.7)
        target = pdf_path.parent / f"page-{i+1}.png"
        bitmap.to_pil().save(target)
        pages.append({"page": i+1, "path": target.relative_to(root).as_posix(), "width": bitmap.width, "height": bitmap.height})
        text = page.get_textpage().get_text_range()
        (pdf_path.parent / f"page-{i+1}.txt").write_text(text, encoding="utf-8")
        bitmap.close()
        page.close()
    outputs.append({"pdf": pdf_path.relative_to(root).as_posix(), "pages": pages})
    pdf.close()
(root / "qa" / "rasterization.json").write_text(json.dumps(outputs, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps([{ "pdf": x["pdf"], "page_count": len(x["pages"]) } for x in outputs]))
