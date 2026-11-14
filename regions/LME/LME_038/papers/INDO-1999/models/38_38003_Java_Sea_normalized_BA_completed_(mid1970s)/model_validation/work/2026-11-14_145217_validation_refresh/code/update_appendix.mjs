import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';
const code=path.dirname(fileURLToPath(import.meta.url));
const run=path.dirname(code),base=path.resolve(run,'../..');
const original=path.join(run,'inputs/taxon_mapping_before.xlsx');
const mode=process.argv[2]??'inspect';
const input=['final','filter'].includes(mode)?path.join(base,'taxon_mapping.xlsx'):original;
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(input));
const qa=path.join(run,'qa');
await fs.mkdir(qa,{recursive:true});
async function render(sheetName,range,name){
 const blob=await wb.render({sheetName,range,scale:1,format:'png'});
 await fs.writeFile(path.join(qa,name+'.png'),new Uint8Array(await blob.arrayBuffer()));
}
if(mode==='inspect'){
 console.log((await wb.inspect({kind:'workbook,sheet,table',maxChars:2500,tableMaxRows:2,tableMaxCols:7})).ndjson);
 await render('Taxon mapping','A1:G9','appendix_before');
 await render('Sources','A9:D12','sources_before');
}else if(mode==='edit'){
 const d=JSON.parse(await fs.readFile(path.join(run,'outputs/mapping_review.json'),'utf8'));
 const s=wb.worksheets.getItem('Taxon mapping'),src=wb.worksheets.getItem('Sources');
 const patches={
  'Taxon mapping':{
    A3:'Independent simple trophic chain: saved classic wet-weight coefficient × landings / 9 once, in tonnes C. Sorted by full-precision PPR descending; taxon name breaks ties.',
    A4:'39 labels lack a classic coefficient/TL; all have zero 2019 landings and zero annual PPR. ? means unavailable. Mapping confidence does not establish current SPPR readiness.',
    A5:`Landings ${d.total_catch_tonnes.toFixed(6)} t; simple-chain PPR ${d.total_simple_chain_ppr_tC.toFixed(6)} t C. Confidence is the weaker membership/allocation component. Very low: 36 taxa, ${d.confidence_summary.find(r=>r.label==='Very low').ppr_percentage.toFixed(4)}% of simple-chain PPR.`,
    D6:'Current mapping verification and complete audit rows'
  },
  Sources:{
    A11:'DirectDiagnostics: Historical GE/TE/With Egestion source-matrix review',
    B11:'Retained historical review of 29 loaded groups and four source columns per method. The current regional workbook marks coefficients pending after removal of the historical extraction bridge. This source does not establish current numerical readiness.',
    B8:'Current regional Catch and Classic PPR tables supply 2019 landings and the saved taxon TL/coefficient. Simple-chain PPR = wet-weight coefficient × landings / 9 once. All 39 taxa lacking TL/coefficient have zero 2019 landings and zero annual contribution.',
    D8:'2026-11-14'
  }
 };
 for(const [sheetName,cells] of Object.entries(patches)){
  const sheet=wb.worksheets.getItem(sheetName);
  for(const [cell,value] of Object.entries(cells))sheet.getRange(cell).values=[[value]];
 }
 wb.recalculate();
 await fs.writeFile(path.join(run,'outputs/appendix_cell_updates.json'),JSON.stringify(patches,null,2),'utf8');
 console.log((await wb.inspect({kind:'region',sheetId:'Taxon mapping',range:'A1:G9',include:'values,formulas',maxChars:2500})).ndjson);
 console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},maxChars:1000})).ndjson);
 await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(run,'outputs/taxon_mapping_artifact.xlsx'));
 console.log('Authored changed cells with bundled artifact runtime.');
}else if(mode==='filter'){
 await render('Taxon mapping','A1:G9','appendix_filter_top');
 console.log('Corrected native-filter appendix imported and rendered.');
}else if(mode==='final'){
 wb.recalculate();
 for(const [sh,range,name] of [['Taxon mapping','A1:G10','appendix_top'],['Taxon mapping','A80:G84','appendix_middle'],['Taxon mapping','A184:G188','appendix_bottom'],['Sources','A1:D8','sources_top'],['Sources','A9:D15','sources_middle'],['Sources','A19:D23','sources_bottom']])await render(sh,range,name);
 console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},maxChars:1000})).ndjson);
 console.log('Final delivered appendix imported and rendered.');
}else throw new Error('Unknown mode');
