from pathlib import Path
import math, textwrap, openpyxl
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter
M=Path(__file__).resolve().parents[4]
p=M/'sppr_source.xlsx';w=openpyxl.load_workbook(p)
for s in w:
    for row in s:
        lines=1
        for c in row:
            c.alignment=Alignment(vertical='center',wrap_text=True)
            width=s.column_dimensions[c.column_letter].width or 13
            txt='' if c.value is None else str(c.value)
            lines=max(lines,sum(max(1,len(textwrap.wrap(t,width=max(8,int(width)-3),break_long_words=True))) for t in txt.split('\n')))
        s.row_dimensions[row[0].row].height=min(400,max(28,lines*15+12))
    s.sheet_view.zoomScale=80
    s.print_title_rows='1:1'
    s.sheet_properties.pageSetUpPr.fitToPage=True
    s.page_setup.orientation='landscape';s.page_setup.paperSize=s.PAPERSIZE_A3
    s.page_setup.fitToWidth=1;s.page_setup.fitToHeight=0
    s.print_options.horizontalCentered=True
    s.print_area=s.dimensions
# Long provenance is prose, so give its value column enough width.
s=w['Sources'];s.column_dimensions['B'].width=100
for row in s:
    s.row_dimensions[row[0].row].height=max(30,math.ceil(len(str(row[1].value or ''))/90)*16+12)
w.save(p);w.close()
print('Coefficient workbook labels and wrapped provenance formatted.')
