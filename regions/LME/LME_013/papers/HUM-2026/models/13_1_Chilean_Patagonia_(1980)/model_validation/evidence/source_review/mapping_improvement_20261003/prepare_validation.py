from pathlib import Path
from copy import deepcopy
from collections import defaultdict
from zipfile import ZipFile
from lxml import etree
import json,sys,math,openpyxl,hashlib
sys.stdout.reconfigure(encoding='utf-8')
OUT=Path(__file__).parent;ROOT=OUT.parents[4];REG=ROOT/'regions/LME_013'
from ooxml_preserve import package,save_package
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main';R='http://schemas.openxmlformats.org/officeDocument/2006/relationships';P='http://schemas.openxmlformats.org/package/2006/relationships';NS={'w':W}
def q(n):return '{'+W+'}'+n
def text(n):return ''.join(n.xpath('.//w:t/text()',namespaces=NS))
def canon(n):return etree.tostring(n,method='c14n')
sys.path.insert(0,str(ROOT/'tools'))
from validation_percentage_format import format_percent
def pct(v):return format_percent(v)
def load(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
ledger=load('decision_ledger.json');bytaxon={r['taxon']:r for r in ledger};summary=load('comparison_summary.json')
book=openpyxl.load_workbook(OUT/'baseline/LME013_taxon_mapping_appendix.xlsx');sh=book['Taxon mapping'];sources=book['Sources']
updates={'Taxon mapping':{},'Sources':{}};links={'Taxon mapping':{},'Sources':{}}
for ri in range(8,sh.max_row+1):
    taxon=sh.cell(ri,1).value;r=bytaxon[taxon]
    reason=r.get('appendix_reason',r['reason'])
    if r['classic_sppr_wet'] is None:reason+=' Classic coefficient unavailable; zero 2019 catch makes the annual contribution zero.'
    updates['Taxon mapping'].update({f'E{ri}':'; '.join(v['group']+' ('+format(v['weight']*100,'.6f')+'%)' for v in r['new_mappings'] if v['weight']>0),f'F{ri}':r['overall_confidence'],f'G{ri}':reason+' See the reassessment evidence on Sources.'})
vl=next(r for r in summary['revised_confidence'] if r['label']=='Very low')
updates['Taxon mapping']['A5']=f"Landings {summary['total_catch_tonnes']:.6f} t; classic PPR {summary['total_simple_chain_ppr_tC']:.6f} t C. Confidence uses the weaker membership/allocation component. Very low: {vl['taxa']} labels, {vl['ppr_percentage']:.6f}% of classic PPR."
updates['Sources']['B5']='PDF4 Table1 supplies operative membership; Table3/PDF6 supplies printed inputs. S1–S7 are now retained and reviewed: calibration/vulnerability/pedigree tables add no species-membership inventory. Source and accepted runtime values remain distinct.'
updates['Sources']['D5']='2026-10-03'
catalogue=load('source_catalogue.json')
new_start=sources.max_row+1
for i,item in enumerate(catalogue,new_start):
    for j,k in enumerate(['description','supports','label','date'],1):updates['Sources'][openpyxl.utils.get_column_letter(j)+str(i)]=item.get(k,'Open source' if k=='label' else '2026-10-03' if k=='date' else '')
    links['Sources']['C'+str(i)]=item['target']
links['Taxon mapping']['D6']='validation_reports/13_1_Chilean_Patagonia_(1980)/mapping_improvement_20261003/decision_ledger.json'
(OUT/'appendix_updates.json').write_text(json.dumps(updates,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'appendix_links.json').write_text(json.dumps(links,ensure_ascii=False,indent=2),encoding='utf-8')
# OOXML fragment edits preserve the original main grid, manual fields and assets.
assert hashlib.sha256((REG/'Model_validation_13_1_Chilean_Patagonia_(1980).docx').read_bytes()).hexdigest()==hashlib.sha256((OUT/'baseline/Model_validation_13_1_Chilean_Patagonia_(1980).docx').read_bytes()).hexdigest(),'concurrent researcher document edit'
infos,parts=package(OUT/'baseline/Model_validation_13_1_Chilean_Patagonia_(1980).docx');xml=etree.fromstring(parts['word/document.xml']);body=xml.find(q('body'));tables=body.findall(q('tbl'));main=tables[0]
mainrows={text(row.find(q('tc'))):row for row in main.findall(q('tr'))[1:]}
manual_names=['SPPR calculation','Open issues and next action','Review and reproducibility']
manual_before={name:canon(mainrows[name]) for name in manual_names}
main_before={name:canon(row) for name,row in mainrows.items()}
rels=etree.fromstring(parts['word/_rels/document.xml.rels'])
def paragraph(value,template):
    p=deepcopy(template);oldrp=p.find('w:r/w:rPr',NS)
    for n in list(p):
        if n.tag!=q('pPr'):p.remove(n)
    r=etree.SubElement(p,q('r'))
    if oldrp is not None:r.append(deepcopy(oldrp))
    t=etree.SubElement(r,q('t'));t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=value
    return p
def replace_p(p,value,keep_links=True):
    n=paragraph(value,p)
    if keep_links:
        for l in p.findall(q('hyperlink')):
            r=etree.SubElement(n,q('r'));t=etree.SubElement(r,q('t'));t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text='  ';n.append(deepcopy(l))
    p.getparent().replace(p,n);return n
def add_link(p,label,target):
    rid='mappingImprovement'+str(len(rels)+1);etree.SubElement(rels,'{'+P+'}Relationship',Id=rid,Type=R+'/hyperlink',Target=target,TargetMode='External')
    gap=etree.SubElement(p,q('r'));etree.SubElement(gap,q('t')).text='  '
    h=etree.SubElement(p,q('hyperlink'));h.set('{'+R+'}id',rid);r=etree.SubElement(h,q('r'));rp=etree.SubElement(r,q('rPr'));etree.SubElement(rp,q('color')).set(q('val'),'0000FF');etree.SubElement(rp,q('u')).set(q('val'),'single');etree.SubElement(r,q('t')).text=label
def set_cell(cell,value):
    ps=cell.findall(q('p'));template=ps[0]
    for n in list(cell):
        if n.tag!=q('tcPr'):cell.remove(n)
    cell.append(paragraph(value,template))
def set_table(table,data):
    oldrows=table.findall(q('tr'));template=oldrows[1]
    for row in oldrows[1:]:table.remove(row)
    for i,vals in enumerate(data):
        row=deepcopy(oldrows[i+1] if i+1<len(oldrows) else template)
        for cell,val in zip(row.findall(q('tc')),vals):set_cell(cell,str(val))
        table.append(row)
set_table(tables[1],[[r['label'],r['taxa'],pct(r['catch_percentage']),pct(r['ppr_percentage'])] for r in summary['revised_confidence']])
rule_words={
'M1':'Explicit named source membership or combined source stages.',
'M2':'Verified synonym or spelling of a source-listed taxon.',
'M3':'Unambiguous fit to an explicit source definition.',
'M4':'Supported extension from listed related source taxa.',
'M5':'Supported ecological assignment with an explicit source or reporting inference.',
'M6':'Partial ecological fit or conflicting regional habitat/reporting evidence.',
'M7':'Broad reporting category with observed composition transferred to this catch.',
'M8':'No defensible source-group assignment.',
'M9':'Regional reporting and ecology support an assumed eligible group set.',
'M10':'Broad-category approximation over compatible represented pools.',
'M11':'Closest represented taxonomic or ecological analogue; mismatches remain.',
'M12':'Documented nearby-model mapping crosswalk.',
'W1':'One reviewed group; no numerical split.',
'W4':'Complete historical source-model catch proportions; composition transfer assumed.',
'W9':'Incomplete source catches rejected; complete model biomass proportions with composition and catchability assumptions.',
'W2':'Applicable observed caught-mass composition.',
'W3':'Observed caught-mass composition transferred across periods or fisheries.',
'W10':'Applicable direct source geographic caught-mass allocation.',
'W11':'Explicit last-resort numerical allocation.',
'W8':'No usable numerical allocation.'}
for table,key in [(tables[2],'membership_summary'),(tables[3],'allocation_summary')]:set_table(table,[[rule_words[r['rule']],r['confidence'],pct(r['ppr_percentage'])] for r in summary[key]])
paras=body.findall(q('p'))
for p in list(paras):
    t=text(p)
    if t.startswith('Unresolved taxa:'):
        squid_share=100*bytaxon['Dosidicus gigas']['simple_chain_ppr_tC']/summary['total_simple_chain_ppr_tC']
        replace_p(p,f"Unresolved taxa: none. The {vl['taxa']} Very low decisions account for {vl['catch_percentage']:.4f}% of landings and {vl['ppr_percentage']:.4f}% of simple-chain PPR. Dosidicus gigas alone contributes {squid_share:.4f}%. Squid and unrepresented fish/ray compartments remain consequential analogues. Full mapping coverage does not establish ecological validity.")
    elif t.startswith('Membership evidence:'):
        np=replace_p(p,'Membership evidence: exact source definitions, historical taxonomy and regional reporting scope.');add_link(np,'Current reassessment','validation_reports/13_1_Chilean_Patagonia_(1980)/mapping_improvement_20261003/decision_ledger.json')
    elif t.startswith('Weights and assumptions:'):
        np=replace_p(p,'Weights and assumptions: Hoki retains the historical source landings split; other complete catch proxies and biomass fallbacks remain fixed across years and bases. Their precision does not establish observed composition.');add_link(np,'Reviewed allocations','validation_reports/13_1_Chilean_Patagonia_(1980)/mapping_improvement_20261003/allocation_residual_review.json')
# Replace only the factual obsolete supplement sentence in the existing extraction entry.
row=mainrows['Model extraction']
old_sentence='Referenced supplements S1–S7 are absent from the retained source set.'
for node in row.xpath('.//w:t',namespaces=NS):
    if node.text and old_sentence in node.text:node.text=node.text.replace(old_sentence,'Supplementary S1–S7 are now retained; calibration and pedigree tables add no species-membership inventory.')
# Reuse existing decision groupings, remove upgraded labels, and append distinct new
# Very low cases or changed numeric decisions with their own exact reasons.
old_decisions=load('baseline_document.json')['tables'][4][1:];vlset=set(summary['very_low_taxa']);covered=set();rows=[]
for labels,reason in old_decisions:
    names=[t.strip() for t in labels.split(';') if t.strip() in vlset and not bytaxon[t.strip()]['numerical_mapping_changed']]
    if names:rows.append(['; '.join(names),reason]);covered.update(names)
for name in sorted(vlset-covered):rows.append([name,bytaxon[name].get('very_low_reason',bytaxon[name]['reason'])])
assert {n.strip() for names,reason in rows for n in names.split(';')}==vlset
assert sum(len(names.split(';')) for names,reason in rows)==len(vlset)
set_table(tables[4],rows)
for name in manual_names:assert canon(mainrows[name])==manual_before[name]
for name in main_before:
    if name!='Model extraction':assert canon(mainrows[name])==main_before[name],name
parts['word/document.xml']=etree.tostring(xml,encoding='utf-8',xml_declaration=True,standalone=True)
parts['word/_rels/document.xml.rels']=etree.tostring(rels,encoding='utf-8',xml_declaration=True,standalone=True)
save_package(REG/'Model_validation_13_1_Chilean_Patagonia_(1980).docx',infos,parts)
(OUT/'document_edit_scope.json').write_text(json.dumps({'manual_cells_preserved':manual_names,'main_grid_unchanged_except':'factual obsolete S1–S7 absence sentence','coverage_derived_from':'decision_ledger.json','very_low_taxa':len(vlset),'very_low_rows':len(rows),'changed_zip_parts':['word/document.xml','word/_rels/document.xml.rels']},indent=2),encoding='utf-8')
print('Validation patched. Very low rows:',len(rows),'taxa:',len(vlset),'new Sources:',len(catalogue))
