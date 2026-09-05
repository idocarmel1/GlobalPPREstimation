import zipfile,xml.etree.ElementTree as E,json,pathlib,sys
p=pathlib.Path(sys.argv[1]); w=p/'extracted/work'; ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
z=zipfile.ZipFile(p/'pone.0094742.s001-eb18ca66.docx'); root=E.fromstring(z.read('word/document.xml')); blocks=[];tables=[]
for el in root.find('w:body',ns):
 if el.tag.endswith('}p'):
  t=''.join(el.itertext()) if False else ''.join(x.text or '' for x in el.findall('.//w:t',ns))
  blocks.append(t)
 if el.tag.endswith('}tbl'):
  rows=[[''.join(t.text or '' for t in c.findall('.//w:t',ns)) for c in r.findall('w:tc',ns)] for r in el.findall('w:tr',ns)]
  tables.append(rows); blocks.append('TABLE '+str(len(tables))+'\n'+'\n'.join('\t'.join(r) for r in rows))
(w/'supplement.txt').write_text('\n'.join(blocks),encoding='utf-8');(w/'docx_tables.json').write_text(json.dumps(tables,ensure_ascii=False,indent=2),encoding='utf-8')
print('tables',[(i+1,len(t),len(t[0]),t[0]) for i,t in enumerate(tables)])
for x in p.glob('*.xls'):print(x.name,x.read_bytes()[:100])
