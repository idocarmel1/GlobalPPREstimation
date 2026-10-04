"""Patch authorized table/cell values while retaining the existing Office package."""
from pathlib import Path
from copy import deepcopy
from zipfile import ZipFile
from lxml import etree
import json,re,os,tempfile
S='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
P='http://schemas.openxmlformats.org/package/2006/relationships'
NS={'s':S}
def q(n):return '{'+S+'}'+n
def package(path):
    with ZipFile(path) as z:return z.infolist(),{i.filename:z.read(i.filename) for i in z.infolist()}
def save_package(path,infos,parts):
    fd,tmp=tempfile.mkstemp(suffix=Path(path).suffix,dir=Path(path).parent);os.close(fd)
    try:
        with ZipFile(tmp,'w') as z:
            done=set()
            for i in infos:z.writestr(i,parts[i.filename]);done.add(i.filename)
            for k,v in parts.items():
                if k not in done:z.writestr(k,v)
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
def sheet_paths(parts):
    w=etree.fromstring(parts['xl/workbook.xml']);rels=etree.fromstring(parts['xl/_rels/workbook.xml.rels'])
    targets={r.get('Id'):r.get('Target') for r in rels}
    return {s.get('name'):('xl/'+targets[s.get('{'+R+'}id')].lstrip('/') if not targets[s.get('{'+R+'}id')].startswith('/') else targets[s.get('{'+R+'}id')].lstrip('/')) for s in w.find(q('sheets'))}
def strings(parts):
    if 'xl/sharedStrings.xml' not in parts:return []
    return [''.join(si.itertext()) for si in etree.fromstring(parts['xl/sharedStrings.xml'])]
def value(c,ss):
    if c is None:return None
    if c.get('t')=='inlineStr':return ''.join(c.xpath('.//s:t/text()',namespaces=NS))
    v=c.find(q('v'))
    if v is None:return None
    if c.get('t')=='s':return ss[int(v.text)]
    if c.get('t')=='b':return v.text=='1'
    if c.get('t') in ['str','e']:return v.text
    try:return float(v.text)
    except (ValueError,TypeError):return v.text
def set_value(c,v):
    for n in list(c):c.remove(n)
    c.attrib.pop('t',None)
    if v is None:return
    if isinstance(v,(dict,list,tuple)):v=json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)
    if isinstance(v,bool):c.set('t','b');etree.SubElement(c,q('v')).text='1' if v else '0'
    elif isinstance(v,(int,float)):etree.SubElement(c,q('v')).text=format(v,'.17g')
    else:
        c.set('t','inlineStr');t=etree.SubElement(etree.SubElement(c,q('is')),q('t'));t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=str(v)
def letters(n):
    s=''
    while n:n,r=divmod(n-1,26);s=chr(65+r)+s
    return s
def shift(row,newnum):
    row.set('r',str(newnum))
    for c in row.findall(q('c')):c.set('r',re.sub(r'\d+$',str(newnum),c.get('r')))
    return row
def row_from(values,num,template=None,style_by_col=None):
    row=deepcopy(template) if template is not None else etree.Element(q('row'))
    for c in list(row):row.remove(c)
    row.set('r',str(num))
    row.attrib.pop('spans',None)
    for col,v in enumerate(values,1):
        if v is None:continue
        c=etree.SubElement(row,q('c'),r=letters(col)+str(num))
        if style_by_col and col in style_by_col and style_by_col[col]:c.set('s',style_by_col[col])
        set_value(c,v)
    return row
def patch_blocks(source,dest,changed):
    infos,parts=package(source);ss=strings(parts);paths=sheet_paths(parts)
    for sheet,blocks in changed.items():
        root=etree.fromstring(parts[paths[sheet]]);data=root.find(q('sheetData'));old=list(data)
        starts=[]
        for i,row in enumerate(old):
            cells={re.sub(r'\d+$','',c.get('r')):c for c in row}
            if value(cells.get('A'),ss)=='@table':starts.append((i,value(cells.get('B'),ss)))
        ranges={name:(i,starts[j+1][0] if j+1<len(starts) else len(old)) for j,(i,name) in enumerate(starts)}
        new=[];done=set();i=0
        while i<len(old):
            item=next(((name,a,z) for name,(a,z) in ranges.items() if a==i),None)
            if item and item[0] in blocks:
                name,a,z=item;h,rows=blocks[name];segment=old[a:z]
                hdr=segment[1] if len(segment)>1 else None
                tmpl=segment[2] if len(segment)>2 else hdr
                header_styles={j:c.get('s') for j,c in enumerate(hdr,1)} if hdr is not None else {}
                styles={int_col(c.get('r')):c.get('s') for c in tmpl} if tmpl is not None else {}
                new.append(shift(deepcopy(segment[0]),len(new)+1))
                new.append(row_from(h,len(new)+1,hdr,header_styles))
                for vals in rows:new.append(row_from(vals,len(new)+1,tmpl,styles))
                new.append(etree.Element(q('row'),r=str(len(new)+1)));done.add(name);i=z
            else:new.append(shift(deepcopy(old[i]),len(new)+1));i+=1
        for name,(h,rows) in blocks.items():
            if name in done:continue
            marker=next((old[a] for a,z in ranges.values()),None);hdr=next((old[a+1] for a,z in ranges.values()),None)
            styles={int_col(c.get('r')):c.get('s') for c in hdr} if hdr is not None else {}
            new.append(row_from(['@table',name],len(new)+1,marker))
            new.append(row_from(h,len(new)+1,hdr,styles))
            for vals in rows:new.append(row_from(vals,len(new)+1))
            new.append(etree.Element(q('row'),r=str(len(new)+1)))
        for row in list(data):data.remove(row)
        for row in new:data.append(row)
        dim=root.find(q('dimension'))
        if dim is not None:dim.set('ref','A1:'+letters(max(int_col(c.get('r')) for row in new for c in row))+str(len(new)))
        parts[paths[sheet]]=etree.tostring(root,encoding='utf-8')
    save_package(dest,infos,parts)
def int_col(ref):
    v=0
    for c in re.sub(r'\d+$','',ref):v=v*26+ord(c)-64
    return v
def patch_cells(source,dest,updates,links=None,extra_rows=None):
    infos,parts=package(source);paths=sheet_paths(parts)
    for sheet,changes in updates.items():
        root=etree.fromstring(parts[paths[sheet]]);data=root.find(q('sheetData'));rowmap={int(r.get('r')):r for r in data}
        template=deepcopy(data[-1]);maxrow=max(rowmap)
        for address,v in changes.items():
            num=int(re.search(r'\d+$',address).group())
            if num not in rowmap:
                row=shift(deepcopy(template),num);rowmap[num]=row;data.append(row)
            row=rowmap[num];c=next((c for c in row if c.get('r')==address),None)
            if c is None:c=etree.SubElement(row,q('c'),r=address)
            set_value(c,v);maxrow=max(maxrow,num)
        # Preserve native table filters and extend only the source-reference table.
        if maxrow>max(int(r.get('r')) for r in etree.fromstring(parts[paths[sheet]]).find(q('sheetData'))):
            dim=root.find(q('dimension'))
            if dim is not None:dim.set('ref',re.sub(r'\d+$',str(maxrow),dim.get('ref')))
            for part in root.findall(q('tableParts')):
                relpath=str(Path(paths[sheet]).parent/'_rels'/(Path(paths[sheet]).name+'.rels')).replace('\\','/')
                rels=etree.fromstring(parts[relpath]);rt={r.get('Id'):r.get('Target') for r in rels}
                for tp in part:
                    target=rt[tp.get('{'+R+'}id')];p=str((Path(paths[sheet]).parent/target)).replace('\\','/')
                    p=os.path.normpath(p).replace('\\','/').lstrip('/')
                    if target.startswith('/'):p=target.lstrip('/')
                    tab=etree.fromstring(parts[p]);tab.set('ref',re.sub(r'\d+$',str(maxrow),tab.get('ref')))
                    af=tab.find(q('autoFilter'))
                    if af is not None:af.set('ref',tab.get('ref'))
                    parts[p]=etree.tostring(tab,encoding='utf-8')
        parts[paths[sheet]]=etree.tostring(root,encoding='utf-8')
    if links:
        for sheet,items in links.items():
            p=paths[sheet];root=etree.fromstring(parts[p]);hyper=root.find(q('hyperlinks'))
            if hyper is None:
                hyper=etree.Element(q('hyperlinks'));idx=next((i for i,n in enumerate(root) if n.tag in [q('pageMargins'),q('pageSetup'),q('tableParts')]),len(root));root.insert(idx,hyper)
            rp=str(Path(p).parent/'_rels'/(Path(p).name+'.rels')).replace('\\','/')
            rels=etree.fromstring(parts[rp]) if rp in parts else etree.Element('{'+P+'}Relationships',nsmap={None:P})
            for address,target in items.items():
                h=next((h for h in hyper if h.get('ref')==address),None)
                if h is not None:
                    rid=h.get('{'+R+'}id');rel=next((r for r in rels if r.get('Id')==rid),None)
                else:
                    rid='mappingReview'+str(len(rels)+1);h=etree.SubElement(hyper,q('hyperlink'),ref=address);h.set('{'+R+'}id',rid);rel=None
                if rel is None:rel=etree.SubElement(rels,'{'+P+'}Relationship',Id=rid,Type=R+'/hyperlink',TargetMode='External')
                rel.set('Target',target)
            parts[rp]=etree.tostring(rels,encoding='utf-8');parts[p]=etree.tostring(root,encoding='utf-8')
    save_package(dest,infos,parts)
