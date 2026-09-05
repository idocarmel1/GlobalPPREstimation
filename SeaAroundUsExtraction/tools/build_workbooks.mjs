import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";
import { resolveReleaseArgs } from "./scope_args.mjs";
import { addCompactSummary, regionalGroupFormulas, appendCsvSheet, groupedPairFlagFormula, regionalExportShard } from "./eez_workbook.mjs";
import {
  transferEfficiencyMethodNote,
  transferEfficiencyNumberFormat,
  transferEfficiencySpprNote,
} from "./workbook_metadata.mjs";


const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const RELEASE = resolveReleaseArgs(process.argv.slice(2));
const IS_GLOBAL = RELEASE.isGlobal;
const IS_EEZ = RELEASE.scopeLabel === 'eez';
const SCOPE_LABEL = RELEASE.scopeLabel;
const OUTPUT = path.join(ROOT, RELEASE.outputDirectory);
const TABLES = path.join(OUTPUT, "tables");
const REGIONAL_OUTPUT = path.join(OUTPUT, "regional_calculations");
const PREVIEWS = path.join(ROOT, "..", "tmp", RELEASE.previewDirectoryName);
const SUMMARY_CSV = `${SCOPE_LABEL}_summary.csv`;
const SUMMARY_XLSX = `PPR_${SCOPE_LABEL}_summary.xlsx`;
const SUMMARY_ONLY = process.argv.includes('--summary-only');
const REGIONS_ONLY = process.argv.includes('--regions-only');
const RESUME = process.argv.includes('--resume');

const PALETTE = {
  navy: "#17324D",
  teal: "#147D92",
  paleTeal: "#DDEFF2",
  paleBlue: "#E8F0F7",
  orange: "#E28A32",
  paleOrange: "#FCEAD8",
  red: "#B42318",
  paleRed: "#FEE4E2",
  gray: "#667085",
  paleGray: "#F2F4F7",
  white: "#FFFFFF",
};

function excelColumn(indexOneBased) {
  let n = indexOneBased;
  let result = "";
  while (n > 0) {
    const r = (n - 1) % 26;
    result = String.fromCharCode(65 + r) + result;
    n = Math.floor((n - 1) / 26);
  }
  return result;
}

function cleanName(value) {
  return value.replace(/[^A-Za-z0-9]/g, "").slice(0, 200);
}

async function addCsvSheet(workbook, csvPath, sheetName) {
  return appendCsvSheet(workbook, await fs.readFile(csvPath, "utf8"), sheetName);
}

function usedDimensions(sheet) {
  const values = sheet.getUsedRange().values;
  return { rows: values.length, cols: values[0]?.length ?? 0, values };
}

function styleDataSheet(sheet, tableName, preferredWidths = {}) {
  const { rows, cols, values } = usedDimensions(sheet);
  if (!rows || !cols) return { rows, cols };
  const end = `${excelColumn(cols)}${rows}`;
  const used = sheet.getRange(`A1:${end}`);
  sheet.showGridLines = false;
  sheet.freezePanes.freezeRows(1);
  used.format.font = { name: "Aptos", size: 9, color: "#1D2939" };
  used.format.rowHeight = 18;
  sheet.getRange(`A1:${excelColumn(cols)}1`).format = {
    fill: PALETTE.navy,
    font: { name: "Aptos Display", size: 10, bold: true, color: PALETTE.white },
    wrapText: true,
    verticalAlignment: "center",
    borders: { bottom: { style: "medium", color: PALETTE.teal } },
  };
  sheet.getRange(`A1:${excelColumn(cols)}1`).format.rowHeight = 32;
  if (rows > 1) {
    const table = sheet.tables.add(`A1:${end}`, true, cleanName(tableName));
    table.style = "TableStyleMedium2";
    table.showBandedColumns = false;
    table.showFilterButton = true;
  }
  for (let c = 0; c < cols; c += 1) {
    const header = String(values[0][c] ?? "");
    let width = 15;
    if (/name|group|source|method|confidence|taxon|unit|check|rationale|url|note|type/i.test(header)) width = 22;
    if (/source|rationale|url|note/i.test(header)) width = 36;
    if (/ppr|catch|tonnes|difference/i.test(header)) width = 18;
    if (/fraction|percent|ratio|coverage/i.test(header)) width = 16;
    if (preferredWidths[header] !== undefined) width = preferredWidths[header];
    sheet.getRangeByIndexes(0, c, rows, 1).format.columnWidth = width;
  }
  return { rows, cols };
}

function applyFormatsByHeaders(sheet) {
  const { rows, cols, values } = usedDimensions(sheet);
  if (rows < 2) return;
  for (let c = 0; c < cols; c += 1) {
    const header = String(values[0][c] ?? "");
    const range = sheet.getRangeByIndexes(1, c, rows - 1, 1);
    if (/year/i.test(header)) range.format.numberFormat = "0";
    else if (/count|rank/i.test(header)) range.format.numberFormat = "#,##0";
    else if (/fraction|percent|coverage/i.test(header)) range.format.numberFormat = "0.00%";
    else if (/tl$|^tl_|_tl|sppr/i.test(header)) range.format.numberFormat = "0.0000";
    else if (/catch|tonnes|ppr|difference|km2/i.test(header)) range.format.numberFormat = "#,##0.00";
    else if (/ratio/i.test(header)) range.format.numberFormat = "0.0000";
  }
}

function addKeyValueSheet(workbook, sheetName, title, rows) {
  const sheet = workbook.worksheets.add(sheetName);
  sheet.showGridLines = false;
  sheet.getRange("A1:C1").merge();
  sheet.getRange("A1").values = [[title]];
  sheet.getRange("A1:C1").format = {
    fill: PALETTE.navy,
    font: { name: "Aptos Display", size: 16, bold: true, color: PALETTE.white },
    rowHeight: 30,
  };
  sheet.getRange("A3:C3").values = [["Field", "Value", "Notes / source"]];
  sheet.getRange(`A4:C${3 + rows.length}`).values = rows;
  sheet.getRange(`A3:C${3 + rows.length}`).format.font = { name: "Aptos", size: 10 };
  sheet.getRange("A3:C3").format = {
    fill: PALETTE.teal,
    font: { bold: true, color: PALETTE.white },
  };
  sheet.getRange(`A3:C${3 + rows.length}`).format.borders = {
    preset: "inside",
    style: "thin",
    color: "#D0D5DD",
  };
  sheet.getRange(`A4:C${3 + rows.length}`).format.wrapText = true;
  sheet.getRange(`A4:A${3 + rows.length}`).format.font = { bold: true, color: PALETTE.navy };
  sheet.getRange(`A1:A${3 + rows.length}`).format.columnWidth = 31;
  sheet.getRange(`B1:B${3 + rows.length}`).format.columnWidth = 28;
  sheet.getRange(`C1:C${3 + rows.length}`).format.columnWidth = 68;
  return sheet;
}

async function renderSheet(workbook, workbookName, sheetName, range) {
  const targetDir = path.join(PREVIEWS, workbookName.replace(/\.xlsx$/i, ""));
  await fs.mkdir(targetDir, { recursive: true });
  const preview = await workbook.render({ sheetName, range, scale: 1.2, format: "png" });
  const file = path.join(targetDir, `${sheetName.replace(/[^A-Za-z0-9_-]/g, "_")}.png`);
  await fs.writeFile(file, new Uint8Array(await preview.arrayBuffer()));
  return file;
}

async function inspectWorkbook(workbook, workbookName, keySheet, keyRange) {
  const table = await workbook.inspect({
    kind: "table",
    range: `${keySheet}!${keyRange}`,
    include: "values,formulas",
    tableMaxRows: 20,
    tableMaxCols: 22,
    maxChars: 12000,
  });
  const errors = await workbook.inspect({
    kind: "match",
    searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
    options: { useRegex: true, maxResults: 300 },
    summary: `${workbookName} final formula error scan`,
    maxChars: 8000,
  });
  return { workbookName, table: table.ndjson, errors: errors.ndjson };
}

async function buildSummaryWorkbook(metadata) {
  const workbook = Workbook.create();
  const compactPlaceholder = IS_EEZ ? workbook.worksheets.add('summarized summary') : null;
  await addCsvSheet(workbook, path.join(TABLES, SUMMARY_CSV), "Summary");
  await addCsvSheet(workbook, path.join(TABLES, "validation.csv"), "Validation");
  await addCsvSheet(workbook, path.join(TABLES, "tl_coverage.csv"), "TL Coverage");
  await addCsvSheet(workbook, path.join(TABLES, "jensen_comparison.csv"), "Jensen Comparison");
  await addCsvSheet(workbook, path.join(TABLES, "ingestion_audit.csv"), "Ingestion Audit");
  const configuration = addKeyValueSheet(workbook, "Configuration", `PPR ${SCOPE_LABEL} configuration`, [
    ["Scope", metadata.scope, IS_EEZ ? 'All EEZs; flags only, no filtering or replacements' : IS_GLOBAL ? "All Sea Around Us-defined LME and High Seas units" : "Not a global estimate or global ranking"],
    ["Spatial units", metadata.unit_count, `${metadata.lme_count} LMEs + ${metadata.highseas_count} High Seas units + ${metadata.eez_count ?? 0} EEZs`],
    ["Year", metadata.year, "Latest year present in every configured catch archive"],
    ["Transfer efficiency", metadata.transfer_efficiency, "Fixed TE for the approved 1995 trophic-chain method"],
    ["SPPR", "(1 / TE)^(TL - 1)", transferEfficiencySpprNote(metadata.transfer_efficiency)],
    ["PPR", "Catch tonnes × SPPR", "Unit: tonnes primary-production equivalent"],
    ["Wet-weight/carbon divisor", "Not applied", "The paper's separate /9 conversion is omitted per the approved specification"],
    ["Catch types", metadata.catch_types.join(", "), "Sea Around Us reconstructed catch scope"],
    ["Reporting status", metadata.reporting_status.join(", "), "Both reported and reconstructed unreported catch"],
    ["TL primary source", "2020 supplement MeanTL", "The supplement's alternative SPPR columns are not used"],
    ["TL secondary source", "Sea Around Us exploited organisms", "Exact scientific-name matches"],
  ]);
  addKeyValueSheet(workbook, "Sources", "Sources and reproducibility notes", [
    ["Sea Around Us data", "https://www.seaaroundus.org/data/", "Region, catch, and High Seas definitions"],
    ["Sea Around Us guide", "https://www.seaaroundus.org/tools-guide/", "Download fields and reconstructed-catch notes"],
    ["Sea Around Us API", "https://api.seaaroundus.org/api/v1/", "Frozen raw downloads stored with the pipeline"],
    ["1995 method", "Pauly & Christensen (1995), Nature 374:255-257", transferEfficiencyMethodNote(metadata.transfer_efficiency)],
    ["2020 supplement", "sources/2020 sup.xlsx", "MeanTL only; no Luong regression SPPR used"],
    ["Interpretation", `${IS_EEZ ? "EEZ" : IS_GLOBAL ? "Global" : "Pilot"} fractions sum to 100%`, IS_EEZ ? 'EEZs overlap LMEs; do not sum spatial systems as a world total' : `Fractions and ranks apply to ${metadata.unit_count} configured units`],
  ]);
  configuration.getRange("B7").format.numberFormat = transferEfficiencyNumberFormat();

  const summary = workbook.worksheets.getItem("Summary");
  const dims = styleDataSheet(summary, "PilotSummaryTable", { region_name: 27 });
  applyFormatsByHeaders(summary);
  if (dims.rows > 1) {
    summary.getRange("P2").formulas = [[`=K2/SUM($K$2:$K$${dims.rows})`]];
    summary.getRange(`P2:P${dims.rows}`).fillDown();
    summary.getRange("Q2").formulas = [[`=RANK(K2,$K$2:$K$${dims.rows},0)`]];
    summary.getRange(`Q2:Q${dims.rows}`).fillDown();
    summary.getRange(`H2:H${dims.rows}`).conditionalFormats.add("cellIs", {
      operator: "lessThan",
      formula: 0.9,
      format: { fill: PALETTE.paleRed, font: { color: PALETTE.red, bold: true } },
    });
    const chartRows = IS_GLOBAL || IS_EEZ ? Math.min(25, dims.rows - 1) : dims.rows - 1;
    summary.getRange("S24:T24").values = [["Region", "Species PPR"]];
    summary.getRange("S25:T25").formulas = [["=B2", "=K2"]];
    summary.getRange(`S25:T${24 + chartRows}`).fillDown();
    const chart = summary.charts.add("bar", summary.getRange(`S24:T${24 + chartRows}`));
    chart.title = `${IS_EEZ ? 'Top 25 EEZ' : IS_GLOBAL ? "Top 25 global" : "Pilot"} PPR ranking (tonnes primary-production equivalent)`;
    chart.hasLegend = false;
    chart.yAxis = { numberFormatCode: "0.00E+00" };
    chart.setPosition("S2", "AC19");
  }
  for (const [sheetName, tableName] of [
    ["Validation", "PilotValidationTable"],
    ["TL Coverage", "PilotTLCoverageTable"],
    ["Jensen Comparison", "PilotJensenTable"],
    ["Ingestion Audit", "PilotIngestionTable"],
  ]) {
    const sheet = workbook.worksheets.getItem(sheetName);
    const d = styleDataSheet(sheet, tableName);
    applyFormatsByHeaders(sheet);
    if (sheetName === 'Validation') sheet.getRange(`D1:D${d.rows}`).format.columnWidth=42;
    if (sheetName === "TL Coverage" && d.rows > 1) {
      sheet.getRange(`J2:J${d.rows}`).conditionalFormats.add("dataBar", { color: PALETTE.teal });
    }
    if (sheetName === "Jensen Comparison" && d.rows > 1) {
      sheet.getRange(`R2:R${d.rows}`).conditionalFormats.add("colorScale", {
        colors: [PALETTE.white, PALETTE.paleOrange, "#F79009"],
        thresholds: ["min", "50%", "max"],
      });
    }
  }

  const previews = [];
  if (IS_EEZ) {
    const compact = addCompactSummary(workbook, summary, 'summarized summary', {target:compactPlaceholder});
    const flags = await addCsvSheet(workbook, path.join(TABLES, 'eez_selection_flags.csv'), 'EEZ Selection Flags');
    const pairs = await addCsvSheet(workbook, path.join(TABLES, 'eez_lme_intersections.csv'), 'EEZ LME Pairs');
    const alternatives = await addCsvSheet(workbook, path.join(TABLES, 'all_areas_summary.csv'), 'All Areas Data');
    const allCompact = addCompactSummary(workbook, alternatives, 'All Areas Summary', {withinType:true});
    for (const sheet of [flags,pairs,alternatives,allCompact]) {
      styleDataSheet(sheet, cleanName(sheet.name)+'Table', {region_name:38, eez_name:38, lme_name:32});
      applyFormatsByHeaders(sheet);
    }
    for (const sheet of [flags,pairs]) {
      const columns=sheet.getUsedRange().values[0];
      sheet.getRange(`A1:${excelColumn(columns.length)}1`).format.rowHeight=48;
      for (let c=0;c<columns.length;c++) {
        if (/flag_|fraction|ratio|mostly_contained/.test(columns[c])) sheet.getRangeByIndexes(0,c,sheet.getUsedRange().values.length,1).format.columnWidth=24;
      }
    }
    const allRows = allCompact.getUsedRange().values.length;
    allCompact.getRange(`H2:H${allRows}`).format.numberFormat = '0.00%';
    const spatial = JSON.parse(await fs.readFile(path.join(TABLES, 'spatial_validation.json'), 'utf8'));
    // Configurable thresholds are visible inputs; polygon intersections are externally computed.
    const thresholds = addKeyValueSheet(workbook, 'Selection Rules', 'Spatial flags — advisory only', [
      ['Low LME overlap', spatial.thresholds?.low_overlap_threshold ?? 0.10, 'Strictly less than; denominator = whole EEZ area; intersect union of LMEs'],
      ['Mostly contained', spatial.thresholds?.containment_threshold ?? 0.90, 'At least this fraction of an LME lies inside the EEZ; provisional definition'],
      ['Prefer EEZ area ratio', spatial.thresholds?.prefer_ratio ?? 1.20, 'EEZ area / whole LME area, inclusive; AND mostly contained'],
      ['Review area ratio', spatial.thresholds?.review_ratio ?? 1.10, 'Inclusive lower bound; below preference ratio; AND mostly contained'],
      ['No replacements', `All ${metadata.unit_count} EEZs retained`, 'Candidate flags are for later decisions; no catches are subtracted or prorated'],
      ['Overlap warning', 'Do not add EEZ + LME + HS', 'All Areas Summary uses within-type shares and ranks, not a mixed-system total'],
      ['Area source', 'Sea Around Us polygons', 'Repaired polygon topology; WGS84 area method and checks in spatial_validation.json'],
      ['Area is not catch', 'No area-weighted catch correction', 'Fishing is not spatially uniform; exact deduplication needs spatial catch data'],
      ['Official definitions', 'https://www.seaaroundus.org/sea-around-us-area-parameters-and-definitions/', 'EEZ units may be distinct facades/territories; boundaries are analytical, not legal'],
      ['Linked LME ID lists', 'Frozen at run thresholds', 'Boolean flags recalculate here; rerun Python to regenerate candidate ID lists after changing thresholds'],
      ['Flag display', '1 = yes; 0 = no', 'Numeric flags remain filterable and formula-linked to the selection thresholds'],
    ]);
    thresholds.getRange('B4:B5').format.numberFormat = '0.00%';
    thresholds.getRange('B6:B7').format.numberFormat = '0.00';
    function columnFor(sheet, header) {
      const index = sheet.getUsedRange().values[0].indexOf(header);
      if (index < 0) throw new Error(`Missing ${sheet.name} field ${header}`);
      return excelColumn(index+1);
    }
    function formulaColumn(sheet, header, formula) {
      const rows = sheet.getUsedRange().values.length;
      if (rows < 2) return;
      const col = columnFor(sheet,header);
      sheet.getRange(`${col}2`).formulas = [[formula]];
      sheet.getRange(`${col}2:${col}${rows}`).fillDown();
    }
    const pairRows = pairs.getUsedRange().values.length;
    const areaE = columnFor(pairs,'eez_area_km2'), areaL = columnFor(pairs,'lme_area_km2');
    const intersect = columnFor(pairs,'intersection_km2'), contained = columnFor(pairs,'lme_mostly_contained');
    const ratio = columnFor(pairs,'eez_to_lme_area_ratio');
    formulaColumn(pairs,'intersection_fraction_of_eez',`=${intersect}2/${areaE}2`);
    formulaColumn(pairs,'intersection_fraction_of_lme',`=${intersect}2/${areaL}2`);
    formulaColumn(pairs,'eez_to_lme_area_ratio',`=${areaE}2/${areaL}2`);
    formulaColumn(pairs,'lme_mostly_contained',`=${columnFor(pairs,'intersection_fraction_of_lme')}2>='Selection Rules'!$B$5`);
    formulaColumn(pairs,'flag_prefer_eez_candidate',`=IF(AND(${contained}2,${ratio}2>='Selection Rules'!$B$6),1,0)`);
    formulaColumn(pairs,'flag_review_110_120',`=IF(AND(${contained}2,${ratio}2>='Selection Rules'!$B$7,${ratio}2<'Selection Rules'!$B$6),1,0)`);
    const whole = columnFor(flags,'area_km2');
    const fraction = columnFor(flags,'lme_overlap_fraction_of_eez');
    formulaColumn(flags,'lme_overlap_fraction_of_eez',`=${columnFor(flags,'lme_union_intersection_km2')}2/${whole}2`);
    formulaColumn(flags,'hs_overlap_fraction_of_eez',`=${columnFor(flags,'hs_union_intersection_km2')}2/${whole}2`);
    formulaColumn(flags,'flag_add_low_lme_overlap',`=${fraction}2<'Selection Rules'!$B$4`);
    const pairKey = columnFor(pairs,'eez_unit_id'), flagKey = columnFor(flags,'unit_id');
    for (const flag of ['flag_prefer_eez_candidate','flag_review_110_120']) {
      const flagCol = columnFor(pairs,flag);
      formulaColumn(flags,flag,pairRows<2?'=FALSE()':groupedPairFlagFormula(`'EEZ LME Pairs'!$${pairKey}$2:$${pairKey}$${pairRows}`,`${flagKey}2`,`'EEZ LME Pairs'!$${flagCol}$2:$${flagCol}$${pairRows}`));
    }
    // Show the three requested flags on the compact sheet, joined by immutable unit ID.
    const flagValues = flags.getUsedRange().values;
    const flagNames = ['flag_add_low_lme_overlap','flag_prefer_eez_candidate','flag_review_110_120'];
    compact.getRange('I1:K1').values = [flagNames];
    const keyCol = excelColumn(flagValues[0].indexOf('unit_id')+1);
    for (let c=0; c<flagNames.length; c++) {
      const sourceCol = excelColumn(flagValues[0].indexOf(flagNames[c])+1);
      if (flagValues[0].indexOf(flagNames[c]) < 0) throw new Error(`Missing flag ${flagNames[c]}`);
      compact.getRange(`${excelColumn(c+9)}2`).formulas = [[`=INDEX('EEZ Selection Flags'!$${sourceCol}$2:$${sourceCol}$${flagValues.length},MATCH(A2,'EEZ Selection Flags'!$${keyCol}$2:$${keyCol}$${flagValues.length},0))`]];
      compact.getRange(`${excelColumn(c+9)}2:${excelColumn(c+9)}${dims.rows}`).fillDown();
    }
    styleDataSheet(compact, 'EEZCompactTable', {region_name:38});
    applyFormatsByHeaders(compact);
    compact.getRange(`H2:H${dims.rows}`).format.numberFormat = '0.00%';
    compact.getRange('A1:K1').format.rowHeight = 48;
    compact.getRange('I1:K1').format = {fill:PALETTE.teal,font:{bold:true,color:PALETTE.white},wrapText:true};
    compact.getRange(`I1:K${dims.rows}`).format.columnWidth = 22;
    for (const sheet of [compact,flags,pairs,alternatives,allCompact,thresholds]) {
      previews.push(await renderSheet(workbook,SUMMARY_XLSX,sheet.name,sheet===thresholds?'A1:C14':sheet===compact?'A1:K20':sheet===allCompact?'A1:H20':'A1:O20'));
    }
  }
  previews.push(await renderSheet(workbook, SUMMARY_XLSX, "Summary", "A1:AC40"));
  previews.push(await renderSheet(workbook, SUMMARY_XLSX, "Validation", "A1:D40"));
  previews.push(await renderSheet(workbook, SUMMARY_XLSX, "TL Coverage", "A1:J40"));
  previews.push(await renderSheet(workbook, SUMMARY_XLSX, "Jensen Comparison", "A1:R30"));
  previews.push(await renderSheet(workbook, SUMMARY_XLSX, "Ingestion Audit", "A1:K30"));
  previews.push(await renderSheet(workbook, SUMMARY_XLSX, "Configuration", "A1:C16"));
  previews.push(await renderSheet(workbook, SUMMARY_XLSX, "Sources", "A1:C10"));
  const qa = await inspectWorkbook(workbook, SUMMARY_XLSX, "Summary", `A1:Q${Math.min(dims.rows, 12)}`);
  const blob = await SpreadsheetFile.exportXlsx(workbook);
  await blob.save(path.join(OUTPUT, SUMMARY_XLSX));
  return { qa, previews };
}

async function buildRegionalWorkbook(pilot, metadata) {
  const workbook = Workbook.create();
  const unitDir = path.join(TABLES, "regions", pilot.id);
  const species = await addCsvSheet(workbook, path.join(unitDir, "species.csv"), "Species");
  const commercial = await addCsvSheet(workbook, path.join(unitDir, "commercial.csv"), "Commercial");
  const functional = await addCsvSheet(workbook, path.join(unitDir, "functional.csv"), "Functional");
  const missing = await addCsvSheet(workbook, path.join(unitDir, "missing_tl.csv"), "Missing TL");
  const validation = await addCsvSheet(workbook, path.join(unitDir, "validation.csv"), "Validation");
  const metadataSheet = addKeyValueSheet(workbook, "Metadata", `${pilot.id} - ${pilot.name}`, [
    ["Unit ID", pilot.id, "Sea Around Us region identifier"],
    ["Transfer efficiency", metadata.transfer_efficiency, "Used by every SPPR formula"],
    ["Year", metadata.year, `Latest year common to all ${metadata.unit_count} datasets`],
    ["Region type", pilot.type, "Sea Around Us spatial classification"],
    ["Catch scope", "Landings + Discards", "Reported + unreported; all sectors, gears, entities, and end uses"],
    ["SPPR formula", "(1 / TE)^(TL - 1)", "TE is the Metadata!B5 value"],
    ["PPR formula", "Catch tonnes × SPPR", "Unit: tonnes primary-production equivalent"],
    ["Wet-weight/carbon divisor", "Not applied", "The paper's /9 conversion is intentionally omitted"],
    ["Primary TL source", "2020 supplement MeanTL", "No SPPR regression from the supplement is used"],
    ["Secondary TL source", "Sea Around Us exploited organisms", "Exact taxon matches, followed by documented fallbacks"],
    ["Catch data URL", "https://www.seaaroundus.org/data/", `Frozen archive: raw_data/SAU_downloads/${pilot.id}-catch.zip`],
    ["Method source", "Pauly & Christensen (1995)", "Nature 374:255-257"],
  ]);

  const speciesDims = styleDataSheet(species, `${pilot.id}SpeciesTable`, {
    taxon: 25,
    common_name: 23,
    functional_group: 30,
    commercial_group: 24,
    tl_source: 40,
    reference_taxon: 25,
  });
  applyFormatsByHeaders(species);
  if (speciesDims.rows > 1) {
    species.getRange("T2").formulas = [[`=IF(O2="","",(1/'Metadata'!$B$5)^(O2-1))`]];
    species.getRange(`T2:T${speciesDims.rows}`).fillDown();
    species.getRange("U2").formulas = [[`=IF(T2="","",I2*T2)`]];
    species.getRange(`U2:U${speciesDims.rows}`).fillDown();
    species.getRange(`R2:R${speciesDims.rows}`).conditionalFormats.add("containsText", {
      text: "low",
      format: { fill: PALETTE.paleOrange, font: { color: "#9A3412" } },
    });
  }

  for (const [sheet, groupCol, tableName] of [
    [commercial, "H", `${pilot.id}CommercialTable`],
    [functional, "G", `${pilot.id}FunctionalTable`],
  ]) {
    const dims = styleDataSheet(sheet, tableName, { commercial_group: 26, functional_group: 34 });
    applyFormatsByHeaders(sheet);
    if (dims.rows > 1) {
      for (const [col,formula] of Object.entries(regionalGroupFormulas(speciesDims.rows,groupCol))) {
        sheet.getRange(`${col}2`).formulas = [[formula]];
        sheet.getRange(`${col}2:${col}${dims.rows}`).fillDown();
      }
      sheet.getRange(`G2:G${dims.rows}`).conditionalFormats.add("cellIs", {
        operator: "lessThan",
        formula: 0.9,
        format: { fill: PALETTE.paleRed, font: { color: PALETTE.red, bold: true } },
      });
      sheet.getRange(`O2:O${dims.rows}`).conditionalFormats.add("dataBar", { color: PALETTE.orange });
    }
  }

  styleDataSheet(missing, `${pilot.id}MissingTLTable`, { taxon: 25, tl_source: 36 });
  applyFormatsByHeaders(missing);
  styleDataSheet(validation, `${pilot.id}ValidationTable`, { check: 34, unit: 34 });
  applyFormatsByHeaders(validation);
  metadataSheet.getRange("B5").format.numberFormat = transferEfficiencyNumberFormat();

  const safeName = pilot.name.replace(/[^A-Za-z0-9]+/g, "_").replace(/^_|_$/g, "");
  const filename = `${pilot.id}_${safeName}.xlsx`;
  const previews = [];
  previews.push(await renderSheet(workbook, filename, "Species", `A1:U${Math.min(speciesDims.rows, 22)}`));
  previews.push(await renderSheet(workbook, filename, "Commercial", "A1:O25"));
  previews.push(await renderSheet(workbook, filename, "Functional", "A1:O25"));
  previews.push(await renderSheet(workbook, filename, "Missing TL", "A1:U12"));
  previews.push(await renderSheet(workbook, filename, "Validation", "A1:D22"));
  previews.push(await renderSheet(workbook, filename, "Metadata", "A1:C16"));
  const qa = await inspectWorkbook(workbook, filename, "Species", `A1:U${Math.min(speciesDims.rows, 12)}`);
  const blob = await SpreadsheetFile.exportXlsx(workbook);
  await blob.save(path.join(REGIONAL_OUTPUT, filename));
  return { qa, previews, filename };
}

await fs.mkdir(OUTPUT, { recursive: true });
await fs.mkdir(REGIONAL_OUTPUT, { recursive: true });
await fs.mkdir(PREVIEWS, { recursive: true });
const metadata = JSON.parse(await fs.readFile(path.join(TABLES, "run_metadata.json"), "utf8"));
const units = JSON.parse(await fs.readFile(path.join(TABLES, "units.json"), "utf8"));
const shard=regionalExportShard(units,process.argv.slice(2));
if (shard.count>1 && !REGIONS_ONLY) throw new Error('Sharded export requires --regions-only');
const reports = [];
if (!REGIONS_ONLY) reports.push(await buildSummaryWorkbook(metadata));
for (const [index,unit] of (SUMMARY_ONLY ? [] : shard.units).entries()) {
  if (RESUME) {
    const safeName = unit.name.replace(/[^A-Za-z0-9]+/g, '_').replace(/^_|_$/g, '');
    const existing = path.join(REGIONAL_OUTPUT,`${unit.unit_id}_${safeName}.xlsx`);
    try { await fs.access(existing); console.log(`Reusing ${unit.unit_id}`); continue; } catch {}
  }
  console.log(`Building ${unit.unit_id} (${index+1}/${shard.units.length}; batch ${shard.index+1}/${shard.count})`);
  reports.push(await buildRegionalWorkbook({ id: unit.unit_id, name: unit.name, type: unit.region_type }, metadata));
}
const qaName = SUMMARY_ONLY ? 'summary_qa.json' : REGIONS_ONLY ? `regional_qa${shard.count>1?`_${shard.index}_of_${shard.count}`:''}.json` : 'workbook_qa.json';
await fs.writeFile(path.join(PREVIEWS, qaName), JSON.stringify(reports, null, 2));
console.log(JSON.stringify({
  scope: SCOPE_LABEL,
  workbooks: [...(REGIONS_ONLY ? [] : [SUMMARY_XLSX]), ...reports.filter(r=>r.filename).map((r) => r.filename)],
  previewCount: reports.flatMap((r) => r.previews).length,
  qaFile: path.join(PREVIEWS, qaName),
}, null, 2));
