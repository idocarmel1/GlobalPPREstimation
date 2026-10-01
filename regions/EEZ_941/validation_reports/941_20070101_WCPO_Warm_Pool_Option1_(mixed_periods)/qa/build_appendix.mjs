import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook,SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const qa=path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/,'$1'));
const evidence=path.dirname(qa),region=path.resolve(evidence,'../..');
// CURRENT_RESIDUAL_SCOPE_GUARD: preserve current adopted content.
try{await fs.access(path.join(evidence,'residual_fish_scope_followup.json'));if(!process.argv.includes('--render'))throw new Error('Current residual scope follow-up exists; use bounded current-state edits, not full appendix regeneration.');}catch(e){if(e.code!=='ENOENT')throw e;}
const data=JSON.parse(await fs.readFile(path.join(evidence,'taxon_audit.json'),'utf8'));
if(process.argv.includes('--render')){
 const imported=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(region,'EEZ941_taxon_mapping_appendix.xlsx')));
 for(const [sheetName,end,step,prefix] of [['Taxon mapping',70,9,'mapping'],['Sources',22,7,'sources']])for(let start=1;start<=end;start+=step){const stop=Math.min(start+step-1,end);const p=await imported.render({sheetName,range:`A${start}:${sheetName==='Sources'?'D':'G'}${stop}`,scale:1,format:'png'});await fs.writeFile(path.join(qa,`appendix_${prefix}_${start}_${stop}.png`),new Uint8Array(await p.arrayBuffer()));}
 console.log('Final appendix imported and rendered');process.exit(0);
}
const nativeLinks=[];
const wb=Workbook.create();const s=wb.worksheets.add('Taxon mapping'),src=wb.worksheets.add('Sources');
const last=7+data.rows.length;
s.getRange(`A1:G${last}`).format.font={name:'Calibri',size:11,color:'#222222'};
s.getRange('A1:G1').merge();s.getRange('A1').values=[['Kiribati (Gilbert Islands) — taxon mapping appendix']];
s.getRange('A1:G1').format={fill:'#193D50',font:{name:'Calibri',size:17,bold:true,color:'#FFFFFF'},rowHeightPx:42};
const notes=[
 `Reference: 2019 landings; exact selected model ${data.model_id}.`,
 'Independent simple trophic chain: saved classic coefficient × catch / 9 once; tonnes C. Sorted by full unrounded PPR, descending; taxon breaks ties.',
 `? = missing TL/coefficient or unresolved mapping. Zero catch gives zero annual PPR. ${data.missing_tl_taxa.length} labels have missing TL/coefficient, all with zero reference-year catch; no unknown annual contribution.`,
 `63 labels; total landings ${data.total_catch_tonnes.toFixed(6)} t; total independent PPR ${data.simple_chain_ppr_tC.toFixed(6)} t C. Overall confidence is the weaker membership/allocation component.`
];
notes.forEach((n,i)=>{const r=i+2;s.getRange(`A${r}:G${r}`).merge();s.getRange(`A${r}`).values=[[n]];s.getRange(`A${r}:G${r}`).format={wrapText:true,rowHeightPx:i===0?28:36};});
s.getRange('A6:C6').merge();s.getRange('A6').values=[['Sources and interpretation']];nativeLinks.push({sheet:1,ref:'A6',target:"#'Sources'!A1"});
s.getRange('D6:G6').merge();s.getRange('D6').values=[['Full membership and allocation evidence']];nativeLinks.push({sheet:1,ref:'D6',target:'validation_reports/'+data.model_id+'/taxon_audit.json'});
s.getRange('A6:G6').format={font:{color:'#0563C1'},rowHeightPx:27};
const headers=['Taxon name','TL','Catch (t)','Simple-chain PPR (t C)','Mapped group names and weights','Confidence level','Reason'];
s.getRange('A7:G7').values=[headers];s.getRange(`A8:G${last}`).values=data.rows.map(r=>[r.taxon,r.tl??'?',r.catch_tonnes,r.simple_chain_ppr_tC??'?',r.mapping_display,r.confidence,r.reason+' Sources: '+r.sources.join('; ')+'; source catch and biomass.']);
const widths=[250,65,135,180,400,112,690];widths.forEach((v,i)=>s.getRange(`${String.fromCharCode(65+i)}1:${String.fromCharCode(65+i)}${last}`).format.columnWidthPx=v);
s.getRange(`A7:G${last}`).format.wrapText=true;s.getRange(`A7:G${last}`).format.verticalAlignment='top';s.getRange('A7:G7').format={fill:'#DCE8ED',font:{bold:true},rowHeightPx:44};
s.getRange(`A8:G${last}`).format.rowHeightPx=136;s.getRange(`B8:B${last}`).setNumberFormat('0.00');s.getRange(`C8:D${last}`).setNumberFormat('#,##0.000000;[Red](#,##0.000000);0.000000');
s.tables.add(`A7:G${last}`,true,'MappingTable');s.freezePanes.freezeRows(7);s.freezePanes.freezeColumns(1);
data.rows.forEach((r,i)=>{if(['Low','Very low','Unresolved'].includes(r.confidence))s.getRange(`F${i+8}`).format.fill=r.confidence==='Unresolved'?'#F4D5D2':r.confidence==='Very low'?'#FAE6CE':'#FFF3D6';});
data.rows.forEach((r,i)=>{if(r.taxon==='Marine pelagic fishes not identified')s.getRange(`A${i+8}:G${i+8}`).format.rowHeightPx=300;});
let sources=data.sources.map(r=>[r.title,r.supports,r.target,r.target.startsWith('http')?'2026-09-30; exact material/access limits stated':'Local retained input; reviewed 2026-09-30']);
sources.push(['NCBI Kajikia audax taxonomy 13721','Current name and homotypic Tetrapturus audax synonym; full entry read','https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=13721','2026-09-30'],['WoRMS billfish corroboration','Indexed Kajikia audax / Istiompax indica entries read; direct page timeout/403, not fully retrieved','https://www.marinespecies.org/aphia.php?id=712907&p=taxdetails','2026-09-30'],['FAO Scombridae identification sheet','PDF5 genera Scomber, Scomberomorus, Thunnus, Katsuwonus, Acanthocybium; historical family context','https://www.fao.org/docrep/pdf/009/e9163e/e9163e4c.pdf#page=5','2026-09-30'],['FAO Gerreidae / Mullidae / Mugilidae evidence','Coastal bottom-feeding habitat: e9163e2g PDF6/13; e9163e3d PDF1; e9163e3c PDF15/17/19. These are general ecology sources, not Kiribati species composition.','https://www.fao.org/docrep/pdf/009/e9163e/e9163e2g.pdf#page=6','2026-09-30'],['Geographic estimate and boundary inputs','SAU repaired EEZ_941 polygon; WGS84 areas; Natural Earth land exclusion; approximate A99.7%, B3.9–4.6% denominator range','validation_reports/'+data.model_id+'/geographic_estimate.json','2026-09-30 local analysis'],['Full review and portable evidence index','Selected variant, initial/final source distinctions, coefficient checks, historical extraction/loader limitations','validation_reports/'+data.model_id+'/reports_index.md','2026-09-30 local analysis']);
const sl=sources.length+4;src.getRange(`A1:D${sl}`).format.font={name:'Calibri',size:11,color:'#222222'};src.getRange('A1:D1').merge();src.getRange('A1').values=[['Descriptive sources — scope and limitations']];src.getRange('A1:D1').format={fill:'#193D50',font:{bold:true,color:'#FFFFFF',size:17},rowHeightPx:40};
src.getRange('A2:D2').merge();src.getRange('A2').values=[['Local links are relative to this workbook; web references support membership/ecology, not observed regional caught-mass weights.']];src.getRange('A2:D2').format={wrapText:true,rowHeightPx:32};src.getRange('A3:D3').merge();src.getRange('A3').values=[['Return to taxon mapping']];nativeLinks.push({sheet:2,ref:'A3',target:"#'Taxon mapping'!A1"});src.getRange('A3:D3').format={font:{color:'#0563C1'},rowHeightPx:25};
src.getRange('A4:D4').values=[['Source / material','What it supports / limits','Link','Retrieved / reviewed']];src.getRange(`A5:D${sl}`).values=sources.map(r=>[r[0],r[1],'Open source',r[3]]);
sources.forEach((r,i)=>nativeLinks.push({sheet:2,ref:`C${i+5}`,target:r[2]}));
src.getRange(`C5:C${sl}`).format.font={color:'#0563C1'};[360,680,390,190].forEach((v,i)=>src.getRange(`${String.fromCharCode(65+i)}1:${String.fromCharCode(65+i)}${sl}`).format.columnWidthPx=v);
src.getRange(`A4:D${sl}`).format={wrapText:true,verticalAlignment:'top'};src.getRange('A4:D4').format={fill:'#DCE8ED',font:{bold:true},rowHeightPx:35};src.getRange(`A5:D${sl}`).format.rowHeightPx=125;src.tables.add(`A4:D${sl}`,true,'SourcesTable');src.freezePanes.freezeRows(4);
wb.recalculate();console.log((await wb.inspect({kind:'sheet,table',maxChars:1300})).ndjson);
const output=await SpreadsheetFile.exportXlsx(wb);await output.save(path.join(region,'EEZ941_taxon_mapping_appendix.xlsx'));
await fs.writeFile(path.join(qa,'hyperlinks.json'),JSON.stringify(nativeLinks,null,2));
console.log('APPENDIX_EXPORTED',data.rows.length,sources.length);
