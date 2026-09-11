"""Taxon catch boundaries and audited, versioned discard-routing responses.

This module evaluates fixed coefficients and interpolates verified group responses.
It never reconstructs an Ecopath model, changes mappings, or touches annual NPP.
"""
from __future__ import annotations
from collections import defaultdict
from copy import deepcopy
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path

POLICY='landings_default_three_bases_v1'
RESPONSE_PATH='research/discard_sensitivity_2026_09_10/results/discard_responses.v1.json'
BASES={'landings':'landings','catch':'full_precision_catch','discards':'discards'}


def finite(x): return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)


def read_catch_components(root,unit,taxa=None,years=None):
    relative=f'SeaAroundUsExtraction/data/catch_by_taxon_year/{unit}.csv.gz'
    path=Path(root)/relative
    values={};labels={};source_years=set()
    if path.exists():
        with gzip.open(path,'rt',encoding='utf-8-sig',newline='') as stream:
            for row in csv.DictReader(stream):
                year=int(row['year']);name=row['taxon'];source_years.add(year)
                labels.setdefault(name,{k:row.get(k,'') for k in ['taxon','common_name','functional_group','commercial_group']})
                amounts={}
                for key in ('catch','landings','discards'):
                    value=row.get(key+'_tonnes')
                    amount=float(value) if value not in (None,'') else None
                    if amount is not None and (not finite(amount) or amount<0):
                        raise ValueError(f'{unit}/{name}/{year}: invalid {key} amount')
                    amounts[key]=amount
                if all(finite(v) for v in amounts.values()) and not math.isclose(amounts['catch'],amounts['landings']+amounts['discards'],rel_tol=1e-9,abs_tol=1e-7):
                    raise ValueError(f'{unit}/{name}/{year}: catch does not equal landings + discards')
                previous=values.setdefault((name,year),dict(catch=0.,landings=0.,discards=0.))
                for key,value in amounts.items(): previous[key]=previous[key]+value if previous[key] is not None and value is not None else None
    if taxa is None: taxa=list(labels)
    if years is None: years=sorted(source_years)
    if set(labels)-set(taxa): raise ValueError(f'{unit}: raw catch taxa absent from exported taxon ordering')
    out={'years':list(years),'taxa':list(taxa),'catch_basis_policy':POLICY}
    for key,field in BASES.items():
        out[field]=[[values.get((name,year),{}).get(key,0.) if year in source_years else None for year in years] for name in taxa]
    classification=[]
    for i,year in enumerate(years):
        if year not in source_years: classification.append('missing_catch')
        elif any(not finite(out[field][t][i]) for field in ('landings','discards') for t in range(len(taxa))): classification.append('missing_classification')
        else: classification.append('complete')
    out['catch_accounting']={'source':relative,'sha256':hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None,
        'classification_status':classification,'precision':'Full source taxon precision; no regional retained-share scaling.',
        'landings_definition':'Reported plus unreported retained landings. Discards are separate.',
        'discard_fraction_definition':'D/(L+D), using full regional catch composition; unavailable for missing classification or no catch.'}
    out['_labels']=labels
    return out


def annual_values(years,source_years,matrix,coefficients,status):
    result={'status':status,'ppr':[None]*len(years),'covered_catch':[None]*len(years)}
    if status!='ok': return result
    if len(matrix)!=len(coefficients) or any(len(row)!=len(source_years) for row in matrix): raise ValueError('Catch/coefficient dimensions do not agree')
    lookup={year:i for i,year in enumerate(source_years)}
    for j,year in enumerate(years):
        if year not in lookup: continue
        i=lookup[year]
        # Unknown mass in any taxon makes the selected catch boundary unknown,
        # including when that taxon has no usable PPR coefficient.
        if any(not finite(row[i]) for row in matrix): continue
        supported=[(row[i],c) for row,c in zip(matrix,coefficients) if finite(c) and c>=0]
        if not supported or any(not finite(x) for x,c in supported): continue
        covered=math.fsum(x for x,c in supported)
        if covered<=0 and math.fsum(row[i] for row in matrix)>0: continue
        result['ppr'][j]=math.fsum(x*c for x,c in supported)
        result['covered_catch'][j]=covered
    return result


def annual_totals(matrix,years):
    return [math.fsum(row[i] for row in matrix) if matrix and all(finite(row[i]) for row in matrix) else None for i in range(len(years))]


def catch_basis_metadata(metadata,taxa,years,components):
    affected={r['name']:r for r in metadata.get('taxa',[])}
    result={}
    for basis,field in BASES.items():
        matrix=components[field]
        matched=[row for name,row in zip(taxa,matrix) if name in affected]
        missing=[row for name,row in zip(taxa,matrix) if name in affected and not finite(affected[name].get('simple_sppr'))]
        def sums(rows):
            return [math.fsum(row[i] for row in rows) if all(finite(row[i]) for row in rows) else None for i in range(len(years))]
        result[basis]={'catch':sums(matched),'missing_simple_catch':sums(missing)}
    return result


def interpolate_response(route,fraction):
    if not finite(fraction) or not 0<=fraction<=1: return None,False,'Discard fraction is missing or outside [0,1].'
    points=sorted(route.get('points',[]),key=lambda p:p['fraction'])
    for p in points:
        if math.isclose(fraction,p['fraction'],abs_tol=1e-12,rel_tol=0):
            if not p.get('valid'): return None,False,'; '.join(p.get('reasons',[])) or f'Invalid or unavailable computed fraction {fraction:g}.'
            return list(p['coefficients']),False,None
    for lo,hi in route.get('valid_intervals',[]):
        if lo<fraction<hi:
            if any(lo<p['fraction']<hi for p in points):
                return None,False,'An interpolation interval skips an intermediate computed point.'
            a=next((p for p in points if p['fraction']==lo),None);b=next((p for p in points if p['fraction']==hi),None)
            if a is None or b is None or not a.get('valid') or not b.get('valid'): return None,False,'An interpolation endpoint is invalid or missing.'
            t=(fraction-lo)/(hi-lo)
            return [x+t*(y-x) if finite(x) and finite(y) else None for x,y in zip(a['coefficients'],b['coefficients'])],True,None
    return None,False,'No verified adjacent interval supports this fraction; no extrapolation or invalid-gap interpolation.'


def compatibility_error(response,workbook_sha,json_sha):
    if not response: return 'No tested response for this exact model.'
    if response.get('source_workbook_sha256')!=workbook_sha: return 'Upstream coefficient-workbook SHA-256 differs from the tested source.'
    if response.get('source_json_sha256')!=json_sha: return 'Model JSON SHA-256 differs from the tested source.'
    if response.get('status')=='not_assessed_zero_source_harvest': return 'Source model has zero harvest; regional discard-routing sensitivity was not assessed.'
    return None


def prepare_responses(scope_response,taxa,baseline,mappings):
    result={'error':None,'construction_invariant':False,'routes':{}}
    if not scope_response: result['error']='Method or source scope was not assessed.';return result
    result['construction_invariant']=bool(scope_response.get('construction_invariant'))
    if not scope_response.get('baseline_valid'): result['error']='The tested baseline is invalid or unavailable for this method/scope.';return result
    names=scope_response['group_names'];groupbase=scope_response['baseline_coefficients']
    normalize=lambda value:' '.join(str(value).split())
    index={normalize(name):i for i,name in enumerate(names)}
    if len(index)!=len(names): result['error']='Group names become ambiguous when normalizing whitespace.';return result
    assignment=[]
    for name,current in zip(taxa,baseline):
        if not finite(current): assignment.append(None);continue
        entries=mappings.get(name,[])
        if not entries or any(normalize(group) not in index or not finite(weight) or weight<0 for group,weight in entries):
            result['error']=f'Missing or incompatible fixed group mapping for supported taxon {name}.';return result
        if not math.isclose(math.fsum(w for g,w in entries),1.,rel_tol=0,abs_tol=1e-9):
            result['error']=f'Mapping weights do not sum to 1 for {name}; no renormalization allowed.';return result
        parts=[(index[normalize(group)],weight) for group,weight in entries]
        if any(not finite(groupbase[i]) for i,w in parts): result['error']=f'Baseline group coefficient unavailable for {name}.';return result
        expected=math.fsum(groupbase[i]*weight for i,weight in parts)
        # Production workbooks store taxon SPPR to six decimal places. Keep that
        # exact baseline and add full-precision weighted group deltas thereafter.
        if not math.isclose(expected,current,rel_tol=2e-10,abs_tol=5.1e-7):
            result['error']=f'Fixed mapping baseline does not reproduce stored taxon SPPR for {name}.';return result
        assignment.append(parts)
    for route,definition in scope_response['routes'].items():
        revised=deepcopy(definition)
        for point in revised['points']:
            groupcoef=point['coefficients'];taxoncoef=[]
            for current,parts in zip(baseline,assignment):
                if parts is None or any(i>=len(groupcoef) or not finite(groupcoef[i]) for i,w in parts): taxoncoef.append(None)
                else: taxoncoef.append(current+math.fsum(w*(groupcoef[i]-groupbase[i]) for i,w in parts))
            point['coefficients']=taxoncoef
        result['routes'][route]=revised
    return result


def evaluate_band(prepared,fraction,landings,baseline,taxa,treatment='method',unidentified=(),scope='all'):
    result={'status':'not_assessed','min_tC':None,'max_tC':None,'route_ppr_tC':{},
        'route_evidence':{},
        'discard_fraction':fraction,'covered_fraction':None,'excluded_routes':{},'interpolated':False,
        'construction_invariant':prepared.get('construction_invariant',False),
        'uncertainty_type':'discard-routing sensitivity envelope; not a confidence interval'}
    reason=prepared.get('error')
    if treatment=='simple' and scope!='all': reason='Unidentified reference trophic chain has no inner/PP source decomposition.'
    if result['construction_invariant']: reason='Routing-invariant fixed-TL benchmark; ecological recycling uncertainty is not assessed.'
    if not finite(fraction): reason=reason or 'No usable regional discard fraction (no catch or missing classification).'
    if any(not finite(x) for x in landings): reason=reason or 'Landed catch classification is missing.'
    if reason: result['reason']=reason;return result
    total_landings=math.fsum(landings)
    if total_landings<=0: result['reason']='No retained landings to evaluate.';return result
    affected={r['name']:r.get('simple_sppr') for r in unidentified}
    def adjust(coeff):
        return [(0. if treatment=='zero' else affected[name]) if treatment!='method' and name in affected else value for name,value in zip(taxa,coeff)]
    central=adjust(baseline)
    support=[i for i,(amount,c) in enumerate(zip(landings,central)) if finite(c) and c>=0]
    result['covered_landings_tonnes']=math.fsum(landings[i] for i in support)
    result['covered_fraction']=result['covered_landings_tonnes']/total_landings
    if not any(landings[i]>0 for i in support): result['reason']='No positive supported landings.';return result
    for route,definition in prepared.get('routes',{}).items():
        values,interpolated,error=interpolate_response(definition,fraction)
        if error: result['excluded_routes'][route]=error;continue
        values=adjust(values)
        missing=[taxa[i] for i in support if landings[i]>0 and (not finite(values[i]) or values[i]<0)]
        if missing: result['excluded_routes'][route]='Scenario loses central positive-landings support: '+', '.join(missing[:5]);continue
        result['route_ppr_tC'][route]=math.fsum(landings[i]*values[i] for i in support if landings[i]>0)/9.
        descriptions={
            'SC':'Imported catch convention: designated discard remains in the combined fishery sink; amount is hypothetical.',
            'SM':'hypothetical M0 accounting proxy; returned biomass increases residual detritus accumulation under fixed consumption.',
            'SE':'hypothetical split between retained catch and a separate external discard sink.',
            'SR':'Documented Humboldt fleet/offal destination with hypothetical designated amount; downstream return increases residual detritus accumulation under fixed consumption.'}
        evidence=sorted({p.get('evidence_status','hypothetical') for p in definition.get('points',[])})
        if route=='SR' and 'source_supported_destination_hypothetical_amount' not in evidence:
            descriptions['SR']='No source-supported positive return scenario; zero-amount accounting identity only.'
        result['route_evidence'][route]={'evidence_status':evidence,'description':descriptions.get(route,'Hypothetical accounting scenario.')}
        result['interpolated']=result['interpolated'] or interpolated
    if len(result['route_ppr_tC'])<2: result['reason']='Fewer than two valid named routing scenarios remain on the same landed taxon support.';return result
    result.update(status='assessed',min_tC=min(result['route_ppr_tC'].values()),max_tC=max(result['route_ppr_tC'].values()),
        reason=None,source_support='Exact tested food web, transferred to regional discard exposure with fixed mapping weights.',
        precision_anchor='Persisted six-decimal taxon baseline + full-precision fixed-weight group coefficient deltas.',
        exposure_assumption='Uniform native-model discard allocation evaluated at regional D/(L+D); not a group-specific source reconstruction.')
    return result


def read_final_mappings(workbook,model_id):
    mappings=defaultdict(list)
    if 'Final mappings' not in workbook.sheetnames: return mappings
    header=None
    for row in workbook['Final mappings'].values:
        if row[0]=='unit_id': header=list(row);continue
        if header is None: continue
        item=dict(zip(header,row))
        if item.get('model_id')==model_id and finite(item.get('weight')):
            mappings[item['taxon']].append((item['group'],item['weight']))
    return dict(mappings)


def load_response_package(root):
    path=Path(root)/RESPONSE_PATH
    if not path.exists(): return {'study_version':None,'response_models':[]}
    package=json.loads(path.read_text(encoding='utf-8'))
    if package.get('schema_version')!=1: raise ValueError('Unsupported discard-response schema')
    return package


def model_sensitivity(root,unit,model,mappings,package):
    response=next((r for r in package.get('response_models',[]) if r['model_id']==model['id']),None)
    json_path=Path(root)/'PPREstimation/real_models/global_cover_jsons'/f'{model["id"]}.json'
    json_sha=hashlib.sha256(json_path.read_bytes()).hexdigest() if json_path.exists() else None
    common_error=compatibility_error(response,model.get('source_sha256'),json_sha)
    years=unit['years'];taxa=unit['taxa'];output={};unavailable={}
    for scope,definition in model['scopes'].items():
        output[scope]={};unavailable[scope]={}
        for index,method in enumerate(definition['methods']):
            baseline=[row[index] for row in definition['values']]
            scope_response=(((response or {}).get('methods',{}).get(method) or {}).get(scope))
            prepared=prepare_responses(scope_response,taxa,baseline,mappings)
            if common_error: prepared['error']=common_error
            if definition['status'].get(method)!='ok': prepared['error']='Selected source-workbook method is flagged unavailable or failed.'
            if method=='simple trophic chain': prepared['construction_invariant']=True
            if prepared.get('error') or prepared.get('construction_invariant'):
                unavailable[scope][method]=('Routing-invariant fixed-TL benchmark; ecological recycling uncertainty is not assessed.'
                    if prepared.get('construction_invariant') else prepared['error'])
                continue
            output[scope][method]={}
            for treatment in ('method','zero','simple'):
                annual=[]
                for i,year in enumerate(years):
                    landed=[row[i] for row in unit['landings']];discard=[row[i] for row in unit['discards']]
                    total_l=math.fsum(landed) if all(finite(x) for x in landed) else None
                    total_d=math.fsum(discard) if all(finite(x) for x in discard) else None
                    fraction=total_d/(total_l+total_d) if total_l is not None and total_d is not None and total_l+total_d>0 else None
                    record=evaluate_band(prepared,fraction,landed,baseline,taxa,treatment,
                        unit.get('unidentified',{}).get('taxa',[]),scope)
                    record.update(year=year,model_id=model['id'],source_hash=model.get('source_sha256'),
                        source_json_sha256=json_sha,study_version=package.get('study_version'),
                        source_validity=(response or {}).get('source_validity'),
                        source_response=RESPONSE_PATH,landings_tonnes=total_l,discards_tonnes=total_d)
                    if finite(total_l) and finite(total_d):
                        affected={r['name']:r.get('simple_sppr') for r in unit.get('unidentified',{}).get('taxa',[])}
                        central=[(0. if treatment=='zero' else affected[t]) if treatment!='method' and t in affected else c for t,c in zip(taxa,baseline)]
                        support=[j for j,c in enumerate(central) if finite(c) and c>=0]
                        covered_l=math.fsum(landed[j] for j in support)
                        covered_d=math.fsum(discard[j] for j in support)
                        record['covered_discard_fraction']=covered_d/(covered_l+covered_d) if covered_l+covered_d>0 else None
                    annual.append(record)
                output[scope][method][treatment]=annual
    return output,unavailable
