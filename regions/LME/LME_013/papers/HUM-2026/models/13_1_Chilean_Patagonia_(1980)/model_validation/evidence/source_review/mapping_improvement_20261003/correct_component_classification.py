from pathlib import Path
from collections import defaultdict
from copy import deepcopy
from lxml import etree
import sys,json,math,hashlib
from ooxml_preserve import package,save_package
sys.stdout.reconfigure(encoding='utf-8');OUT=Path(__file__).parent;REG=OUT.parents[2]
ROOT=OUT.parents[4];sys.path.insert(0,str(ROOT/'tools'))
from validation_percentage_format import format_percent
def load(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def save(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
names={'Auxis','Clupeidae','Clupeiformes'};ledger=load('decision_ledger.json');review=load('reconciled_decisions.json');journal=[]
for r in ledger:
    if r['taxon'] in names:
        assert r['membership_rule']=='M7' and r['membership_confidence']=='Medium'
        reason='Regional composition is explicitly assumed and unmeasured in the review evidence. M7 requires observed composition; M9 describes the supported assumed eligible group set. Groups, weights and component/overall confidence are unchanged.'
        journal.append({'taxon':r['taxon'],'proposed_rule':'M7','adopted_rule':'M9','reason':reason})
        r['membership_rule']='M9';r['parent_component_adjudication']=reason
        review[r['taxon']]['membership_rule']='M9';review[r['taxon']]['parent_component_adjudication']=reason
save('decision_ledger.json',ledger);save('reconciled_decisions.json',review)
adopted=load('adopted_tables.json');changes=load('regional_changed_blocks.json');metadata={}
for sheet,table in [('PPR','Mapping review'),('Diagnostics','Taxon mapping validation')]:
    h,rows=adopted[sheet][table];ti=h.index('taxon');mi=h.index('membership_rule')
    for r in rows:
        if r[ti] in names:r[mi]='M9'
    changes[sheet][table]=[h,rows];metadata.setdefault(sheet,{})[table]=[h,rows]
save('adopted_tables.json',adopted);save('regional_changed_blocks.json',changes);save('classification_changed_blocks.json',metadata)
summary=load('comparison_summary.json');totals=defaultdict(lambda:{'taxa':0,'ppr_tC':0.0})
for r in ledger:
    v=totals[r['membership_rule'],r['membership_confidence']];v['taxa']+=1;v['ppr_tC']+=r['simple_chain_ppr_tC'] or 0
summary['membership_summary']=sorted([{'rule':rule,'confidence':conf,'taxa':d['taxa'],'ppr_percentage':100*d['ppr_tC']/summary['total_simple_chain_ppr_tC']} for (rule,conf),d in totals.items()],key=lambda r:-r['ppr_percentage'])
save('comparison_summary.json',summary)
# Patch this one derived Word table; all other nodes/parts are retained.
doc=REG/'Model_validation_13_1_Chilean_Patagonia_(1980).docx';before=hashlib.sha256(doc.read_bytes()).hexdigest()
infos,parts=package(doc);W='http://schemas.openxmlformats.org/wordprocessingml/2006/main';NS={'w':W};q=lambda n:'{'+W+'}'+n
xml=etree.fromstring(parts['word/document.xml']);table=xml.find(q('body')).findall(q('tbl'))[2];oldrows=table.findall(q('tr'))
phrases={'M11':'Closest represented taxonomic or ecological analogue; mismatches remain.','M1':'Explicit named source membership or combined source stages.','M5':'Supported ecological assignment with an explicit source or reporting inference.','M4':'Supported extension from listed related source taxa.','M3':'Unambiguous fit to an explicit source definition.','M10':'Broad-category approximation over compatible represented pools.','M9':'Regional reporting and ecology support an assumed eligible group set.','M6':'Partial ecological fit or conflicting regional habitat/reporting evidence.','M2':'Verified synonym or spelling of a source-listed taxon.'}
for row in oldrows[1:]:table.remove(row)
for i,r in enumerate(summary['membership_summary']):
    row=deepcopy(oldrows[min(i+1,len(oldrows)-1)])
    for cell,value in zip(row.findall(q('tc')),[phrases[r['rule']],r['confidence'],format_percent(r['ppr_percentage'])]):
        p=cell.find(q('p'));rp=p.find('w:r/w:rPr',NS)
        for n in list(p):
            if n.tag!=q('pPr'):p.remove(n)
        run=etree.SubElement(p,q('r'))
        if rp is not None:run.append(deepcopy(rp))
        etree.SubElement(run,q('t')).text=value
        for extra in cell.findall(q('p'))[1:]:cell.remove(extra)
    table.append(row)
parts['word/document.xml']=etree.tostring(xml,encoding='utf-8',xml_declaration=True,standalone=True)
assert hashlib.sha256(doc.read_bytes()).hexdigest()==before,'concurrent document edit'
save_package(doc,infos,parts);save('component_classification_adjudication.json',journal)
print('Three assumed-composition rules corrected; no numerical inputs or results changed.')
