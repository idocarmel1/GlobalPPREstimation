import { Workbook } from '@oai/artifact-tool';
const w=Workbook.create();w.worksheets.add('Taxon mappings');
console.log(w.help('range hyperlink', {search:'hyperlink',include:'index,examples,notes',maxChars:3000}).ndjson);
