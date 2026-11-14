import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const require=createRequire('C:/Users/idoca/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/entry.mjs');
const {FileBlob,SpreadsheetFile}=require('@oai/artifact-tool');
const run=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const dest=path.resolve(run,'../../taxon_mapping.xlsx');
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(dest));
console.log((await wb.inspect({kind:'workbook,sheet,table',maxChars:4000,tableMaxRows:2,tableMaxCols:7})).ndjson);
const mode=process.argv[2]||'preview';
if(mode==='preview'||mode==='verify-final') {
 const views=mode==='preview'?[['Taxon mapping','A1:G10','appendix_before'],['Sources','A1:D9','sources_before']]:[['Taxon mapping','A1:G10','appendix_final'],['Sources','A9:D14','sources_final_diagnostics'],['Sources','A18:D21','sources_final_exposure']];
 for(const [sheetName,range,name] of views){
  const p=await wb.render({sheetName,range,scale:1,format:'png'});
  await fs.writeFile(path.join(run,'qa',name+'.png'),new Uint8Array(await p.arrayBuffer()));
 }
} else {
 const sh=wb.worksheets.getItem('Taxon mapping');
 sh.getRange('A2').values=[['Reference: 2019 total catch; Scotland candidate 22_20251990_East_Coast_of_Scotland_(1991-1995). All 384 exact catch labels. Regional selection remains ICES_WGSAM2015_North_Sea_1991.']];
 sh.getRange('A2:G2').format.rowHeight=38;
 const sources=wb.worksheets.getItem('Sources');
 for (const sheet of [sh,sources]) for (const t of sheet.tables.items) t.showFilterButton=true;
 sources.getRange('B11').values=[['Historical baseline matrices: GE/With Egestion OK; TE FAIL. These matrices precede the seabird self-diet correction. Fresh corrected-runtime diagnostics are linked from the validation report; this mapping appendix uses independent simple-chain PPR.']];
 sources.getRange('B20').values=[['Historical baseline method-specific contributor exposure only. These GE/TE/With Egestion shares predate the corrected seabird runtime and do not describe its updated coefficients.']];
 sources.getRange('B13').values=[['Retained Scotland candidate decisions match its saved regional snapshot. Current regional PPR/Matching is empty under the ICES selection. Membership and allocation confidence remain separate, with the weaker component reported; no new mapping adoption.']];
 wb.recalculate();
 console.log((await wb.inspect({kind:'table',range:"'Taxon mapping'!A1:G9",include:'values,formulas',tableMaxRows:9,tableMaxCols:7,maxChars:5000})).ndjson);
 console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:100},summary:'formula errors',maxChars:2000})).ndjson);
 for(const [sheetName,range,name] of [['Taxon mapping','A1:G10','appendix_after'],['Sources','A9:D14','sources_after_diagnostics'],['Sources','A18:D21','sources_after_exposure']]){
  const p=await wb.render({sheetName,range,scale:1,format:'png'});
  await fs.writeFile(path.join(run,'qa',name+'.png'),new Uint8Array(await p.arrayBuffer()));
 }
 await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(run,'outputs','taxon_mapping_candidate.xlsx'));
}
