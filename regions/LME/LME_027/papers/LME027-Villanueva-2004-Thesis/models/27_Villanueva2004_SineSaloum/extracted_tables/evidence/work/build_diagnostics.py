"""Record the source admission blocker without constructing a surrogate model."""
from pathlib import Path
import json,hashlib,datetime
C=Path(__file__).resolve().parents[1];ROOT=C.parents[3]
def write(path,value):
 p=C/path;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
reason=('Thesis Table 6.5 (PDF138, printed114) identifies source group20 as Epinephelus aeneus*, '
 'while Annex II.A (PDF235–236, printed211–212) identifies row20 as Hemichromis fasciatus. '
 'Table3.3 (PDF83, printed59) places Epinephelus/Lutjanus bottom predators and Hemichromis in separate compartments. '
 'No source-specific numerical crosswalk or native release resolves this mismatch. Ordinal equality alone is not biological identity.')
admission={'model_id':C.name,'variant_id':'thesis_1991-1992_Table6_5_AnnexIIA','status':'BLOCKED_SOURCE_IDENTITY',
 'reason':reason,'constructor_executed':False,'source_preserved':True,
 'computational_input_created':False,'loaded_state_created':False,
 'unapproved_changes':[], 'remaining_missing_inputs':['source-specific GS/assimilation values','biomass accumulation','complete migration/import and detritus-routing conventions'],
 'resolution_group27':'Table3.3 identifies Liza grandisquamis and Liza falcipinnis within the same mullet pool; representative-name difference retained.',
 'methods':['GE','TE','With Egestion'],'no_numerical_substitution':'No chapter38group values, donorSPPR or EcoBase118 mappings were used to complete the thesis.'}
write('computational_inputs/ADMISSION.json',admission)
reports={m:{'status':'NOT_RUN','reason':reason,'stage':'pre-constructor source admission','diagnostic_return':None,
 'rho_living':None,'b':None,'detritus_sppr':None,'negative_sppr_entries':None,'matrix':None,'coefficients':None} for m in admission['methods']}
write('diagnostics/direct_reports.json',reports)
write('diagnostics/summary.json',reports)
write('diagnostics/loaded_state.json',{'availability':'missing','reason':'Constructor deliberately not executed because source biological identities cannot be joined defensibly.','state':None})
write('diagnostics/transformation_ledger.json',{'source_to_computational_changes':[],'normalization_executed':False,'defaults_applied':False,'repairs_applied':False})
write('diagnostics/execution_evidence.json',{'record_date':'2026-10-03','constructor_executed':False,'diagnostics_executed':False,'admission':'../computational_inputs/ADMISSION.json',
 'canonical_input':'../model.json','method_options':None,'settings':None,'reason':reason,
 'engine_hashes':{n:hashlib.sha256((ROOT/'tools/scientific_code/PPREstimation'/n).read_bytes()).hexdigest() for n in ['ModelData.py','PPRCalculator.py','utils.py']}})
(C/'diagnostics/DIRECT_DIAGNOSTICS.md').write_text('# Thesis candidate direct diagnostics\n\nGE, TE and With Egestion are **NOT_RUN**.\n\n'+reason+'\n\nNo constructor, solver, matrix sign check, convergence check or budget diagnostic was performed. Numeric fields are unknown, not zero. Group27 can be crosswalked to the same mullet pool; group20 remains unresolved. Missing GS/BA and routing would require an explicit computational convention even after identity is resolved.\n',encoding='utf8')
print('All three methods recorded NOT_RUN at source admission; no source values or active results changed.')
