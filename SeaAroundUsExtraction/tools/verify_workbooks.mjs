// Verify exported XLSX files by reopening them with artifact-tool.

import path from "node:path";
import fs from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";
import { resolveReleaseArgs } from "./scope_args.mjs";


const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const RELEASE = resolveReleaseArgs(process.argv.slice(2));
const OUTPUT = path.join(ROOT, RELEASE.outputDirectory);
const SCOPE_LABEL = RELEASE.scopeLabel;
const units = JSON.parse(await fs.readFile(path.join(OUTPUT, "tables", "units.json"), "utf8"));
const files = [
  path.join(OUTPUT, `PPR_${SCOPE_LABEL}_summary.xlsx`),
  ...units.map((unit) => {
    const safeName = unit.name.replace(/[^A-Za-z0-9]+/g, "_").replace(/^_|_$/g, "");
    return path.join(OUTPUT, "regional_calculations", `${unit.unit_id}_${safeName}.xlsx`);
  }),
];

const results = [];
for (const file of files) {
  const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(file));
  const errors = await workbook.inspect({
    kind: "match",
    searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
    options: { useRegex: true, maxResults: 100 },
    maxChars: 4000,
  });
  const isSummary = file.endsWith(`PPR_${SCOPE_LABEL}_summary.xlsx`);
  const formulaSheet = isSummary ? "Summary" : "Species";
  // fraction_{scope}_ppr / rank_{scope}_ppr moved from P/Q to N/O when the summary
  // table shrank from 17 to 15 columns (ppr_commercial_correct/ppr_functional_correct/
  // ppr_commercial_jensen/ppr_functional_jensen collapsed into ppr_commercial/
  // ppr_functional) - sample the columns build_workbooks.mjs now actually writes
  // formulas into.
  const formulaRange = isSummary ? "N2:O6" : "T2:U5";
  const formulas = await workbook.inspect({
    kind: "table",
    range: `${formulaSheet}!${formulaRange}`,
    include: "values,formulas",
    tableMaxRows: 10,
    tableMaxCols: 4,
    maxChars: 4000,
  });
  const errorText = String(errors.ndjson ?? "");
  if (!errorText.includes("Cell search matched 0 entries")) {
    throw new Error(`Formula errors in ${path.basename(file)}: ${errorText}`);
  }
  results.push({
    file: path.basename(file),
    errorScan: "clear",
    formulaSample: formulas.ndjson,
  });
}

const reportPath = path.join(OUTPUT, "workbook_verification.json");
await fs.writeFile(reportPath, JSON.stringify(results, null, 2));
console.log(JSON.stringify({
  scope: SCOPE_LABEL,
  verifiedWorkbooks: results.length,
  formulaErrorScans: "clear",
  report: reportPath,
}, null, 2));
