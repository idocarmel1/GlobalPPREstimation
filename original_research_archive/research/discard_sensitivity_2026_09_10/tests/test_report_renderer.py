import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('discard_report_renderer', ROOT/'src/render_report.py')
renderer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(renderer)
NODE = shutil.which('node') or 'C:/Users/idoca/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'


def study():
    row = dict(scenario_id='bay|method|all|SC|0', model_id='34_1_Bay_of_Bengal_(1978)',
        method='new_GE', scope='all', route='SC', fraction=0, valid=True, status='valid', reasons=[],
        ppr_fixed_H_tC=10., ppr_retained_L_tC=10.)
    return dict(schema_version=1, fraction_grid=[0,.01,.05], methods=['new_GE'], scopes=['all'], routes=['S0','SC','SM','SE','SR'],
        models=[dict(model_id=row['model_id'], model_label='Bay',native_harvest=1)], records=[row],
        groups={row['scenario_id']:[dict(group_id=1,name='Fish',sppr=90.,H=1.,L=1.)]})


def js(expression, evidence=None):
    source=(ROOT/'src/report_template.html').read_text(encoding='utf-8').split("<script>\n",1)[1].split('</script>',1)[0]
    # Keep all declarations/event registration; suppress only the final UI startup.
    source=source.rsplit('syncChoices();render();',1)[0]
    package=dict(study=study(),evidence=evidence or {},external_reference=[])
    harness=r'''
const vm=require('node:vm');
const input=JSON.parse(require('node:fs').readFileSync(0,'utf8'));
const nodes={};
const context={console,document:{getElementById(id){
  if(!nodes[id])nodes[id]={textContent:id==='study-data'?JSON.stringify(input.package):'',innerHTML:'',
    selectedOptions:[{textContent:'PPR'}],addEventListener(){},querySelectorAll(){return [];}};
  return nodes[id];},querySelectorAll(){return [];}},setTimeout};
vm.createContext(context);vm.runInContext(input.source,context);
console.log(JSON.stringify(vm.runInContext(input.expression,context)));
'''
    completed=subprocess.run([NODE,'-e',harness],input=json.dumps(dict(package=package,source=source,expression=expression)),text=True,encoding='utf-8',capture_output=True)
    assert completed.returncode==0,completed.stderr
    return json.loads(completed.stdout)


def test_template_javascript_compiles_and_all_method_names_are_friendly():
    assert js("[names['SPPR_1995_TE0.1'],names.SPPR_1986,names.Ulanowicz_TE].every(x=>typeof x==='string'&&x.length>4)")


def test_missing_grid_point_breaks_curve_but_adjacent_valid_points_connect():
    for fractions,expected_l in [([0,.05],False),([0,.01],True)]:
        svg=js("state.metric='ppr';curve("+json.dumps([dict(route='SC',fraction=f,valid=True,ppr_fixed_H_tC=10+f) for f in fractions])+ ");$('curve').innerHTML")
        path=re.search(r'<path d="([^"]*)" fill="none"',svg).group(1)
        assert ('L' in path)==expected_l
        if not expected_l:assert path.count('M')==2


def test_invalid_grid_point_breaks_curve():
    svg=js("curve([{route:'SC',fraction:0,valid:true,ppr_fixed_H_tC:10},{route:'SC',fraction:.01,valid:false},{route:'SC',fraction:.05,valid:true,ppr_fixed_H_tC:12}]);$('curve').innerHTML")
    path=re.search(r'<path d="([^"]*)" fill="none"',svg).group(1)
    assert path.count('M')==2 and 'L' not in path


def test_unavailable_percentages_and_reference_do_not_become_zero():
    assert js("[pct(null),pct(undefined),pct(NaN),percentPoints(null),pct(0),percentPoints(2.5)]")==['Unavailable','Unavailable','Unavailable','Unavailable','0%','2.5%']
    assert js("state.metric='standard_excess';value({valid:true,fraction:0,ppr_fixed_H_tC:10,fixed_standard_ppr_tC:null})") is None


def test_incompatible_native_denominator_hides_ratio_but_preserves_ppr():
    assert js("const r={valid:true,ppr_fixed_H_tC:10,denominator_value:100,native_denominator_compatible:false};state.metric='native_percent';const ratio=value(r);state.metric='ppr';[ratio,value(r)]")==[None,10]


def test_source_evidence_matches_short_id_and_shows_precise_citations():
    evidence=dict(models=[dict(model_id='34_1',name='Bay',source_period='1978',source_area_km2=6205000,
        source_supported_sr_status='hypothetical_destination_only',source_fidelity_caveats=['PDF 9, Catch section.'],
        files=[dict(path='inputs/paper.pdf',sha256='a'*64,role='publication')])])
    assert js("evidenceFor('34_1_Bay_of_Bengal_(1978)').model_id",evidence)=='34_1'
    html=js("sourceEvidenceHTML(evidenceFor('34_1_Bay_of_Bengal_(1978)'))",evidence)
    assert 'PDF 9' in html and '1978' in html and '6,205,000' in html and 'a'*64 in html
    assert 'hypothetical' in html.lower()


def test_validation_allows_unavailable_record_without_groups():
    data=study();row=data['records'][0]
    data['groups']={};row.update(valid=False,status='unavailable',reasons=['Method does not support this scope.'],ppr_fixed_H_tC=None,ppr_retained_L_tC=None)
    renderer.validate(data)


def test_baseline_route_can_be_separate_from_experiment_routes():
    data=study();data['routes']=['SC','SM','SE','SR'];data['records'][0]['route']='S0'
    renderer.validate(data)


def test_render_output_hash_matches_exact_bytes_and_data_stays_embedded(tmp_path,monkeypatch):
    for directory in ['results','src','verification']:(tmp_path/directory).mkdir()
    data=study();data['models'][0]['model_label']='Bay </script> & reference'
    (tmp_path/'results/study.json').write_text(json.dumps(data),encoding='utf-8')
    (tmp_path/'results/external_reference_audit.csv').write_text('method,status\n',encoding='utf-8')
    (tmp_path/'src/report_template.html').write_text((ROOT/'src/report_template.html').read_text(encoding='utf-8'),encoding='utf-8')
    monkeypatch.setattr(renderer,'ROOT',tmp_path);renderer.render()
    report=(tmp_path/'report.html').read_bytes();check=json.loads((tmp_path/'verification/report_data.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(report).hexdigest()==check['html_sha256']
    embedded=re.search(r'<script id="study-data" type="application/json">(.*?)</script>',report.decode('utf-8'),re.S).group(1)
    assert json.loads(embedded)['study']==data


@pytest.mark.parametrize('fault',['duplicate_coordinate','boolean_ppr','invalid_without_reason','valid_without_groups','nonfinite','unknown_fraction'])
def test_validation_rejects_misleading_schema(fault):
    data=study();row=data['records'][0]
    if fault=='duplicate_coordinate':
        extra=copy.deepcopy(row);extra['scenario_id']='another';data['records'].append(extra);data['groups']['another']=[]
    elif fault=='boolean_ppr':row['ppr_fixed_H_tC']=True
    elif fault=='invalid_without_reason':row.update(valid=False,ppr_fixed_H_tC=None,ppr_retained_L_tC=None)
    elif fault=='valid_without_groups':data['groups']={}
    elif fault=='nonfinite':data['groups'][row['scenario_id']][0]['sppr']=float('nan')
    elif fault=='unknown_fraction':row['fraction']=.03
    with pytest.raises((AssertionError,ValueError)):renderer.validate(data)
