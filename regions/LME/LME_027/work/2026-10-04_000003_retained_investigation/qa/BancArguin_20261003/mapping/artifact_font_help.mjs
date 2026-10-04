import { Workbook } from '@oai/artifact-tool';
const w=Workbook.create();
console.log(w.help('*',{search:'underline',include:'index,examples,notes',maxChars:4000}).ndjson);
