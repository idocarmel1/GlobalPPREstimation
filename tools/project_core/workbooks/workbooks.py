from __future__ import annotations
"""Portable workbook tables. Scientific values are Python-calculated, never cached formulas."""
import hashlib, json, math, os, tempfile
from pathlib import Path
import openpyxl
from tools.project_core.validation.runtime_equivalence import verified_runtime_equivalence
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.cell import WriteOnlyCell
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter

YEARS = list(range(1950, 2020))
REGION_SHEETS = ['Overview', 'Catch', 'Classic PPR', 'Selected model groups', 'PPR', 'NPP', 'PPR–NPP', 'Diagnostics']
SIMPLE = 'simple trophic chain'

def finite(v): return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
def numeric_status(status):
    """Explicit provisional research display is distinct from reviewed 'ok' results."""
    return status == 'ok' or (isinstance(status,str) and status.startswith('provisional:'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def clean(v):
    if isinstance(v, (dict, list, tuple)): return json.dumps(v, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    if isinstance(v, float) and not math.isfinite(v): return None
    return v

def digest_tables(tables):
    # Excel writes numbers with 16 significant digits. Canonicalize before hashing.
    def canon(v):
        if v == '' if isinstance(v,str) else False: return None
        if finite(v): return format(float(v), '.16g')
        if isinstance(v, (list, tuple)): return [canon(x) for x in v]
        return v
    return hashlib.sha256(json.dumps(canon(tables), ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()

def read_book(path, *, sheets=None):
    """Read @table blocks; selected sheets are scoped evidence, not full validation."""
    if isinstance(sheets, str):
        raise TypeError('sheets must be an iterable of worksheet names, not a string')
    requested = None if sheets is None else set(sheets)
    w = openpyxl.load_workbook(path, read_only=True, data_only=False)
    result = {}
    try:
        if requested is not None and requested - set(w.sheetnames):
            raise ValueError('Missing requested worksheet: ' + ', '.join(sorted(requested - set(w.sheetnames))))
        for s in w:
            if requested is not None and s.title not in requested:
                continue
            blocks = {}; name = None; header = None; records = []
            for row in s.values:
                vals = list(row)
                while vals and vals[-1] is None: vals.pop()
                if not vals: continue
                if vals[0] == '@table':
                    if name is not None: blocks[name] = (header or [], records)
                    name = vals[1]; header = None; records = []
                elif name is not None:
                    if header is None:
                        # Native Excel tables require string headers; the research API uses integer years.
                        header = [int(v) if isinstance(v,str) and v.isdigit() and int(v) in YEARS else v for v in vals]
                    else:
                        if any(isinstance(v, str) and v.startswith('=') for v in vals):
                            raise ValueError(f'{path}/{s.title}/{name}: formulas are not supported in authoritative tables; use calculated values')
                        records.append((vals + [None] * len(header))[:len(header)])
            if name is not None: blocks[name] = (header or [], records)
            result[s.title] = blocks
    finally: w.close()
    return result

def rows(book, sheet, table): return book.get(sheet, {}).get(table, ([], []))[1]
def records(book, sheet, table):
    header, data = book.get(sheet, {}).get(table, ([], []))
    return [dict(zip(header, r)) for r in data]
def overview(book): return dict(rows(book, 'Overview', 'Settings'))
def input_hash(book):
    blocks = [(s, n, h, r) for s in ['Catch', 'Classic PPR', 'Selected model groups', 'PPR', 'NPP']
              for n, (h, r) in book.get(s, {}).items() if n in ['Catch', 'Taxa', 'Groups', 'Group SPPR', 'Matching', 'NPP']]
    return digest_tables(blocks)

def write_book(path, book):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    w = openpyxl.Workbook(write_only=True)
    native_tables = path.name == 'Project.xlsx'
    table_id = 0
    for title, blocks in book.items():
        s = w.create_sheet(title); s.freeze_panes = 'D3'; s.sheet_view.showGridLines = False
        s.sheet_properties.pageSetUpPr.fitToPage = True
        s.column_dimensions['A'].width = 28
        for col in ['B','C','D','E','F','G','H']: s.column_dimensions[col].width = 23
        if native_tables:
            for header, _ in blocks.values():
                if 'atlas_region_rank' in header:
                    s.column_dimensions[get_column_letter(header.index('atlas_region_rank')+1)].width = 22
                for field in ['researcher_review_status','researcher_name','researcher_review_date','validation_report_path',
                              'validation_report_sha256','reviewed_model_sha256','reviewed_calculation_input_sha256','researcher_review_summary']:
                    if field in header:
                        dimension=s.column_dimensions[get_column_letter(header.index(field)+1)]
                        dimension.width=65 if field=='validation_report_path' else 28
                        dimension.hidden=field.endswith('sha256') or field=='researcher_review_summary'
        if title=='Overview':
            s.column_dimensions['A'].width=34;s.column_dimensions['B'].width=110;s.freeze_panes='B3'
        row_number=0
        for name, (header, data) in blocks.items():
            s.append(['@table', name])
            row_number+=1
            cells = []
            for value in header:
                if native_tables: value = str(value)
                c = WriteOnlyCell(s, value=value); c.font = Font(name='Calibri', bold=True, color='FFFFFF', size=11)
                c.fill = PatternFill('solid', fgColor='174C58'); c.alignment = Alignment(wrap_text=True, vertical='top'); cells.append(c)
            if native_tables: s.row_dimensions[row_number+1].height = 43.5
            s.append(cells)
            row_number+=1
            header_row = row_number
            for record in data:
                row_number+=1
                if title=='Overview':s.row_dimensions[row_number].height=max(24,16*math.ceil(len(str(record[1] or ''))/95))
                vals = []
                researcher_status = (record[header.index('researcher_review_status')]
                    if native_tables and title=='Models & coverage' and name=='Models'
                    and 'researcher_review_status' in header else None)
                for field_index,value in enumerate(record):
                    v = clean(value)
                    if isinstance(v,str):
                        if len(v)>32767: raise ValueError(f'{title}/{name}: text exceeds Excel cell limit')
                        c=WriteOnlyCell(s,value=v); c.data_type='s'
                        if title=='Overview':c.alignment=Alignment(wrap_text=True,vertical='top')
                        if researcher_status in ['Validated by researcher','Disqualified by researcher'] and header[field_index] in ['model_id','researcher_review_status']:
                            c.font=Font(name='Calibri',size=11,bold=True,color='B42318' if researcher_status=='Disqualified by researcher' else '187344')
                        vals.append(c)
                    else:
                        c=WriteOnlyCell(s,value=v)
                        if finite(v): c.number_format='#,##0.######'
                        vals.append(c)
                s.append(vals)
            if native_tables and header:
                table_id += 1
                table = Table(displayName=f'PPR_Table_{table_id}', ref=f'A{header_row}:{get_column_letter(len(header))}{row_number}')
                table._initialise_columns()
                for column, value in zip(table.tableColumns, header): column.name = str(value)
                table.tableStyleInfo = TableStyleInfo(name='TableStyleMedium2', showRowStripes=True)
                s.add_table(table)
            s.append([])
            row_number+=1
    fd, temp = tempfile.mkstemp(suffix='.xlsx', dir=path.parent); os.close(fd)
    try:
        w.save(temp)
        check=openpyxl.load_workbook(temp,read_only=True); assert check.sheetnames==list(book); check.close()
        os.replace(temp, path)
    finally:
        if os.path.exists(temp): os.unlink(temp)

def table_dict(records):
    records=list(records); header=list(dict.fromkeys(k for r in records for k in r))
    return header, [[clean(r.get(k)) for k in header] for r in records]

def update_book(path, book):
    """Update table blocks while retaining manual sheets, styles and hyperlinks.

    Existing block cells are edited in place. Row growth is inserted before the
    following block; unparsed worksheets and their contents remain untouched.
    """
    import copy
    path=Path(path)
    if not path.exists():return write_book(path,book)
    baseline=sha(path);original=read_book(path);w=openpyxl.load_workbook(path)
    try:
        for title,blocks in book.items():
            if not blocks:continue
            s=w[title] if title in w.sheetnames else w.create_sheet(title)
            markers={str(s.cell(i,2).value):i for i in range(1,s.max_row+1) if s.cell(i,1).value=='@table'}
            for name,(header,data) in blocks.items():
                if original.get(title,{}).get(name)==(header,data):continue
                start=markers.get(name)
                if start is None:
                    start=s.max_row+2 if s.max_row>1 or s['A1'].value else 1;markers[name]=start
                following=min([v for k,v in markers.items() if v>start] or [s.max_row+2])
                needed=len(data)+3;available=following-start
                if needed>available:
                    growth=needed-available;s.insert_rows(following,growth)
                    markers={k:v+growth if v>=following else v for k,v in markers.items()};following+=growth
                template=s.cell(start+2,1)
                style=copy.copy(template._style)
                old_header,old_data=original.get(title,{}).get(name,([],[]))
                last_table_row=max(start+1+len(old_data),start+1+len(data))
                width=max(len(old_header),len(header),2)
                old_links={cell.coordinate:(cell.value,copy.copy(cell.hyperlink)) for row in s.iter_rows(min_row=start,max_row=last_table_row,max_col=width) for cell in row if cell.hyperlink}
                for row in s.iter_rows(min_row=start,max_row=last_table_row,max_col=width):
                    for cell in row:
                        if cell.value is not None:cell.value=None;cell.hyperlink=None
                s.cell(start,1,'@table');s.cell(start,2,name)
                for col,value in enumerate(header,1):s.cell(start+1,col,value)
                for i,row in enumerate(data,start+2):
                    for col,value in enumerate(row,1):
                        cell=s.cell(i,col,clean(value))
                        prior=old_links.get(cell.coordinate)
                        if prior and prior[0]==cell.value:cell.hyperlink=prior[1]
                        if not cell.has_style and style:cell._style=copy.copy(style)
            # Adjust existing native filter ranges without replacing their style.
            for table in s.tables.values():
                top=openpyxl.utils.cell.range_boundaries(table.ref)[1]
                marker=next((i for i in markers.values() if i+1==top),None)
                if marker:
                    name=str(s.cell(marker,2).value)
                    if name in blocks:
                        headers,data=blocks[name];table.ref=f'A{marker+1}:{get_column_letter(len(headers))}{marker+1+len(data)}'
                        from openpyxl.worksheet.table import TableColumn
                        previous={c.name:c for c in table.tableColumns}
                        table.tableColumns=[copy.copy(previous[str(label)]) if str(label) in previous else TableColumn(id=i,name=str(label)) for i,label in enumerate(headers,1)]
                        for i,c in enumerate(table.tableColumns,1):c.id=i
                        if table.autoFilter:table.autoFilter.ref=table.ref
        fd,tmp=tempfile.mkstemp(dir=path.parent,suffix='.xlsx');os.close(fd)
        try:
            w.save(tmp)
            if sha(path)!=baseline:raise ValueError(f'{path}: workbook changed during table update')
            os.replace(tmp,path)
        finally:
            if os.path.exists(tmp):os.unlink(tmp)
    finally:w.close()

def chunks(key, value, size=28000):
    text=json.dumps(value, ensure_ascii=False, separators=(',',':'), allow_nan=False)
    return [[key, i//size, text[i:i+size]] for i in range(0,len(text),size)]

def unchunks(data):
    grouped={}
    for key,i,text in data: grouped.setdefault(key,[]).append((int(i),text))
    return {k:json.loads(''.join(t for _,t in sorted(v))) for k,v in grouped.items()}

ANNUAL_HEADER=['model_id','scope','method','catch_basis','unidentified','metric','status',*YEARS]

def flatten_method(model, scope, method, value):
    result=[]
    for treatment in ['method','zero','simple']:
        v=value if treatment=='method' else value.get('unidentified_'+treatment)
        if v is None: continue
        for basis in ['landings','catch','discards']:
            b=v if basis=='landings' else v.get('catch_bases',{}).get(basis,{})
            for metric in ['ppr','catch','covered_catch']:
                result.append([model,scope,method,basis,treatment,metric,b.get('status','unavailable'),*b.get(metric,[None]*70)])
            if basis=='landings':
                sensitivity=v.get('sensitivity',[])
                for field in ['min_tC','max_tC']:
                    result.append([model,scope,method,basis,treatment,field,v.get('sensitivity_unavailable','assessed'),
                                   *[(s.get(field) if s else None) for s in sensitivity]] if sensitivity else
                                  [model,scope,method,basis,treatment,field,v.get('sensitivity_unavailable','unavailable'),*[None]*70])
    return result

def validate_region(book, path, require_fresh=True):
    o=overview(book); unit=o.get('unit_id'); selected=o.get('selected_model_id')
    if not unit or Path(path).stem!=unit: raise ValueError(f'{path}: workbook filename and unit_id must match')
    if selected:
        p=(Path(path).parent/str(o.get('model_path',''))).resolve()
        if not p.is_relative_to(Path(path).parent.resolve()) or not p.is_file(): raise ValueError(f'{unit}: selected model path missing or outside region')
        if o.get('results_model_id') and o['results_model_id']!=selected: raise ValueError(f'{unit}: stale results belong to another selected model; run_region.py first')
        if o.get('results_model_sha256') and sha(p)!=o['results_model_sha256']:
            if not verified_runtime_equivalence(Path(path).parent, p, o['results_model_sha256']):
                raise ValueError(f'{unit}: model JSON changed; regenerate SPPR before publication')
    if require_fresh and o.get('calculation_input_sha256')!=input_hash(book):
        raise ValueError(f'{unit}: calculation inputs changed; refresh regional calculations before publication')
    for r in records(book,'PPR','Matching'):
        if r.get('model_id')!=selected: raise ValueError(f'{unit}: mapping belongs to another model')
    return o
