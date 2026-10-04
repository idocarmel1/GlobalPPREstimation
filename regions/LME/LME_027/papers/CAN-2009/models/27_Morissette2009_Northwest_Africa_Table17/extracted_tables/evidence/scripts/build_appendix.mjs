import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';
const candidate=process.argv[2];
if(!candidate) throw new Error('Pass absolute candidate directory');
const read=async p=>JSON.parse(await fs.readFile(path.join(candidate,p),'utf8'));
const rows=await read('mapping/appendix_rows.json');
const sources=await read('mapping/appendix_sources.json');
const coverage=await read('mapping/coverage_summary.json');
const wb=Workbook.create();
const sheet=wb.worksheets.add('Taxon mapping');
const src=wb.worksheets.add('Sources');
for(const s of [sheet,src]) {s.showGridLines=false;s.tabColor='#315D70';}
const headers=['Taxon name','TL','Catch (t)','Simple-chain PPR (t C)','Mapped group names and weights','Confidence level','Reason'];
const data=rows.map(r=>headers.map(h=>r[h]??'?'));
sheet.getRange('A1:G1').merge();sheet.getRange('A1').values=[['Northwest Africa candidate taxon mapping']];
sheet.getRange('A2:G2').merge();sheet.getRange('A2').values=[['2019 landings | Independent simple trophic chain | tonnes C | Descending unrounded PPR, then taxon; unknown last']];
sheet.getRange('A3:G3').merge();sheet.getRange('A3').values=[['Candidate review only. Same published model as EcoBase 118; researcher disqualification and active selection remain unchanged.']];
sheet.getRange('A4:G4').merge();sheet.getRange('A4').values=[[`${coverage.taxa} taxa | Landings ${coverage.total_catch_tonnes.toLocaleString('en-US',{maximumFractionDigits:2})} t | Simple-chain PPR ${coverage.total_simple_chain_ppr_tC.toLocaleString('en-US',{maximumFractionDigits:2})} t C | ${coverage.missing_classic_coefficients.length} missing coefficients at zero catch`]];
sheet.getRange('A5:G5').merge();sheet.getRange('A5').values=[['Sources and full allocation evidence are linked on the Sources sheet. Weights are assumed source-model proportions, not observed 2019 mixtures.']];
sheet.getRange('A7:G7').values=[headers];
sheet.getRange(`A8:G${7+rows.length}`).values=data;
const all=sheet.getRange(`A1:G${7+rows.length}`);all.format.font={name:'Arial',size:10};all.format.wrapText=true;all.format.verticalAlignment='center';
sheet.getRange('A1:G1').format.font={name:'Arial',size:15,bold:true,color:'#172F3A'};
sheet.getRange('A2:G5').format.rowHeight=26;
sheet.getRange('A1:G1').format.rowHeight=32;
sheet.getRange('A7:G7').format={fill:'#315D70',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:34,verticalAlignment:'center'};
for(const [col,width] of Object.entries({A:29,B:8,C:18,D:23,E:60,F:16,G:95}))sheet.getRange(`${col}:${col}`).format.columnWidth=width;
sheet.getRange(`B8:B${7+rows.length}`).setNumberFormat('0.00');
sheet.getRange(`C8:D${7+rows.length}`).setNumberFormat('#,##0.00;[Red]-#,##0.00;0.00');
for(let i=0;i<data.length;i++){
  const row=i+8;
  const lines=Math.max(Math.ceil(String(data[i][6]).length/110),Math.ceil(String(data[i][4]).length/62),Math.ceil(String(data[i][0]).length/28));
  sheet.getRange(`A${row}:G${row}`).format.rowHeight=Math.max(46,lines*15+18);
  if(i%2===1)sheet.getRange(`A${row}:G${row}`).format.fill='#F1F5F7';
  if(data[i][5]==='Very low')sheet.getRange(`F${row}`).format={fill:'#FFF1D6',font:{name:'Arial',size:10,color:'#784B00',bold:true}};
}
const t=sheet.tables.add(`A7:G${7+rows.length}`,true,'CandidateTaxonMapping');t.showFilterButton=true;t.style='TableStyleMedium2';
sheet.freezePanes.freezeRows(7);
src.getRange('A1:D1').merge();src.getRange('A1').values=[['Sources and interpretation limits']];
src.getRange('A2:D2').merge();src.getRange('A2').values=[['Relative local links travel with the repository. Public URLs identify the original data providers.']];
src.getRange('A4:D4').values=[['Source','What this evidence supports','Open evidence','Access or record date']];
for(let i=0;i<sources.length;i++){
  const r=i+5,s=sources[i];
  const target=/^https?:\/\//i.test(s.target)?s.target:path.posix.normalize('mapping/'+s.target);
  src.getRange(`A${r}:D${r}`).values=[[s.title,s.supports,s.id,s.date??'']];
  src.getRange(`A${r}:D${r}`).format.rowHeight=Math.max(66,Math.ceil(s.supports.length/115)*15+25);
}
const end=4+sources.length;src.getRange(`A1:D${end}`).format.font={name:'Arial',size:10};src.getRange(`A1:D${end}`).format.wrapText=true;src.getRange(`A1:D${end}`).format.verticalAlignment='center';
src.getRange('A1:D1').format.font={name:'Arial',size:15,bold:true,color:'#172F3A'};src.getRange('A1:D2').format.rowHeight=30;
src.getRange('A4:D4').format={fill:'#315D70',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:34};
for(const [col,width] of Object.entries({A:43,B:110,C:32,D:23}))src.getRange(`${col}:${col}`).format.columnWidth=width;
src.getRange(`C5:C${end}`).format.font={name:'Arial',size:10,color:'#0563C1',underline:'single'};
const st=src.tables.add(`A4:D${end}`,true,'CandidateSources');st.showFilterButton=true;st.style='TableStyleMedium2';src.freezePanes.freezeRows(4);
wb.recalculate();
const checks=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',options:{useRegex:true,maxResults:50},summary:'Appendix errors'});
await fs.writeFile(path.join(candidate,'qa/appendix_artifact_inspection.json'),checks.ndjson);
const output=await SpreadsheetFile.exportXlsx(wb);await output.save(path.join(candidate,'LME027_candidate_taxon_mapping_appendix.xlsx'));
for(const [name,sheetName,range] of [['appendix_top','Taxon mapping','A1:G12'],['appendix_middle','Taxon mapping','A250:G254'],['appendix_bottom','Taxon mapping','A515:G519'],['sources','Sources',`A1:D${end}`]]){
  const blob=await wb.render({sheetName,range,scale:1,format:'png'});
  await fs.writeFile(path.join(candidate,`qa/${name}.png`),new Uint8Array(await blob.arrayBuffer()));
}
console.log(JSON.stringify({rows:rows.length,sources:sources.length,output:'LME027_candidate_taxon_mapping_appendix.xlsx'}));
