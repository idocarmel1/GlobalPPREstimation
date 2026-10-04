import {Workbook} from '@oai/artifact-tool';
const w=Workbook.create();w.worksheets.add('x');
console.log(w.help('range.format.font',{include:'index,examples,notes',maxChars:4500}).ndjson);
