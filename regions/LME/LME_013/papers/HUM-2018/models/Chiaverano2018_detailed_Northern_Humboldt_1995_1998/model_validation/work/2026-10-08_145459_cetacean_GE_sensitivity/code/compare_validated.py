from pathlib import Path
import json,csv,sys,math,hashlib
RUN=Path(__file__).resolve().parents[1];MODEL=Path(__file__).resolve().parents[4]
ROOT=next(p for p in MODEL.parents if (p/'Project.xlsx').exists());sys.path.insert(0,str(ROOT))
from tools.project_core.workbooks.workbooks import read_book,records,overview,sha
from tools.project_core.validation.researcher_review import approved_review
from tools.project_core.registry.discovery import resolve_model,region_directory
for f in ['inputs','outputs','qa']: (RUN/f).mkdir(exist_ok=True)
p=read_book(ROOT/'Project.xlsx',sheets=['Models & coverage']);projecthash=sha(ROOT/'Project.xlsx')
chosen={'LME_028':{'Baleines':True,'Dauphins':True},'LME_032':{'Marine Mammals':True},
 'LME_036':{'Other mammals':False},'LME_047':{'Marine mammals':True}}
out=[];reviewed=[]
for r in records(p,'Models & coverage','Models'):
    if r.get('researcher_review_status')!='Validated by researcher':continue
    region=region_directory(ROOT,r['unit_id']);model=resolve_model(region,r['model_id'])
    assert model==(ROOT/r['model_path']).resolve()
    b=read_book(region/(r['unit_id']+'.xlsx'),sheets=['Overview','Selected model groups'])
    review=approved_review(ROOT,r,b);assert review
    reviewed.append(dict(unit_id=r['unit_id'],model_id=r['model_id'],review_fresh=True,
        model_path=model.relative_to(ROOT).as_posix(),model_sha256=sha(model),
        region_path=(region/(r['unit_id']+'.xlsx')).relative_to(ROOT).as_posix(),
        region_sha256=sha(region/(r['unit_id']+'.xlsx')),review_report_sha256=r['validation_report_sha256'],
        relevant_groups=list(chosen.get(r['unit_id'],{}))))
    source=json.loads(model.read_text(encoding='utf-8-sig'))
    for g in source['group']:
        if g['group_name'] not in chosen.get(r['unit_id'],{}):continue
        name=g['group_name'];pb=float(g['pb']);qb=float(g['qb']);ge=pb/qb
        cg=next(v for v in records(b,'Selected model groups','Groups') if v['group_name']==name)
        coef=[v for v in records(b,'Selected model groups','Group SPPR') if v['group']==name and v['method']=='new_GE']
        out.append(dict(unit_id=r['unit_id'],model_id=r['model_id'],group_id=int(g['group_seq']),
            group_name=name,PB=pb,QB=qb,GE=ge,explicit_source_GE=g.get('ge'),
            strict_cetacean_membership=chosen[r['unit_id']][name],source_membership=g.get('taxon_descr'),
            researcher_excluded=name in review['excluded_group_ids'],
            SPPR_GE={v['scope']:v['sppr'] for v in coef},coefficient_method='new_GE',
            source_model_sha256=sha(model),model_path=model.relative_to(ROOT).as_posix(),
            configuration={k:v for k,v in overview(b).items() if k in ['det_collapse_mode','sppr_configuration','diagnostic_manifest','computational_runtime_evidence']}))
        print(r['unit_id'],name,'GE',ge,'SPPR',out[-1]['SPPR_GE'],'excluded',out[-1]['researcher_excluded'],flush=True)
cohorts={}
for label,cohort in [('strict_cetaceans',[r for r in out if r['strict_cetacean_membership']]),('including_other_mammals_proxy',out)]:
    means={s:math.fsum(r['SPPR_GE'][s] for r in cohort)/len(cohort) for s in ['all','inner','PP']}
    by_model={}
    for r in cohort:by_model.setdefault(r['model_id'],[]).append(r)
    cohorts[label]=dict(groups=len(cohort),models=len(by_model),mean_GE=math.fsum(r['GE'] for r in cohort)/len(cohort),
        mean_SPPR_GE=means,model_equal_mean_GE=math.fsum(math.fsum(r['GE'] for r in rows)/len(rows) for rows in by_model.values())/len(by_model),
        model_equal_mean_SPPR_GE={s:math.fsum(math.fsum(r['SPPR_GE'][s] for r in rows)/len(rows) for rows in by_model.values())/len(by_model) for s in ['all','inner','PP']},
        approved_group_estimates=sum(not r['researcher_excluded'] for r in cohort))
assert sha(ROOT/'Project.xlsx')==projecthash
report=dict(status='PASS',cohort_definition='Currently registered and freshness-verified researcher validated models; cetacean groups identified by source taxonomy; pinnipeds excluded.',
    averaging='Arithmetic mean across group-level observations; model-equal means separately retained.',
    project_sha256=projecthash,reviewed_models=reviewed,groups=out,cohorts=cohorts,
    caveat='All cetacean and proxy groups were explicitly excluded from displayed PPR by the researcher; these are saved model coefficients, not approved cetacean benchmarks.')
(RUN/'outputs/validated_cetacean_comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('COHORT_MEANS',json.dumps(cohorts,indent=2),flush=True)
