import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';
const C=process.argv[2];
const read=async f=>JSON.parse(await fs.readFile(path.join(C,f),'utf8'));
const rows=await read('mapping/appendix_rows.json'),sources=await read('mapping/appendix_sources.json'),cov=await read('mapping/coverage_summary.json');
const headers=['Taxon name','TL','Catch (t)','Simple-chain PPR (t C)','Mapped group names and weights','Confidence level','Reason'];
const wb=Workbook.create(),s=wb.worksheets.add('Taxon mapping'),src=wb.worksheets.add('Sources');
for(const sh of [s,src]){sh.showGridLines=false;sh.tabColor='#315D70';}
const opening=[
 'Sine Saloum thesis candidate taxon mapping',
 '2019 landings excluding discards. Independent simple trophic chain in tonnes C. Descending unrounded PPR then taxon. Unknown last.',
 '37 source groups from thesis Table 6.5, 1991–1992. Candidate assignments remain unadopted. Model SPPR unavailable because group 20 diet identity is unresolved.',
 `${cov.taxa} taxa. Landings ${cov.total_catch_tonnes.toLocaleString('en-US',{maximumFractionDigits:2})} t. Simple-chain PPR ${cov.total_simple_chain_ppr_tC.toLocaleString('en-US',{maximumFractionDigits:2})} t C.`,
 'Missing inputs display ?. Zero recorded catch contributes zero PPR even with an unavailable coefficient. Detailed source and allocation evidence are on Sources.'
];
for(let i=0;i<opening.length;i++){s.getRange(`A${i+1}:G${i+1}`).merge();s.getRange(`A${i+1}`).values=[[opening[i]]];}
s.getRange('A7:G7').values=[headers];s.getRange(`A8:G${7+rows.length}`).values=rows.map(r=>headers.map(h=>r[h]??'?'));
s.getRange(`A1:G${7+rows.length}`).format={font:{name:'Arial',size:10},wrapText:true,verticalAlignment:'center'};
s.getRange('A1:G1').format={font:{name:'Arial',size:15,bold:true,color:'#172F3A'},rowHeight:32};
s.getRange('A2:G5').format.rowHeight=30;
s.getRange('A7:G7').format={fill:'#315D70',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:34,verticalAlignment:'center',horizontalAlignment:'center'};
for(const [col,width] of Object.entries({A:31,B:8,C:18,D:23,E:56,F:16,G:87}))s.getRange(`${col}:${col}`).format.columnWidth=width;
s.getRange(`B8:B${7+rows.length}`).setNumberFormat('0.00');s.getRange(`C8:D${7+rows.length}`).setNumberFormat('#,##0.00;[Red]-#,##0.00;0.00');
for(let i=0;i<rows.length;i++){
 const r=i+8,v=rows[i],lines=Math.max(Math.ceil(String(v.Reason).length/91),Math.ceil(String(v['Mapped group names and weights']).length/55),Math.ceil(String(v['Taxon name']).length/31));
 s.getRange(`A${r}:G${r}`).format.rowHeight=Math.max(44,lines*15+16);
 if(i%2===1)s.getRange(`A${r}:G${r}`).format.fill='#F1F5F7';
 if(v['Confidence level']==='Very low')s.getRange(`F${r}`).format={fill:'#FFF1D6',font:{name:'Arial',size:10,bold:true,color:'#784B00'}};
 if(v['Confidence level']==='Unresolved')s.getRange(`F${r}`).format={fill:'#FDE9E7',font:{name:'Arial',size:10,bold:true,color:'#9C2525'}};
}
const t=s.tables.add(`A7:G${7+rows.length}`,true,'ThesisCandidateTaxonMapping');t.showFilterButton=true;t.style='TableStyleMedium2';s.freezePanes.freezeRows(7);
src.getRange('A1:D1').merge();src.getRange('A1').values=[['Sources and applicability']];src.getRange('A2:D2').merge();src.getRange('A2').values=[['Thesis source membership and proxy weights are distinct from whole LME applicability and diagnostic availability.']];
src.getRange('A4:D4').values=[['Source','What this evidence supports','Open evidence','Record date']];
for(let i=0;i<sources.length;i++){let r=i+5,v=sources[i];src.getRange(`A${r}:D${r}`).values=[[v.title,v.supports,'Open '+v.id,v.date??'2026-10-03']];src.getRange(`A${r}:D${r}`).format.rowHeight=Math.max(62,Math.ceil(String(v.supports).length/100)*15+18);}
const end=4+sources.length;src.getRange(`A1:D${end}`).format={font:{name:'Arial',size:10},wrapText:true,verticalAlignment:'center'};
src.getRange('A1:D1').format={font:{name:'Arial',size:15,bold:true,color:'#172F3A'},rowHeight:32};src.getRange('A2:D2').format.rowHeight=28;
src.getRange('A4:D4').format={fill:'#315D70',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:34};
for(const [col,width] of Object.entries({A:44,B:104,C:34,D:21}))src.getRange(`${col}:${col}`).format.columnWidth=width;
src.getRange(`C5:C${end}`).format.font={name:'Arial',size:10,color:'#0563C1',underline:'single'};
const st=src.tables.add(`A4:D${end}`,true,'ThesisCandidateSources');st.showFilterButton=true;st.style='TableStyleMedium2';src.freezePanes.freezeRows(4);
wb.recalculate();
await fs.writeFile(path.join(C,'qa/appendix_inspection.ndjson'),(await wb.inspect({kind:'table',range:'Taxon mapping!A7:G12',include:'values,formulas',tableMaxRows:6,tableMaxCols:7,maxChars:3500})).ndjson);
await fs.writeFile(path.join(C,'qa/appendix_errors.ndjson'),(await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',options:{useRegex:true,maxResults:30}})).ndjson);
await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(C,'LME027_Villanueva2004_thesis_taxon_mapping_appendix.xlsx'));
for(const [name,sheetName,range] of [['appendix_top','Taxon mapping','A1:G12'],['appendix_middle','Taxon mapping','A255:G259'],['appendix_bottom','Taxon mapping',`A${3+rows.length}:G${7+rows.length}`],['sources_top','Sources',`A1:D${Math.min(end,10)}`],['sources_bottom','Sources',`A${Math.max(5,end-5)}:D${end}`]]){
 const blob=await wb.render({sheetName,range,scale:1,format:'png'});await fs.writeFile(path.join(C,`qa/${name}.png`),new Uint8Array(await blob.arrayBuffer()));
}
console.log(JSON.stringify({rows:rows.length,sources:sources.length,output:'LME027_Villanueva2004_thesis_taxon_mapping_appendix.xlsx'}));
