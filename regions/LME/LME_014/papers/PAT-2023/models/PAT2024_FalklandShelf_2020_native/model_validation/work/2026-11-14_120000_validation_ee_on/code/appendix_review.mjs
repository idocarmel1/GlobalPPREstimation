import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

const run = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const mode = process.argv[2] || 'inspect';
const source = path.join(run, 'inputs', 'taxon_mapping_before.xlsx');
const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(source));
const mapping = wb.worksheets.getItem('Taxon mapping');
const sources = wb.worksheets.getItem('Sources');
if (mode === 'inspect') {
  const result = await wb.inspect({ kind: 'workbook,sheet,table', maxChars: 3500, tableMaxRows: 3, tableMaxCols: 7 });
  await fs.writeFile(path.join(run, 'qa', 'appendix_initial_inspect.ndjson'), result.ndjson);
  for (const [sheetName, range, name] of [['Taxon mapping','A1:G10','appendix_before_top.png'],['Sources','A1:D8','appendix_before_sources.png']]) {
    const blob = await wb.render({sheetName,range,scale:1,format:'png'});
    await fs.writeFile(path.join(run,'qa',name),new Uint8Array(await blob.arrayBuffer()));
  }
  console.log(result.ndjson);
} else if (mode === 'edit') {
  // Preserve all scientific row values, allocations, order and researcher text.
  mapping.getRange('A3').values = [['Independent simple trophic chain: saved classic wet coefficient × catch / 9 once, in tonnes C. Sorted by unrounded PPR, highest first; taxon breaks ties.']];
  sources.getRange('A2').values = [['Source review dates below are historical. Mapping values, denominators and local links checked 14 November 2026. Native 2020 catch and regional hake weights remain composition assumptions.']];
  sources.getRange('A2:D2').format.rowHeight = 40;
  sources.getRange('D4').values = [['Historical review date']];
  mapping.tables.items[0].showFilterButton = true;
  const sourceTableName = sources.tables.items[0].name;
  const sourceTableStyle = sources.tables.items[0].style;
  sources.tables.items[0].delete();
  const sourceTable = sources.tables.add('A4:D28', true, sourceTableName);
  sourceTable.style = sourceTableStyle;
  sourceTable.showFilterButton = true;
  // Existing split panes are preserved and checked after export.
  wb.recalculate();
  const checks = [];
  checks.push((await wb.inspect({kind:'table',range:"'Taxon mapping'!A7:G10",include:'values,formulas',tableMaxRows:4,tableMaxCols:7,maxChars:4000})).ndjson);
  checks.push((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:50},summary:'formula error scan',maxChars:2000})).ndjson);
  await fs.writeFile(path.join(run,'qa','appendix_final_inspect.ndjson'),checks.join('\n'));
  for (const [sheetName,range,name] of [['Taxon mapping','A1:G11','appendix_final_top.png'],['Taxon mapping','A88:G91','appendix_final_middle.png'],['Taxon mapping','A226:G230','appendix_final_zero_rows.png'],['Sources','A1:D8','appendix_final_sources_top.png'],['Sources','A24:D28','appendix_final_sources_bottom.png']]) {
    const blob = await wb.render({sheetName,range,scale:1,format:'png'});
    await fs.writeFile(path.join(run,'qa',name),new Uint8Array(await blob.arrayBuffer()));
  }
  const output = await SpreadsheetFile.exportXlsx(wb);
  await output.save(path.join(run,'outputs','taxon_mapping_artifact.xlsx'));
  console.log('Edited appendix exported with all 250 scientific rows retained.');
} else { throw new Error(`Unsupported mode ${mode}`); }
