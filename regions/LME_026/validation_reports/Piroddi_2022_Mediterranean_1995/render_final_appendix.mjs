import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const out=path.dirname(fileURLToPath(import.meta.url));
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(path.resolve(out,'../../LME026_taxon_mapping_appendix.xlsx')));
const pic=await wb.render({sheetName:'Sources',range:'A4:E8',scale:1.4,format:'png'});
await fs.writeFile(path.join(out,'qa/sources_final_links.png'),new Uint8Array(await pic.arrayBuffer()));
console.log('Rendered final imported Sources links.');
