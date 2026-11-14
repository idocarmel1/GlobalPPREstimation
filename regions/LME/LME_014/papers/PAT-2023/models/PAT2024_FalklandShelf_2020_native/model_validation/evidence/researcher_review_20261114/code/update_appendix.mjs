import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';
process.on('uncaughtException', error => { console.error(error.message); process.exit(1); });

const run = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const mode = process.argv[2] ?? 'inspect';
const source = mode === 'final-qa' ? path.join(run, 'outputs', 'taxon_mapping.xlsx') : path.join(run, 'inputs', 'taxon_mapping_before.xlsx');
const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(source));
const mapping = wb.worksheets.getItem('Taxon mapping');
const sources = wb.worksheets.getItem('Sources');

async function render(sheetName, range, name) {
  const blob = await wb.render({ sheetName, range, scale: 1, format: 'png' });
  await fs.writeFile(path.join(run, 'qa', name), new Uint8Array(await blob.arrayBuffer()));
}

if (mode === 'final-qa') {
  await render('Sources', 'A24:D31', 'appendix_final_sources_tail.png');
  await render('Taxon mapping', 'A88:G91', 'appendix_final_middle.png');
  await render('Taxon mapping', 'A226:G230', 'appendix_final_zero_rows.png');
  const errors = await wb.inspect({ kind: 'match', searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!', options: { useRegex: true, maxResults: 50 }, maxChars: 1000 });
  await fs.writeFile(path.join(run, 'qa', 'appendix_final_inspect.ndjson'), errors.ndjson);
  console.log('Final staged workbook imported, rendered and scanned for formula errors.');
} else if (mode === 'help') {
  console.log(wb.help('range.format.font', { include: 'index,examples,notes', maxChars: 4000 }).ndjson);
} else if (mode === 'inspect') {
  await render('Taxon mapping', 'A1:G10', 'appendix_before_top.png');
  await render('Sources', 'A14:D17', 'appendix_before_diagnostics.png');
  await render('Sources', 'A24:D28', 'appendix_before_source_tail.png');
  const result = await wb.inspect({ kind: 'workbook,sheet,table', maxChars: 2500, tableMaxRows: 3, tableMaxCols: 7 });
  await fs.writeFile(path.join(run, 'qa', 'appendix_before_inspect.ndjson'), result.ndjson);
  console.log(result.ndjson);
} else if (mode === 'edit') {
  mapping.getRange('A2').values = [['Reference: 2019 landings; selected model PAT2024_FalklandShelf_2020_native. All 250 exact catch labels. GE/TE setup: source-exact separate pools; EE floor ON 0.1.']];
  sources.getRange('A2').values = [['Mapping reviews below are historical (30 September 2026); values and links checked 14 November 2026. Current adopted GE/TE: source-exact separate pools, EE floor ON 0.1. Native 2020 catch and regional hake weights remain composition assumptions.']];
  sources.getRange('A2:D2').format.rowHeight = 42;
  sources.getRange('D4').values = [['Retrieved / reviewed']];
  sources.getRange('A16:B16').values = [[
    'Historical diagnostics: Full GE/TE/With Egestion return',
    'Every source and recipient including unfished groups. WARN and TE balance gap retained. Earlier setup; not the adopted floor-ON source-reconciled result.'
  ]];
  sources.getRange('A16:D16').format.rowHeight = 65;
  sources.getRange('A24:B24').values = [[
    'Historical shark exposure: All Sharks 27 candidate and TE exposure review',
    'Primary habitat comparisons, competing Dogfish/Skates pools and source coefficient versus mapped catch exposure; Prionace dominates regional TE at Very low. Historical coefficient configuration; these exposure percentages were not recalculated for the adopted run.'
  ]];
  sources.getRange('A24:D24').format.rowHeight = 76;
  const newSources = [
    ['Adopted GE/TE: source-exact separate pools', 'EE floor ON 0.1, applied once. Fleet discard returns 0.005859525 to Detritus 36; Discards 35 remains separate. GE and TE WARN; both strict balance checks pass. No negative source–recipient SPPR entries. The native Discards deficit remains a physical limitation.', 'Open adopted diagnostics', '2026-11-14'],
    ['Native pool reconciliation: Discards 35 / Detritus 36', 'Native Discards deficit −0.207503632 (t km−2 yr−1): source Export and copy-only EwE 6.7 residual agree; BA=0 and explicit import=0. Computed closure is not observed import. Runtime floor-effective BA is distinct. Native mass basis is not explicitly confirmed.', 'Open native verification', '2026-11-14'],
    ['Physical detritus merge: sensitivity only', 'Physical pool merge was not adopted. The approved calculation retains separate source pools and native fate. Sensitivity results are a comparison, not a source correction.', 'Open merge sensitivity', '2026-11-14']
  ];
  for (let i = 0; i < newSources.length; i++) {
    const row = 29 + i;
    sources.getRange(`A${row}:B${row}`).copyFrom(sources.getRange('A28:B28'), 'all');
    sources.getRange(`D${row}`).copyFrom(sources.getRange('D28'), 'all');
    sources.getRange(`C${row}`).format = {font: {name: 'Calibri', size: 11, color: '#0563C1'}, wrapText: true, verticalAlignment: 'top'};
    sources.getRange(`A${row}:D${row}`).values = [newSources[i]];
    sources.getRange(`A${row}:D${row}`).format.rowHeight = i === 2 ? 56 : 86;
  }
  const tableName = sources.tables.items[0].name;
  const tableStyle = sources.tables.items[0].style;
  sources.tables.items[0].delete();
  const sourceTable = sources.tables.add('A4:D31', true, tableName);
  sourceTable.style = tableStyle;
  sourceTable.showFilterButton = true;
  mapping.tables.items[0].showFilterButton = true;
  wb.recalculate();
  const inspections = [];
  inspections.push((await wb.inspect({ kind: 'table', range: "'Sources'!A29:D31", include: 'values,formulas', tableMaxRows: 3, tableMaxCols: 4, maxChars: 3500 })).ndjson);
  inspections.push((await wb.inspect({ kind: 'match', searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!', options: { useRegex: true, maxResults: 50 }, summary: 'formula error scan', maxChars: 2000 })).ndjson);
  await fs.writeFile(path.join(run, 'qa', 'appendix_after_inspect.ndjson'), inspections.join('\n'));
  await render('Taxon mapping', 'A1:G11', 'appendix_after_top.png');
  await render('Taxon mapping', 'A88:G91', 'appendix_after_middle.png');
  await render('Taxon mapping', 'A226:G230', 'appendix_after_zero_rows.png');
  await render('Sources', 'A1:D8', 'appendix_after_sources_top.png');
  await render('Sources', 'A14:D17', 'appendix_after_historical_diagnostics.png');
  await render('Sources', 'A24:D31', 'appendix_after_sources_tail.png');
  const output = await SpreadsheetFile.exportXlsx(wb);
  await output.save(path.join(run, 'outputs', 'taxon_mapping_artifact.xlsx'));
  console.log('Staged appendix authored; portable source relationships will be verified/patched separately.');
} else {
  throw new Error(`Unsupported mode ${mode}`);
}
