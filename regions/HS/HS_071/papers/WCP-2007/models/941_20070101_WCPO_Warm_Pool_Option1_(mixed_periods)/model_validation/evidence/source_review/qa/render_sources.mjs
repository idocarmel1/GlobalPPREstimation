import path from 'node:path';
import fs from 'node:fs/promises';
import {SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const qa=path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/,'$1'));
const region=path.resolve(qa,'../../..');
const workbook=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(region,'HS071_taxon_mapping_appendix.xlsx')));
const rendered=await workbook.render({sheetName:'Sources',range:'A1:D18',scale:1,format:'png'});
await fs.writeFile(path.join(qa,'appendix_sources_full.png'),new Uint8Array(await rendered.arrayBuffer()));
