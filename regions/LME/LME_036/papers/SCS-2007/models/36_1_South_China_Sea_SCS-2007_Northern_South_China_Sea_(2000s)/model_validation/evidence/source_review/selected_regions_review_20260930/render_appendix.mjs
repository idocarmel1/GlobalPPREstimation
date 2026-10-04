import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {FileBlob,SpreadsheetFile} from 'file:///C:/Users/idoca/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const here=path.dirname(fileURLToPath(import.meta.url));
const region=path.resolve(here,'../../..');
const out=path.join(here,'render');await fs.mkdir(out,{recursive:true});
const workbook=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(region,'LME036_taxon_mapping_appendix.xlsx')));
for(const [name,range,stem] of [['Taxon appendix','A1:G14','appendix'],['Taxon appendix','A100:G107','changed_family'],['Taxon appendix','A210:G216','changed_species'],['Coverage','A1:D35','coverage'],['Allocation evidence','A1:J10','allocation'],['Allocation evidence','A28:J30','changed_size_set'],['Sources','A561:C567','sources_new'],['Sources','A1:C16','sources']]){
 const image=await workbook.render({sheetName:name,range,scale:1,format:'png'});
 await fs.writeFile(path.join(out,stem+'.png'),new Uint8Array(await image.arrayBuffer()));
 console.log(name,range,'rendered');
}
