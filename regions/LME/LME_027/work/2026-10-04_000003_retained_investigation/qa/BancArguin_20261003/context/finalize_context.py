from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E
out=Path(__file__).resolve().parent
root=out.parents[4]
paper=root/'regions/LME_027/papers/CAN-2014'
recovery=paper/'recovery_20261003'
src=json.loads((paper/'extracted/work/docx_tables.json').read_text(encoding='utf8'))[9]
native=E.parse(recovery/'ecobase689_input.xml').getroot()
ng={int(g.findtext('group_seq')):g for g in native.findall('./group_descr/group')}
s8=[]
for row in src:
 if not row[0].isdigit():continue
 n=int(row[0]);s8.append({'group_id':n,'name':row[1],'M30_B':row[5],'M30_EE':row[6],'Base_B':row[7],'Base_EE':row[8],'P30_B':row[9],'P30_EE':row[10],'native_B':ng[n].findtext('biomass'),'native_EE':ng[n].findtext('ee')})
(out/'native689_vs_S8.json').write_text(json.dumps(s8,indent=2),encoding='utf8')
summary={
 'schema_version':1,'access_date':'2026-10-03','source_doi':'10.1371/journal.pone.0094742',
 'recovered_native':'EcoBase689 Mauritanie 1991; exact authors/publication and51groups; distinct deposited numerical variant, not adopted as source Base/M30/P30',
 'native_findings':[
  'Complete input XML includes51groups, diets/import, flags,6multi-stanza records,4fleets and stock-level BA splits; output XML includes51groups.',
  'All multi-stanza life-stage z tags are0, while group pb equals printed Z. Stage ages13months and bab_split parameters recovered, but flat PB interpretation is not justified by native tag naming.',
  'Fourth fleet carries10BA/plants removals matching group export fields. It cannot be relabeled ordinary commercial catch or counted twice.',
  'Native diet resolves printed Groupers ad–BA L crustaceans1.34 as0.1399813 and Coastal birds–shelf molluscs blank as0.02 in this deposit only. Source publication remains unchanged.',
  'Native B/EE conflict with both Table1 and S8 Base: BA phytoplankton EE0.428428173 vs Table1 0.260 and S8Base0.40; BA L crustaceans EE0.9463351 vs0.877 and0.88; BA macrozooplankton B2.60428452 vs2.5/2.50. Deposit is not demonstrated identical to a named published variant.'
 ],
 'publisher_search':{'xml':'../../../papers/CAN-2014/recovery_20261003/publisher_article.xml','outcome':'One linked S1 DOCX; fresh file SHA256 identical to retained eb18ca6633d0440941039fea12b6b827eee8b7e7a9e316875c2b3563b1926a8c'},
 'figshare_search':{'query':'10.1371/journal.pone.0094742','api':'https://api.figshare.com/v2/articles/search','outcome':'12 linked records:9figures,Table1,Table2,FileS1; no extra scenario matrices/native attachments','file_S1_article':996672,'file_S1_download_id':1461558},
 'institutional_search':{'thesis':'https://www.imrop.mr/wp-content/uploads/2021/01/these_-beyah-VF-1.pdf','outcome':'220page institutional thesis reproduces article PDF181–196 and supplements including S8 PDF213–214. No separate complete M30/P30 matrix located.','conference':'https://halieutique.institut-agro.fr/files/fichiers/pdf/4892.pdf','conference_outcome':'Identifies later2010 model updated from1991–2006 usingMeissa2013 stock assessments; incompatible date/parameter state, not a missing1991scenario export.'},
 'predecessor_search':{'references':['Ould Taleb Ould Sidi & Guénette 2003/2004 Mauritanian EEZ1987/1998','Ould Taleb Ould Sidi & Diop 2003/2004 Banc d Arguin1988–1998'],'outcome':'Article distinguishes these older wholeEEZ/park-only models from its new shelf/Banc structure. Official EcoBase listing confirms distinct periods. No explicit lineage authorizes transferring missing Base/M30/P30diet cells from them.'},
 'missing_after_bounded_search':['Complete M30 and P30diet/import matrices corresponding to S8 settings','Author-confirmed relationship between deposited EcoBase689 and published Base/M30/P30','Unambiguous flat-model P/B for multistanza stage groups'],
 'source_scope':'No author contact or numerical repairs; no regional workbook,selection,map or model directory written by context owner.',
 'geography_report_text':'A. Region covered by study: approximately3.0% (about2.5–3.5%). B. Study area covered by region: approximately95–100%.',
 'geography_detail':'Original study area33,224km², coast-to200m shelf, articleMethods PDF2 andFigure1 PDF3. Land-excluded trace≈35,510km² and99.16%within LME; geodesic LMEarea1,123,611.8km². Footprint rectangle is not source polygon; its legacy9%claim not independently reproduced.',
 'context_record':'workbook_context.json',
 'researcher_status':'Current selected model27_118_Northwest_Africa_(1987) remains selected; Project Models & coverage row6 disqualified byIdo Carmel2026-10-02. Exact reason inrecordZ6.',
 'artifacts':[]
}
for p in sorted(out.iterdir()):
 if p.is_file() and p.name!='context_summary.json':summary['artifacts'].append({'path':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(out/'context_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
print('Context summary and source comparisons saved.')
