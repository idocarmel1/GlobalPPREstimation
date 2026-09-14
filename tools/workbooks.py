"""Portable workbook tables. Scientific values are Python-calculated, never cached formulas."""
from __future__ import annotations
import hashlib, json, math, os, tempfile
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.cell import WriteOnlyCell

YEARS = list(range(1950, 2020))
REGION_SHEETS = ['Overview', 'Catch', 'Classic PPR', 'Selected model groups', 'PPR', 'NPP', 'PPR–NPP', 'Diagnostics']
SIMPLE = 'simple trophic chain'

def finite(v): return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
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

def read_book(path):
    w = openpyxl.load_workbook(path, read_only=True, data_only=False)
    result = {}
    try:
        for s in w:
            blocks = {}; name = None; header = None; records = []
            for row in s.values:
                vals = list(row)
                while vals and vals[-1] is None: vals.pop()
                if not vals: continue
                if vals[0] == '@table':
                    if name is not None: blocks[name] = (header or [], records)
                    name = vals[1]; header = None; records = []
                elif name is not None:
                    if header is None: header = vals
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
    for title, blocks in book.items():
        s = w.create_sheet(title); s.freeze_panes = 'D3'; s.sheet_view.showGridLines = False
        s.sheet_properties.pageSetUpPr.fitToPage = True
        s.column_dimensions['A'].width = 28
        for col in ['B','C','D','E','F','G','H']: s.column_dimensions[col].width = 23
        if title=='Overview':
            s.column_dimensions['A'].width=34;s.column_dimensions['B'].width=110;s.freeze_panes='B3'
        row_number=0
        for name, (header, data) in blocks.items():
            s.append(['@table', name])
            row_number+=1
            cells = []
            for value in header:
                c = WriteOnlyCell(s, value=value); c.font = Font(name='Calibri', bold=True, color='FFFFFF', size=11)
                c.fill = PatternFill('solid', fgColor='174C58'); c.alignment = Alignment(wrap_text=True, vertical='top'); cells.append(c)
            s.append(cells)
            row_number+=1
            for record in data:
                row_number+=1
                if title=='Overview':s.row_dimensions[row_number].height=max(24,16*math.ceil(len(str(record[1] or ''))/95))
                vals = []
                for value in record:
                    v = clean(value)
                    if isinstance(v,str):
                        if len(v)>32767: raise ValueError(f'{title}/{name}: text exceeds Excel cell limit')
                        c=WriteOnlyCell(s,value=v); c.data_type='s'
                        if title=='Overview':c.alignment=Alignment(wrap_text=True,vertical='top')
                        vals.append(c)
                    else:
                        c=WriteOnlyCell(s,value=v)
                        if finite(v): c.number_format='#,##0.######'
                        vals.append(c)
                s.append(vals)
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
        if o.get('results_model_sha256') and sha(p)!=o['results_model_sha256']: raise ValueError(f'{unit}: model JSON changed; regenerate SPPR before publication')
    if require_fresh and o.get('calculation_input_sha256')!=input_hash(book):
        raise ValueError(f'{unit}: calculation inputs changed; refresh regional calculations before publication')
    for r in records(book,'PPR','Matching'):
        if r.get('model_id')!=selected: raise ValueError(f'{unit}: mapping belongs to another model')
    return o
