import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
// Resolve the public package entry from the bundled runtime, without copying
// dependencies or retaining a node_modules junction inside the source package.
const runtimeRequire=createRequire('C:/Users/idoca/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bootstrap.cjs');
const {Workbook, SpreadsheetFile}=await import(pathToFileURL(runtimeRequire.resolve('@oai/artifact-tool')).href);

const audit=path.dirname(fileURLToPath(import.meta.url)), root=path.dirname(audit);
const d=JSON.parse(await fs.readFile(path.join(audit,'workbook_data.json'),'utf8'));
const wb=Workbook.create();
const sheets={};
for(const name of ['Read me','DC carbon','DC wet','Label hypothesis','Carbon flows','Arrow ledger','Groups','Budget checks']) sheets[name]=wb.worksheets.add(name);
const navy='#173D4C', teal='#176D72', amber='#FFF0CC', pale='#E9F3F3', red='#FCE3E3';
const col=n=>{let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const num=v=>v===null?'n.a.':typeof v==='string'&&!isNaN(Number(v))?Number(v):v;
function layout(sh,lastcol,lastrow,title,note){
 sh.showGridLines=false;
 sh.getRange(`A1:${lastcol}${lastrow}`).format.font={name:'Arial',size:11,color:'#21343B'};
 sh.getRange(`A1:${lastcol}1`).merge();sh.getRange('A1').values=[[title]];
 sh.getRange(`A1:${lastcol}1`).format={fill:navy,font:{name:'Arial',size:17,bold:true,color:'#FFFFFF'},rowHeight:34};
 sh.getRange(`A2:${lastcol}3`).merge();sh.getRange('A2').values=[[note]];
 sh.getRange(`A2:${lastcol}3`).format={fill:amber,wrapText:true,verticalAlignment:'center',rowHeight:25};
 sh.getRange(`A4:${lastcol}${lastrow}`).format.rowHeight=25;
 sh.freezePanes.freezeRows(6);sh.freezePanes.freezeColumns(2);
 sh.tabColor=teal;
}
function head(sh,r,lastcol){sh.getRange(`A${r}:${lastcol}${r}`).format={fill:teal,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,verticalAlignment:'center',rowHeight:60};}
const source='Source: Gorbatenko & Melnikov (2019), Fig. 9, printed p.157 / PDF p.15. https://izvestiya.tinro-center.ru/jour/article/download/497/467';
const read=sheets['Read me'];
layout(read,'H',26,'OKHOTSK · Figure 9 diet reconstruction','PROVISIONAL RESEARCH CANDIDATE — uncertain routes and unresolved labels; not ready for Ecopath balancing or SPPR/PPR.');
read.getRange('A4:H26').format.columnWidth=13;
const notes=[
 ['Scope','2000–2014 epipelagic community (0–200 m); 22 groups, 20 consumers.'],
 ['Source basis','Numeric labels are carbon consumption flows; box values are production.'],
 ['Zero rule','Missing displayed feeding arrows = zero, as instructed. Other unknown parameters remain unknown.'],
 ['Readable labels','78 readings: 43 clearly traced routes, 33 tentative routes, 2 overprinted labels.'],
 ['DC carbon','19/20 columns numerically complete under the adopted routes; 1 column unresolved.'],
 ['DC wet','16/20 columns numerically complete; microbial conversions and whale labels are missing.'],
 ['Label hypothesis','Illustrative only: assumes F62 = 0.023 and F67 = 0.05 million tC/year.'],
 ['Normalization','Each consumer column = prey flow / sum of all its incoming flows; no rounding of stored values.'],
 ['Wet conversion','Convert each prey flow with its own Table 3 wet/C factor before normalization.'],
 ['Bacteria','A single detritus prey yields DC = 1 even though its wet consumption and Q/B remain unknown.'],
 ['Balance','Energy and predation checks fail. Column sums of 1 do not establish biological consistency.'],
 ['Review first','Arrow ledger: amber routes are hypotheses; red readings are unresolved.'],
 ['Raw converter','The native converter dropped 3 groups and misclassified 3 consumers. Its output is rejected.'],
 ['Preserved candidate','model.json keeps all 22 groups and unknowns; its status is BLOCKED, not a selected model.'],
 ['Files','Original PDFs: ../../papers/OKH-GM2019; figure crop, per-cell provenance and checks: audit/.'],
 ['No integration','Selected model, validation DOCX, map and regional workbook are unchanged.'],
 ['Display','Percentages display 3 decimals. A displayed 0.000% may be a small positive value.'],
 ['Reproduction','python reconstruct.py; node audit/build_review.mjs; python finalize_package.py.']
];
for(let k=0;k<notes.length;k++){const r=k+5;read.getRange(`A${r}:B${r}`).merge();read.getRange(`C${r}:H${r}`).merge();read.getRange(`A${r}`).values=[[notes[k][0]]];read.getRange(`C${r}`).values=[[notes[k][1]]];read.getRange(`A${r}:H${r}`).format={wrapText:true,rowHeight:k===7||k===12?44:35,verticalAlignment:'center',fill:k%2?pale:'#FFFFFF'};read.getRange(`A${r}:B${r}`).format.font.bold=true;}
read.freezePanes.unfreeze();
function matrixSheet(name,data,note,flows=false){
 const sh=sheets[name];layout(sh,'V',32,name==='Carbon flows'?'Annual feeding flows · carbon':name==='Label hypothesis'?'DC carbon · illustrative label hypothesis':`Diet composition · ${name==='DC wet'?'wet weight':'carbon'}`,note);
 sh.getRange('A4:V4').merge();sh.getRange('A4').values=[[flows?source:'Columns = consumers; rows = prey. All numeric columns remain provisional because 33 endpoint assignments are tentative.']];sh.getRange('A4:V4').format={font:{size:10,color:'#53676E'},rowHeight:25};
 sh.getRange('A6:V6').values=[['ID','Prey',...d.groups.slice(1,21).map(g=>`${g.n} ${g.name}`)]];head(sh,6,'V');
 sh.getRange('A7:B28').values=d.groups.map(g=>[g.n,g.name]);
 sh.getRange('A:A').format.columnWidth=5;sh.getRange('B:B').format.columnWidth=32;sh.getRange('C:V').format.columnWidth=13;
 sh.getRange('A7:B28').format.fill=pale;
 if(name==='DC carbon'){
  sh.getRange('C7:V28').formulas=d.carbon_dc.map((row,i)=>row.map((v,j)=>{const c=col(j+3),r=i+7;return `=IF('Carbon flows'!${c}${r}=0,0,IF(ISNUMBER('Carbon flows'!${c}$30),'Carbon flows'!${c}${r}/'Carbon flows'!${c}$30,"n.a."))`;}));
 }else sh.getRange('C7:V28').values=data.map(row=>row.map(num));
 sh.getRange('A30:B30').merge();sh.getRange('A30').values=[[flows?'Consumer total, million tC/year':'Column sum (numeric completeness only)']];
 sh.getRange('C30:V30').formulas=[Array.from({length:20},(_,j)=>{const c=col(j+3);return `=IF(COUNT(${c}7:${c}28)=22,SUM(${c}7:${c}28),"n.a.")`})];
 sh.getRange('A30:V30').format={fill:navy,font:{bold:true,color:'#FFFFFF'},rowHeight:35,wrapText:true};
 sh.getRange('C7:V30').setNumberFormat(flows?'0.00000':'0.000%');
 const unknown=data.map((row,i)=>row.map((v,j)=>v===null?[i+7,j+3]:null).filter(Boolean)).flat();
 for(const[r,c]of unknown)sh.getRange(`${col(c)}${r}`).format.fill=red;
 sh.getRange('A32:V32').merge();sh.getRange('A32').values=[[flows?'n.a. = displayed arrow with unresolved reading; zero = no adopted displayed arrow. Million tonnes C/year.':'n.a. = fraction not identifiable; a known zero remains zero even when another entry in the column is unknown.']];sh.getRange('A32:V32').format={wrapText:true,rowHeight:30,font:{size:10,color:'#53676E'}};
}
matrixSheet('Carbon flows',d.carbon_flow,'Missing arrows are zero. F62 and F67 remain unknown; tentative routes are adopted for this research candidate.',true);
matrixSheet('DC carbon',d.carbon_dc,'19/20 numerically complete columns. The baleen-whale column is unresolved. Read the Arrow ledger before using these diets.');
matrixSheet('DC wet',d.wet_dc,'16/20 numerically complete columns. Prey-specific mass conversion is applied; missing microbial factors are not borrowed from a pooled row.');
matrixSheet('Label hypothesis',d.carbon_hypothesis_dc,'ILLUSTRATIVE ONLY — assumes overprinted F62 = 0.023 and F67 = 0.05. These are possible readings, not verified source numbers.');
const led=sheets['Arrow ledger'];layout(led,'J',86,'Source arrow ledger · every adopted label','33 tentative endpoint assignments require review. Two overprinted readings remain unknown; their possible readings appear only as hypotheses.');
led.getRange('A4:J4').merge();led.getRange('A4').values=[[source]];
led.getRange('A6:J6').values=[['Flow','Prey ID','Prey','Consumer ID','Consumer','Literal label','Readable C flow','Hypothesis only','Route status','Trace note; label pixel x,y']];head(led,6,'J');
led.getRange('A7:J84').values=d.flows.map(f=>[f.flow_id,f.prey_id,f.prey,f.consumer_id,f.consumer,f.source_literal,num(f.readable_carbon_flow),num(f.hypothesis_reading),f.routing_status,`${f.note} (${f.label_centre_pixels.join(',')})`]);
for(const[c,w]of Object.entries({A:8,B:8,C:29,D:9,E:29,F:24,G:14,H:15,I:15,J:76}))led.getRange(`${c}:${c}`).format.columnWidth=Number(w);
led.getRange('A7:J84').format={wrapText:true,verticalAlignment:'center',rowHeight:45};led.getRange('G7:H84').setNumberFormat('0.00000');
for(let i=0;i<d.flows.length;i++)if(d.flows[i].routing_status!=='clear')led.getRange(`A${i+7}:J${i+7}`).format.fill=d.flows[i].routing_status==='overprinted'?red:amber;
const gr=sheets.Groups;layout(gr,'K',58,'Functional groups · production and stock inputs','IDs are local figure order. Table 3 pools bacteria/protozoa and includes groups absent from the figure. No stock allocation or additional arrows is invented.');
gr.getRange('A4:K4').merge();gr.getRange('A4').values=[['Source: same article, Table 3, printed p.154 / PDF p.12; Fig.9 p.157. https://izvestiya.tinro-center.ru/jour/article/download/497/467']];
gr.getRange('A6:K6').values=[['ID','English group','Russian figure name','Type','Source tier','Figure P, million tC/year','Table B wet, million t','Wet/C factor','Table B C, million t','Table P/B, /year','Table P C, million t/year']];head(gr,6,'K');
const rowsByID=new Map(d.table3.filter(r=>r.figure_group_id!==null).map(r=>[r.figure_group_id,r]));
gr.getRange('A7:K28').values=d.groups.map(g=>{const t=rowsByID.get(g.n);return[g.n,g.name,g.source_name,g.group_type,g.source_trophic_tier,num(g.figure_production_carbon_million_t_per_year),...(['biomass_wet_million_t','wet_per_carbon','biomass_carbon_million_t','pb_per_year','production_carbon_million_t_per_year'].map(k=>t?num(t[k]):'n.a.'))];});
for(const[c,w]of Object.entries({A:6,B:31,C:32,D:12,E:11,F:18,G:17,H:12,I:16,J:15,K:19}))gr.getRange(`${c}:${c}`).format.columnWidth=Number(w);
gr.getRange('A7:K28').format={rowHeight:30,wrapText:true};gr.getRange('F7:K28').setNumberFormat('0.000');
gr.getRange('A31:K31').merge();gr.getRange('A31').values=[['Table 3 · raw transcription, including pooled and omitted rows']];gr.getRange('A31:K31').format={fill:navy,font:{bold:true,color:'#FFFFFF'}};
gr.getRange('A33:K33').values=[['Tier','Source group','B wet, million t','Wet/C','B C, million t','P/B','P wet, million t/year','P C, million t/year','P C, g/m2/year','Tier share %','Mapped ID']];head(gr,33,'K');
gr.getRange('A34:K56').values=d.table3.map(r=>[r.trophic_tier,r.source_name,...['biomass_wet_million_t','wet_per_carbon','biomass_carbon_million_t','pb_per_year','production_wet_million_t_per_year','production_carbon_million_t_per_year','production_gC_per_m2_per_year','tier_share_percent','figure_group_id'].map(k=>num(r[k]))]);
gr.getRange('A34:K56').format={rowHeight:30,wrapText:true};gr.getRange('C34:J56').setNumberFormat('0.000');
for(let i=0;i<d.table3.length;i++)if(d.table3[i].figure_group_id===null||d.table3[i].figure_group_id===20)gr.getRange(`A${i+34}:K${i+34}`).format.fill=amber;
const bud=sheets['Budget checks'];layout(bud,'K',46,'Independent checks · failed consistency','Failures are retained, not repaired. Predation checks use the illustrative route/label hypothesis and zero BA/catch assumptions; those are not author balance results.');
bud.getRange('A6:K6').values=[['ID','Group','Figure P C','Q C, readable','Q C, hypothesis','P / Q C','Predation / P, hypothesis','Q wet, readable','Q/B wet, derived','P > Q C','Predation > P']];head(bud,6,'K');
bud.getRange('A7:K27').values=d.diagnostics.map(r=>[r.group_id,r.group,num(r.figure_P_carbon),num(r.conservative_Q_carbon),num(r.hypothesis_Q_carbon),num(r.P_over_Q_carbon),num(r.hypothesis_predation_over_P),num(r.conservative_Q_wet),num(r.derived_QB_wet),r.energy_failure?'FAIL':'—',r.predation_failure_hypothesis?'FAIL':'—']);
for(const[c,w]of Object.entries({A:6,B:32,C:16,D:17,E:17,F:16,G:20,H:19,I:19,J:13,K:15}))bud.getRange(`${c}:${c}`).format.columnWidth=Number(w);
bud.getRange('C7:I27').setNumberFormat('0.000');for(let i=0;i<d.diagnostics.length;i++)if(d.diagnostics[i].energy_failure||d.diagnostics[i].predation_failure_hypothesis)bud.getRange(`A${i+7}:K${i+7}`).format.fill=red;
bud.getRange('A30:K30').merge();bud.getRange('A30').values=[['Independent prose consumption (million tonnes wet weight/year) · no rescaling to force agreement']];bud.getRange('A30:K30').format={fill:navy,font:{bold:true,color:'#FFFFFF'}};
bud.getRange('A32:G32').values=[['ID','Group','Reported Q wet','Reconstructed Q wet','Reconstructed / reported','Printed page','Assessment']];head(bud,32,'G');
bud.getRange('A33:G41').values=d.comparisons.map(r=>[r.group_id,r.group,num(r.reported_Q_wet_million_t_per_year),num(r.figure_derived_Q_wet_million_t_per_year),num(r.fraction_of_reported_Q),r.printed_page,r.assessment]);
bud.getRange('A33:G41').format={rowHeight:48,wrapText:true};bud.getRange('C33:E41').setNumberFormat('0.000');bud.getRange('G33:G41').format.fill=amber;
await wb.recalculate();
const inspection=await wb.inspect({kind:'region',sheetId:'DC carbon',range:'A28:V30',maxChars:3500,tableMaxCols:22});
await fs.writeFile(path.join(audit,'workbook_inspection.json'),JSON.stringify(inspection,null,2));
const output=await SpreadsheetFile.exportXlsx(wb);await output.save(path.join(root,'DC_reconstruction_review.xlsx'));
for(const name of ['Read me','DC carbon','DC wet','Label hypothesis','Carbon flows','Arrow ledger','Groups','Budget checks']){
 const preview=await wb.render({sheetName:name,autoCrop:'all',scale:1,format:'png'});
 await fs.writeFile(path.join(audit,`review_${name.replaceAll(' ','_')}.png`),new Uint8Array(await preview.arrayBuffer()));
}
console.log(JSON.stringify({output:path.join(root,'DC_reconstruction_review.xlsx'),sheets:Object.keys(sheets),previewCount:8}));
