"""Catch boundaries and routing responses must share exact taxon support."""
import csv
import gzip
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from discard_data import (read_catch_components,annual_values,interpolate_response,
                          compatibility_error,prepare_responses,evaluate_band,load_response_package,
                          RESPONSE_PATH)


def test_live_response_copy_requires_matching_original_package(tmp_path):
    import hashlib
    import json
    original = tmp_path/RESPONSE_PATH
    original.parent.mkdir(parents=True)
    original.write_text(json.dumps({'schema_version':1,'response_models':[]}))
    live = tmp_path/'data/discard_responses.current.json'
    live.parent.mkdir()
    live.write_text(json.dumps({'schema_version':1,'response_models':[],
        'refresh_provenance':{'original_package':RESPONSE_PATH,
          'original_package_sha256':hashlib.sha256(original.read_bytes()).hexdigest()}}))
    assert load_response_package(tmp_path)['_source_path']=='data/discard_responses.current.json'
    original.write_text('{}')
    with pytest.raises(ValueError,match='original discard'):
        load_response_package(tmp_path)


def response():
    return {'baseline_valid':True,'group_ids':[1,2],'group_names':['low','high'],
        'baseline_coefficients':[10.,100.],'construction_invariant':False,'routes':{
        'SC':{'points':[{'fraction':f,'valid':True,'coefficients':[10.,100.]} for f in (0.,.5,1.)],
              'valid_intervals':[[0.,.5],[.5,1.]]},
        'SM':{'points':[{'fraction':f,'valid':True,'coefficients':[10*(1+2*f),100*(1+2*f)]} for f in (0.,.5,1.)],
              'valid_intervals':[[0.,.5],[.5,1.]]}}}


def prepared():
    return prepare_responses(response(),['low','high'],[10.,100.],{'low':[('low',1.)],'high':[('high',1.)]})


def test_different_landed_and_discarded_composition_is_evaluated_per_taxon():
    landings=[[10.],[1.]];discards=[[0.],[9.]];total=[[10.],[10.]]
    assert annual_values([2019],[2019],landings,[10.,100.],'ok')['ppr']==[200.]
    assert annual_values([2019],[2019],discards,[10.,100.],'ok')['ppr']==[900.]
    assert annual_values([2019],[2019],total,[10.,100.],'ok')['ppr']==[1100.]
    band=evaluate_band(prepared(),.45,[10.,1.],[10.,100.],['low','high'])
    assert band['status']=='assessed'
    assert band['min_tC']==pytest.approx(200/9)
    assert band['max_tC']==pytest.approx(380/9)


def test_zero_discard_matches_baseline_exactly():
    b=evaluate_band(prepared(),0.,[10.,1.],[10.,100.],['low','high'])
    assert b['min_tC']==b['max_tC']==200/9


def test_each_included_route_preserves_evidence_classification():
    b=evaluate_band(prepared(),.25,[10.,1.],[10.,100.],['low','high'])
    assert set(b['route_evidence'])==set(b['route_ppr_tC'])
    assert 'hypothetical' in b['route_evidence']['SM']['description']


def test_zero_landings_and_missing_classification_do_not_invent_band():
    assert evaluate_band(prepared(),1.,[0.,0.],[10.,100.],['low','high'])['status']=='not_assessed'
    assert annual_values([2019],[2019],[[None],[1.]],[10.,100.],'ok')['ppr']==[None]
    assert evaluate_band(prepared(),None,[None,1.],[10.,100.],['low','high'])['status']=='not_assessed'


def test_missing_classification_in_unsupported_taxon_still_blocks_year():
    assert annual_values([2019],[2019],[[1.],[None]],[10.,None],'ok')['ppr']==[None]


def test_positive_unsupported_mass_is_unavailable_but_known_zero_is_preserved():
    assert annual_values([2019],[2019],[[0.],[5.]],[10.,None],'ok')['ppr']==[None]
    assert annual_values([2019],[2019],[[0.],[0.]],[10.,None],'ok')['ppr']==[0.]
    assert annual_values([2019],[2019],[[0.],[5.]],[10.,0.],'ok')['ppr']==[0.]


def test_malformed_nonadjacent_valid_interval_cannot_skip_interior_point():
    route=response()['routes']['SM']
    route['points'][1]['valid']=False
    route['valid_intervals']=[[0.,1.]]
    assert interpolate_response(route,.25)[2]


def test_interpolation_stops_at_invalid_sample_and_weight_fallback():
    r=response()['routes']['SM'];r['points'][1]['valid']=False;r['valid_intervals']=[]
    assert interpolate_response(r,.25)[2]
    assert interpolate_response(r,1.1)[2]
    r=response()['routes']['SM'];r['valid_intervals']=[[0.,.5]]
    assert interpolate_response(r,.75)[2]
    assert interpolate_response(r,.5)[0]==[20.,200.]


def test_source_hash_mismatch_and_unsupported_baseline_are_unavailable():
    assert compatibility_error({'source_workbook_sha256':'A','source_json_sha256':'B'},'X','B')
    assert compatibility_error({'source_workbook_sha256':'A','source_json_sha256':'B'},'A','X')
    r=response();r['baseline_valid']=False
    assert prepare_responses(r,['low'],[10.],{'low':[('low',1.)]})['error']


def test_mapping_baseline_mismatch_is_rejected_and_rounding_anchor_is_exact():
    assert prepare_responses(response(),['low'],[12.],{'low':[('low',1.)]})['error']
    p=prepare_responses(response(),['low'],[10.0000004],{'low':[('low',1.)]})
    b=evaluate_band(p,0.,[9.],[10.0000004],['low'])
    assert b['min_tC']==10.0000004


def test_failed_scenario_coefficient_keeps_common_positive_landed_support():
    p=prepared();p['routes']['SM']['points'][1]['coefficients'][1]=None
    b=evaluate_band(p,.5,[10.,1.],[10.,100.],['low','high'])
    assert b['status']=='not_assessed'
    assert 'SM' in b['excluded_routes']
    assert b['min_tC'] is None


def test_unidentified_treatments_apply_to_same_landed_vector_and_scope():
    p=prepared();affected=[{'name':'high','simple_sppr':20.}]
    zero=evaluate_band(p,.5,[10.,1.],[10.,100.],['low','high'],treatment='zero',unidentified=affected)
    simple=evaluate_band(p,.5,[10.,1.],[10.,100.],['low','high'],treatment='simple',unidentified=affected)
    assert zero['max_tC']==pytest.approx(200/9)
    assert simple['max_tC']==pytest.approx(220/9)
    assert evaluate_band(p,.5,[10.,1.],[10.,100.],['low','high'],treatment='simple',unidentified=affected,scope='PP')['status']=='not_assessed'


def test_invariant_benchmark_does_not_claim_zero_ecological_uncertainty():
    p=prepared();p['construction_invariant']=True
    b=evaluate_band(p,.5,[10.,1.],[10.,100.],['low','high'])
    assert b['status']=='not_assessed'
    assert b['construction_invariant']


def test_raw_component_loader_preserves_full_precision_and_unknown_split(tmp_path):
    d=tmp_path/'SeaAroundUsExtraction/data/catch_by_taxon_year';d.mkdir(parents=True)
    with gzip.open(d/'LME_001.csv.gz','wt',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=['unit_id','year','taxon','catch_tonnes','landings_tonnes','discards_tonnes'])
        writer.writeheader();writer.writerows([
            dict(unit_id='LME_001',year=2019,taxon='a',catch_tonnes=1.123456789,landings_tonnes=1.,discards_tonnes=.123456789),
            dict(unit_id='LME_001',year=2019,taxon='b',catch_tonnes=2.,landings_tonnes='',discards_tonnes='')])
    x=read_catch_components(tmp_path,'LME_001',['a','b'],[2019])
    assert x['full_precision_catch']==[[1.123456789],[2.]]
    assert x['landings']==[[1.],[None]]
    assert x['catch_accounting']['classification_status']==['missing_classification']


def test_time_series_exports_each_boundary_and_reindexes_the_same_band():
    from build_time_series import export_models
    from discard_data import POLICY
    unit={'catch_basis_policy':POLICY,'years':[2019],'taxa':['low','high'],
        'catch':[[10.],[10.]],'full_precision_catch':[[10.],[10.]],
        'landings':[[10.],[1.]],'discards':[[0.],[9.]],'unidentified':{'taxa':[]},
        'default_model':0,'models':[{'id':'fixture','verified':True,'scopes':{'all':{
            'methods':['new_GE'],'status':{'new_GE':'ok'},'values':[[10.],[100.]]}},
            'discard_sensitivity':{'all':{'new_GE':{'method':[{'year':2019,'status':'assessed','min_tC':200/9,'max_tC':380/9}]}}}}]}
    models,_=export_models(unit,[2018,2019])
    record=models[0]['scopes']['all']['methods']['new_GE']
    assert record['ppr']==[None,200.]
    assert record['catch_bases']['catch']['ppr']==[None,1100.]
    assert record['catch_bases']['discards']['ppr']==[None,900.]
    assert record['catch']==[None,11.]
    assert record['sensitivity'][0] is None
    assert record['sensitivity'][1]['min_tC']==200/9
    assert record['unidentified_zero']['ppr']==record['ppr']


def test_simple_trophic_reference_uses_taxon_composition_on_every_boundary():
    from build_time_series import simple_basis_values
    components={'years':[2019],'taxa':['low','high'],'full_precision_catch':[[10.],[10.]],
        'landings':[[10.],[1.]],'discards':[[0.],[9.]]}
    record=simple_basis_values(components,[2019],{'low':2.,'high':3.},{'taxa':[]})
    assert record['ppr']==[200.]
    assert record['catch_bases']['discards']['ppr']==[900.]
    assert record['catch_bases']['catch']['ppr']==[1100.]


def test_annual_band_metadata_tracks_selected_treatment_support(tmp_path):
    import hashlib
    from discard_data import model_sensitivity
    source=tmp_path/'PPREstimation/real_models/global_cover_jsons/fixture.json'
    source.parent.mkdir(parents=True);source.write_text('{}',encoding='utf8')
    package={'study_version':'fixture','response_models':[{'model_id':'fixture',
        'source_workbook_sha256':'book','source_json_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'source_validity':'accounting_baseline_with_inferred_accumulation','methods':{'new_GE':{'all':response()}}}]}
    unit={'years':[2019],'taxa':['low','high'],'landings':[[1.],[1.]],'discards':[[0.],[9.]],
        'unidentified':{'taxa':[{'name':'high','simple_sppr':None}]}}
    model={'id':'fixture','source_sha256':'book','scopes':{'all':{
        'methods':['new_GE'],'values':[[10.],[None]],'status':{'new_GE':'ok'}}}}
    bands,unavailable=model_sensitivity(tmp_path,unit,model,{'low':[('low',1.)]},package)
    records=bands['all']['new_GE']
    assert records['method'][0]['covered_fraction']==.5
    assert records['method'][0]['covered_discard_fraction']==0.
    assert records['zero'][0]['covered_fraction']==1.
    assert records['zero'][0]['covered_discard_fraction']==pytest.approx(9/11)
    assert records['simple'][0]['covered_discard_fraction']==0.
    assert records['zero'][0]['source_validity']=='accounting_baseline_with_inferred_accumulation'
