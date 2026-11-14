"""Independent retained-package group-display arithmetic and byte checks."""
import importlib.util, math, zipfile
from pathlib import Path
p=Path(__file__).with_name('adopt_retained.py')
s=importlib.util.spec_from_file_location('retained',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
plan=m.verify_package()
book=m.read_book(m.PACKAGE/'regional/LME_022.xlsx')
from tools.project_core.validation.researcher_review import sheet_xml
with zipfile.ZipFile(m.RUN/'inputs/pre_adoption/LME_022.xlsx') as a,zipfile.ZipFile(m.PACKAGE/'regional/LME_022.xlsx') as b:
    for sheet in ['Catch','Classic PPR','NPP']:
        m.require(a.read(sheet_xml(a,sheet)[0])==b.read(sheet_xml(b,sheet)[0]),'Independent sheet XML changed: '+sheet)
mapping=m.read(m.MAPPING)['rows'];run=m.read(m.PRIMARY/'run_manifest.json')['answer']['methods']
catch={(r['taxon'],r['catch_basis']):r for r in m.records(book,'Catch','Catch')}
annual={(r['method'],r['scope'],r['catch_basis']):r for r in m.records(book,'PPR','Annual') if r['unidentified']=='method' and r['metric']=='ppr'}
effects=[];max_delta_error=0;max_rounding_difference=0
for key in m.KEYS:
    for scope in ['all','inner','PP']:
        coefficients=run[key]['scopes'][scope]
        for basis in ['landings','catch','discards']:
            for year in m.YEARS:
                full=[];included=[];excluded=[]
                for taxon in mapping:
                    c=catch[taxon['taxon'],basis][year]
                    if not m.finite(c):continue
                    for g in taxon['groups']:
                        value=c*g['weight']*coefficients[g['group_name']]
                        full.append(value)
                        (excluded if g['group_id'] in m.EXCLUDED else included).append(value)
                all_ppr=math.fsum(full);included_ppr=math.fsum(included);excluded_ppr=math.fsum(excluded)
                err=abs(all_ppr-included_ppr-excluded_ppr);max_delta_error=max(max_delta_error,err)
                m.require(math.isclose(all_ppr,included_ppr+excluded_ppr,rel_tol=1e-14,abs_tol=1e-7),'Whole-period filtering does not conserve retained contributions')
                expected_excluded=catch['Cetorhinus maximus',basis][year]*coefficients['BaleenWhales']
                m.require(math.isclose(expected_excluded,excluded_ppr,rel_tol=1e-14,abs_tol=1e-7),'Exclusion includes wrong taxon/share')
                saved=annual[key,scope,basis][year]
                difference=abs(all_ppr-saved);max_rounding_difference=max(max_rounding_difference,difference)
                rounding_bound=math.fsum(r[year] for (t,b),r in catch.items() if b==basis)*0.00000050001
                m.require(difference<=rounding_bound+1e-6,'Regional/display difference exceeds six-decimal coefficient rounding bound')
                effects.append({'method':key,'scope':scope,'basis':basis,'year':year,'full_ppr_wet_tonnes':all_ppr,'included_ppr_wet_tonnes':included_ppr,'removed_ppr_wet_tonnes':excluded_ppr,'removed_catch_tonnes':catch['Cetorhinus maximus',basis][year]})
try:m.apply(None)
except ValueError as e:m.require('Active caller publication required' in str(e),'Unexpected transaction guard error')
else:raise ValueError('Unguarded apply accepted')
try:m.check_inputs({m.rel(m.REGION):'0'*64})
except ValueError as e:m.require('Changed input' in str(e),'Unexpected byte guard error')
else:raise ValueError('Changed-input guard accepted mismatch')
m.write(m.RUN/'qa/display_and_preservation.json',{'passed':True,'independent_sheet_XML_exact':['Catch','Classic PPR','NPP'],'whole_period_method_scope_basis_year_checks':len(effects),'max_full_minus_included_minus_removed_error_wet_tonnes':max_delta_error,'max_display_vs_regional_rounding_difference_wet_tonnes':max_rounding_difference,'six_decimal_regional_coefficient_bound_checked':True,'unguarded_apply_rejected':True,'changed_input_rejected':True,'no_renormalization':True,'effects':effects})
print({'passed':True,'whole_period_checks':len(effects),'max_rounding_difference_wet_tonnes':max_rounding_difference,'independent_sheet_XML_exact':True})
