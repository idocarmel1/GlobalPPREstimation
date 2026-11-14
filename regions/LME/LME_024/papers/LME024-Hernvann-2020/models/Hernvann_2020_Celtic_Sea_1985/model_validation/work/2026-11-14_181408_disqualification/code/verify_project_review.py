import sys,json,hashlib,io,zipfile
from pathlib import Path
from xml.etree import ElementTree as E
root=Path.cwd().resolve();sys.path.insert(0,str(root))
from tools.project_core.validation.researcher_review import table_rows,read_report,column_index,S
work=Path(__file__).resolve().parents[1]
packet=json.loads((work/'outputs/signed_review_packet.json').read_text(encoding='utf-8'))
raw=(root/'Project.xlsx').read_bytes()
with zipfile.ZipFile(io.BytesIO(raw)) as z:
 sheet,headers,_,rows=table_rows(z,'Models & coverage','Models')
 matches=[(r,d) for r,d in rows if d.get('unit_id')==packet['unit_id'] and d.get('model_id')==packet['model_id']]
 assert len(matches)==1
 row,data=matches[0]
 styles=E.fromstring(z.read('xl/styles.xml'));fonts=styles.find('{'+S+'}fonts');xfs=styles.find('{'+S+'}cellXfs')
 colors={}
 for field in ('model_id','researcher_review_status'):
  cell=next((c for c in row if column_index(c.get('r'))==headers.index(field)+1),None)
  if cell is not None:
   xf=xfs[int(cell.get('s','0'))];font=fonts[int(xf.get('fontId','0'))];color=font.find('{'+S+'}color');colors[field]=color.attrib if color is not None else {}
summary=json.loads(data.get('researcher_review_summary') or '{}')
expected={'researcher_review_status':'Disqualified by researcher','researcher_name':packet['researcher_name'],'researcher_review_date':packet['review_date'],'validation_report_path':packet['report_path'],'validation_report_sha256':packet['report_sha256'],'reviewed_model_sha256':packet['canonical_sha256']}
checks={k:data.get(k)==v for k,v in expected.items()}
checks.update({'exact_verdict':summary.get('verdict')==packet['summary']['verdict'],'exact_reason':summary.get('reason')==packet['summary']['reason'],'no_approved_sections':summary.get('sections')==[],'no_display_exclusions':summary.get('excluded_group_ids')==[],'model_and_status_red':all(colors.get(f,{}).get('rgb')=='FFB42318' for f in ('model_id','researcher_review_status')),'source_docx_unchanged':hashlib.sha256((root/packet['report_path']).read_bytes()).hexdigest()==packet['report_sha256']})
result={'registered':all(checks.values()),'project_sha256':hashlib.sha256(raw).hexdigest(),'row_number':row.get('r'),'observed':{k:data.get(k) for k in expected},'summary':summary,'checks':checks,'colors':colors}
(work/'outputs/project_readback.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
