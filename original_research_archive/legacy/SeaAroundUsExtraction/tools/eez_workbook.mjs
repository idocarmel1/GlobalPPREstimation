import { Workbook } from '@oai/artifact-tool';

export async function appendCsvSheet(workbook, text, name) {
  // CSV hydration requires an empty document. Parse in a fresh artifact workbook
  // and append typed values without disturbing already authored destination sheets.
  const imported = await Workbook.fromCSV(text.replace(/^\uFEFF/,''), {sheetName:name});
  const values = imported.worksheets.getItem(name).getUsedRange().values;
  for (let row=1; row<values.length; row++) values[row]=values[row].map(coerceCsvValue);
  const sheet = workbook.worksheets.add(name);
  if (values.length && values[0]?.length) sheet.getRangeByIndexes(0,0,values.length,values[0].length).values=values;
  return sheet;
}

function column(index) {
  let text = '';
  for (let n = index + 1; n > 0; n = Math.floor((n - 1) / 26)) text = String.fromCharCode(65 + (n - 1) % 26) + text;
  return text;
}

export function coerceCsvValue(value) {
  if (value === 'True') return true;
  if (value === 'False') return false;
  if (typeof value==='string' && /^-?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?$/.test(value.trim())) return Number(value);
  return value;
}

export function groupedPairFlagFormula(keyRange, unitCell, flagRange) {
  return `=SUMIF(${keyRange},${unitCell},${flagRange})>0`;
}

export function regionalExportShard(units, argv) {
  const number=(name,fallback)=>Number(argv.find(x=>x.startsWith(`--${name}=`))?.split('=')[1]??fallback);
  const count=number('shards',1), index=number('shard',0);
  if (!Number.isInteger(count)||count<1||!Number.isInteger(index)||index<0||index>=count) throw new Error('Invalid export shard');
  return {count,index,units:units.filter((_,position)=>position%count===index)};
}

export function regionalGroupFormulas(speciesRows, groupColumn) {
  // The group table is now [group(A), catch_tonnes_matched(B), tl_weighted(C),
  // sppr(D), ppr(E)] - the catch-weighted-mean-TL (Jensen-affected) aggregation
  // only, with no corrected/comparison figure left to reconstruct via SUMIF
  // against the Species sheet. B and C come straight from the CSV (the
  // catch-weighted mean TL isn't a single-cell formula); D and E are still
  // recomputed live from them, the same independent-verification pattern used
  // everywhere else in these workbooks, rather than trusted verbatim from the CSV.
  // speciesRows/groupColumn are no longer used (there is nothing left to SUMIF
  // from the Species sheet) but are kept in the signature to avoid touching the
  // call site.
  void speciesRows;
  void groupColumn;
  return {
    D: `=IF(C2="","",(1/'Metadata'!$B$5)^(C2-1))`,
    E: '=IF(B2=0,"",B2*D2)',
  };
}

export function addCompactSummary(workbook, source, name, { withinType = false, target = null } = {}) {
  const values = source.getUsedRange().values;
  const headers = values[0];
  const rows = values.length;
  const sheet = target ?? workbook.worksheets.add(name);
  const fields = ['unit_id','region_name','region_type','total_catch_tonnes','ppr_species'];
  sheet.getRange('A1:H1').values = [[...fields, withinType ? 'fraction_type_ppr' : 'fraction_eez_ppr',
    withinType ? 'rank_type_ppr' : 'rank_eez_ppr', 'accumulated fraction']];
  if (rows < 2) return sheet;
  const sourceName = source.name.replaceAll("'", "''");
  sheet.getRange('A2:E2').formulas = [fields.map(field => {
    const index = headers.indexOf(field);
    if (index < 0) throw new Error(`Missing summary field ${field}`);
    return `='${sourceName}'!${column(index)}2`;
  })];
  sheet.getRange(`A2:E${rows}`).fillDown();
  const denominator = withinType ? `SUMIF($C$2:$C$${rows},C2,$E$2:$E$${rows})` : `SUM($E$2:$E$${rows})`;
  sheet.getRange('F2').formulas = [[`=IF(${denominator}=0,"",E2/${denominator})`]];
  sheet.getRange(`F2:F${rows}`).fillDown();
  // Competition rank plus a source-order tie break matches the deterministic CSV rank.
  sheet.getRange('G2').formulas = [[withinType
    ? `=COUNTIFS($C$2:$C$${rows},C2,$E$2:$E$${rows},">"&E2)+COUNTIFS($C$2:C2,C2,$E$2:E2,E2)`
    : `=RANK(E2,$E$2:$E$${rows},0)+COUNTIF($E$2:E2,E2)-1`]];
  sheet.getRange(`G2:G${rows}`).fillDown();
  const cumulative=withinType?'SUMIF($C$2:C2,C2,$F$2:F2)':'SUM($F$2:F2)';
  sheet.getRange('H2').formulas = [[`=IF(${denominator}=0,"",${cumulative})`]];
  sheet.getRange(`H2:H${rows}`).fillDown();
  return sheet;
}
