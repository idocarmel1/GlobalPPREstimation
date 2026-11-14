import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const require=createRequire('C:/Users/idoca/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/package.json');
const {Workbook, SpreadsheetFile, FileBlob}=require('@oai/artifact-tool');
const work=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const data=JSON.parse(await fs.readFile(path.join(work,'inputs/appendix_data.json'),'utf8'));
for(const row of data.rows){
 if(row[5]==='Unresolved')row[4]='Unresolved';
 const split=row[6].split(' Sources:');
 if(split.length>2)row[6]=split[0]+' Sources:'+split.at(-1);
}
const qa=path.join(work,'qa');
const previous=await SpreadsheetFile.importXlsx(await FileBlob.load(data.old_path));
try { const p=await previous.render({sheetName:'Taxon mapping',range:'A1:G9',scale:1,format:'png'}); await fs.writeFile(path.join(qa,'before_top.png'),new Uint8Array(await p.arrayBuffer())); } catch(e){ await fs.writeFile(path.join(qa,'before_render_error.txt'),String(e)); }
const wb=Workbook.create();
const s=wb.worksheets.add('Taxon mapping'),src=wb.worksheets.add('Sources');
const last=data.rows.length+7;
for(const ws of [s,src]){ws.showGridLines=false;ws.tabColor='#174C58';}
s.getRange(`A1:G${last}`).format.font={name:'Arial',size:11,color:'#172B36'};
s.getRange(`A1:G${last}`).format.verticalAlignment='top';
s.getRange(`A1:G${last}`).format.wrapText=true;
const widths=[29,8,17,22,64,17,105];
for(let c=0;c<7;c++)s.getRangeByIndexes(0,c,last,1).format.columnWidth=widths[c];
for(let r=1;r<=5;r++)s.mergeCells(`A${r}:G${r}`);
s.getRange('A1').values=[['Papua New Guinea - taxon mapping appendix']];
s.getRange('A2').values=[['Reference: 2019 landings; exact selected model '+data.summary.model_id+'.']];
s.getRange('A3').values=[['Independent simple trophic chain: saved classic coefficient × catch / 9 once; tonnes C. Descending order uses full, unrounded PPR; taxon name breaks ties.']];
s.getRange('A4').values=[['? = unavailable input or unresolved mapping. All 47 labels missing TL/coefficient have zero reference-year catch and contribute zero annual PPR; no unknown annual contributions.']];
s.getRange('A5').values=[['102 labels; total landings 512,724.621421 t; independent PPR 140,786,408.795223 t C. Overall confidence is the weaker membership/allocation component.']];
s.getRange('A1:G1').format.font={name:'Arial',size:15,bold:true,color:'#174C58'};
s.getRange('A1:G1').format.rowHeight=26;
s.getRange('A2:G5').format.rowHeight=25;
s.mergeCells('A6:C6');s.mergeCells('D6:G6');
s.getRange('A6').formulas=[['=HYPERLINK("#\'Sources\'!A1","Sources and interpretation")']];
s.getRange('D6').formulas=[['=HYPERLINK("evidence/mapping/taxon_mapping_audit.json","Full membership and allocation evidence")']];
const headers=['Taxon name','TL','Catch (t)','Simple-chain PPR (t C)','Mapped group names and weights','Confidence level','Reason'];
s.getRange('A7:G7').values=[headers];s.getRange(`A8:G${last}`).values=data.rows;
const table=s.tables.add(`A7:G${last}`,true,'TaxonMapping');table.style='TableStyleMedium2';table.showFilterButton=true;
s.getRange('A7:G7').format={fill:'#174C58',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},horizontalAlignment:'center',verticalAlignment:'center',wrapText:true,rowHeight:34};
s.getRange(`B8:B${last}`).setNumberFormat('0.00');s.getRange(`C8:D${last}`).setNumberFormat('#,##0.00');s.getRange(`B8:D${last}`).format.horizontalAlignment='right';
for(let i=0;i<data.rows.length;i++){
 const row=data.rows[i],r=i+8;
 const groupLines=row[4].split('; ').reduce((n,t)=>n+Math.ceil(t.length/64),0);
 const reasonLines=Math.ceil(row[6].length/104);
 s.getRange(`A${r}:G${r}`).format.rowHeight=Math.max(60,Math.min(260,Math.max(groupLines,reasonLines)*14.3+12));
 if(row[5]==='Very low')s.getRange(`F${r}`).format.fill='#FFF2D5';
 if(row[5]==='Unresolved')s.getRange(`F${r}`).format.fill='#FCE4D6';
}
s.freezePanes.freezeRows(7);s.freezePanes.freezeColumns(1);
const slast=data.sources.length+4;
src.getRange(`A1:D${slast}`).format={font:{name:'Arial',size:11,color:'#172B36'},wrapText:true,verticalAlignment:'top'};
for(const [col,w]of [['A',78],['B',115],['C',18],['D',28]])src.getRange(`${col}1:${col}${slast}`).format.columnWidth=w;
src.mergeCells('A1:D1');src.mergeCells('A2:D2');
src.getRange('A1').values=[['Descriptive sources - scope and limitations']];
src.getRange('A1:D1').format.font={name:'Arial',size:15,bold:true,color:'#174C58'};
src.getRange('A1:D1').format.rowHeight=26;
src.getRange('A2').values=[['Local evidence links are relative to this workbook. Historical source retrievals support membership/ecology; they are not observed regional caught-mass composition. Current mapping verification: 14 November 2026.']];
src.getRange('A2:D2').format.rowHeight=33;
src.getRange('A3').formulas=[['=HYPERLINK("#\'Taxon mapping\'!A1","Return to taxon mapping")']];
src.getRange('A4:D4').values=[['Source / material','What it supports / limits','Link','Retrieved / reviewed']];
src.getRange(`A5:D${slast}`).values=data.sources.map(o=>[o.title,o.supports,'Open source',o.reviewed]);
const st=src.tables.add(`A4:D${slast}`,true,'MappingSources');st.style='TableStyleMedium2';st.showFilterButton=true;
src.getRange('A4:D4').format={fill:'#174C58',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},horizontalAlignment:'center',rowHeight:30};
for(let i=0;i<data.sources.length;i++){
 const o=data.sources[i],r=i+5;
 src.getRange(`C${r}`).formulas=[[`=HYPERLINK("${o.target.replaceAll('"','""')}","Open source")`]];
 src.getRange(`A${r}:D${r}`).format.rowHeight=Math.max(66,Math.ceil(Math.max(o.title.length/75,o.supports.length/110, String(o.reviewed).length/25))*14.3+14);
}
src.freezePanes.freezeRows(4);
for(const [ws,rg]of [[s,'A6'],[s,'D6'],[src,'A3'],[src,`C5:C${slast}`]])ws.getRange(rg).format.font={name:'Arial',size:11,color:'#0563C1',underline:'single'};
wb.recalculate();
const inspection=await wb.inspect({kind:'table',range:'Taxon mapping!A7:G10',include:'values,formulas',tableMaxRows:4,tableMaxCols:7,maxChars:4000});
await fs.writeFile(path.join(qa,'artifact_inspection.ndjson'),inspection.ndjson);
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:100},summary:'Final formula error scan'});
await fs.writeFile(path.join(qa,'formula_errors.ndjson'),errors.ndjson);
const renders=[['Taxon mapping','A1:G10','mapping_top'],['Taxon mapping','A18:G21','mapping_mid'],['Taxon mapping','A102:G109','mapping_bottom'],['Sources','A1:D10','sources_top'],['Sources',`A20:D${slast}`,'sources_bottom']];
for(const [sheetName,range,name]of renders){const p=await wb.render({sheetName,range,scale:1.2,format:'png'});await fs.writeFile(path.join(qa,name+'.png'),new Uint8Array(await p.arrayBuffer()));}
const out=await SpreadsheetFile.exportXlsx(wb);await out.save(data.output_path);
console.log(JSON.stringify({output:data.output_path,rows:data.rows.length,sourceRows:data.sources.length,renders:renders.length}));
