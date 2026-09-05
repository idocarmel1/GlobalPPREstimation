const COLUMNS = ['lookup_key','unit_id','region_name','region_type','year',
  'total_catch_tonnes','matched_catch_tonnes','missing_tl_catch_tonnes',
  'catch_tl_coverage_fraction','taxa_count','matched_taxa_count','ppr_species',
  'ppr_commercial_correct','ppr_functional_correct','ppr_commercial_jensen',
  'ppr_functional_jensen','source_data_status'];

function col(n) { let s=''; for(n++;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s; return s; }
function plain(value) {
  if(value===undefined||typeof value==='number'&&!Number.isFinite(value))return null;
  return value!==null&&typeof value==='object'?JSON.stringify(value):value;
}
function table(sheet,values,name,{firstRow=1,widths={}}={}) {
  if(!values.length)return;
  const last=firstRow+values.length-1, end=col(values[0].length-1);
  sheet.getRange(`A${firstRow}:${end}${last}`).values=values;
  sheet.showGridLines=false;
  sheet.getRange(`A${firstRow}:${end}${last}`).format.font={name:'Aptos',size:10,color:'#1D2939'};
  sheet.getRange(`A${firstRow}:${end}${last}`).format.rowHeight=18;
  const header=sheet.getRange(`A${firstRow}:${end}${firstRow}`);
  header.format={fill:'#17324D',font:{name:'Aptos',size:10,bold:true,color:'#FFFFFF'},wrapText:true,verticalAlignment:'center'};
  header.format.rowHeight=36;
  for(let c=0;c<values[0].length;c++)sheet.getRange(`${col(c)}${firstRow}:${col(c)}${last}`).format.columnWidth=widths[c]??19;
  if(values.length>1) {const t=sheet.tables.add(`A${firstRow}:${end}${last}`,true,name);t.style='TableStyleMedium2';}
  sheet.freezePanes.freezeRows(firstRow);
}

export async function addHistorySheets(workbook,{annual,selected,metrics={},scenarios=[],progress=()=>{}}) {
  if(!annual.length||!selected.length)throw new Error('Annual results and selected regions are required');
  const selectedUnits=[...selected].sort((a,b)=>a.unit_id.localeCompare(b.unit_id));
  if(new Set(selectedUnits.map(x=>x.unit_id)).size!==selectedUnits.length)throw new Error('Duplicate selected unit');
  // Use a literal-safe separator: the preview engine treats | as a regex
  // alternation even in MATCH(...,0), whereas Excel treats it literally.
  const keys=annual.map(x=>`${x.unit_id}__${x.year}`);
  if(new Set(keys).size!==keys.length)throw new Error('Duplicate annual unit-year');
  const unitBounds=new Map();
  annual.forEach((record,index)=>{
    const bounds=unitBounds.get(record.unit_id);
    if(bounds)bounds.last=index;else unitBounds.set(record.unit_id,{first:index,last:index});
  });
  const years=[...new Set(annual.map(x=>x.year))].sort((a,b)=>a-b);
  const summary=workbook.worksheets.add('Global Estimation');
  const data=workbook.worksheets.add('Annual Regional PPR');
  const membership=workbook.worksheets.add('Selected Regions');
  const helper=workbook.worksheets.add('Selected Year');
  const yearSheet=workbook.worksheets.add('Available Years');
  const spatial=workbook.worksheets.add('Spatial Coverage');
  const annualRows=[COLUMNS,...annual.map((r,i)=>COLUMNS.map(k=>plain(k==='lookup_key'?keys[i]:r[k])))];
  progress('Writing annual data table');
  table(data,annualRows,'HistoricalRegionYears',{widths:{0:24,2:40,4:10,16:24}});
  data.getRange(`F2:H${annualRows.length}`).setNumberFormat('#,##0.00');
  data.getRange(`L2:P${annualRows.length}`).setNumberFormat('#,##0.00');
  data.getRange(`I2:I${annualRows.length}`).setNumberFormat('0.00%');
  const selectedFields=Array.from(new Set(['unit_id','region_name','region_type','area_km2','selection_reason',...selectedUnits.flatMap(Object.keys)]));
  table(membership,[selectedFields,...selectedUnits.map(r=>selectedFields.map(k=>plain(r[k])))],'SelectedWholeRegions',{widths:{1:40,4:65}});
  membership.getRange(`D2:D${selectedUnits.length+1}`).setNumberFormat('#,##0.00');
  selectedFields.forEach((field,index)=>{
    if(field.endsWith('_km2'))membership.getRange(`${col(index)}2:${col(index)}${selectedUnits.length+1}`).setNumberFormat('#,##0.00');
    if(field.includes('fraction'))membership.getRange(`${col(index)}2:${col(index)}${selectedUnits.length+1}`).setNumberFormat('0.00%');
  });
  membership.getRange(`E2:E${selectedUnits.length+1}`).format.wrapText=true;
  membership.getRange(`A2:${col(selectedFields.length-1)}${selectedUnits.length+1}`).format.rowHeight=36;
  table(yearSheet,[['year'],...years.map(y=>[y])],'HistoricalYears',{widths:{0:14}});
  progress('Annual data and fixed selection written');

  const n=selectedUnits.length,last=n+1, dataLast=annual.length+1;
  const valid=`COUNTIF('Available Years'!$A$2:$A$${years.length+1},'Global Estimation'!$B$3)=1`;
  const quoted="'Annual Regional PPR'";
  const helperHeaders=['unit_id','region_name','region_type','annual_source_row','catch_tonnes','matched_catch_tonnes',
    'missing_tl_catch_tonnes','ppr_species','catch_tl_coverage_fraction','source_data_status','sort_order'];
  table(helper,[helperHeaders,...selectedUnits.map(r=>[r.unit_id,r.region_name,r.region_type,null,null,null,null,null,null,null,null])],
    'SelectedYearCalculations',{widths:{1:40,9:25}});
  const helperFormulas=[];
  for(let row=2;row<=last;row++) {
    const formulas=Array(8).fill(null);
    const put=(column,value)=>{formulas[column.charCodeAt(0)-68]=value;};
    // Search only the selected unit's bounded source block. The returned
    // position still indexes the full annual table; unsorted/interleaved rows
    // are safe because the exact key includes both unit and year.
    const bounds=unitBounds.get(selectedUnits[row-2].unit_id);
    const lookup=bounds?`${quoted}!$A$${bounds.first+2}:$A$${bounds.last+2}`:null;
    const sourceValue=field=>bounds?`INDEX(${quoted}!$${field}$${bounds.first+2}:$${field}$${bounds.last+2},D${row}-${bounds.first})`:'""';
    put('D',bounds?`=IF(${valid},IF(COUNTIF(${lookup},A${row}&"__"&'Global Estimation'!$B$3)=0,0,MATCH(A${row}&"__"&'Global Estimation'!$B$3,${lookup},0)+${bounds.first}),0)`:'=0');
    put('J',`=IF(${valid},IF(D${row}=0,"missing_year",${sourceValue('Q')}),"invalid_year")`);
    for(const [target,source] of [['E','F'],['F','G'],['G','H'],['H','L'],['I','I']]) {
      let value=sourceValue(source);
      if(target==='I')value=`IF(E${row}=0,"",F${row}/E${row})`;
      put(target,`=IF(J${row}="available",${value},"")`);
    }
    put('K',`=IF(J${row}="available",COUNTIFS($J$2:$J$${last},"available",$H$2:$H$${last},">"&H${row})+COUNTIFS($J$2:J${row},"available",$H$2:H${row},H${row}),COUNT($H$2:$H$${last})+ROWS($J$2:J${row})-COUNTIF($J$2:J${row},"available"))`);
    helperFormulas.push(formulas);
  }
  helper.getRange(`D2:K${last}`).formulas=helperFormulas;
  progress('Year-lookup formulas written');
  helper.getRange(`E2:H${last}`).setNumberFormat('#,##0.00');
  helper.getRange(`I2:I${last}`).setNumberFormat('0.00%');

  summary.showGridLines=false;
  summary.getRange(`A1:J${n+10}`).format.font={name:'Aptos',size:10,color:'#1D2939'};
  summary.getRange('A1').values=[['Global PPR estimation']];
  summary.getRange('A1').format.font={name:'Aptos',size:16,bold:true};
  summary.getRange('A2').values=[['Fixed selected set. Change the year below to update values and ranking.']];
  summary.getRange('A3:B8').values=[['Selected year',years.at(-1)],['Selected regions',n],['PPR estimate (t PP equivalent)',null],
    ['Catch (tonnes)',null],['Catch without TL (tonnes)',null],['Regions without catch data',null]];
  summary.getRange('E3:F3').values=[['Transfer efficiency',0.1]];
  summary.getRange('F3').setNumberFormat('0.00');
  summary.getRange('B3').format.fill='#FFF2CC';
  summary.getRange('B3').setNumberFormat('0');
  summary.getRange('B3').dataValidation={rule:{type:'list',formula1:`'Available Years'!$A$2:$A$${years.length+1}`}};
  for(const [target,source]of [['B5','H'],['B6','E'],['B7','G']])summary.getRange(target).formulas=[[`=IF(${valid},SUM('Selected Year'!$${source}$2:$${source}$${last}),"")`]];
  summary.getRange('B8').formulas=[[`=IF(${valid},${n}-COUNTIF('Selected Year'!$J$2:$J$${last},"available"),"")`]];
  summary.getRange('B5:B7').setNumberFormat('#,##0.00');
  summary.getRange('E5').values=[['Whole-region sum; residual spatial overlap is not deducted.']];
  summary.getRange('E6').values=[['Coverage and overlap details: Spatial Coverage sheet.']];
  summary.getRange('E7').formulas=[[`=IF(${valid},IF(B8>0,"Partial total: some selected regions have no catch data.",IF(B7>0,"Partial PPR: some catch has no trophic level.","PPR calculated for all recorded selected-region catch.")),"Choose a year from Available Years.")`]];
  summary.getRange('E8').values=[['Shares describe this selected-region sum, not verified unique global PPR.']];
  const mainHeaders=['unit_id','region_name','region_type','total_catch_tonnes','ppr_species','fraction_selected_ppr','rank_selected_ppr','accumulated fraction','catch_tl_coverage','data availability'];
  table(summary,[mainHeaders,...selectedUnits.map(()=>Array(10).fill(null))],'GlobalSelectedRanking',{firstRow:10,widths:{0:31,1:40,2:17,3:22,4:24,5:20,6:19,7:20,8:20,9:24}});
  const rankingFormulas=[];
  for(let r=11;r<=n+10;r++) {
    const formulas=Array(10).fill(null);
    const put=(column,value)=>{formulas[column.charCodeAt(0)-65]=value;};
    const position=r-10;
    const source=`MATCH(${position},'Selected Year'!$K$2:$K$${last},0)`;
    for(const[target,field]of [['A','A'],['B','B'],['C','C'],['J','J']])put(target,`=IF(${valid},INDEX('Selected Year'!$${field}$2:$${field}$${last},${source}),"")`);
    for(const[target,field]of [['D','E'],['E','H'],['I','I']]) {
      let value=`INDEX('Selected Year'!$${field}$2:$${field}$${last},${source})`;
      if(target==='I')value=`IF(D${r}=0,"",${value})`;
      put(target,`=IF(J${r}="available",${value},"")`);
    }
    put('F',`=IF(J${r}="available",IF($B$5=0,"",E${r}/$B$5),"")`);
    put('G',`=IF(J${r}="available",${position},"")`);
    put('H',`=IF(J${r}="available",IF($B$5=0,"",SUM($F$11:F${r})),"")`);
    rankingFormulas.push(formulas);
  }
  summary.getRange(`A11:J${n+10}`).formulas=rankingFormulas;
  progress('Live ranking formulas written');
  summary.getRange(`D11:E${n+10}`).setNumberFormat('#,##0.00');
  summary.getRange(`F11:F${n+10}`).setNumberFormat('0.00%');
  summary.getRange(`H11:I${n+10}`).setNumberFormat('0.00%');
  summary.getRange('A3:A8').format.columnWidth=31;
  summary.getRange('A2:J2').format.rowHeight=24;
  summary.getRange('E5:J8').format.font={name:'Aptos',size:10,color:'#667085'};
  summary.tabColor='#147D92';

  const metricRows=[];
  function flatten(value,prefix='') {
    for(const[k,v]of Object.entries(value)) {
      const key=prefix?`${prefix}.${k}`:k;
      if(v&&typeof v==='object'&&!Array.isArray(v))flatten(v,key);
      else metricRows.push([key,Array.isArray(v)?JSON.stringify(v):plain(v)]);
    }
  }
  flatten(metrics);
  const notes=[
    ['Definition','Value'],
    ['Selection basis','Whole SAU polygons; LME preference. Fixed geography across years.'],
    ['Coverage denominator','Union of all available LME, EEZ and High Seas polygons; not an independent ocean mask.'],
    ['Overlap interpretation','Geographic overlap is measured. Its catch/PPR contribution is unknown.'],
    ['PPR interpretation','Sum of recorded selected-region PPR. No area-based subtraction or gap extrapolation.'],
    ['99% PPR target','Not verifiable from region-aggregated catch; no 1% area surrogate imposed.'],
    ['Temporal TL assumption','Frozen supplement/SAU trophic levels applied across catch years; TL is not a reconstructed historical series.'],
    ['Original sheets','Preserved as the 2019 reference. Global Estimation is the year-controlled selected-set view.'],
    ['SAU area definitions','https://www.seaaroundus.org/sea-around-us-area-parameters-and-definitions/'],
    ['SAU catch methods','https://www.seaaroundus.org/catch-reconstruction-and-allocation-methods/'],
    ...metricRows
  ];
  table(spatial,notes,'SpatialSelectionMetrics',{widths:{0:65,1:100}});
  for(let i=1;i<notes.length;i++) {
    if(typeof notes[i][1]==='number')spatial.getRange(`B${i+1}`).setNumberFormat(/fraction/.test(notes[i][0])?'0.00%':'#,##0.00');
    const lines=Math.max(Math.ceil(String(notes[i][0]).length/58),Math.ceil(String(notes[i][1]??'').length/105));
    spatial.getRange(`A${i+1}:B${i+1}`).format.rowHeight=Math.max(24,lines*17+8);
  }
  spatial.getRange(`A2:B${notes.length}`).format.wrapText=true;
  spatial.getRange(`A2:B${notes.length}`).format.verticalAlignment='center';
  if(scenarios.length) {
    const fields=['scenario','selection and overlap penalty','regions','coverage_fraction','twice_covered_fraction','duplicate_excess_fraction'];
    const scenarioRows=scenarios.map(r=>[r.scenario,
      `${typeof r.selected_counts_by_type==='string'?r.selected_counts_by_type:JSON.stringify(r.selected_counts_by_type)}; penalty=${r.overlap_penalty??'baseline'}${r.recommended?'; recommended':''}`,
      r.selected_count,r.coverage_fraction,r.twice_covered_fraction_of_union,r.duplicate_excess_fraction_of_union]);
    table(spatial,[fields,...scenarioRows],'SpatialSelectionScenarios',
      {firstRow:notes.length+4,widths:{0:65,1:100}});
    spatial.getRange(`B${notes.length+5}:B${notes.length+4+scenarios.length}`).format.wrapText=true;
    spatial.getRange(`A${notes.length+5}:F${notes.length+4+scenarios.length}`).format.rowHeight=32;
    spatial.getRange(`D${notes.length+5}:F${notes.length+4+scenarios.length}`).setNumberFormat('0.00%');
    spatial.freezePanes.freezeRows(1);
  }
  progress('Spatial coverage documentation written');
  return {summary,data,membership,helper,yearSheet,spatial,years,selectedUnits};
}
