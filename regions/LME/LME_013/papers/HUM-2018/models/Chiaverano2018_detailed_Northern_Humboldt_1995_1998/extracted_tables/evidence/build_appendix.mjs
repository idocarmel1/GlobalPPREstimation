import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const dir=path.dirname(fileURLToPath(import.meta.url)),region=path.resolve(dir,'../..');
const data=JSON.parse(await fs.readFile(path.join(dir,'mapping/mapping_review.json'),'utf8'));
const rows=[...data.taxa].sort((a,b)=>(b.simple_chain_ppr_tC??-Infinity)-(a.simple_chain_ppr_tC??-Infinity)||a.taxon.localeCompare(b.taxon));
const wb=Workbook.create(),map=wb.worksheets.add('Taxon mappings'),src=wb.worksheets.add('Sources');
const fmt=x=>x===null||x===undefined?'?':x;
const pct=x=>`${Number((x*100).toPrecision(3))}%`;
const vals=rows.map(r=>[r.taxon,fmt(r.tl),fmt(r.catch_t),fmt(r.simple_chain_ppr_tC),(r.candidates?.length?r.candidates.map(c=>`${c.group_name} (${c.weight===null||c.weight===undefined?'?':pct(c.weight)})`).join('; '):'Unresolved'),r.overall_confidence,r.reason+' Sources: '+r.sources.join(', ')+'.']);
map.getRange('A1').values=[['Northern Humboldt candidate taxon mappings']];
map.getRange('A2').values=[['2019 landings; all 218 labels including zero catch; candidate HUM2018 resolved native supplement']];
map.getRange('A3').values=[['Descending independent simple-chain PPR; saved wet-weight SPPR multiplied by catch and divided by 9 once']];
map.getRange('A4').values=[['? = unavailable TL, catch, PPR or weight. Missing classic coefficients only affect zero-catch labels in 2019.']];
map.getRange('A5:G5').values=[['Total landings (t)',null,rows.reduce((s,r)=>s+(r.catch_t??0),0),'Simple-chain PPR (t C)',rows.reduce((s,r)=>s+(r.simple_chain_ppr_tC??0),0),null,null]];
const headers=['Taxon name','TL','Catch (t)','Simple-chain PPR (t C)','Mapped group names and weights','Confidence level','Reason'];
map.getRange('A7:G7').values=[headers];map.getRange(`A8:G${rows.length+7}`).values=vals;
map.tables.add(`A7:G${rows.length+7}`,true,'CandidateMappings').showFilterButton=true;
map.freezePanes.freezeRows(7);map.freezePanes.freezeColumns(1);map.showGridLines=false;map.tabColor='#244a64';
map.getRange(`A1:G${rows.length+7}`).format.font={name:'Arial',size:10,color:'#222222'};
map.getRange('A1').format.font={name:'Arial',size:14,bold:true,color:'#000000'};
map.getRange('A7:G7').format={fill:'#244a64',font:{name:'Arial',size:10,bold:true,color:'#ffffff'},wrapText:true,horizontalAlignment:'center',verticalAlignment:'center',rowHeight:34};
map.getRange(`A8:G${rows.length+7}`).format.wrapText=true;map.getRange(`A8:G${rows.length+7}`).format.verticalAlignment='center';
const widths=[28,8,17,25,48,17,92];widths.forEach((w,i)=>map.getRange(`${String.fromCharCode(65+i)}1:${String.fromCharCode(65+i)}${rows.length+7}`).format.columnWidth=w);
map.getRange(`B8:B${rows.length+7}`).setNumberFormat('0.00');map.getRange(`C8:D${rows.length+7}`).setNumberFormat('#,##0.00');map.getRange('C5:E5').setNumberFormat('#,##0.00');
for(let i=0;i<vals.length;i++){const v=vals[i],lines=Math.max(Math.ceil(v[0].length/28),Math.ceil(v[4].length/45),Math.ceil(v[6].length/90));map.getRange(`A${i+8}:G${i+8}`).format.rowHeight=Math.min(290,Math.max(38,lines*14+14));}
src.showGridLines=false;src.getRange('A1').values=[['Sources for candidate membership and allocation']];
src.getRange('A2').values=[['Source table/cell evidence and limitations are retained in the linked audit. Retrieval date 3 October 2026 unless noted.']];
src.getRange('A4:D4').values=[['Source','Reference','Link','What the source supports']];
function sourceTarget(s){
 let t=s.target||s.url||'';
 if(/^https?:|^#/.test(t))return t;
 const fragment=t.includes('#')?t.slice(t.indexOf('#')):'';t=t.split('#')[0];
 let absolute;
 if(path.isAbsolute(t))absolute=t;
 else if(t.startsWith('regions/')||t.startsWith('tools/')||t.startsWith('common_reference_data/'))absolute=path.resolve(dir,'../../../..',t);
 else absolute=path.resolve(dir,'mapping',t);
 return path.relative(region,absolute).replaceAll('\\','/')+fragment;
}
const sources=[...data.sources,{id:'Candidate audit',title:'Fresh extraction, diagnostics and candidate calculations',target:'../README.md',supports:'Source identity, scientific restrictions, complete run evidence'},{id:'Regional input',title:'LME_013.xlsx Catch, Classic PPR / Taxa, NPP',target:'../../../LME_013.xlsx',supports:'2019 landings and independent saved classic coefficients; NPP series in tonnes C/year'},{id:'Validation',title:'Northern Humboldt candidate validation DOCX',target:'../../../Model_validation_HUM2018_Northern_Humboldt_candidate_20261003.docx',supports:'Candidate review awaiting researcher decision'}];
src.getRange(`A5:D${sources.length+4}`).values=sources.map(s=>[s.id,s.title,'Open source',s.supports]);
await fs.writeFile(path.join(dir,'qa/appendix_links.json'),JSON.stringify(sources.map((s,i)=>({cell:`C${i+5}`,target:sourceTarget(s)})),null,2));
src.getRange(`A1:D${sources.length+4}`).format.font={name:'Arial',size:10,color:'#222222'};src.getRange('A1').format.font={name:'Arial',size:14,bold:true};
src.getRange('A4:D4').format={fill:'#244a64',font:{name:'Arial',size:10,bold:true,color:'#ffffff'},wrapText:true,horizontalAlignment:'center',rowHeight:30};
src.getRange(`A5:D${sources.length+4}`).format.wrapText=true;src.getRange(`A5:D${sources.length+4}`).format.rowHeight=70;src.getRange(`A5:D${sources.length+4}`).format.verticalAlignment='center';
src.getRange(`C5:C${sources.length+4}`).format.font.color='#0563c1';
[['A',27],['B',85],['C',20],['D',105]].forEach(([c,w])=>src.getRange(`${c}1:${c}${sources.length+4}`).format.columnWidth=w);
src.freezePanes.freezeRows(4);src.tables.add(`A4:D${sources.length+4}`,true,'CandidateSources').showFilterButton=true;
wb.recalculate();
await fs.mkdir(path.join(dir,'qa/appendix'),{recursive:true});
for(const [name,sheet,range] of [['top','Taxon mappings','A7:G13'],['middle','Taxon mappings','A100:G105'],['bottom','Taxon mappings',`A${rows.length+2}:G${rows.length+7}`],['sources','Sources','A4:D10']]){
 const png=await wb.render({sheetName:sheet,range,scale:1.5,format:'png'});await fs.writeFile(path.join(dir,`qa/appendix/${name}.png`),new Uint8Array(await png.arrayBuffer()));
}
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',options:{useRegex:true,maxResults:20},summary:'Candidate appendix formula error scan'})).ndjson);
const result=await SpreadsheetFile.exportXlsx(wb);await result.save(path.join(region,'LME013_HUM2018_candidate_taxon_mapping_appendix_20261003.xlsx'));
await fs.writeFile(path.join(dir,'qa/appendix/artifact_verification.json'),JSON.stringify({row_count:rows.length,source_count:sources.length,catch:rows.reduce((s,r)=>s+(r.catch_t??0),0),ppr_tC:rows.reduce((s,r)=>s+(r.simple_chain_ppr_tC??0),0)},null,2));
console.log('Exported candidate appendix',rows.length,'rows');
