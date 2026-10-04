"""Bounded EEZ_598 source/runtime diet audit. Writes audit evidence only."""
from pathlib import Path
from decimal import Decimal as D
import hashlib,json,csv,shutil,sys,subprocess,zipfile,xml.etree.ElementTree as ET
import pymupdf

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
REG=ROOT/'regions/EEZ_598'
MID='941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)'
MODEL=REG/'models'/MID
SELECTED=MODEL/(MID+'.json')
SOURCE=ROOT/'regions/EEZ_941/papers/WCP-2007/extraction_evidence'
PREDECESSOR=ROOT/'regions/EEZ_941/models/941_200701_WCPO_Warm_Pool_Final_(mixed_periods)'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x): p.write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')

def prepare():
    protected={rel(p):sha(p) for p in REG.rglob('*') if p.is_file() and OUT not in p.parents}
    write(OUT/'protected_before.json',protected)
    settings=read(MODEL/'diagnostic_evidence/experiment_PROVENANCE.json')['loader_settings']
    write(OUT/'loader_settings.json',settings)
    roots={'historical':PREDECESSOR/'diagnostics/executed_code','current':ROOT/'tools/scientific_code/PPREstimation'}
    manifest={}
    for label,base in roots.items():
        dest=OUT/(label+'_executed_code');dest.mkdir(exist_ok=True)
        for name in ['ModelData.py','PPRCalculator.py','utils.py']:
            p=base/name;before=sha(p);shutil.copyfile(p,dest/name);assert sha(p)==before==sha(dest/name)
            manifest[label+'/'+name]={'source_path':rel(p),'before_sha256':before,'pinned_path':rel(dest/name)}
    write(OUT/'executing_code_hashes_before.json',manifest)
    for label in roots:
        r=subprocess.run([sys.executable,str(OUT/'capture_runtime.py'),str(OUT/(label+'_executed_code')),str(SELECTED),str(OUT/(label+'_runtime')),str(OUT/'loader_settings.json')],capture_output=True,text=True,encoding='utf-8')
        (OUT/(label+'_capture_stdout.txt')).write_text(r.stdout+'\n'+r.stderr,encoding='utf-8')
        assert r.returncode==0,(label,r.stderr)
    write(OUT/'executing_code_hashes_after_load.json',{k:{**v,'after_sha256':sha(ROOT/v['source_path']),'pinned_sha256':sha(ROOT/v['pinned_path'])} for k,v in manifest.items()})

def source_audit():
    a=read(SELECTED);gmap={g['group_seq']:g for g in a['group']}
    extraction=read(SOURCE/'final_extraction.json');evidence=read(SOURCE/'cell_evidence.json')
    pdf=REG/'papers/WCP-2007/download-0adcf55e.pdf'
    assert sha(pdf)==extraction['source_identity']['source_sha256']
    doc=pymupdf.open(pdf)
    # Independently verify every retained Table 4 final token against the actual local PDF word coordinates.
    pagewords={}
    for page in [12,13]:
        p=doc[page-1]
        pagewords[page]=[(w[4],list(pymupdf.Rect(w[:4])*p.rotation_matrix)) for w in p.get_text('words')]
    verified=[]
    for i,c in enumerate(evidence):
        if c['table']!=4 or not c['column'].endswith('|Final'): continue
        matched=[w for w in pagewords[c['page']] if w[0]==c['text'] and max(abs(x-y) for x,y in zip(w[1],c['bbox']))<1e-6]
        verified.append({'cell_evidence_index':i,'verified_in_primary_pdf':bool(matched)})
    assert all(x['verified_in_primary_pdf'] for x in verified)
    lookup={(c['row'],c['column']):(i,c) for i,c in enumerate(evidence) if c['table']==4 and c['column'].endswith('|Final')}
    ledger=[];differences=[];sums=[]
    for gi,g in enumerate(a['group']):
        seq=g['group_seq'];native={c['prey_seq']:(j,c) for j,c in enumerate((g.get('diet_descr') or {}).get('diet') or [])}
        sourcecells=extraction['diet'].get(seq,{})
        total=D(0)
        for prey in a['group']:
            ps=prey['group_seq'];source=sourcecells.get(ps);entry=native.get(ps)
            adopted=entry[1]['proportion'] if entry else None
            info=lookup.get((prey['group_name'],g['group_name']+'|Final'))
            if source is not None:
                assert info and info[1]['text']==source
                same=source==adopted
                if not same:differences.append([seq,ps,source,adopted])
                total+=D(source)
                status='printed_numeric'
            elif adopted is not None:
                assert D(adopted)==0,(seq,ps,adopted)
                same=True;status='absent_source_link_encoded_zero_for_detritus_routing'
            else:
                same=True;status='absent_link_in_sparse_source' if seq in extraction['diet'] else 'inapplicable_nonfeeding_group'
            ledger.append({'consumer_seq':seq,'consumer':g['group_name'],'prey_seq':ps,'prey':prey['group_name'],'source_literal':source,'adopted_literal':adopted,'source_status':status,'exact_equal':same,'primary_pdf':rel(pdf),'primary_pdf_sha256':sha(pdf),'pdf_page':info[1]['page'] if info else (12 if int(seq)<=14 else 13) if seq in extraction['diet'] else None,'table':4 if seq in extraction['diet'] else None,'source_display_bbox':info[1]['bbox'] if info else None,'source_ledger_pointer':'/'+str(info[0]) if info else None,'selected_json_pointer':f'/group/{gi}/diet_descr/diet/{entry[0]}/proportion' if entry else None,'accepted_diet_correction':None,'researcher_review_status':'not_established_by_this_audit'})
        imp=g.get('diet_imp');sourceimp=sourcecells.get('import','0')
        assert imp==sourceimp=='0'
        ledger.append({'consumer_seq':seq,'consumer':g['group_name'],'prey_seq':'import','prey':'external diet import','source_literal':'0','adopted_literal':imp,'source_status':'explicit_source_no_living_import_convention_p7','primary_pdf':rel(pdf),'primary_pdf_sha256':sha(pdf),'pdf_page':7,'table':None,'source_display_bbox':None,'selected_json_pointer':f'/group/{gi}/diet_imp','exact_equal':True,'accepted_diet_correction':None,'researcher_review_status':'not_established_by_this_audit'})
        sums.append({'consumer_seq':seq,'consumer':g['group_name'],'feeding':seq in extraction['diet'],'source_prey_sum':str(total),'diet_import_literal':imp,'source_diet_plus_import_sum':str(total+D(imp)),'selected_prey_sum':str(sum((D(v[1]['proportion']) for v in native.values()),D(0))),'missing_import':False,'missing_positive_diet_cells':False,'review_status':'not_established_by_this_audit','native_unknown_or_zero_note':'No normalization inference from the sum; exact source cells and restoration history determine status.'})
    aliases={rel(p):sha(p) for p in [SELECTED,MODEL/'model.json',MODEL/'diagnostic_evidence/941_200701_WCPO_Warm_Pool_Final_(mixed_periods).json']}
    assert len(set(aliases.values()))==1
    predecessor=read(PREDECESSOR/'model.json')
    assert [(g['diet_descr'],g['diet_imp']) for g in predecessor['group']]==[(g['diet_descr'],g['diet_imp']) for g in a['group']]
    write(OUT/'cell_ledger.json',ledger)
    write(OUT/'consumer_sums.json',sums)
    write(OUT/'primary_coordinate_verification.json',{'pdf_path':rel(pdf),'pdf_sha256':sha(pdf),'rotation_convention':'PyMuPDF word bboxes transformed through page.rotation_matrix to source display points','verified_final_table4_tokens':verified,'all_verified':True})
    write(OUT/'source_comparison.json',{'normalization_status':'verified_unnormalized_source_diet_unchanged','reextraction_required':False,'selected_alias_sha256':aliases,'source_extraction_sha256':sha(SOURCE/'final_extraction.json'),'source_cell_ledger_sha256':sha(SOURCE/'cell_evidence.json'),'predecessor_sha256':sha(PREDECESSOR/'model.json'),'printed_diet_differences':differences,'printed_nonzero_cell_count':len(verified),'full_matrix_ledger_rows':len(ledger),'source_fidelity_limits':'Table 4 printed Final proportions and p7 no-import convention verified; this does not validate source biology or native multistanza balance. Absent sparse cells are absent links, not invented printed zeros. Source extraction precedes accepted PB/EE scenario.','conversion_history_path':rel(PREDECESSOR/'extracted_tables/converter_to_canonical_audit.json'),'restoration_builder_path':rel(SOURCE/'build_artifacts.py'),'scenario_builder_path':rel(PREDECESSOR/'balance_investigation/correction_scenarios/run_scenarios.py')})
    # Capture Word scientific text read-only; no document editing, saving or rendering.
    word=REG/('Model_validation_'+MID+'.docx')
    xml=ET.fromstring(zipfile.ZipFile(word).read('word/document.xml'))
    ns='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    paras=[''.join(t.text or '' for t in p.iter(ns+'t')) for p in xml.iter(ns+'p')]
    selectedparas=[s for s in paras if any(k in s.lower() for k in ['diet','normal','fixed','1.412','2.530','researcher','accepted','manual','p/b','p/b'])]
    write(OUT/'researcher_override_evidence.json',{'overview_authority':rel(REG/'EEZ_598.xlsx')+' / Overview','word_path':rel(word),'word_sha256':sha(word),'read_only_paragraphs':selectedparas,'accepted_decision_path':rel(MODEL/'SELECTION_AND_PROVENANCE.json'),'accepted_decision':read(MODEL/'SELECTION_AND_PROVENANCE.json'),'accepted_parameter_values_preserved':[{'seq':g['group_seq'],'pb':g['pb'],'ee':g['ee'],'biomass_accum':g['biomass_accum'],'biomass_accum_rate':g['biomass_accum_rate']} for g in a['group'] if g['group_seq'] in ['11','12']],'diet_specific_correction_found':False})

if __name__=='__main__':
    prepare();source_audit()
    print('EEZ_598 source audit and pinned loader capture complete.')
