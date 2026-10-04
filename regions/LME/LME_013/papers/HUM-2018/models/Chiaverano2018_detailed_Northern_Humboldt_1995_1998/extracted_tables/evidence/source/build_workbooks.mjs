import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root=path.dirname(fileURLToPath(import.meta.url));
const payload=JSON.parse(await fs.readFile(path.join(root,'workbook_payload.json'),'utf8'));
const native=path.join(root,'resolved_native');
const qa=path.join(root,'evidence');
function endcol(c){let x='';while(c){const r=(c-1)%26;x=String.fromCharCode(65+r)+x;c=Math.floor((c-1)/26)}return x}
async function author(name,sheets){
  const wb=Workbook.create();
  for(const [sname,rows] of Object.entries(sheets)){
    const sh=wb.worksheets.add(sname);
    const width=Math.max(...rows.map(r=>r.length));
    const rect=rows.map(r=>r.concat(Array(width-r.length).fill(null)).map(v=>v===undefined?null:v));
    const range=sh.getRange(`A1:${endcol(width)}${rows.length}`);
    range.values=rect;
    range.format.font={name:'Arial',size:10};range.format.verticalAlignment='center';
    sh.showGridLines=false;
    sh.getRange(`A1:${endcol(width)}1`).format={fill:'#263D54',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'}};
    sh.getRange(`A1:${endcol(width)}${rows.length}`).format.columnWidth=18;
    sh.getRange(`A1:A${rows.length}`).format.columnWidth=10;
    if(width>=2)sh.getRange(`B1:B${rows.length}`).format.columnWidth=31;
    if(sname==='Taxonomy'){
      sh.getRange(`C1:C${rows.length}`).format.columnWidth=100;
      sh.getRange(`C2:C${rows.length}`).format.wrapText=true;
      sh.getRange(`A2:C${rows.length}`).format.rowHeight=42;
    }
    if(sname==='Groups'){
      sh.getRange(`C2:${endcol(width)}${rows.length}`).setNumberFormat('0.########');
      sh.getRange(`A1:${endcol(width)}1`).format.wrapText=true;
      sh.getRange(`A1:${endcol(width)}1`).format.rowHeight=36;
    }
    if(name==='Metadata.xlsx'){
      sh.getRange('A1:A4').format.columnWidth=24;
      sh.getRange('B1:B4').format.columnWidth=42;
    }
    if(rows.length>10)sh.freezePanes.freezeRows(1);
  }
  wb.recalculate();
  const inspect=await wb.inspect({kind:'sheet',include:'id,name',maxChars:1200});
  console.log(name,inspect.ndjson);
  for(const [sname,rows] of Object.entries(sheets)){
    const width=Math.min(Math.max(...rows.map(r=>r.length)),8);
    const image=await wb.render({sheetName:sname,range:`A1:${endcol(width)}${Math.min(rows.length,12)}`,scale:1.4,format:'png'});
    await fs.writeFile(path.join(qa,`${name.replace('.xlsx','')}-${sname}.png`),new Uint8Array(await image.arrayBuffer()));
  }
  const out=await SpreadsheetFile.exportXlsx(wb);await out.save(path.join(native,name));
}
await author('TL.xlsx',{Sheet1:payload.artifacts.TL});
await author('Metadata.xlsx',{Sheet1:payload.artifacts.Metadata});
await author('Taxonomy.xlsx',{Taxonomy:payload.artifacts.Taxonomy});
const typed={};
for(const [name,rows] of Object.entries(payload.reconstruction))typed[name]=rows.map((r,i)=>r.map((v,c)=>i>0&&c!==1&&v!==''&&v!==null&&Number.isFinite(Number(v))?Number(v):v===''?null:v));
await author('reconstructed.xlsx',typed);
// Independent source views rendered from original stored cell values/formats.
const wb=Workbook.create();
for(const [sname,src] of Object.entries(payload.native_sheets)){
  const sh=wb.worksheets.add(sname.slice(0,31));
  const width=sname.includes('diet')?40:sname.includes('fate')?7:12;
  const rows=src.values.map(r=>r.slice(0,width));
  sh.getRange(`A1:${endcol(width)}${rows.length}`).values=rows;
  sh.getRange(`A1:${endcol(width)}${rows.length}`).format.font={name:'Arial',size:10};
  sh.getRange(`A1:${endcol(width)}${rows.length}`).format.columnWidth=14;
  sh.getRange(`A1:A${rows.length}`).format.columnWidth=sname.includes('diet')?30:8;
  if(!sname.includes('diet'))sh.getRange(`B1:B${rows.length}`).format.columnWidth=31;
  if(sname.includes('diet')){
    sh.getRange('B3:AN3').format.wrapText=true;
    sh.getRange('A3:AN3').format.rowHeight=40;
  }
  for(const cell of src.cells){
    if(cell.column>width||cell.row<3)continue;
    sh.getRange(cell.address).setNumberFormat(cell.number_format);
    if(cell.bold)sh.getRange(cell.address).format.font.bold=true;
  }
  let range=sname.includes('diet')?'A3:H43':sname.includes('fate')?'A3:G44':'A3:L46';
  const img=await wb.render({sheetName:sh.name,range,scale:1.7,format:'png'});
  await fs.writeFile(path.join(qa,sname.includes('diet')?'fresh-resolved-diet-detail.png':sname.includes('fate')?'fresh-resolved-fate.png':'fresh-resolved-parameters.png'),new Uint8Array(await img.arrayBuffer()));
}
console.log('Four XLSX artifacts exported; native source table QA renders saved.');
