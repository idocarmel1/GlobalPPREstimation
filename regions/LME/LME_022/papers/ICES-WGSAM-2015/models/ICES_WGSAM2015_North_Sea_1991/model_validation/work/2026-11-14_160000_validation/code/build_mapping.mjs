import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const root = process.cwd();
const modelDir = path.join(root, 'regions/LME/LME_022/papers/ICES-WGSAM-2015/models/ICES_WGSAM2015_North_Sea_1991');
const outputDir = path.join(modelDir, 'model_validation');
const loaderRepair = process.argv.includes('--loader-repair');
const work = path.join(outputDir, loaderRepair ? 'work/2026-11-14_161706_loader_repair' : 'work/2026-11-14_160000_validation');
const qaDir = path.join(work, 'qa');
const audit = JSON.parse(await fs.readFile(path.join(root,'regions/LME/LME_022/work/2026-11-14_160000_validation/outputs/mapping_audit.json'),'utf8'));
const workbook = Workbook.create();
if (loaderRepair) {
  const diagDir=path.join(modelDir,'results/diagnostics/2026-11-14_loader_repair');
  const summary=JSON.parse(await fs.readFile(path.join(diagDir,'summary.json'),'utf8'));
  const negativeText=await fs.readFile(path.join(diagDir,'negative_entries.tsv'),'utf8');
  const negativeLines=negativeText.trim().split(/\r?\n/);
  if(summary.model_id!=='ICES_WGSAM2015_North_Sea_1991'||!summary.canonical_unchanged||negativeLines.length!==1) throw new Error('Unexpected diagnostic identity or negative ledger');
  const methods=summary.methods;
  if(methods.length!==3||methods.some(m=>m.execution_status!=='ok'||m.diagnostic.status!=='WARN'||m.negative_entries.length!==0||m.matrix_checks.shape.join(',')!=='70,5'||Object.values(m.matrix_checks.mask_counts).some(n=>n!==0))) throw new Error('Unexpected method outcomes');
  const sh=workbook.worksheets.add('SPPR diagnostics');
  sh.showGridLines=false;
  sh.getRange('A1:J29').format.font={name:'Arial',size:11,color:'#202020'};
  const merged=(row,value,height=30,fill=null)=>{
    const r=sh.getRange(`A${row}:J${row}`);r.merge();sh.getRange(`A${row}`).values=[[value]];r.format.wrapText=true;r.format.rowHeight=height;r.format.verticalAlignment='center';if(fill)r.format.fill=fill;
  };
  merged(1,'SPPR diagnostics: repaired source loader',30);
  sh.getRange('A1:J1').format.font={name:'Arial',size:15,bold:true,color:'#243B53'};
  merged(2,'ICES_WGSAM2015_North_Sea_1991 | Official rerun: 14 November 2026 | Raw SPPR coefficients below; no /9 carbon conversion. Taxon-mapping PPR in the first sheet remains in tonnes C.',32);
  merged(3,'All three methods completed with WARN: no negative coefficients; 350 finite values per method (70 recipient groups × 5 basal sources). PP budgets close on the effective runtime. Numerical convergence is not researcher approval.',34,'#FFF2CC');
  merged(4,'Configuration: EE floor ON, floor = 0.1, threshold = 0.1; diet normalization, GS defaults, zero catch, zero BA and BA reconciliation OFF. Detritus collapse = never; closed boundary (open mode none; theta = 1; external SPPR = 0).',36);
  merged(5,'Repaired loader preserves source producer/detritus routing, TL, catch and known BA; accounts for documented fleet discard returns once. Four missing nonfeeding synthetic-import diet cells become structural runtime zeros; canonical source missingness is retained.',36);
  merged(6,'Named detritus coefficients are PP units per unit detritus. Negative source count covers all five source columns; negative entry count covers the full 70 × 5 matrix. Zero below is an observed count, not a substituted coefficient.',32);
  const headers=['Method (engine ID)','Overall status','Living spectral radius (ρ)','Detritus coupling (b)','DetritusDOMWaterColumn (67) raw SPPR','DetritusPOMSediment (68) raw SPPR','Discards (69) raw SPPR','Negative entries','Negative sources','Finite matrix values'];
  sh.getRange('A7:J7').values=[headers];
  const values=methods.map(m=>{const d=m.diagnostic.divergence;const pools=Object.fromEntries(d.sppr_det.items);return [m.method,m.diagnostic.status,d.rho_living,d.b,pools[67],pools[68],pools[69],m.negative_entries.length,m.matrix_checks.negative_source_count,350];});
  sh.getRange('A8:J10').values=values;
  const table=sh.tables.add('A7:J10',true,'ICES1991SPPRMethodSummary');table.showFilterButton=true;
  sh.getRange('A7:J7').format={fill:'#243B53',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},wrapText:true,verticalAlignment:'center',horizontalAlignment:'center',rowHeight:64};
  sh.getRange('A8:J10').format.wrapText=true;sh.getRange('A8:J10').format.rowHeight=36;sh.getRange('A8:J10').format.verticalAlignment='center';
  sh.getRange('C8:G10').setNumberFormat('0.000000000000');sh.getRange('H8:J10').setNumberFormat('0');
  merged(12,'Negative-entry ledger: empty for GE, TE and With Egestion (strict test < 0; tolerance 0). For every method, DetritusDOMWaterColumn (67), DetritusPOMSediment (68) and Discards (69) each have 0 negative entries. No negative-pair rows are omitted.',36);
  merged(13,'Warnings retained from the diagnostics',26,'#D9E2F3');
  methods.forEach((m,i)=>merged(i+14,`${m.method}: ${m.diagnostic.warnings.join(' | ')}`,50,'#FFF2CC'));
  merged(18,'Primary-production budget in the effective runtime (raw model PP currency; no carbon conversion)',26,'#D9E2F3');
  const blocks=[['A','B','Method'],['C','D','PP inflow'],['E','F','PP outflow'],['G','H','Relative gap (fraction)'],['I','J','Balance status']];
  for(const [a,b,label] of blocks){sh.getRange(`${a}19:${b}19`).merge();sh.getRange(`${a}19`).values=[[label]];}
  sh.getRange('A19:J19').format={fill:'#243B53',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},rowHeight:28};
  methods.forEach((m,i)=>{const row=i+20;const d=m.diagnostic.balance;for(const [j,v] of [m.method,d.inflow,d.outflow,d.rel_gap,d.status].entries()){const [a,b]=blocks[j];sh.getRange(`${a}${row}:${b}${row}`).merge();sh.getRange(`${a}${row}`).values=[[v]];}sh.getRange(`A${row}:J${row}`).format.rowHeight=28;});
  sh.getRange('C20:F22').setNumberFormat('0.000000000000');sh.getRange('G20:H22').setNumberFormat('0.000000000000E+00');
  merged(24,'Source versus effective state: source detritus BA = 0 is retained before the EE floor. Positive effective detritus BA is the floor-runtime stock closure under the operational detritus EE = 1 convention; it is not observed author BA or an invented source export. Native equivalence remains unestablished.',46,'#FFF2CC');
  merged(25,'The EE-floor mortality sink is a calculation assumption (total 1.983704066273114 in model flow currency). TE now includes returned-catch coupling (b = 0.1554967742366123); the former b = 0 convention does not describe this run. Source catch and canonical inputs remain unchanged.',38);
  const links=[
    [27,'A','E','report_ready.json','Diagnostic summary and interpretation'],[27,'F','J','negative_entries.tsv','Complete negative-entry ledger (header only)'],
    [28,'A','E','runtime_accounting_review.json','Source / pre-floor / effective accounting review'],[28,'F','J','summary.json','Full-precision official method diagnostics'],
    [29,'A','E','source_loader_audit.json','Source-loader preservation audit'],[29,'F','J','run_manifest.json','Official run manifest and evidence provenance'],
  ];
  for(const [row,a,b,file,label] of links){await fs.access(path.join(diagDir,file));sh.getRange(`${a}${row}:${b}${row}`).merge();sh.getRange(`${a}${row}`).formulas=[[`=HYPERLINK("../results/diagnostics/2026-11-14_loader_repair/${file}","${label}")`]];sh.getRange(`${a}${row}:${b}${row}`).format.rowHeight=27;sh.getRange(`${a}${row}`).format.font={name:'Arial',size:11,color:'#0563C1',underline:'single'};}
  for(const [c,width] of Object.entries({A:25,B:13,C:19,D:19,E:25,F:25,G:23,H:13,I:13,J:14})) sh.getRange(`${c}1:${c}29`).format.columnWidth=width;
  sh.freezePanes.freezeRows(7);sh.freezePanes.freezeColumns(1);
  workbook.recalculate();
  for(const folder of ['inputs','outputs','qa'])await fs.mkdir(path.join(work,folder),{recursive:true});
  const before=path.join(work,'inputs/taxon_mapping_before_diagnostics.xlsx');try{await fs.access(before);}catch{await fs.copyFile(path.join(outputDir,'taxon_mapping.xlsx'),before);}
  const exported=await SpreadsheetFile.exportXlsx(workbook);await exported.save(path.join(work,'outputs/sppr_diagnostics_sheet.xlsx'));
  for(const [name,range] of [['diagnostics_top','A1:J16'],['diagnostics_bottom','A18:J29']]){const preview=await workbook.render({sheetName:'SPPR diagnostics',range,scale:1,format:'png'});await fs.writeFile(path.join(qaDir,`${name}.png`),new Uint8Array(await preview.arrayBuffer()));}
  console.log(JSON.stringify({authoredSheet:'SPPR diagnostics',summaryTable:'A7:J10',negativeEntries:0,statuses:methods.map(m=>[m.method,m.diagnostic.status])}));
  process.exit(0);
}
if (process.argv.includes('--diagnostics')) {
  const diagDir=path.join(modelDir,'results/diagnostics/2026-11-14_validation/structural_zero');
  const ready=JSON.parse(await fs.readFile(path.join(diagDir,'report_ready.json'),'utf8'));
  const text=await fs.readFile(path.join(diagDir,'negative_entries.tsv'),'utf8');
  const lines=text.trim().split(/\r?\n/); const keys=lines.shift().split('\t');
  const rows=lines.map(line=>Object.fromEntries(line.split('\t').map((v,i)=>[keys[i],v])));
  rows.sort((a,b)=>a.method.localeCompare(b.method)||Number(a.source_id)-Number(b.source_id)||Number(a.group_id)-Number(b.group_id));
  if(rows.length!==264 || ready.summary.some(s=>s.status!=='FAIL')) throw new Error('Diagnostic identity/count changed');
  const diagnostic=workbook.worksheets.add('SPPR diagnostics');
  const end=rows.length+7;
  diagnostic.showGridLines=false;
  diagnostic.getRange(`A1:G${end}`).format.font={name:'Arial',size:11,color:'#202020'};
  const overview=[
    'SPPR diagnostics: full negative source–group entries',
    'ICES_WGSAM2015_North_Sea_1991. Diagnostic run: 14 November 2026. Raw source-specific SPPR coefficients, without /9 carbon conversion. Matrices: 70 recipient groups × 5 sources; all entries finite.',
    'Operational adaptation: only four nonfeeding synthetic-import diet cells DC[66–69,70] changed from missing to 0 in an ephemeral runtime copy. Canonical source inputs and missingness remain unchanged.',
    'EE floor ON (0.1); diet normalization, GS defaults and BA reconciliation OFF. Detritus collapse: never; closed boundary. This adaptation does not correct producer routing, detritus self-routing, source TL loss or runtime BA residuals.',
    'GE: FAIL, 132 negative entries. TE: FAIL, no negative entries. With Egestion: FAIL, 132 negative entries. All three fail the PP-balance check (gap about 79%). No negative TE entries does not establish a diagnostic pass.',
  ];
  overview.forEach((v,i)=>{
    const n=i+1;diagnostic.getRange(`A${n}:G${n}`).merge();diagnostic.getRange(`A${n}`).values=[[v]];
    diagnostic.getRange(`A${n}:G${n}`).format.wrapText=true;
    diagnostic.getRange(`A${n}:G${n}`).format.rowHeight=[28,28,34,40,34][i];
  });
  diagnostic.getRange('A1:G1').format.font={name:'Arial',size:15,bold:true,color:'#243B53'};
  diagnostic.getRange('A5:G5').format.fill='#FCE8E6';
  diagnostic.getRange('A6:C6').merge();diagnostic.getRange('D6:G6').merge();
  diagnostic.getRange('A6').formulas=[['=HYPERLINK("../results/diagnostics/2026-11-14_validation/structural_zero/report_ready.json","Configuration and diagnostic summary")']];
  diagnostic.getRange('D6').formulas=[['=HYPERLINK("../results/diagnostics/2026-11-14_validation/structural_zero/negative_entries.tsv","Full-precision source ledger (strict negative test; tolerance 0)")']];
  diagnostic.getRange('A6:G6').format.rowHeight=26;
  for(const address of ['A6','D6']) diagnostic.getRange(address).format.font={name:'Arial',size:11,color:'#0563C1',underline:'single'};
  diagnostic.getRange('A7:G7').values=[['Method (engine ID)','Source ID','Source name','Group ID','Recipient group name','Raw SPPR coefficient','Sign tolerance']];
  diagnostic.getRange(`A8:G${end}`).values=rows.map(r=>[r.method,Number(r.source_id),r.source_name,Number(r.group_id),r.group_name,Number(r.value),Number(r.comparison_tolerance)]);
  const dt=diagnostic.tables.add(`A7:G${end}`,true,'ICES1991SPPRNegativeEntries');dt.showFilterButton=true;
  diagnostic.getRange('A7:G7').format={fill:'#243B53',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},wrapText:true,verticalAlignment:'center',horizontalAlignment:'center',rowHeight:34};
  diagnostic.getRange(`A8:G${end}`).format.wrapText=true;diagnostic.getRange(`A8:G${end}`).format.rowHeight=32;
  diagnostic.getRange(`A8:G${end}`).format.verticalAlignment='center';
  diagnostic.getRange(`F8:F${end}`).setNumberFormat('0.000000000000');
  for(const c of ['B','D','G']) diagnostic.getRange(`${c}8:${c}${end}`).setNumberFormat('0');
  for(const [c,width] of Object.entries({A:24,B:10,C:34,D:10,E:58,F:24,G:14})) diagnostic.getRange(`${c}1:${c}${end}`).format.columnWidth=width;
  diagnostic.freezePanes.freezeRows(7);diagnostic.freezePanes.freezeColumns(1);
  workbook.recalculate();
  await fs.mkdir(qaDir,{recursive:true});
  await fs.mkdir(path.join(work,'inputs'),{recursive:true});
  const before=path.join(work,'inputs/taxon_mapping_before_diagnostics.xlsx');
  try{await fs.access(before);}catch{await fs.copyFile(path.join(outputDir,'taxon_mapping.xlsx'),before);}
  const exported=await SpreadsheetFile.exportXlsx(workbook);await exported.save(path.join(work,'outputs/sppr_diagnostics_sheet.xlsx'));
  for(const [name,range] of [['diagnostics_top','A1:G16'],['diagnostics_bottom',`A260:G${end}`]]){
    const preview=await workbook.render({sheetName:'SPPR diagnostics',range,scale:1,format:'png'});
    await fs.writeFile(path.join(qaDir,`${name}.png`),new Uint8Array(await preview.arrayBuffer()));
  }
  console.log(JSON.stringify({authoredSheet:'SPPR diagnostics',negativeEntries:rows.length,methods:ready.summary.map(s=>[s.method,s.status,s.negative_entries])}));
  process.exit(0);
}
const sheet = workbook.worksheets.add('Taxon mapping');
const sources = workbook.worksheets.add('Sources');
if (process.argv.includes('--help-font')) {
  console.log(workbook.help('range.format.font', {include:'index,notes,examples',maxChars:4500}).ndjson);
  process.exit(0);
}
await fs.mkdir(qaDir,{recursive:true});
const end = audit.rows.length + 7;
sheet.showGridLines = false;
sheet.getRange(`A1:G${end}`).format.font = {name:'Arial',size:11,color:'#202020'};
sheet.getRange('A1:G1').merge();
sheet.getRange('A1').values = [['North Sea LME_022 taxon mapping appendix']];
sheet.getRange('A1:G1').format.font = {name:'Arial',size:15,bold:true,color:'#243B53'};
sheet.getRange('A1:G1').format.rowHeight = 30;
const notes = [
 'Reference: 2019 total catch (landings plus discards). Selected model: ICES_WGSAM2015_North_Sea_1991. All 384 exact catch labels.',
 'Independent simple trophic chain: catch × saved classic coefficient / 9 once, in tonnes C. Sorted by unrounded PPR descending, then taxon name; unavailable PPR last.',
 '72 labels lack a saved TL/coefficient; all have zero recorded 2019 catch and zero annual PPR. ? means unavailable. No annual contribution is unknown.',
 'Total catch: 2,717,260.698205 t. Simple-chain PPR: 188,909,420.829195 t C. Exact-model mappings and allocations are absent for all 384 taxa.',
];
for (let i=0;i<notes.length;i++) {
  const r=i+2;
  sheet.getRange(`A${r}:G${r}`).merge();
  sheet.getRange(`A${r}`).values=[[notes[i]]];
  sheet.getRange(`A${r}:G${r}`).format.wrapText=true;
  sheet.getRange(`A${r}:G${r}`).format.rowHeight=30;
}
sheet.getRange('A6:C6').merge();
sheet.getRange('A6').formulas=[['=HYPERLINK("#\'Sources\'!A1","Sources and limitations")']];
sheet.getRange('D6:G6').merge();
sheet.getRange('D6').values=[['Unresolved means no retained exact-model mapping; biological impossibility is not inferred.']];
sheet.getRange('D6:G6').format.wrapText=true;
sheet.getRange('A6:G6').format.rowHeight=30;
const headers=['Taxon name','TL','Catch (t)','Simple-chain PPR (t C)','Mapped group names and weights','Confidence level','Reason'];
sheet.getRange('A7:G7').values=[headers];
sheet.getRange(`A8:G${end}`).values=audit.rows.map(r=>[r.taxon,r.tl??'?',r.catch_tonnes??'?',r.simple_chain_ppr_tC??'?', 'Unresolved',r.overall_confidence,r.reason]);
const table=sheet.tables.add(`A7:G${end}`,true,'ICES1991TaxonMapping');
table.showFilterButton=true;
sheet.getRange('A7:G7').format={fill:'#243B53',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},wrapText:true,verticalAlignment:'center',horizontalAlignment:'center',rowHeight:38};
sheet.getRange(`A8:G${end}`).format.wrapText=true;
sheet.getRange(`A8:G${end}`).format.verticalAlignment='center';
sheet.getRange(`A8:G${end}`).format.rowHeight=42;
sheet.getRange(`B8:D${end}`).format.horizontalAlignment='right';
sheet.getRange(`B8:B${end}`).setNumberFormat('0.00');
sheet.getRange(`C8:D${end}`).setNumberFormat('#,##0.000000');
for (let i=0;i<audit.rows.length;i++) if(audit.rows[i].missing_coefficient) sheet.getRange(`A${i+8}:G${i+8}`).format.rowHeight=62;
for(const [c,width] of Object.entries({A:31,B:8,C:20,D:25,E:27,F:15,G:78})) sheet.getRange(`${c}1:${c}${end}`).format.columnWidth=width;
sheet.freezePanes.freezeRows(7);
sheet.freezePanes.freezeColumns(1);

sources.showGridLines=false;
sources.getRange('A1:D16').format.font={name:'Arial',size:11,color:'#202020'};
sources.getRange('A1:D1').merge();
sources.getRange('A1').values=[['Descriptive sources and mapping limitations']];
sources.getRange('A1:D1').format.font={name:'Arial',size:15,bold:true,color:'#243B53'};
sources.getRange('A1:D1').format.rowHeight=30;
sources.getRange('A2:D2').merge();
sources.getRange('A2').values=[['Sources identify current inputs and the absence of an ICES-model catch crosswalk. The Scotland model appendix is a separate candidate record.']];
sources.getRange('A2:D2').format.wrapText=true;
sources.getRange('A2:D2').format.rowHeight=32;
sources.getRange('A3').formulas=[['=HYPERLINK("#\'Taxon mapping\'!A1","Return to taxon mapping")']];
sources.getRange('A4:D4').values=[['Source / material','What it supports / limits','Link','Reviewed']];
sources.getRange('A4:D4').format={fill:'#243B53',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},wrapText:true,verticalAlignment:'center',rowHeight:28};
const sourceRows = audit.sources.map(s=>[`${s.id}: ${s.title}`,`${s.locator}. ${s.supports}.`,'Open source','2026-11-14']);
sources.getRange(`A5:D${4+sourceRows.length}`).values=sourceRows;
for(let i=0;i<audit.sources.length;i++){
  const s=audit.sources[i];
  const rel=path.relative(outputDir,path.join(root,s.path)).split(path.sep).join('/');
  sources.getRange(`C${i+5}`).formulas=[[`=HYPERLINK("${rel.replaceAll('"','""')}","Open source")`]];
}
sources.getRange('A14:D14').merge();
sources.getRange('A14').values=[['Membership and allocation confidence are separately unavailable. The Unresolved category records the missing mapping handoff; no M8/W8 biological rejection or Very low decision is claimed.']];
sources.getRange('A15:D15').merge();
sources.getRange('A15').values=[['Model scope: 69 source ecological groups, including 3 detritus pools. The source inventory excludes its 11 fleets and any synthetic computational import.']];
sources.getRange('A5:D15').format.wrapText=true;
sources.getRange('A5:D15').format.verticalAlignment='center';
sources.getRange('A5:D12').format.rowHeight=66;
sources.getRange('A14:D15').format.rowHeight=38;
for(const [c,width] of Object.entries({A:52,B:91,C:18,D:17})) sources.getRange(`${c}1:${c}15`).format.columnWidth=width;
sources.freezePanes.freezeRows(4);
for(const r of [sheet.getRange('A6'),sources.getRange('A3'),sources.getRange('C5:C12')]) r.format.font={name:'Arial',size:11,color:'#0563C1',underline:'single'};
workbook.recalculate();
console.log((await workbook.inspect({kind:'sheet,table',maxChars:2000,tableMaxRows:2,tableMaxCols:7})).ndjson);
const out=await SpreadsheetFile.exportXlsx(workbook);
await out.save(path.join(outputDir,'taxon_mapping.xlsx'));
for(const [name,sh,range] of [['mapping_top','Taxon mapping','A1:G17'],['mapping_bottom','Taxon mapping',`A379:G${end}`],['sources','Sources','A1:D15']]){
  const preview=await workbook.render({sheetName:sh,range,scale:1,format:'png'});
  await fs.writeFile(path.join(qaDir,`${name}.png`),new Uint8Array(await preview.arrayBuffer()));
}
console.log(JSON.stringify({output:path.join(outputDir,'taxon_mapping.xlsx'),rows:audit.rows.length}));
