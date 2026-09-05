import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";


const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const IS_GLOBAL = process.argv.includes("--global");
const SCOPE_LABEL = IS_GLOBAL ? "global" : "pilot";
const OUTPUT = path.join(ROOT, IS_GLOBAL ? "global_output" : "output");
const TABLES = path.join(OUTPUT, "tables");
const REGIONAL_OUTPUT = path.join(OUTPUT, "regional_calculations");
const PREVIEWS = path.join(ROOT, "..", "tmp", IS_GLOBAL ? "global_workbook_previews" : "workbook_previews");
const SUMMARY_CSV = `${SCOPE_LABEL}_summary.csv`;
const SUMMARY_XLSX = `PPR_${SCOPE_LABEL}_summary.xlsx`;

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
  const text = (await fs.readFile(csvPath, "utf8")).replace(/^\uFEFF/, "");
  await workbook.fromCSV(text, { sheetName });
  const sheet = workbook.worksheets.getItem(sheetName);
  const used = sheet.getUsedRange();
  const values = used.values;
  const numericPattern = /^-?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?$/;
  for (let r = 1; r < values.length; r += 1) {
    for (let c = 0; c < (values[r]?.length ?? 0); c += 1) {
      const value = values[r][c];
      if (typeof value === "string" && numericPattern.test(value.trim())) {
        values[r][c] = Number(value);
      }
    }
  }
  used.values = values;
  return sheet;
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
    else if (/catch|tonnes|ppr|difference/i.test(header)) range.format.numberFormat = "#,##0.00";
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
  await addCsvSheet(workbook, path.join(TABLES, SUMMARY_CSV), "Summary");
  await addCsvSheet(workbook, path.join(TABLES, "validation.csv"), "Validation");
  await addCsvSheet(workbook, path.join(TABLES, "tl_coverage.csv"), "TL Coverage");
  await addCsvSheet(workbook, path.join(TABLES, "jensen_comparison.csv"), "Jensen Comparison");
  await addCsvSheet(workbook, path.join(TABLES, "ingestion_audit.csv"), "Ingestion Audit");
  addKeyValueSheet(workbook, "Configuration", `PPR ${SCOPE_LABEL} configuration`, [
    ["Scope", metadata.scope, IS_GLOBAL ? "All Sea Around Us-defined LME and High Seas units" : "Not a global estimate or global ranking"],
    ["Spatial units", metadata.unit_count, `${metadata.lme_count} LMEs + ${metadata.highseas_count} High Seas units`],
    ["Year", metadata.year, "Latest year present in every configured catch archive"],
    ["Transfer efficiency", metadata.transfer_efficiency, "Fixed TE for the approved 1995 trophic-chain method"],
    ["SPPR", "(1 / TE)^(TL - 1)", "With TE=0.1, SPPR = 10^(TL-1)"],
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
    ["1995 method", "Pauly & Christensen (1995), Nature 374:255-257", "TE=0.1 trophic-chain calculation"],
    ["2020 supplement", "sources/2020 sup.xlsx", "MeanTL only; no Luong regression SPPR used"],
    ["Interpretation", `${IS_GLOBAL ? "Global" : "Pilot"} fractions sum to 100%`, `Fractions and ranks apply to ${metadata.unit_count} configured units`],
  ]);

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
    const chartRows = IS_GLOBAL ? Math.min(25, dims.rows - 1) : dims.rows - 1;
    summary.getRange("S24:T24").values = [["Region", "Species PPR"]];
    summary.getRange("S25:T25").formulas = [["=B2", "=K2"]];
    summary.getRange(`S25:T${24 + chartRows}`).fillDown();
    const chart = summary.charts.add("bar", summary.getRange(`S24:T${24 + chartRows}`));
    chart.title = `${IS_GLOBAL ? "Top 25 global" : "Pilot"} PPR ranking (tonnes primary-production equivalent)`;
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
      sheet.getRange("H2").formulas = [[`=IF(E2=0,"",I2/E2)`]];
      sheet.getRange(`H2:H${dims.rows}`).fillDown();
      sheet.getRange("I2").formulas = [[
        `=SUMIF('Species'!$${groupCol}$2:$${groupCol}$${speciesDims.rows},A2,'Species'!$U$2:$U$${speciesDims.rows})`,
      ]];
      sheet.getRange(`I2:I${dims.rows}`).fillDown();
      sheet.getRange("K2").formulas = [[`=IF(J2="","",(1/'Metadata'!$B$5)^(J2-1))`]];
      sheet.getRange(`K2:K${dims.rows}`).fillDown();
      sheet.getRange("L2").formulas = [[`=IF(E2=0,"",E2*K2)`]];
      sheet.getRange(`L2:L${dims.rows}`).fillDown();
      sheet.getRange("M2").formulas = [[`=I2-L2`]];
      sheet.getRange(`M2:M${dims.rows}`).fillDown();
      sheet.getRange("N2").formulas = [[`=IF(L2=0,"",I2/L2)`]];
      sheet.getRange(`N2:N${dims.rows}`).fillDown();
      sheet.getRange("O2").formulas = [[`=IF(L2=0,"",M2/L2)`]];
      sheet.getRange(`O2:O${dims.rows}`).fillDown();
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
  metadataSheet.getRange("B5").format.numberFormat = "0.0";

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
const reports = [];
reports.push(await buildSummaryWorkbook(metadata));
for (const unit of units) {
  reports.push(await buildRegionalWorkbook({ id: unit.unit_id, name: unit.name, type: unit.region_type }, metadata));
}
await fs.writeFile(path.join(PREVIEWS, "workbook_qa.json"), JSON.stringify(reports, null, 2));
console.log(JSON.stringify({
  scope: SCOPE_LABEL,
  workbooks: [SUMMARY_XLSX, ...reports.slice(1).map((r) => r.filename)],
  previewCount: reports.flatMap((r) => r.previews).length,
  qaFile: path.join(PREVIEWS, "workbook_qa.json"),
}, null, 2));
