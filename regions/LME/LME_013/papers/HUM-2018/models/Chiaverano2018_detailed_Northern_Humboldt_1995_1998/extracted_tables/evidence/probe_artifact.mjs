import {Workbook} from '@oai/artifact-tool';
const w=Workbook.create();
console.log(w.help('underline',{include:'index,notes,examples',maxChars:2500}).ndjson);
