import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const work=path.dirname(new URL(import.meta.url).pathname).replace(/^\/([A-Za-z]:)/,'$1');
const root=decodeURIComponent(path.resolve(work,'..'));
for(const year of ['1970s','2000s']){
 const dir=path.join(root,`SCS-2007_Northern_South_China_Sea_${year}`);
 const files=(await fs.readdir(dir)).filter(f=>f.endsWith('.xlsx'));
 for(const file of files){
  const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(dir,file)));
  const info=await wb.inspect({kind:'sheet',include:'id,name',maxChars:3000});
  await fs.writeFile(path.join(root,'work',`${year}-${file}.sheets.txt`),info.ndjson);
  const sheets=wb.worksheets.items;
  for(const sheet of sheets){
   sheet.getRange('A1:AN42').format.autofitColumns();
   const range=sheet.name==='Metadata' || file==='Metadata.xlsx'?'A1:B4':file==='TL.xlsx'?'A1:C14':sheet.name==='Basic input'?'A1:K10':sheet.name==='Diet composition'?'A1:J12':'A1:D12';
   const preview=await wb.render({sheetName:sheet.name,range,scale:1,format:'png'});
   await fs.writeFile(path.join(root,'work',`${year}-${file}-${sheet.name.replaceAll(' ','_')}.png`),new Uint8Array(await preview.arrayBuffer()));
  }
  await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(dir,file));
  console.log(year,file,sheets.length);
 }
}
