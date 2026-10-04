import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const dir=path.dirname(fileURLToPath(import.meta.url));
const region=path.resolve(dir,'../../..');
const load=async name=>JSON.parse(await fs.readFile(path.join(dir,name),'utf8'));
const evidence=await load('taxonomy_evidence.json');
const sources=await load('sources.json');
const headerStyle={fill:'#243F55',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,verticalAlignment:'center',horizontalAlignment:'center'};
const writeMatrix=(s,cell,rows)=>s.getRange(cell).write(rows);
function baseFormat(s,range){s.showGridLines=false;s.getRange(range).format.font={name:'Arial',size:10,color:'#172B3A'};s.getRange(range).format.verticalAlignment='top';s.getRange(range).format.wrapText=true;}
async function finish(w,file,previews){
 w.recalculate();
 const scan=await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!',options:{useRegex:true,maxResults:20},summary:'formula error check'});
 await fs.writeFile(path.join(dir,path.basename(file)+'.inspect.json'),scan.ndjson);
 const x=await SpreadsheetFile.exportXlsx(w);await x.save(file);
 for (const [sheetName,range,tag] of previews){
  const blob=await w.render({sheetName,range,scale:1,format:'png'});
  await fs.writeFile(path.join(dir,tag+'.png'),new Uint8Array(await blob.arrayBuffer()));
 }
 console.log(path.basename(file));
}
{
 const w=Workbook.create();const s=w.worksheets.add('Taxonomy');
 const rows=[['seq','group_name','taxon_descr'],...evidence.groups.map(g=>[g.seq,g.group_name,g.taxon_descr])];
 writeMatrix(s,'A1',rows);baseFormat(s,'A1:C52');s.getRange('A1:C1').format=headerStyle;
 s.getRange('A1:A52').format.columnWidth=8;s.getRange('B1:B52').format.columnWidth=26;s.getRange('C1:C52').format.columnWidth=115;
 s.getRange('A1:C1').format.rowHeight=28;
 for(let i=1;i<rows.length;i++){const lines=Math.ceil(String(rows[i][2]).length/105);s.getRange(`A${i+1}:C${i+1}`).format.rowHeight=Math.max(32,lines*14+12);}
 s.freezePanes.freezeRows(1);s.tables.add('A1:C52',true,'SourceTaxonomy');
 await finish(w,path.join(dir,'Taxonomy.xlsx'),[['Taxonomy','A1:C6','taxonomy_preview']]);
}
for(const variant of ['Base','M30','P30']){
 const w=Workbook.create(),s=w.worksheets.add('Taxon mappings'),src=w.worksheets.add('Sources');
 const model=`Guenette2014_BancArguin_${variant}_1991`;
 const raw=await load(`${variant}_appendix_rows.json`),mapping=(await load(`${variant}_mapping_evidence.json`)).mapping;
 const byTax=new Map(mapping.map(x=>[x.taxon,x]));
 // Keep compact readable reasons; complete decision fields remain in the linked evidence.
 const rows=raw.map(row=>{const d=byTax.get(row[0]);const a=d.allocation_rule==='W1'?'One group (100%).':d.allocation_rule==='W4'?'Weights: 1991 source total-catch proportions; reported zero candidates retained. Fixed transfer across LME years/bases is assumed.':'Weights: complete model biomass; candidate catch total is zero. Geographic/catchability transfer is assumed.';const groups=d.candidates.map(c=>`${c.group} (${Number((c.weight*100).toPrecision(4))}%)`).join('; ');return [...row.slice(0,4),groups,row[5],d.membership_reason+' '+a+' Sources: '+[...d.membership_references,...d.allocation_references].join(', ')+'.'];});
 s.getRange('A2').values=[[`Banc d’Arguin ${variant}: candidate taxon mappings`]];s.getRange('A2').format.font={name:'Arial',size:14,bold:true,color:'#172B3A'};
 s.getRange('A3').values=[['2019 landings (t wet weight). Simple trophic chain PPR (t C); all 512 catch labels, including zeros.']];
 s.getRange('A4').values=[['Sorted by unrounded simple-chain PPR, descending; unavailable last. Candidate review; no regional model selection adopted.']];
 s.getRange('A5').values=[['100 missing coefficients belong to zero-landings labels: annual PPR is zero. Full source/mapping evidence is linked on Sources.']];
 s.getRange('A3:G5').format.font={name:'Arial',size:10,italic:true,color:'#465568'};s.getRange('A3:G5').format.wrapText=false;
 const heads=['Taxon name','TL','Catch (t)','Simple-chain PPR (t C)','Mapped group names and weights','Confidence level','Reason'];
 writeMatrix(s,'A6',[heads,...rows]);baseFormat(s,'A6:G518');s.getRange('A6:G6').format=headerStyle;s.getRange('A6:G6').format.rowHeight=36;
 const widths=[34,9,18,23,74,17,110];for(let c=0;c<7;c++)s.getRangeByIndexes(5,c,513,1).format.columnWidth=widths[c];
 s.getRange('B7:B518').setNumberFormat('0.00');s.getRange('C7:D518').setNumberFormat('#,##0.000000');
 s.getRange('B7:D518').format.horizontalAlignment='right';
 for(let i=0;i<rows.length;i++){
  const row=rows[i],n=i+7;
  const needed=Math.max(Math.ceil(String(row[4]).length/66),Math.ceil(String(row[6]).length/102),Math.ceil(String(row[0]).length/30));
  s.getRange(`A${n}:G${n}`).format.rowHeight=Math.max(44,needed*14+15);
  if(row[5]==='Very low')s.getRange(`F${n}`).format={fill:'#FFF1DC',font:{color:'#7A480B'}};
  if(i%2===1)s.getRange(`A${n}:E${n}`).format.fill='#F4F6F8';
 }
 s.freezePanes.freezeRows(6);s.freezePanes.freezeColumns(1);s.tables.add('A6:G518',true,`Mappings_${variant}`).style='TableStyleLight1';
 const extras=[
  {id:'MAPPING_EVIDENCE',description:`Complete ${variant} mapping decisions, candidate raw values, weights and component confidence.`,locator:'Machine-readable candidate review',link_from_region:`validation_reports/BancArguin_20261003/mapping/${variant}_mapping_evidence.json`,supports:'Every zero candidate, rejected catch attempt, variant inheritance and assumption retained.',material_read:'Generated from independent current review'},
  {id:'SEARCH_EVIDENCE',description:'Actual bounded online composition and taxonomy searches.',locator:'Queries, dates, accessed material, limitations and decisions',link_from_region:'validation_reports/BancArguin_20261003/mapping/online_search_evidence.json',supports:'No matching observed age0–1 mass or exact geographic catch allocation recovered; model proxies remain assumptions.',material_read:'Search results and retrieved source sections'},
  {id:'SOURCE_TAXONOMY',description:'Source group taxonomy and membership scope.',locator:'51 source groups; S1 orphan Hake row and source inconsistencies',link_from_region:'validation_reports/BancArguin_20261003/mapping/taxonomy_evidence.json',supports:'Does not silently convert ecological analogues into source members.',material_read:'Original paper and supplement reviewed'},
  {id:'MODEL',description:`Exact candidate ${model}.`,locator:'Source-faithful candidate model directory',link_from_region:`models/${model}/model.json`,supports:'Study1991; Base catch inherited for variants; unavailable variant diets remain explicit.',material_read:'Fresh extraction'},
  {id:'ARITHMETIC',description:'Frozen workbook evidence and independent classic-PPR reconciliation.',locator:'All three catch bases,1950–2019',link_from_region:'validation_reports/BancArguin_20261003/mapping/classic_reconciliation.json',supports:'All210 year/basis sums reconcile with saved classic totals; carbon divided exactly once.',material_read:'Independent arithmetic'}
 ];
 const all=[...sources,...extras];
 src.getRange('A2').values=[['Sources and interpretation']];src.getRange('A2').format.font={name:'Arial',size:14,bold:true};
 writeMatrix(src,'A4',[['Source ID','Reference','Locator','Link','What the evidence supports / access'],...all.map(x=>[x.id,x.description,x.locator,'Open source',x.supports+' Access: '+x.material_read+(x.retrieved?'. Retrieved '+x.retrieved:'')])]);
 baseFormat(src,`A4:E${all.length+4}`);src.getRange('A4:E4').format=headerStyle;src.getRange('A4:E4').format.rowHeight=30;
 [23,90,46,18,100].forEach((width,c)=>src.getRangeByIndexes(3,c,all.length+1,1).format.columnWidth=width);
 for(let i=0;i<all.length;i++){
  const n=i+5,x=all[i];
  src.getRange(`D${n}`).format.font={name:'Arial',size:10,color:'#0563C1'};
  const lines=Math.max(Math.ceil(x.description.length/83),Math.ceil(x.locator.length/40),Math.ceil((x.supports+x.material_read).length/92));
  src.getRange(`A${n}:E${n}`).format.rowHeight=Math.max(55,lines*14+16);
 }
 src.freezePanes.freezeRows(4);src.tables.add(`A4:E${all.length+4}`,true,`Sources_${variant}`).style='TableStyleLight1';
 await fs.writeFile(path.join(dir,`${variant}_appendix_hyperlinks.json`),JSON.stringify(all.map((x,i)=>({cell:`D${i+5}`,target:x.link_from_region})),null,2));
 await finish(w,path.join(region,`LME027_Guenette2014_${variant}_taxon_mapping_appendix.xlsx`),[['Taxon mappings','A1:G12',`${variant}_mapping_preview`],['Sources','A1:E8',`${variant}_sources_preview`]]);
}
