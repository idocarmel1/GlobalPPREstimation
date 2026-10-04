"""Metadata-derived labels and explicit original-reference provenance."""
import json
from pathlib import Path
from baseline import ROOT

def enrich(meta,base):
    selected=json.loads((ROOT/'results/selected_models.json').read_text(encoding='utf-8'))
    entries={r['model_id']:r for r in selected}
    old=json.loads((ROOT/'inputs/original_results/study.json').read_text(encoding='utf-8'))
    refs={r['model_id']:r for r in old['models']}
    mid=meta['model_id']
    common=dict(carbon_conversion=9.,group_count=base.n_groups,
        denominator_name='Native modeled primary-producer production / 9',
        denominator_kind='model_period_PP_not_satellite_NPP',
        raw_catch_status='positive_living_harvest' if base.catch.sum()>0 else 'explicit_zero_in_raw_source',
        closure='Freeze completed living P,Q,diet,predation,accumulation,migration. Solve EE for SM; detritus accumulation absorbs routed inflow at fixed predation. No new consumption is assumed.',
        group_identity_source='UTF-8 frozen JSON group_seq/group_name; immutable numeric sequence.',
        native_import_production_tC=float(base.p.loc[base.get_Import_seq()].sum()/9.))
    meta.update(common)
    if mid in entries:
        row=entries[mid];m=row['metadata'];currency=m.get('currency_units','unknown')
        explicit='t/km' in currency.lower()
        meta.update(cohort='additional',metadata=m,ecological_sha256=row['ecological_sha256'],selection_rank=row['selection_rank'],
            geographic_stratum=row['stratum'],source_validity='screened_numerically_eligible_existing_marine_JSON',
            model_label=f"{m.get('model_name',base._model.model_name)} ({m.get('model_year',base._model.model_year)})",
            native_currency=currency,native_units=(currency+' per native time unit'),
            ppr_units=('t C equivalent km-2 per native time unit' if explicit else 'native wet-weight production equivalent / 9'),
            native_time_unit='not explicitly recorded in this JSON metadata; no annual reconstruction or cross-model absolute aggregation',
            native_area_unit='km2 explicitly recorded' if explicit else 'not explicitly recorded by currency enum',
            source_screening=row['screening'],sr_routing=None,
            limitations=['Numerical eligibility does not establish ecological truth or global representativeness.',
                'Existing JSON metadata establishes natural detritus fate; no fleet discard-return destination was extracted.',
                'Detritus export is excluded from fishery H by the unchanged loader; detritus accumulation remains the dependent residual.',
                'Native currency '+currency+'; missing area/time normalization stays unknown.'],
            baseline_validation='Fresh unmodified frozen calculator + zero-discard adapter equality, independent analytic and conservation checks; no saved workbook required.')
    else:
        assert mid in refs
        original=refs[mid]
        for key in ['source_validity','limitations','native_units','ppr_units','sr_routing','native_currency','native_time_unit','native_area_unit']:
            if key in original:meta[key]=original[key]
        meta.update(cohort='original_reference',model_label=original['model_label'],baseline_validation='Frozen original saved workbook and overlapping original solved study points.')
    return meta
