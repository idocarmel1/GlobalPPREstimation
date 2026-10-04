import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const out=path.dirname(fileURLToPath(import.meta.url));
const mode=process.argv[2]||'baseline';
const region=path.resolve(out,'../../..');
const filename=mode==='baseline'?path.join(out,'baseline/LME013_taxon_mapping_appendix.xlsx'):path.join(region,'LME013_taxon_mapping_appendix.xlsx');
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(filename));
console.log((await wb.inspect({kind:'sheet,table',maxChars:1500,tableMaxRows:1,tableMaxCols:3})).ndjson);
if(mode==='author'){
  const data=JSON.parse(await fs.readFile(path.join(out,'appendix_updates.json'),'utf8'));
  for(const [sheet,cells] of Object.entries(data)){
    const sh=wb.worksheets.getItem(sheet);
    for(const [address,value] of Object.entries(cells))sh.getRange(address).values=[[value]];
  }
  wb.recalculate();
  const x=await SpreadsheetFile.exportXlsx(wb);await x.save(path.join(out,'appendix_authored.xlsx'));
}
for(const [sheet,range,name] of [['Taxon mapping','A1:G12','top'],['Taxon mapping','A150:G154','small'],['Taxon mapping','A185:G190','zero'],['Sources','A1:D10','sources'],['Sources','A23:D27','current_evidence'],['Sources','A60:D64','elasm_evidence']]){
  const p=await wb.render({sheetName:sheet,range,scale:1,format:'png'});
  await fs.writeFile(path.join(out,`${mode}_${name}.png`),new Uint8Array(await p.arrayBuffer()));
}
