import test from 'node:test';
import assert from 'node:assert/strict';
import { Workbook } from '@oai/artifact-tool';
import * as eez from '../tools/eez_workbook.mjs';

test('CSV sheets append safely after existing sheet edits', async () => {
  const wb = Workbook.create();
  const first = wb.worksheets.add('First');
  first.getRange('A1').values = [['preserve']];
  await eez.appendCsvSheet(wb,'id,value,flag\nEEZ_001,1.25,True\n','Data');
  await eez.appendCsvSheet(wb,'label,total\nsecond,2\n','More');
  assert.equal(first.getRange('A1').values[0][0],'preserve');
  assert.deepEqual(wb.worksheets.getItem('Data').getRange('A2:C2').values,[['EEZ_001',1.25,true]]);
  assert.equal(wb.worksheets.getItem('More').getRange('B2').values[0][0],2);
});

test('regional export shards partition all units without omissions or overlap', () => {
  const units=Array.from({length:282},(_,index)=>index);
  const shards=Array.from({length:3},(_,index)=>eez.regionalExportShard(units,[`--shards=3`,`--shard=${index}`]));
  assert.deepEqual(shards.map(s=>s.units.length),[94,94,94]);
  assert.deepEqual(shards.flatMap(s=>s.units).sort((a,b)=>a-b),units);
  assert.deepEqual(eez.regionalExportShard(units,[]).units,units);
  assert.throws(()=>eez.regionalExportShard(units,['--shards=3','--shard=3']));
  assert.throws(()=>eez.regionalExportShard(units,['--shards=0']));
});

test('CSV booleans retain boolean type and unit identifiers remain text', () => {
  assert.equal(typeof eez.coerceCsvValue,'function');
  assert.equal(eez.coerceCsvValue('True'),true);
  assert.equal(eez.coerceCsvValue('False'),false);
  assert.equal(eez.coerceCsvValue('EEZ_001'),'EEZ_001');
  assert.equal(eez.coerceCsvValue('1.23e-4'),.000123);
});

test('pair flag aggregation sums numeric logical results and stays live', () => {
  const wb = Workbook.create();
  const pairs = wb.worksheets.add('Pairs');
  pairs.getRange('A2:A4').values = [['EEZ_036'],['EEZ_036'],['EEZ_012']];
  pairs.getRange('C2:C4').values = [[.99],[.95],[.1]];
  pairs.getRange('B2').formulas = [['=IF(C2>=0.9,1,0)']];
  pairs.getRange('B2:B4').fillDown();
  const flags = wb.worksheets.add('Flags');
  flags.getRange('A2').values = [['EEZ_036']];
  flags.getRange('B2').formulas = [[eez.groupedPairFlagFormula("'Pairs'!$A$2:$A$4",'A2',"'Pairs'!$B$2:$B$4")]];
  assert.equal(Boolean(flags.getRange('B2').values[0][0]),true);
  pairs.getRange('C2:C3').values = [[.1],[.2]];
  assert.equal(Boolean(flags.getRange('B2').values[0][0]),false);
});

test('compact comparison preserves reference columns and computes within-type shares', () => {
  assert.equal(typeof eez.addCompactSummary, 'function');
  const wb = Workbook.create();
  const source = wb.worksheets.add('All Areas');
  source.getRange('A1:E5').values = [
    ['unit_id','region_name','region_type','total_catch_tonnes','ppr_species'],
    ['EEZ_001','A','EEZ',3,30], ['EEZ_002','B','EEZ',1,10],
    ['LME_001','C','LME',10,100], ['HS_001','D','High Seas',0,0],
  ];
  const sheet = eez.addCompactSummary(wb, source, 'summarized summary', {withinType:true});
  assert.deepEqual(sheet.getRange('A1:E1').values[0], ['unit_id','region_name','region_type','total_catch_tonnes','ppr_species']);
  assert.deepEqual(sheet.getRange('F2:H4').values, [[.75,1,.75],[.25,2,1],[1,1,1]]);
  assert.equal(sheet.getRange('F5').values[0][0], '');
  source.getRange('E2').values = [[10]];
  assert.equal(sheet.getRange('F2').values[0][0], .5);
  source.getRange('E3').values = [[60]];
  assert.equal(sheet.getRange('G2').values[0][0], 2);
  assert.equal(sheet.getRange('G3').values[0][0], 1);
});

test('single-scope compact summary uses whole scope and cumulative fraction', () => {
  assert.equal(typeof eez.addCompactSummary, 'function');
  const wb = Workbook.create();
  const source = wb.worksheets.add('Summary');
  source.getRange('A1:E3').values = [
    ['unit_id','region_name','region_type','total_catch_tonnes','ppr_species'],
    ['EEZ_001','A','EEZ',3,30], ['EEZ_002','B','EEZ',1,10],
  ];
  const sheet = eez.addCompactSummary(wb, source, 'summarized summary');
  assert.deepEqual(sheet.getRange('F2:H3').values, [[.75,1,.75],[.25,2,1]]);
  assert.equal(sheet.getRange('F1').values[0][0], 'fraction_eez_ppr');
});

test('zero-share rows retain cumulative fraction within a nonzero spatial type', () => {
  for (const withinType of [false,true]) {
    const wb=Workbook.create();
    const source=wb.worksheets.add('Data');
    source.getRange('A1:E3').values=[['unit_id','region_name','region_type','total_catch_tonnes','ppr_species'],
      ['HS_001','Nonzero','High Seas',10,100],['HS_018','Empty','High Seas',0,0]];
    const summary=eez.addCompactSummary(wb,source,'Compact',{withinType});
    assert.equal(summary.getRange('F3').values[0][0],0);
    assert.equal(summary.getRange('H3').values[0][0],1);
  }
});

test('regional formulas distinguish unmatched groups from matched zero catch', () => {
  assert.equal(typeof eez.regionalGroupFormulas,'function');
  const wb = Workbook.create();
  const species = wb.worksheets.add('Species');
  const metadata = wb.worksheets.add('Metadata');
  const group = wb.worksheets.add('Commercial');
  metadata.getRange('B5').values = [[.1]];
  species.getRange('H2').values = [['Test']];
  group.getRange('A2:E2').values = [['Test',1,0,5,0]];
  for (const [col,formula] of Object.entries(eez.regionalGroupFormulas(2,'H'))) group.getRange(`${col}2`).formulas = [[formula]];
  assert.equal(group.getRange('I2').values[0][0],'');
  assert.equal(group.getRange('M2').values[0][0],'');
  group.getRange('C2:E2').values = [[1,0,0]];
  species.getRange('U2').values = [[0]];
  assert.equal(group.getRange('I2').values[0][0],0);
  assert.equal(group.getRange('H2').values[0][0],'');
  assert.equal(group.getRange('M2').values[0][0],'');
});
