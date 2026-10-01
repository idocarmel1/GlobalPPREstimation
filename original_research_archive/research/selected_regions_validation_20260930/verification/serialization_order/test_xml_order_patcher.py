"""Regression: appending sparse inserted cells must not hide existing columns."""
from zipfile import ZipFile
from lxml import etree as E
import openpyxl
import correct_residual_scope as C
from fast_reader import read_book
p=C.SCR/'xml_order_fixture_red_green.xlsx';wb=openpyxl.Workbook();s=wb.active;s.title='PPR';s.append(['@table','Matching']);s.append(['model_id','taxon','group','weight','confidence','evidence','explanation']);s['A3']='model';s['B3']='taxon';s['E3']='Very low';s['F3']='source';s['G3']='reason';t=wb.create_sheet('Order');t['A1']='a';t['Z1']='z';t['AB1']='ab';wb.save(p)
C.patch_package(p,[('PPR','C3',None,'group'),('PPR','D3',None,1.0),('Order','AA1',None,'aa'),('Order','C1',None,'c')]);canonical=C.W.read_book(p);independent=read_book(p)
assert canonical==independent,'Canonical reader lost existing E/F/G after sparse C/D insertion.'
assert canonical['PPR']['Matching'][1]==[['model','taxon','group',1,'Very low','source','reason']]
with ZipFile(p) as z:
 root=E.fromstring(z.read('xl/worksheets/sheet2.xml'));assert [c.get('r') for c in root.find(C.SN('sheetData'))[0]]==['A1','C1','Z1','AA1','AB1'],'Numeric column insertion must order Z before AA and AB.'
print('PASS: real sparse patch preserves canonical E/F/G values and numeric A/C/Z/AA/AB order.')
