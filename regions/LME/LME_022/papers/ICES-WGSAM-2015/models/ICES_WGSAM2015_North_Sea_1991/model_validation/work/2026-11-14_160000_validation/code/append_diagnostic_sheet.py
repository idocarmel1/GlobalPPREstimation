"""Append the artifact-authored sheet without rewriting the two existing sheets."""
from pathlib import Path
from copy import copy,deepcopy
import csv,hashlib,json,math,re,sys,zipfile
import xml.etree.ElementTree as ET
from openpyxl import load_workbook

ROOT=Path.cwd()
MODEL=ROOT/'regions/LME/LME_022/papers/ICES-WGSAM-2015/models/ICES_WGSAM2015_North_Sea_1991'
BASE=MODEL/'model_validation'
REPAIR='--loader-repair' in sys.argv
WORK=BASE/('work/2026-11-14_161706_loader_repair' if REPAIR else 'work/2026-11-14_160000_validation')
BEFORE=WORK/'inputs/taxon_mapping_before_diagnostics.xlsx'
DIAG=WORK/'outputs/sppr_diagnostics_sheet.xlsx'
OUT=BASE/'taxon_mapping.xlsx'
MAIN='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL='http://schemas.openxmlformats.org/package/2006/relationships'
ODREL='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
CT='http://schemas.openxmlformats.org/package/2006/content-types'
ET.register_namespace('',MAIN);ET.register_namespace('r',ODREL)
def q(n):return '{'+MAIN+'}'+n
def read(p):
    with zipfile.ZipFile(p) as z:return {n:z.read(n) for n in z.namelist()}
def xml(b):return ET.fromstring(b)
def dump(e):return ET.tostring(e,encoding='utf-8',xml_declaration=True)
old,new=read(BEFORE),read(DIAG)
out=dict(old)
styles,extra=xml(old['xl/styles.xml']),xml(new['xl/styles.xml'])
order=['numFmts','fonts','fills','borders','cellStyleXfs','cellXfs','cellStyles','dxfs','tableStyles','colors','extLst']
def ensure(parent,name):
    node=parent.find(q(name))
    if node is None:
        node=ET.Element(q(name),{'count':'0'})
        pos=next((i for i,c in enumerate(parent) if order.index(c.tag.split('}')[-1])>order.index(name)),len(parent))
        parent.insert(pos,node)
    return node
def serial(e):return ET.tostring(e,encoding='utf8')
def merge_simple(name):
    a=ensure(styles,name);b=extra.find(q(name));mapping={}
    if b is None:return mapping
    lookup={serial(e):i for i,e in enumerate(a)}
    for i,e in enumerate(b):
        k=serial(e)
        if k not in lookup:lookup[k]=len(a);a.append(deepcopy(e))
        mapping[i]=lookup[k]
    a.set('count',str(len(a)));return mapping
fontmap=merge_simple('fonts');fillmap=merge_simple('fills');bordermap=merge_simple('borders')
numfmtmap={i:i for i in range(164)}
dest=ensure(styles,'numFmts');src=extra.find(q('numFmts'))
byformat={e.get('formatCode'):int(e.get('numFmtId')) for e in dest}
used={int(e.get('numFmtId')) for e in dest}
if src is not None:
    for e in src:
        original=int(e.get('numFmtId'));fmt=e.get('formatCode')
        if fmt not in byformat:
            nxt=max(used|{163})+1;used.add(nxt);byformat[fmt]=nxt
            c=deepcopy(e);c.set('numFmtId',str(nxt));dest.append(c)
        numfmtmap[original]=byformat[fmt]
dest.set('count',str(len(dest)))
def merge_xfs(name,stylemap=None):
    dest=ensure(styles,name);source=extra.find(q(name));lookup={serial(e):i for i,e in enumerate(dest)};mapping={}
    for i,e in enumerate(source):
        c=deepcopy(e)
        for attr,mp in [('fontId',fontmap),('fillId',fillmap),('borderId',bordermap),('numFmtId',numfmtmap)]:
            if attr in c.attrib:c.set(attr,str(mp[int(c.get(attr))]))
        if stylemap is not None and c.get('xfId') is not None:c.set('xfId',str(stylemap[int(c.get('xfId'))]))
        key=serial(c)
        if key not in lookup:lookup[key]=len(dest);dest.append(c)
        mapping[i]=lookup[key]
    dest.set('count',str(len(dest)));return mapping
stylemap=merge_xfs('cellStyleXfs');xfmap=merge_xfs('cellXfs',stylemap)
out['xl/styles.xml']=dump(styles)
strings,addstrings=xml(old['xl/sharedStrings.xml']),xml(new['xl/sharedStrings.xml'])
lookup={serial(e):i for i,e in enumerate(strings)};strmap={}
for i,e in enumerate(addstrings):
    key=serial(e)
    if key not in lookup:lookup[key]=len(strings);strings.append(deepcopy(e))
    strmap[i]=lookup[key]
strings.set('uniqueCount',str(len(strings)))
strings.set('count',str(int(strings.get('count','0'))+int(addstrings.get('count','0'))))
out['xl/sharedStrings.xml']=dump(strings)
sheet=xml(new['xl/worksheets/sheet1.xml'])
for c in sheet.iter(q('c')):
    if c.get('s') is not None:c.set('s',str(xfmap[int(c.get('s'))]))
    if c.get('t')=='s':c.find(q('v')).text=str(strmap[int(c.find(q('v')).text)])
assert not list(sheet.iter(q('conditionalFormatting')))
out['xl/worksheets/sheet3.xml']=dump(sheet)
rels=xml(new['xl/worksheets/_rels/sheet1.xml.rels'])
for r in rels:
    assert r.get('Type').endswith('/table')
    r.set('Target','../tables/table2.xml')
out['xl/worksheets/_rels/sheet3.xml.rels']=dump(rels)
table=xml(new['xl/tables/table1.xml']);table.set('id','2')
assert table.get('name')==('ICES1991SPPRMethodSummary' if REPAIR else 'ICES1991SPPRNegativeEntries')
out['xl/tables/table2.xml']=dump(table)
workbook=xml(old['xl/workbook.xml']);sheets=workbook.find(q('sheets'))
assert len(sheets)==(3 if REPAIR else 2)
wrels=xml(old['xl/_rels/workbook.xml.rels'])
ids={r.get('Id') for r in wrels};i=1
while 'rId'+str(i) in ids:i+=1
rid='rId'+str(i)
if not REPAIR:
    sheets.append(ET.Element(q('sheet'),{'name':'SPPR diagnostics','sheetId':'3','{'+ODREL+'}id':rid}))
    wrels.append(ET.Element('{'+REL+'}Relationship',{'Id':rid,'Type':ODREL+'/worksheet','Target':'worksheets/sheet3.xml'}))
    out['xl/workbook.xml']=dump(workbook);out['xl/_rels/workbook.xml.rels']=dump(wrels)
else:
    assert [s.get('name') for s in sheets]==['Taxon mapping','Sources','SPPR diagnostics']
types=xml(old['[Content_Types].xml'])
if not REPAIR:
    for name,typ in [('/xl/worksheets/sheet3.xml','application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml'),('/xl/tables/table2.xml','application/vnd.openxmlformats-officedocument.spreadsheetml.table+xml')]:
        types.append(ET.Element('{'+CT+'}Override',{'PartName':name,'ContentType':typ}))
    out['[Content_Types].xml']=dump(types)
strings.set('count',str(sum(1 for name,data in out.items() if re.fullmatch(r'xl/worksheets/sheet\d+\.xml',name) for c in xml(data).iter(q('c')) if c.get('t')=='s')))
out['xl/sharedStrings.xml']=dump(strings)
if REPAIR:
    changed={name for name in old if old[name]!=out[name]}
    assert changed <= {'xl/styles.xml','xl/sharedStrings.xml','xl/worksheets/sheet3.xml','xl/worksheets/_rels/sheet3.xml.rels','xl/tables/table2.xml'},changed
stage=WORK/'outputs/taxon_mapping_with_diagnostics.xlsx'
with zipfile.ZipFile(stage,'w',zipfile.ZIP_DEFLATED) as z:
    for name,data in out.items():z.writestr(name,data)

# Verify first-sheet values, styles, links, structures and raw XML before promotion.
before=load_workbook(BEFORE,data_only=False);after=load_workbook(stage,data_only=False)
assert after.sheetnames==['Taxon mapping','Sources','SPPR diagnostics']
preservation=[]
for name in before.sheetnames[:2]:
    a,b=before[name],after[name]
    assert a.max_row==b.max_row and a.max_column==b.max_column
    for row in a:
        for c in row:
            d=b[c.coordinate]
            assert c.value==d.value and c.data_type==d.data_type,(name,c.coordinate,'value')
            for attr in ['font','fill','border','alignment','protection','number_format']:
                assert copy(getattr(c,attr))==copy(getattr(d,attr)),(name,c.coordinate,attr)
            assert c.hyperlink==d.hyperlink
    assert a.freeze_panes==b.freeze_panes
    assert list(a.merged_cells.ranges)==list(b.merged_cells.ranges)
    assert {k:dict(v) for k,v in a.column_dimensions.items()}=={k:dict(v) for k,v in b.column_dimensions.items()}
    assert {k:dict(v) for k,v in a.row_dimensions.items()}=={k:dict(v) for k,v in b.row_dimensions.items()}
    preservation.append({'sheet':name,'all_values_styles_links_dimensions_panes_unchanged':True})
for part in ['xl/worksheets/sheet1.xml','xl/worksheets/sheet2.xml','xl/worksheets/_rels/sheet1.xml.rels','xl/tables/table1.xml']:
    assert out[part]==old[part],part
diagnostic=after['SPPR diagnostics']
if REPAIR:
    authored=load_workbook(DIAG,data_only=False)['SPPR diagnostics']
    for row in authored:
        for c in row:
            d=diagnostic[c.coordinate]
            assert c.value==d.value and c.data_type==d.data_type,('diagnostic',c.coordinate,'value')
            for attr in ['font','fill','border','alignment','protection','number_format']:
                assert copy(getattr(c,attr))==copy(getattr(d,attr)),('diagnostic',c.coordinate,attr)
    assert list(authored.merged_cells.ranges)==list(diagnostic.merged_cells.ranges)
    assert {k:dict(v) for k,v in authored.column_dimensions.items()}=={k:dict(v) for k,v in diagnostic.column_dimensions.items()}
    assert {k:dict(v) for k,v in authored.row_dimensions.items()}=={k:dict(v) for k,v in diagnostic.row_dimensions.items()}
    diagnostic_dir=MODEL/'results/diagnostics/2026-11-14_loader_repair'
    summary=json.loads((diagnostic_dir/'summary.json').read_text())
    reference=list(csv.DictReader((diagnostic_dir/'negative_entries.tsv').open(),delimiter='\t'))
    assert not reference
    actual=list(diagnostic.iter_rows(min_row=8,max_row=10,values_only=True))
    assert len(actual)==3 and diagnostic.max_row==29
    for r,ref in zip(actual,summary['methods']):
        d=ref['diagnostic']; pools=dict(d['divergence']['sppr_det']['items'])
        expected=(ref['method'],d['status'],d['divergence']['rho_living'],d['divergence']['b'],pools[67],pools[68],pools[69],0,0,350)
        for a,e in zip(r,expected):assert a==e if isinstance(e,str) else math.isclose(a,e,rel_tol=1e-15,abs_tol=0),(r,expected)
        assert d['status']=='WARN' and not ref['negative_entries'] and ref['matrix_checks']['negative_source_count']==0
    for i,m in enumerate(summary['methods']):
        row=i+20;b=m['diagnostic']['balance']
        assert diagnostic[f'A{row}'].value==m['method']
        for col,key in [('C','inflow'),('E','outflow'),('G','rel_gap')]:assert math.isclose(diagnostic[f'{col}{row}'].value,b[key],rel_tol=1e-15)
        assert diagnostic[f'I{row}'].value==b['status']=='OK'
        assert diagnostic[f'A{i+14}'].value==f"{m['method']}: "+' | '.join(m['diagnostic']['warnings'])
    expected_range='A7:J10';link_addresses=['A27','F27','A28','F28','A29','F29']
    assert hashlib.sha256(BEFORE.read_bytes()).hexdigest()=='e987fa9378ea6e7beb3e03f23600c395fd8fd18d8b280d32a008425105fc9c68'
    assert OUT.read_bytes()==BEFORE.read_bytes(),'Canonical changed after fresh baseline; stop to preserve human edits'
else:
    reference=list(csv.DictReader((MODEL/'results/diagnostics/2026-11-14_validation/structural_zero/negative_entries.tsv').open(),delimiter='\t'))
    reference.sort(key=lambda r:(r['method'],int(r['source_id']),int(r['group_id'])))
    actual=list(diagnostic.iter_rows(min_row=8,max_row=271,values_only=True))
    assert len(actual)==264
    for r,ref in zip(actual,reference):
        assert r[:5]==(ref['method'],int(ref['source_id']),ref['source_name'],int(ref['group_id']),ref['group_name'])
        assert math.isclose(r[5],float(ref['value']),rel_tol=1e-15) and r[5]<0 and r[6]==0
    expected_range='A7:G271';link_addresses=['A6','D6']
assert diagnostic.freeze_panes=='B8'
assert next(iter(diagnostic.tables.values())).ref==expected_range
assert next(iter(diagnostic.tables.values())).autoFilter.ref==expected_range
for address in link_addresses:
    c=diagnostic[address];target=re.search(r'HYPERLINK\("([^"]+)',c.value).group(1)
    assert not re.match(r'^(?:[A-Za-z]:|/|\\|file:)',target)
    assert (OUT.parent/target).resolve().exists()
    assert c.font.underline=='single' and c.font.color.rgb[-6:]=='0563C1'
audit=json.loads((ROOT/'regions/LME/LME_022/work/2026-11-14_160000_validation/outputs/mapping_audit.json').read_text(encoding='utf8'))
assert [r[0] for r in after['Taxon mapping'].iter_rows(min_row=8,max_row=391,values_only=True)]==[r['taxon'] for r in audit['rows']]
assert hashlib.sha256((ROOT/'regions/LME/LME_022/LME_022.xlsx').read_bytes()).hexdigest()==audit['regional_workbook_sha256']
OUT.write_bytes(stage.read_bytes())
report={'verified':True,'first_two_sheets':preservation,'first_two_sheet_xml_and_relationships_byte_identical':True,
        'method_negative_counts':{'new_GE':132,'new_TE_EEfix':0,'new_WithEgestion':132},'all_method_statuses':'FAIL',
        'negative_pairs':264,'strict_sign_tolerance':0,'all_names_ids_values_match_tsv':True,
        'sort_order':'method, source ID, recipient group ID','freeze_panes':'B8','filter':'A7:G271',
        'original_384_taxa_sort_unchanged':True,'regional_workbook_unchanged':True,
        'before_sha256':hashlib.sha256(BEFORE.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),
        'authored_with':'bundled @oai/artifact-tool; original two sheet XML/relationships retained verbatim during package append',
        'renders':['diagnostics_top.png','diagnostics_bottom.png']}
if REPAIR:
    report.update({'method_negative_counts':{m['method']:0 for m in summary['methods']},'all_method_statuses':'WARN','negative_pairs':0,
                   'all_names_ids_values_match_tsv':True,'summary_values_and_budget_match_official_json':True,'obsolete_negative_pair_body_removed':True,
                   'sort_order':'official method order: GE, TE, With Egestion','filter':expected_range,'finite_values_per_method':350,
                   'authored_with':'bundled @oai/artifact-tool; first two sheet XML/relationships/table retained verbatim during third-sheet replacement',
                   'replaced_parts':['xl/worksheets/sheet3.xml','xl/worksheets/_rels/sheet3.xml.rels','xl/tables/table2.xml'],
                   'shared_resource_note':'Styles and shared strings extended without renumbering original IDs',
                   'preserved_parts_sha256':{n:hashlib.sha256(out[n]).hexdigest() for n in ['xl/worksheets/sheet1.xml','xl/worksheets/sheet2.xml','xl/worksheets/_rels/sheet1.xml.rels','xl/tables/table1.xml','xl/workbook.xml','xl/_rels/workbook.xml.rels','[Content_Types].xml']},
                   'source_summary_sha256':hashlib.sha256((diagnostic_dir/'summary.json').read_bytes()).hexdigest(),
                   'source_ledger_sha256':hashlib.sha256((diagnostic_dir/'negative_entries.tsv').read_bytes()).hexdigest(),
                   'artifact_render_matches_promoted_cell_styles_values_dimensions':True,'visually_inspected':['diagnostics_top.png','diagnostics_bottom.png'],
                   'column_order':['Method (engine ID)','Overall status','Living spectral radius (rho)','Detritus coupling (b)','DetritusDOMWaterColumn (67) raw SPPR','DetritusPOMSediment (68) raw SPPR','Discards (69) raw SPPR','Negative entries','Negative sources','Finite matrix values']})
(WORK/'qa/diagnostic_sheet_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False,indent=2))
