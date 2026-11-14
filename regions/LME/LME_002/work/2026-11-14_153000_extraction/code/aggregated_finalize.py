"""Write portable source/evidence handoff for the official aggregate extraction."""
from pathlib import Path
import csv, json, hashlib, sys, subprocess, shutil
from decimal import Decimal
from aggregated_extract import ROOT,RUN,MODEL,PAPER,MODEL_ID,COMMIT,CITATION,PDF,SOURCE_PATHS,dump,sha,relative,rows

def main():
    ev=MODEL/'extracted_tables/evidence'
    summary=json.loads((RUN/'qa/aggregated_summary.json').read_text(encoding='utf-8'))
    source=json.loads((MODEL/'inputs/provenance.json').read_text(encoding='utf-8'))
    loader=json.loads((ev/'loader_schema_check.json').read_text(encoding='utf-8'))
    nativecheck=json.loads((ev/'native_canonical_verification.json').read_text(encoding='utf-8'))
    roundtrip=json.loads((ev/'SOURCE_FIDELITY_CHECK.json').read_text(encoding='utf-8'))
    for name in ['aggregated_source_facts.json','aggregated_summary.json']:
        shutil.copy2(RUN/'qa'/name,ev/name)
    base=rows(MODEL/'inputs/native/Ecosense_GOA_base.csv')
    native=[dict(zip(base[0],r)) for r in base[1:]]
    comparison={'scope':'Illustrative scalar aggregation checks against source-rounded Aydin2007 extracted Appendix C values; not proof of complete parameter or native-version equivalence.','formula':'B=sum(B_i); PB=sum(B_i*PB_i)/sum(B_i); QB=sum(B_i*QB_i)/sum(B_i)','rounding':'Original printed inputs are rounded; no equality threshold or correction inferred.','groups':[]}
    original=RUN/'outputs/numeric_writer_input.json'
    if original.exists():
        full=json.loads(original.read_text(encoding='utf-8'))
        comparison['comparison_source_sha256']=sha(original)
        comparison['comparison_source_role']='Contemporaneous extraction of original Appendix C; original publication retained underGOA-2007, not independent native original.'
        gs={int(g['n']):g for g in full['groups']}
        for ag,ids in [(1,[1,2,3,4]),(2,[5]),(3,[6,7,8,9,10]),(4,list(range(11,19))),(5,[19,24]),(6,[20,23]),(7,[21,27]),(8,[22]),(9,[25,28]),(10,[26]),(11,[29,30,31]),(12,[32,33]),(13,[34,35]),(15,[38,39,40,41]),(16,list(range(42,51)))]:
            vals=[gs[i] for i in ids];b=sum(Decimal(str(g['biomass'])) for g in vals)
            computed={'Biomass':b,'PB':sum(Decimal(str(g['biomass']))*Decimal(str(g['pb'])) for g in vals)/b,'QB':sum(Decimal(str(g['biomass']))*Decimal(str(g['qb'])) for g in vals)/b}
            comparison['groups'].append({'aggregate_id':ag,'aggregate_name':native[ag-1]['Group'],'original_ids':ids,'original_names':[g['name'] for g in vals],
              'original_operands':[{'group_id':g['n'],'name':g['name'],'biomass':g['biomass'],'pb':g['pb'],'qb':g['qb']} for g in vals],
              'original_locator':'Aydin et al. 2007 Appendix C Tables C1-C2; full source PDF in GOA-2007/sources',
              'source_rounded_aggregation':{k:str(v) for k,v in computed.items()},'native_aggregate':{k:native[ag-1][k] for k in computed},'native_minus_rounded_aggregation':{k:str(Decimal(native[ag-1][k])-v) for k,v in computed.items()},'membership_status':'Table 1 interpreted against original source labels; Steller west/central split mapped to all 4 published groups for other pinnipeds'})
    else:comparison['unavailable_reason']='Temporary original writer input no longer present; no numerical equivalence claimed.'
    dump(ev/'comparison_with_original_publication.json',comparison)
    notes=f'''# Gulf of Alaska official Rpath aggregate

## Source identity

{CITATION}

This is the official NOAA-EDAB/Rpath **Ecosense.GOA** parameter object, pinned to commit `{COMMIT}`. It contains **49 biological groups (46 consumers, one primary producer and two detritus pools) plus one fleet**. The original CSVs and R object are retained in [inputs/native](inputs/native/); [provenance](inputs/provenance.json) records exact bytes and SHA-256 hashes. The RDA file is archived, not independently decoded. The extraction uses the three CSVs that the official builder identifies as the object's inputs.

## Modeled period and area

The source documentation calls this a 1990s model aggregated from Aydin et al. (2007); **1990–1994** is the inherited original model period. The 2020 article is the publication of the aggregate, available online 25 May 2020. Its modeled shelf area is **291,840 km²**, 140°W–170°W (article §2.2.3, p.4). No new geographic coverage percentage or boundary was derived.

## Departures from the publication

The native aggregate is a distinct model from the 133-compartment published extraction. The 2020 article describes summing B and catch and biomass-weighting P/B, Q/B and DC, with one producer, two detritus pools and one fleet. Its text calls the preaggregation GOA model138 groups; this does not establish a one-to-one relationship with the133 published Appendix C compartments. The official documentation says no stanzas. Neither the original detailed diets nor a balanced native result have been substituted into this aggregate.

All native numeric literals, blanks, zeros and source order are preserved in companions. The canonical49 biological groups retain exact native names. Only strict import files use `Urchins dollars cucumbers` for native `Urchins, dollars, cucumbers` (group31), because the maintained writer forbids commas. This reversible representation decision was made by the extraction agent under the authorized task, not as a researcher scientific correction. [Label crosswalk](extracted_tables/companions/Group_label_crosswalk.csv) and [independent verification](extracted_tables/evidence/native_canonical_verification.json) record the mapping. Embedded import source tables intentionally retain the alias.

Native all-blank EE values and the two missing detritus biomasses remain unknown. Source BA values are retained, including pollock−1.35, pelagic forage fish−0.11 and other demersals−0.002 t/km²/year. Habitat fraction, TL, mortality Z, other mortality, detritus export and unavailable native fields are not filled. The native producer diet column is nonfeeding and all prey cells are blank, with Import0. Its full column is preserved in the native diet companion and its Import0 in canonical `diet_imp`.

Rpath's balance routine changes NA diet cells to0 on a separate runtime array. This extraction preserves raw NA cells as blanks in imports and−9999 in canonical diet entries. Therefore the canonical model is a source-faithful sparse parameter representation; it is not a balanced Rpath execution result. A future authorized calculation must explicitly reconcile native NA-as-zero semantics, unknown EE and detritus biomass. No balance or PPR solve was performed.

Two source fate rows (the detritus pools) are explicitly0+0, so the generic import validator reports two sum errors. No export fraction was invented to remove them. The native fleet routing fractions0.3908825/0.6091174 are retained in the companion; exact destination-name duplicate columns make these supported by ModelData without changing native fields. These are native fleet returns, distinct from the biological detritus fate rows.

## Evidence links

[Extraction report](extracted_tables/evidence/REPORT.md), [source reconstruction check](extracted_tables/evidence/SOURCE_FIDELITY_CHECK.json), [native/canonical checks](extracted_tables/evidence/native_canonical_verification.json), [schema admission](extracted_tables/evidence/loader_schema_check.json), [mass-balance source check](extracted_tables/evidence/MASS_BALANCE.md), [Table1 membership](extracted_tables/companions/Aggregation_membership_Table1.csv), [illustrative comparison](extracted_tables/evidence/comparison_with_original_publication.json), [evidence inventory](extracted_tables/evidence/evidence_index.json).

The NOAA article was read through its indexed full text; local PDF retrieval returned 403 and screenshot retrieval failed. Table 1's membership companion is therefore explicitly pending visual verification and did not determine numerical extraction. ModelData schema admission is `{loader['admitted']}`; this is not calculator construction, numerical readiness, model selection or researcher approval.

The [source-to-loader ledger](extracted_tables/evidence/source_to_loader_ledger.json) checks 490 scalar fields and 2,254 diet entries. All diet values and NaN masks agree. The only 47 scalar differences are blank native DetInput values becoming runtime 0; the native Rpath code explicitly uses that runtime default too. Canonical source blanks stay unknown. All 49 unknown EE values and both unknown detritus biomasses remain unknown in the loader. The source checker uses a generic “BA unknown” section heading, but the actual indeterminate reasons are sparse diet cells; all 49 BA values are known.
'''
    (MODEL/'model_notes.md').write_text(notes,encoding='utf-8')
    report=f'''# Gulf of Alaska (1990–1994), official Rpath49 aggregate

**Source:** {CITATION}
**LME:**2 Gulf of Alaska. **Model ID:**{MODEL_ID}. **Extracted:**2026-11-14.
**Groups:**49 (47living including primary producer,2detritus). **Fleet:**Fishery/Subsistence.

## Source tables

The numerical source is the official NOAA-EDAB/Rpath repository commit `{COMMIT}`. Original CSV literals are read with Python's CSV parser; no PDF OCR, image digitization or manual numerical transcription was used. `Ecosense_GOA_base.csv` contains50 rows and14 columns: Group,Type,Biomass,PB,QB,EE,ProdCons,BioAcc,Unassim,DetInput,PelDetFate,BenthDetFate,F_Fishery,D_Fishery. The fleet row has Type3 and remains in companions, not as a biological group. Biomass is t/km²; PB/QB are year⁻¹; BA, detritus import and catch flows are t/km²/year; efficiencies, diets and fates are dimensionless.

`Ecosense_GOA_diet.csv` contains49 prey rows and an Import row, with47 biological columns (46consumers and nonfeeding primary production). Standard Diet_composition.csv has49prey×46consumer cells plusImport/Sum/(1−Sum). The complete47-column source table remains in `Rpath_diet_native.csv`. The native source is sparse: blank diet cells are NA, not literal zeros. Native Rpath runtime explicitly replaces diet NA with0; this action has not been written back into the extraction.

`Ecosense_GOA_pedigree.csv` is retained in full. Its numeric input values have not been mislabeled as original1–8 pedigree grades. The exact builder `Rpath_unbalanced_data.R` names these three CSVs as inputs to Ecosense.GOA. The RDA object and source/reader code are retained for provenance; no RDA decode or native balance execution was performed.

## Biomass accumulation

Native BioAcc explicitly supplies all49biological values. Walleye pollock(group12)−1.35, Pelagic forage fish(group14)−0.11 and Other demersals(group18)−0.002 t/km²/year are negative; other biological groups are0. No steady-state assumption overrides these source values. Pelagic forage fish includes Pacific herring; Other demersals includes greenlings, per2020Table1. BA rate is not computed or supplied.

## Values from prose

Area291,840km² and140°W–170°W (§2.2.3,p4); official documentation identifies the model as1990s and aggregated from Aydin2007; exact1990–1994 period is inherited from that base model. Publication available online25May2020. §2.2.4(pp4–7) describes sum of biomass/catch and biomass-weighted PB,QB,DC; no reconstruction of these aggregate values was used as an input. Table1 crosswalk was transcribed from indexed PDF text and awaits visual review because download/screenshot access failed.

## Conventions applied

No biological parameter convention, zero completion, normalization, EE/B solve or source repair. Whole-model-area biomass/BA metadata is supported by the native area-standardized model and source units. The one import-only label alias for group31 is reversible; canonical scientific identity is original. The complete native parameter companion adds exact duplicate destination-name routing columns solely for the supported fleet-return loader schema. Native original columns and separate verbatim companion remain present. `--dir-name aggregated_stage` was used for collision-free temporary staging in this shared regional run.

## Deliberate blanks

All49 EE values; all ProdCons values; detritus B(group48/49); nonconsumer QB; habitat fractions; TL; Z; other mortality; source-unspecified detritus export; BA rate; and raw diet NA cells remain unknown. All three native CSVs, the native object documentation, builder, parameter reader and balance-code field semantics were inspected. Rpath would solve missing EE/DET B when balanced; no such solve is part of this extraction. Do not interpret canonical−9999 or import blanks as measured zeros.

## Unresolved and flagged

This is an official aggregated source, not recovery of the exact133group native source. The138original-group count in2020 does not match133published biological rows, and no full version equivalence is asserted. Group names in Table1 are coarser than west/central Steller source labels. The illustrative B/PB/QB comparisons use rounded original published values and cannot prove exact native equivalence. Full original native recovery search and rejected CGOA/EBS/ECOTRAN candidates are recorded separately in the regional recovery evidence.

## Validation

Maintained validate.py returned two errors (native detritus fate0+0 rows48/49) and one warning (49missing TL). These source states were retained. Consumer known-entry diet sums range {summary['known_diet_sum_range'][0]} to {summary['known_diet_sum_range'][1]}; all46columns include raw blank cells, so complete canonical source sums remain unknown. No diet normalization occurred. Fleet routing sums1; biological source DET routing rows sum0, with unknown export.

All {len(nativecheck['checks'])} native-to-canonical checks passed, including group labels, type codes, parameter literal/missing masks, catches, fates, every represented consumer diet cell, source native table companions and original source hashes. Standard/companion workbook reconstruction checked{roundtrip['cells_checked']}cells; numeric and missing-mask match={roundtrip['numeric_value_and_missing_mask_match']}, exact match={roundtrip['exact_value_and_missing_mask_match']}, max numeric difference={roundtrip['max_numeric_difference']}. Exact group31 import name differs intentionally via explicit crosswalk; the standard reconstruction retains the literal alias.

## Mass balance

The maintained converter's source checker ran unchanged. It reported **0errors,46indeterminate,11warnings,1note**; full outcomes are inMASS_BALANCE.md. This is not evidence of a balanced model: unknown EE and sparse diet inputs prevent complete source checking. Its producer input-count warning and ten marine-mammal/seabird P/Q warnings are retained, without repairs. No PPRCalculator or native Rpath balance was run, and no SPPR/regional arithmetic was computed.

## Source-to-loader check

ModelData schema admission={loader['admitted']}. It appends a synthetic diet_import group and performs supported runtime accounting. Native unknown EE and DET biomass remain source unknowns. The full source-facing fields, loader parameter view, unavailable counts and fleet-routing metadata are retained in loader_schema_check.json and loader_parameter_view.csv. Admission does not establish numerical readiness or researcher approval. No source/default replacement was promoted from the loaded view.

The source_to_loader_ledger.json audit compares 490 scalar fields and 2,254 diet cells. All source diet values and missing masks match the loaded matrix. The 47 scalar differences are source-blank DetInput values represented as runtime 0, consistent with explicit native Rpath runtime behavior. All 49 unknown EE values and both unknown detritus biomasses remain unknown. Runtime diet and fate matrices are separate evidence CSVs. The generated mass-balance check's generic “BA unknown” heading does not describe this model's BA: all 49 BA values are known, and its listed indeterminate reasons concern unknown diet cells.
'''
    (ev/'REPORT.md').write_text(report,encoding='utf-8')
    source_manifest={'schema_version':1,'paper_folder_id':'GOA-2020','citation':CITATION,'doi':'10.1016/j.ecolmodel.2020.109074','publication_year':2020,'available_online':'2020-05-25','source_identity_verified_from':'NOAA article full text p1 and official Rpath source documentation','models':[MODEL_ID],
      'files':[{'path':f'models/{MODEL_ID}/inputs/'+x['path'],**{k:v for k,v in x.items() if k!='path'}} for x in source['files']],
      'remote_article':{'url':PDF,'record_url':'https://repository.library.noaa.gov/view/noaa/30747','local_availability':'missing','acquisition_status':'download403; web-indexed fulltext read; screenshot cache miss','role':'publication identity, area, aggregation method and contextual membership'},
      'limitations':['Source CSVs identify official aggregate; no exact numeric equality to2007full model is claimed.','RDA object archived with original hash; CSV extraction follows official builder.']}
    dump(PAPER/'source_manifest.json',source_manifest)
    # Exact recovery record: distinct candidates are not silently substituted.
    recovery=RUN/'inputs/recovery'
    filefacts=[{'path':relative(p,RUN),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(recovery.iterdir()) if p.is_file()]
    dump(RUN/'qa/native_recovery.json',{'schema_version':1,'date':'2026-11-14','requested_original':'Aydin2007GOA1990–1994,291840km²','exact_original_native_recovered':False,
      'official_aggregate_extracted':{'model_id':MODEL_ID,'paper_id':'GOA-2020','commit':COMMIT,'canonical_path':relative(MODEL/'model.json',ROOT),'canonical_sha256':sha(MODEL/'model.json')},
      'sources_read':[
       {'url':'https://repository.library.noaa.gov/view/noaa/22894','finding':'Official2007record exposes publicationPDF; exact nativeGOA file not recovered.'},
       {'url':'https://faculty.washington.edu/kerim/toolshop/','finding':'Public author workshop archive containsCGOA/GLOBEC andEBS models. CGOA_PathData.h identifiesCGOA_GLOBEC_TMagg.evv,138total=119living+5dead+14gear,2010workshop strings. Pollock biomasses/BA differ fromfullGOA. Not substituted.'},
       {'url':'https://www.bco-dmo.org/dataset/546765','finding':'2019ECOTRANexpandedCentralGOA model; not proven exact2007fullGOA; not used as numeric input.'},
       {'url':'https://noaa-edab.github.io/Rpath/reference/Ecosense.GOA.html','finding':'Official49biological+1fleet aggregate fromWhitehouse&Aydin2020; notesoriginalAydin2007andno stanzas.'},
       {'url':PDF,'finding':'Article confirms291840km², aggregation methods andTable1membership. Fulltextindexed, localdownload403, screenshotcachemiss.'}],
      'downloaded_files':filefacts,'contacts':'No author messages sent.','recovery_limits':'Bounded search did not recover exact original native fullGOA. Aggregate extraction separately authorized, not a correction or replacement.'})
    shutil.copy2(RUN/'qa/native_recovery.json',ev/'native_recovery.json')
    artifacts=[]
    def present(role,path):artifacts.append({'role':role,'path':relative(path,ev),'sha256':sha(path),'availability':'present'})
    present('canonical_model',MODEL/'model.json');present('model_notes',MODEL/'model_notes.md');present('provenance',MODEL/'inputs/provenance.json')
    present('report',ev/'REPORT.md');present('source_manifest',PAPER/'source_manifest.json')
    for name in SOURCE_PATHS:present('native_source',MODEL/'inputs/native'/name)
    for p in sorted((MODEL/'extracted_tables').iterdir()):
        if p.is_file():present('standard_import',p)
    for p in sorted((MODEL/'extracted_tables/companions').iterdir()):present('source_companion',p)
    for p in sorted(ev.iterdir()):
        if p.is_file() and p.name not in ['evidence_index.json','completeness.json','REPORT.md']:
            present({'native_canonical_verification.json':'native_fidelity','SOURCE_FIDELITY_CHECK.json':'roundtrip','loader_schema_check.json':'schema_load','MASS_BALANCE.md':'source_mass_balance','reconstructed.xlsx':'reconstruction'}.get(p.name,'supporting_evidence'),p)
    for p in [RUN/'code/aggregated_extract.py',RUN/'code/aggregated_finalize.py',RUN/'code/aggregated_audit_loader.py']:present('reproduction_code',p)
    artifacts += [
      {'role':'article_pdf','availability':'missing','reason':'403 on local download; full text read through web index; nativeCSV is numerical source.','acquisition_status':'attempted'},
      {'role':'Table1_visual_review','availability':'failed','reason':'PDF screenshot returned cache miss; crosswalk markedtext-only/contextual.','acquisition_status':'attempted'},
      {'role':'PPRCalculator_and_SPPR','availability':'inapplicable','reason':'Authorized extraction/comparison scope only.','acquisition_status':'not_requested'},
      {'role':'researcher_approval','availability':'inapplicable','reason':'Extraction does not imply researcher signoff.','acquisition_status':'not_requested'}]
    index={'schema_version':1,'run_id':RUN.name,'region_id':'LME_002','model_id':MODEL_ID,'variant_id':'official_Rpath_Ecosense.GOA_unbalanced_inputs',
      'source_identity':{'citation':CITATION,'commit':COMMIT},'computational_input_identity':{'path':'../../model.json','sha256':sha(MODEL/'model.json'),'scope':'schema-load only'},
      'methods':['maintained writer','maintained validator','maintained converter and source mass-balance checker','native-to-canonical fidelity','reconstruction roundtrip','ModelData constructor only'],
      'required_roles':['canonical_model','model_notes','provenance','report','native_source','standard_import','source_companion','native_fidelity','roundtrip','schema_load','source_mass_balance','reconstruction','reproduction_code'],
      'artifacts':artifacts,'reconciliation':{'native_values_and_missingness':nativecheck['all_passed'],'roundtrip_numeric_and_missingness':roundtrip['numeric_value_and_missing_mask_match']},
      'limitations':'Inventory complete for native numerical extraction; article PDF/visual crosswalk remains unavailable. No scientific approval or readiness is asserted.'}
    dump(ev/'evidence_index.json',index)
    proc=subprocess.run([sys.executable,str(ROOT/'tools/skills/paper-to-ppr/scripts/check_evidence.py'),str(ev/'evidence_index.json'),'--output',str(ev/'completeness.json')],capture_output=True,text=True,encoding='utf-8',errors='replace')
    (RUN/'qa/aggregated_evidence_check.log').write_text(proc.stdout+proc.stderr,encoding='utf-8')
    assert proc.returncode==0,proc.stdout+proc.stderr
    # Only own redundant staging representations are removed after checked handoff.
    stage=(RUN/'outputs/aggregated_stage').resolve();allowed=(RUN/'outputs').resolve()
    assert stage.parent==allowed and stage.name=='aggregated_stage'
    if stage.exists():
        assert not any(p.is_symlink() for p in stage.rglob('*'))
        shutil.rmtree(stage)
    writer=RUN/'outputs/aggregated_writer_input.json'
    if writer.exists():writer.unlink()
    dump(RUN/'qa/aggregated_dispositions.json',{'removed':['outputs/aggregated_stage','outputs/aggregated_writer_input.json'],'reason':'Redundant writer/converter model representations removed after native fidelity, reconstruction and evidence checks; sole canonical model remains.','canonical_path':relative(MODEL/'model.json',ROOT),'canonical_sha256':sha(MODEL/'model.json')})
    print(json.dumps({'canonical':str(MODEL/'model.json'),'sha256':sha(MODEL/'model.json'),'evidence_complete':True,'source_validator':'2source fate errors;1missingTL warning','source_mass_balance':'0errors;46indeterminate;11warnings;1note','schema_admitted':loader['admitted'],'native_checks':len(nativecheck['checks'])},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
