import test from 'node:test';
import assert from 'node:assert/strict';
import {Workbook} from '@oai/artifact-tool';
import {addHistorySheets} from '../tools/history_workbook.mjs';

const fixture = () => ({
  annual:[
    {unit_id:'LME_001',region_name:'First',region_type:'LME',year:1950,total_catch_tonnes:2,matched_catch_tonnes:2,missing_tl_catch_tonnes:0,catch_tl_coverage_fraction:1,ppr_species:1010,source_data_status:'available'},
    {unit_id:'LME_001',region_name:'First',region_type:'LME',year:2019,total_catch_tonnes:2,matched_catch_tonnes:2,missing_tl_catch_tonnes:0,catch_tl_coverage_fraction:1,ppr_species:20,source_data_status:'available'},
    {unit_id:'EEZ_002',region_name:'Second',region_type:'EEZ',year:1950,total_catch_tonnes:1,matched_catch_tonnes:1,missing_tl_catch_tonnes:0,catch_tl_coverage_fraction:1,ppr_species:100,source_data_status:'available'},
    {unit_id:'EEZ_002',region_name:'Second',region_type:'EEZ',year:2019,total_catch_tonnes:0,matched_catch_tonnes:0,missing_tl_catch_tonnes:0,catch_tl_coverage_fraction:null,ppr_species:0,source_data_status:'available'},
    {unit_id:'HS_003',region_name:'Empty',region_type:'High Seas',year:1950,total_catch_tonnes:null,matched_catch_tonnes:null,missing_tl_catch_tonnes:null,catch_tl_coverage_fraction:null,ppr_species:null,source_data_status:'empty_catch_archive'},
    {unit_id:'HS_003',region_name:'Empty',region_type:'High Seas',year:2019,total_catch_tonnes:null,matched_catch_tonnes:null,missing_tl_catch_tonnes:null,catch_tl_coverage_fraction:null,ppr_species:null,source_data_status:'empty_catch_archive'},
    {unit_id:'EEZ_999',region_name:'Excluded',region_type:'EEZ',year:2019,total_catch_tonnes:999,matched_catch_tonnes:999,missing_tl_catch_tonnes:0,catch_tl_coverage_fraction:1,ppr_species:999999,source_data_status:'available'},
  ],
  selected:[
    {unit_id:'LME_001',region_name:'First',region_type:'LME',area_km2:10,selection_reason:'LME preference'},
    {unit_id:'EEZ_002',region_name:'Second',region_type:'EEZ',area_km2:12,selection_reason:'Added coverage'},
    {unit_id:'HS_003',region_name:'Empty',region_type:'High Seas',area_km2:20,selection_reason:'High Seas'},
  ],metrics:{coverage_fraction:0.9,excess_overlap_km2:1},scenarios:[]
});

test('year selection recalculates PPR, rank, shares and excludes nonselected areas', async()=>{
  const workbook=Workbook.create();
  const {summary}=await addHistorySheets(workbook,fixture());
  if(process.env.PPR_DEBUG)console.log(JSON.stringify(workbook.worksheets.getItem('Selected Year').getUsedRange().values));
  assert.equal(summary.getRange('B5').values[0][0],20);
  assert.equal(summary.getRange('A11').values[0][0],'LME_001');
  assert.equal(summary.getRange('E12').values[0][0],0);
  assert.equal(summary.getRange('G12').values[0][0],2);
  assert.equal(summary.getRange('B8').values[0][0],1);
  summary.getRange('B3').values=[[1950]];
  assert.equal(summary.getRange('B5').values[0][0],1110);
  assert.equal(summary.getRange('E11').values[0][0],1010);
  assert.ok(Math.abs(summary.getRange('F11').values[0][0]-1010/1110)<1e-12);
  assert.equal(summary.getRange('H12').values[0][0],1);
  assert.equal(summary.getRange('E13').values[0][0],'');
});

test('invalid years do not display plausible zero totals or stale rankings',async()=>{
  const workbook=Workbook.create();
  const {summary}=await addHistorySheets(workbook,fixture());
  summary.getRange('B3').values=[[1900]];
  assert.equal(summary.getRange('B5').values[0][0],'');
  assert.equal(summary.getRange('A11').values[0][0],'');
});

test('ties remain distinct and use stable unit order',async()=>{
  const data=fixture();
  data.annual.find(x=>x.unit_id==='EEZ_002'&&x.year===2019).ppr_species=20;
  const workbook=Workbook.create();
  const {summary}=await addHistorySheets(workbook,data);
  assert.equal(summary.getRange('A11').values[0][0],'EEZ_002');
  assert.equal(summary.getRange('A12').values[0][0],'LME_001');
});

test('changing the year changes which region appears first',async()=>{
  const data=fixture();
  data.annual.find(x=>x.unit_id==='EEZ_002'&&x.year===1950).ppr_species=2000;
  const workbook=Workbook.create();
  const {summary}=await addHistorySheets(workbook,data);
  assert.equal(summary.getRange('A11').values[0][0],'LME_001');
  summary.getRange('B3').values=[[1950]];
  assert.equal(summary.getRange('A11').values[0][0],'EEZ_002');
  assert.equal(summary.getRange('A12').values[0][0],'LME_001');
  assert.equal(summary.getRange('B5').values[0][0],3010);
});

test('bounded lookups support interleaved inputs and selected units absent from the source',async()=>{
  const data=fixture();
  data.annual=[data.annual[6],data.annual[0],data.annual[2],data.annual[4],data.annual[1],data.annual[3],data.annual[5]];
  data.selected.push({unit_id:'EEZ_000',region_name:'No source',region_type:'EEZ',area_km2:1,selection_reason:'Test gap'});
  const workbook=Workbook.create();
  const {summary}=await addHistorySheets(workbook,data);
  assert.equal(summary.getRange('B5').values[0][0],20);
  assert.equal(summary.getRange('B8').values[0][0],2);
  summary.getRange('B3').values=[[1950]];
  assert.equal(summary.getRange('B5').values[0][0],1110);
  assert.equal(summary.getRange('A11').values[0][0],'LME_001');
});
