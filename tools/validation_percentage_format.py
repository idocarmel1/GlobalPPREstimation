"""Format display percentages in validation Word tables without rewriting the document.

Scientific values and ordering remain in their original workbooks/evidence.
The same verifier is used before an authorized signed-review map handoff.
"""
import argparse,os,re,tempfile,zipfile
from decimal import Decimal,ROUND_HALF_UP
from pathlib import Path
from xml.etree import ElementTree as E
from xml.parsers import expat
from xml.sax.saxutils import escape

W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS={'w':W}
NUMBER=r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)'
PERCENT=re.compile(r'(?<![\w.])('+NUMBER+r')\s*%')
RANGE=re.compile(r'(?<![\w.])('+NUMBER+r')\s*[–−-]\s*('+NUMBER+r')\s*%')

def format_percent(value):
    """Input is already in percentage points; never multiply it by 100."""
    number=Decimal(str(value).strip().removesuffix('%').strip())
    if not number.is_finite():raise ValueError('Percentage must be finite')
    if not number:return '0%'
    quantum=Decimal(1).scaleb(number.adjusted()-1)
    rounded=number.quantize(quantum,rounding=ROUND_HALF_UP)
    if rounded.adjusted()>number.adjusted():
        rounded=rounded.quantize(Decimal(1).scaleb(rounded.adjusted()-1))
    return format(rounded,'f')+'%'

def table_edits(document):
    """Return cell-local substitutions, including percentages inside table prose."""
    for ti,table in enumerate(document.findall('.//w:tbl',NS)):
        rows=table.findall('w:tr',NS)
        if not rows:continue
        headers=[''.join(c.itertext()) for c in rows[0].findall('w:tc',NS)]
        percentage_columns={i for i,h in enumerate(headers) if '%' in h or 'percentage' in h.lower()}
        for ri,row in enumerate(rows):
            for ci,cell in enumerate(row.findall('w:tc',NS)):
                # Exclude a nested table's text; it is visited as its own table.
                nodes=cell.findall('w:p//w:t',NS)
                value=''.join(n.text or '' for n in nodes)
                edits={}
                if ri and ci in percentage_columns and re.fullmatch(r'\s*'+NUMBER+r'\s*%?\s*',value):
                    edits[(0,len(value))]=format_percent(value)
                else:
                    for match in PERCENT.finditer(value):
                        edits[match.span()]=format_percent(match.group(1))
                    for match in RANGE.finditer(value):
                        edits[match.span(1)]=format_percent(match.group(1))[:-1]
                edits=[(start,end,new) for (start,end),new in sorted(edits.items()) if value[start:end]!=new]
                if edits:yield ti,ri,ci,nodes,value,edits

def verify_report(path):
    """Fail if any numeric table percentage is not in the agreed display format."""
    with zipfile.ZipFile(path) as archive:document=E.fromstring(archive.read('word/document.xml'))
    pending=list(table_edits(document))
    if pending:raise ValueError(f'{path}: {len(pending)} table cells need two-significant-digit percentages')

def format_report(path):
    """Patch only affected w:t contents; preserve every other DOCX ZIP member."""
    path=Path(path)
    with zipfile.ZipFile(path) as archive:
        parts=[(info,archive.read(info.filename)) for info in archive.infolist()]
    xml=dict((i.filename,data) for i,data in parts)['word/document.xml']
    document=E.fromstring(xml);all_nodes=document.findall('.//w:t',NS)
    index={node:i for i,node in enumerate(all_nodes)};new_text={};changes=[]
    for ti,ri,ci,nodes,value,edits in table_edits(document):
        bounds=[];position=0
        for node in nodes:
            original=node.text or '';bounds.append((node,position,position+len(original)));position+=len(original)
        for start,end,new in reversed(edits):
            for node,lo,hi in bounds:
                if max(lo,start)>=min(hi,end):continue
                current=new_text.get(index[node],node.text or '')
                a=max(start,lo)-lo;b=min(end,hi)-lo
                new_text[index[node]]=current[:a]+(new if lo<=start<hi else '')+current[b:]
            changes.append({'table':ti,'row':ri,'column':ci,'before':value[start:end],'after':new})
    if not changes:return []
    # Expat provides byte offsets so serialization cannot alter namespace,
    # run/cell properties, links, manual cells or unrelated XML formatting.
    parser=expat.ParserCreate(namespace_separator='}')
    spans=[];active=None
    def start(name,attrs):
        nonlocal active
        if name==W+'}t':
            offset=xml.index(b'>',parser.CurrentByteIndex)+1
            active=len(spans);spans.append([offset,offset])
    def end(name):
        nonlocal active
        if name==W+'}t':
            spans[active][1]=parser.CurrentByteIndex;active=None
    parser.StartElementHandler=start;parser.EndElementHandler=end;parser.Parse(xml,True)
    assert len(spans)==len(all_nodes)
    for i,value in sorted(new_text.items(),reverse=True):
        lo,hi=spans[i];xml=xml[:lo]+escape(value).encode('utf-8')+xml[hi:]
    fd,temporary=tempfile.mkstemp(suffix='.docx',dir=path.parent);os.close(fd)
    try:
        with zipfile.ZipFile(temporary,'w') as archive:
            for info,data in parts:archive.writestr(info,xml if info.filename=='word/document.xml' else data)
        verify_report(temporary)
        os.replace(temporary,path)
    finally:
        if os.path.exists(temporary):os.unlink(temporary)
    return changes

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reports',nargs='+',type=Path);parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    for report in args.reports:
        if args.check:verify_report(report);print(str(report)+': percentage format verified')
        else:print(str(report)+': '+str(len(format_report(report)))+' percentage values formatted')
