"""Bind the existing signed negative review to the explicitly included candidate.

No scientific content, signature, date, verdict or reason is authored here.
The source review cell is copied byte-for-byte; separate provenance records
the researcher's explicit extension to every canonical LME026 model.
"""
from pathlib import Path
from zipfile import ZipFile
from copy import deepcopy
from datetime import datetime,timezone
from html import escape
import argparse,hashlib,json,re,sys
from lxml import etree as E

SCRIPT=Path(__file__).resolve();RUN=SCRIPT.parents[1];MODEL=RUN.parents[2]
ROOT=next(p for p in MODEL.parents if (p/'Project.xlsx').is_file())
ORIGINAL=MODEL.parent/'Piroddi_2022_Mediterranean_1995'
SOURCE=ORIGINAL/'model_validation/validation.docx';TEMPLATE=ROOT/'tools/templates/validation.docx'
STAGED=RUN/'outputs/validation.docx';FINAL=MODEL/'model_validation/validation.docx'
EVIDENCE=MODEL/'model_validation/evidence/source_review/researcher_review_20261114'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main';NS={'w':W}
SOURCE_SHA='092dafe37aa0125198f63b61da8d41f88e30fe9a87d675f0109327f886fef0a5'
MODEL_SHA='281d8543a165bf67652168cbc47f09db224e51bddb6768e9365f8c52d03ac956'
ORIGINAL_SHA='f038707bf7837962933eec3e6daeae53eb0b9a7f48837763b0ce621edcdc3a9e'
QUOTE='all models for this region are disqualified for the reason I mentioned'
ROOT_CHAT='01a1daa4-cbff-7830-8cb0-b8342b49ec5d'
ROOT_MESSAGE='01a1db40-1b39-7aa2-aaad-562fd6b1dc4e'
sys.path.insert(0,str(ROOT))
from tools.project_core.validation.researcher_review import read_report,table_rows
from tools.project_core.registry.discovery import discover_models

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf8'))
def rel(path,base=MODEL):return Path(path).resolve().relative_to(Path(base).resolve()).as_posix()
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def require(test,message):
    if not test:raise ValueError(message)
def text(node):return ''.join(node.xpath('.//w:t/text()',namespaces=NS))
def opening(xml):return re.search(r'<w:document\b[^>]*>',xml).group()
def rows(xml):
    result={}
    for raw in re.findall(r'<w:tr(?:\s[^>]*)?>.*?</w:tr>',xml,re.S):
        cells=re.findall(r'<w:tc(?:\s[^>]*)?>.*?</w:tc>',raw,re.S)
        if len(cells)!=2:continue
        tree=E.fromstring((opening(xml)+'<w:body>'+raw+'</w:body></w:document>').encode())
        label=text(tree.find('.//w:tc',NS));result[label]=(raw,cells)
    return result
def replace_cell(cell,value):
    # Reuse the real template's first paragraph and run properties, with one
    # plain text value. Other template paragraphs are deliberately out of scope.
    properties=re.search(r'<w:tcPr>.*?</w:tcPr>',cell,re.S).group()
    paragraph=re.search(r'<w:p(?:\s[^>]*)?>.*?</w:p>',cell,re.S).group()
    pp=re.search(r'<w:pPr>.*?</w:pPr>',paragraph,re.S)
    rp=re.search(r'<w:rPr>.*?</w:rPr>',paragraph,re.S)
    return '<w:tc>'+properties+'<w:p>'+(pp.group() if pp else '')+'<w:r>'+(rp.group() if rp else '')+'<w:t xml:space="preserve">'+escape(value)+'</w:t></w:r></w:p></w:tc>'
def make_row(template_row,left,right,*,raw_right=False):
    raw,cells=template_row
    prefix=raw[:raw.index(cells[0])];suffix=raw[raw.index(cells[1])+len(cells[1]):]
    return prefix+replace_cell(cells[0],left)+(right if raw_right else replace_cell(cells[1],right))+suffix
def para(value):
    return '<w:p><w:pPr><w:spacing w:before="140" w:after="100"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="21"/></w:rPr><w:t xml:space="preserve">'+escape(value)+'</w:t></w:r></w:p>'
def guards():
    require(sha(SOURCE)==SOURCE_SHA,'Original signed source changed')
    require(sha(MODEL/'model.json')==MODEL_SHA and sha(ORIGINAL/'model.json')==ORIGINAL_SHA,'Canonical input changed')
    models=discover_models(ROOT/'regions/LME/LME_026')
    require(set(models)=={MODEL.name,ORIGINAL.name},'Canonical scope changed')

def prepare():
    guards();require(not FINAL.exists(),'Candidate review already exists; do not overwrite')
    require(not STAGED.exists(),'Prepared document already exists')
    with ZipFile(SOURCE) as z:source=z.read('word/document.xml').decode('utf8')
    with ZipFile(TEMPLATE) as z:
        template=z.read('word/document.xml').decode('utf8');parts=[(i,z.read(i.filename)) for i in z.infolist()]
    signed=rows(source)['Review and reproducibility'][1][1]
    require('w:hyperlink' not in signed and 'r:id' not in signed,'Signed cell contains external relationships requiring dedicated copy')
    tr=rows(template);body=E.fromstring(template.encode()).find('w:body',NS)
    title=re.search(r'<w:p(?:\s[^>]*)?>.*?</w:p>',template,re.S).group()
    title=re.sub(r'<w:t[^>]*>.*?</w:t>','<w:t>Mediterranean pooled model disqualification</w:t>',title,count=1,flags=re.S)
    table=re.search(r'<w:tbl(?:\s[^>]*)?>.*?</w:tbl>',template,re.S).group()
    table_start=table[:table.index('<w:tr')]
    grid=tr['Field'][0]+make_row(tr['Region'],'Region','Mediterranean Sea, LME_026')+make_row(tr['Selected model'],'Candidate model',MODEL.name)+make_row(tr['Review and reproducibility'],'Review and reproducibility',signed,raw_right=True)
    sect=re.search(r'<w:sectPr\b.*?</w:sectPr>',template,re.S).group()
    intro=para('Researcher disqualification for the pooled Mediterranean 1995 candidate identified below.')
    provenance=para('On 14 November 2026 the researcher clarified: “'+QUOTE+'”. This candidate-specific decision record reproduces the signed review entry unchanged from the original Mediterranean model report. It records the disqualification decision only.')
    # Preserve original source namespace declarations so its review cell remains
    # literal XML; all template styles, theme, layout and other ZIP parts remain.
    output='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'+opening(source)+'<w:body>'+title+intro+table_start+grid+'</w:tbl>'+provenance+sect+'</w:body></w:document>'
    E.fromstring(output.encode())
    STAGED.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(STAGED,'w') as z:
        for info,data in parts:z.writestr(info,output.encode() if info.filename=='word/document.xml' else data)
    authorization={'schema_version':1,'kind':'explicit_region_wide_disqualification_applicability','unit_id':'LME_026','model_id':MODEL.name,'created_utc':datetime.now(timezone.utc).isoformat(),
        'human_authorization':{'chat_id':ROOT_CHAT,'message_id':ROOT_MESSAGE,'quote':QUOTE,'question_context':'Clarification explicitly asked whether existing Ido Carmel 14/11/2026 signature and disqualification reason apply to pooled candidate despite original model identity in signed report','verification':'Actual userMessage read through read_thread; quote preserved verbatim'},
        'original_handoff':{'chat_id':'01a1dac3-5159-7640-853c-732622460a5c','message_id':'01a1db39-70cd-7760-8f7d-707cd08609c6','quote':'I disqualified this model.\nupdate the coordinator and let it handle the updating of project.xlsx, the map, and trends\n'},
        'existing_signed_source':{'repository_relative_path':rel(SOURCE,ROOT),'sha256':SOURCE_SHA,'review_cell_xml_sha256':hashlib.sha256(signed.encode()).hexdigest()},
        'template':{'repository_relative_path':rel(TEMPLATE,ROOT),'sha256':sha(TEMPLATE)},
        'canonical_scope':[{'model_id':ORIGINAL.name,'sha256':ORIGINAL_SHA},{'model_id':MODEL.name,'sha256':MODEL_SHA}],
        'derived_source':{'model_relative_path':'model_validation/validation.docx','sha256':sha(STAGED),'purpose':'Exact model binding of the same explicitly broadened negative decision; no copied scientific approval sections'},
        'preservation':{'signed_review_cell_copied_verbatim':True,'original_signed_DOCX_unchanged':True,'canonical_models_unchanged':True,'selection_unchanged':True,'scientific_results_unchanged':True,'new_signature_date_reason_authored':False,'new_calculations':False,'sensitivity_adopted':False},
        'registration':{'researcher_name':'Ido Carmel','researcher_review_date':'2026-11-14','status':'Disqualified by researcher','excluded_seq':[],'scope_for_candidate':'model_source','Project_and_views_written_by_this_task':False}}
    write(RUN/'outputs/authorization.json',authorization)
    metadata={'unit_id':'LME_026','model_id':MODEL.name,'model_path':rel(MODEL/'model.json',ROOT),'selected':False,'paper_ids':'MED-2022__LME_026','model_year':1995,'model_years':'1995','publication_year':2022,'doi':'10.1038/s41598-022-18017-x',
        'variant':'Derived model with 69 unchanged non-detrital groups and one pooled Discards and Detritus compartment; explicit pooled routing assumption retained in model-local provenance.'}
    write(RUN/'outputs/proposed_central_metadata.json',{'row':metadata,'unknown_fields_remain_blank':['source_filename','model_area_km2','target_coverage_ratio','coverage_class','coverage_note','production_eligible','configuration','diagnostic_grades'],
        'provenance':{'paper_article_id':'MED-2022__LME_026','paper_row_at_inspection':189,'existing_original_model_row_at_inspection':40,'canonical_sha256':MODEL_SHA,'model_notes_sha256':sha(MODEL/'model_notes.md')},
        'review_to_register_with_supported_helper':{'report':rel(FINAL,ROOT),'excluded_seq':[]},'no_Project_mutation_performed':True})
    return verify()

def verify():
    guards()
    with ZipFile(SOURCE) as z:source=z.read('word/document.xml').decode('utf8')
    with ZipFile(STAGED) as z:
        output=z.read('word/document.xml').decode('utf8');require(z.testzip() is None,'Bad DOCX ZIP')
        with ZipFile(TEMPLATE) as t:
            require(set(z.namelist())==set(t.namelist()),'Unexpected package parts')
            require(all(z.read(n)==t.read(n) for n in z.namelist() if n!='word/document.xml'),'Template package part changed outside content')
    require(rows(output)['Review and reproducibility'][1][1]==rows(source)['Review and reproducibility'][1][1],'Signed cell XML changed')
    require(set(rows(output))=={'Field','Region','Candidate model','Review and reproducibility'},'Unexpected scientific fields in decision record')
    name,date,summary=read_report(ROOT,STAGED,MODEL.name)
    old_name,old_date,old_summary=read_report(ROOT,SOURCE,ORIGINAL.name)
    require(name==old_name and date==old_date,'Signer/date changed')
    require(summary=={**old_summary,'model_id':MODEL.name},'Decision changed beyond model identity')
    require(summary['status']=='Disqualified by researcher' and summary['sections']==[],'Unexpected positive review content')
    auth=read(RUN/'outputs/authorization.json');require(auth['derived_source']['sha256']==sha(STAGED),'Authorization source binding changed')
    proof={'passed':True,'staged_sha256':sha(STAGED),'original_source_sha256':SOURCE_SHA,'signed_cell_XML_exact':True,'template_styles_and_parts_exact':True,'parser_output':[name,date,summary],'builder_sha256':sha(SCRIPT),'scientific_changes':False}
    write(RUN/'qa/structural_verification.json',proof);return proof

def install():
    proof=verify();visual=read(RUN/'qa/visual_qa.json')
    require(visual['passed'] is True and visual['docx_sha256']==sha(STAGED),'Visual QA required before canonical save')
    require(not FINAL.exists(),'Candidate source unexpectedly appeared')
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    require(not (EVIDENCE/'authorization.json').exists(),'Authorization source unexpectedly appeared')
    guards()
    with FINAL.open('xb') as stream:stream.write(STAGED.read_bytes())
    with (EVIDENCE/'authorization.json').open('xb') as stream:stream.write((RUN/'outputs/authorization.json').read_bytes())
    require(sha(FINAL)==proof['staged_sha256'],'Installed report differs')
    require(read_report(ROOT,FINAL,MODEL.name)==read_report(ROOT,STAGED,MODEL.name),'Canonical parser result differs')
    guards();proof['canonical_report']=rel(FINAL,ROOT);proof['authorization']=rel(EVIDENCE/'authorization.json',ROOT)
    write(RUN/'qa/completion.json',proof);return proof

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['prepare','verify','install']);args=parser.parse_args()
    print(json.dumps(globals()[args.command](),ensure_ascii=False))
