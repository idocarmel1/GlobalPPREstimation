import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook, SpreadsheetFile, FileBlob} from '@oai/artifact-tool';
const work=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
if(process.argv.includes('--help-hyperlinks')) {
 const wb=Workbook.create();wb.worksheets.add('Sources');
 console.log(wb.help('range.hyperlink',{include:'index,examples,notes',maxChars:3500}).ndjson);
 process.exit(0);
}
for(const period of ['1990_1994','2008_2012']) {
 const data=JSON.parse(await fs.readFile(path.join(work,`outputs/appendix_${period}.json`),'utf8'));
 if(process.argv.includes('--verify-final')) {
  const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(data.output));
  for(const [sheet,range,suffix] of [['Taxon mapping','A1:G9','mapping'],['Sources','A1:C6','sources'],['Taxon mapping','A15:G18','long_rows']]) {
   const preview=await wb.render({sheetName:sheet,range,scale:1,format:'png'});
   await fs.writeFile(path.join(work,`qa/final_${period}_${suffix}.png`),new Uint8Array(await preview.arrayBuffer()));
  }
  console.log('Inspected final saved workbook',period);continue;
 }
 const wb=Workbook.create();const s=wb.worksheets.add('Taxon mapping');
 s.showGridLines=false;
 s.getRange('A1:G1').merge();s.getRange('A1').values=[[data.title]];
 s.getRange('A2:G2').merge();s.getRange('A2').values=[[data.subtitle]];
 s.getRange('A3:G3').merge();s.getRange('A3').values=[['? means unavailable; recorded zero catch gives zero annual PPR. Proposals have not been adopted.']];
 const end=4+data.matrix.length;
 s.getRange(`A5:G${end}`).values=data.matrix;
 s.getRange(`A1:G${end}`).format.font={name:'Calibri',size:11};
 s.getRange('A1:G1').format.font={name:'Calibri',size:17,bold:true,color:'#163F50'};
 s.getRange('A1:G1').format.rowHeight=30;s.getRange('A2:G3').format.rowHeight=27;
 s.getRange(`A5:G${end}`).format.wrapText=true;s.getRange(`A5:G${end}`).format.verticalAlignment='center';
 s.getRange('A5:G5').format.fill='#244F60';s.getRange('A5:G5').format.font={bold:true,color:'#FFFFFF'};s.getRange('A5:G5').format.rowHeight=32;
 const widths=[29,10,16,21,65,18,91];const letters='ABCDEFG';
 for(let i=0;i<7;i++)s.getRange(`${letters[i]}:${letters[i]}`).format.columnWidth=widths[i];
 s.getRange(`B6:B${end}`).setNumberFormat('0.00');s.getRange(`C6:D${end}`).setNumberFormat('#,##0.00');
 s.getRange(`A5:G${end}`).format.borders={preset:'all',style:'thin',color:'#D9D9D9'};
 for(let i=1;i<data.matrix.length;i++) {
  const row=5+i,r=data.matrix[i];
  const lines=Math.max(Math.ceil(String(r[4]).length/58),Math.ceil(String(r[6]).length/86),2);
  s.getRange(`A${row}:G${row}`).format.rowHeight=Math.max(42,16*lines+9);
  if(i%2===0)s.getRange(`A${row}:G${row}`).format.fill='#F3F7F8';
  if(r[5]==='Very low')s.getRange(`F${row}`).format.font={color:'#945521',bold:true};
 }
 s.freezePanes.freezeRows(5);const table=s.tables.add(`A5:G${end}`,true,`Mappings${period.replaceAll('_','')}`);table.showFilterButton=true;
 const src=wb.worksheets.add('Sources');src.showGridLines=false;
 src.getRange(`A1:C${data.sources.length}`).values=data.sources;
 src.getRange(`A1:C${data.sources.length}`).format.font={name:'Calibri',size:11};
 src.getRange(`A1:C${data.sources.length}`).format.wrapText=true;src.getRange(`A1:C${data.sources.length}`).format.rowHeight=72;
 src.getRange('A:A').format.columnWidth=53;src.getRange('B:B').format.columnWidth=84;src.getRange('C:C').format.columnWidth=57;
 src.getRange('A1:C1').format.fill='#244F60';src.getRange('A1:C1').format.font={bold:true,color:'#FFFFFF'};src.getRange('A1:C1').format.rowHeight=28;
 src.getRange(`C2:C${data.sources.length}`).format.font={color:'#0563C1'};
 src.freezePanes.freezeRows(1);
 wb.recalculate();
 console.log((await wb.inspect({kind:'region',sheetId:s.name,range:'A5:D9',maxChars:1600,tableMaxRows:5,tableMaxCols:4})).ndjson);
 await (await SpreadsheetFile.exportXlsx(wb)).save(data.output);
 const preview=await wb.render({sheetName:s.name,range:'A1:G9',scale:1,format:'png'});
 await fs.writeFile(data.preview,new Uint8Array(await preview.arrayBuffer()));
 console.log('Saved',data.output);
}
