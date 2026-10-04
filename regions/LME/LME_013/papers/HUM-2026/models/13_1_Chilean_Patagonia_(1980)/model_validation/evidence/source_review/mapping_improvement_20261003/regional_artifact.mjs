import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const out=path.dirname(fileURLToPath(import.meta.url));
const mutations=JSON.parse(await fs.readFile(path.join(out,'regional_changed_blocks.json'),'utf8'));
const wb=Workbook.create();
const manifest=[];
for(const [name,blocks] of Object.entries(mutations)){
  const sh=wb.worksheets.add(name);let r=1;
  for(const [block,[header,rows]] of Object.entries(blocks)){
    const matrix=[['@table',block],header,...rows,[]];
    const width=Math.max(...matrix.map(x=>x.length));
    const normalized=matrix.map(row=>Array.from({length:width},(_,i)=>{
      const v=row[i]??null;return typeof v==='object'&&v!==null?JSON.stringify(v):v;
    }));
    sh.getRange(`A${r}`).write(normalized);
    manifest.push({sheet:name,block,start:r,rows:matrix.length,width});r+=matrix.length;
  }
}
wb.recalculate();
await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(out,'regional_authored.xlsx'));
await fs.writeFile(path.join(out,'regional_authoring_manifest.json'),JSON.stringify(manifest,null,2));
console.log((await wb.inspect({kind:'sheet',maxChars:1000})).ndjson);
