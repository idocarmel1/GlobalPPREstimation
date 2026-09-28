"""Serialize central/map adoption and verify selected-pair and metadata preservation."""
from pathlib import Path
import sys,json,math,collections
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'tools'),str(HERE.parent/'regional_ge_integration_20260928')]
from workbooks import *
from xml_audit_reader import read_book
import update_project,original_atlas_data,build_html,verify_html
update_project.read_book=read_book;original_atlas_data.read_book=read_book;verify_html.read_book=read_book
from regional import result_hash

def canonical(rr):return digest_tables(sorted([list(r.items()) for r in rr],key=repr))

def main():
    app=json.loads((HERE/'APPLICATION_VERIFICATION.json').read_text(encoding='utf-8'))
    plans=json.loads((HERE/'reviewed_plans.json').read_text(encoding='utf-8'))['pairs']
    documented=sum(str(p.get('action','')).startswith('document') for pair in plans for p in pair['proposals'])
    new_or_revised=sum(len(pair['proposals']) for pair in plans)-documented
    units={r['unit_id'] for r in app};assert len(units)==23
    project=ROOT/'Project.xlsx'
    assert sha(project)==sha(HERE/'baseline/Project.xlsx'),'Project changed since baseline; merge fresh edits before adoption'
    baseline=read_book(project)
    oldregions=records(baseline,'Regions & status','Regions')
    paths=[ROOT/r['workbook'] for r in oldregions if r['unit_id'] in units]
    for a in app:
        p=ROOT/'regions'/a['unit_id']/(a['unit_id']+'.xlsx')
        assert sha(p)==a['prepared_sha256']
    print('Updating central workbook with 23 reviewed selected pairs',flush=True)
    update_project.update(ROOT,paths)
    current=read_book(project)
    for s,t in [('Papers','Papers'),('Models & coverage','Models')]:
        assert canonical(records(baseline,s,t))==canonical(records(current,s,t)),s
    for s,blocks in baseline.items():
        for table,(header,_) in blocks.items():
            if 'unit_id' not in header:continue
            old=[r for r in records(baseline,s,table) if r.get('unit_id') not in units]
            new=[r for r in records(current,s,table) if r.get('unit_id') not in units]
            assert canonical(old)==canonical(new),(s,table,'unrelated records changed')
    newregions={r['unit_id']:r for r in records(current,'Regions & status','Regions')}
    cells=0
    for r in oldregions:
        if r['unit_id'] not in units:
            assert sha(ROOT/r['workbook'])==r['sha256'],(r['unit_id'],'unselected workbook changed')
            continue
        unit=r['unit_id'];p=ROOT/r['workbook'];b=read_book(p);o=validate_region(b,p)
        assert overview(b)['calculation_result_sha256']==result_hash(b)
        assert o['selected_model_id']==r['selected_model_id'] and o['selection_rationale']==r['selection_rationale']
        assert newregions[unit]['sha256']==sha(p)
        for sheet in ['Classic PPR','PPR']:
            expected=records(b,sheet,'Annual')
            actual=[{k:v for k,v in x.items() if k!='unit_id'} for x in records(current,'Regional PPR','Annual') if x['unit_id']==unit and bool(x['model_id'])==(sheet=='PPR')]
            assert canonical(expected)==canonical(actual),(unit,sheet)
            cells+=len(actual)*70
        npp=[{k:v for k,v in x.items() if k!='unit_id'} for x in records(current,'Regional NPP','NPP') if x['unit_id']==unit]
        assert canonical(npp)==canonical(records(b,'NPP','NPP'))
        print('Central verified',unit,flush=True)
    build_html.build(project,ROOT/'interactive_map/index.html')
    verify_html.verify(project,ROOT/'interactive_map/index.html')
    report={'selected_pairs_reviewed':23,'pairs_with_allocation_ledger':sum(x['adopted_taxa']>0 for x in app),'taxon_pair_allocations_recorded':sum(x['adopted_taxa'] for x in app),'unselected_workbooks_unchanged':len(oldregions)-23,'central_annual_cells_verified':cells,'project_sha256':sha(project),'map_sha256':sha(ROOT/'interactive_map/index.html'),'trends_sha256':sha(ROOT/'interactive_map/trends.html'),'checks':['Exact central Papers and Models metadata preserved','All unrelated central rows and 343 unselected workbooks preserved','All selected model IDs/rationales/source coefficients/diagnoses preserved','Catch/ClassicPPR/NPP preserved in every regional workbook','Previously numeric source scopes retained','Independent weighted SPPR and annual method PPR checks pass','Saved regional hash checks and central numerical equality pass'],'pairs':app}
    report.update(new_or_revised_taxon_pair_allocations=new_or_revised,existing_allocations_documented=documented)
    (HERE/'FINAL_VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# Selected-model size/stage allocation results','','Reviewed all 23 selected model-region pairs. Online primary-source searches preceded adoption of model-catch proxies. No compatible observed whole-region caught-mass shares were adopted. All adopted weights remain provisional assumptions; no model diagnosis was upgraded.','',f"Recorded {report['taxon_pair_allocations_recorded']} taxon-pair allocations across {report['pairs_with_allocation_ledger']} pairs, including existing allocations preserved and relabeled. LME026 retains four blocked mapping proposals because usable groups/SPPR are absent.",'','Coverage below uses 2019 total catch, GE, all source categories, native unidentified treatment. Assumed coverage includes previously present assumptions; it is not simply the gain. PPR is tonnes carbon equivalent. Regions overlap; do not sum them.','','| Region | Taxa recorded | Before coverage | After coverage | Gain (pp) | Catch dependent on these assumptions | Before PPR (tC) | After PPR (tC) |','|---|---:|---:|---:|---:|---:|---:|---:|']
    fmt=lambda v:('unavailable' if v is None else f'{v:,.2f}')
    for x in sorted(app,key=lambda x:x['unit_id']):
        a,b=x['before'],x['after'];gain=b['coverage_pct']-a['coverage_pct'] if b['coverage_pct'] is not None and a['coverage_pct'] is not None else None
        assumed=100*x['assumed_catch']/b['total_catch'] if finite(x['assumed_catch']) and b['total_catch'] else None
        lines.append(f"| {x['unit_id']} | {x['adopted_taxa']} | {fmt(a['coverage_pct'])}% | {fmt(b['coverage_pct'])}% | {fmt(gain)} | {fmt(assumed)}% | {fmt(a['ppr_tC'])} | {fmt(b['ppr_tC'])} |")
    lines+=['',f'{new_or_revised} taxon-pair allocations are new or revised; {documented} document existing weights.','', '## Interpretation and retained gaps','','- Source model catch mixtures are fixed historical proxies, not measured annual regional size composition. Pool-to-species and catch-basis transfers are recorded.','- Baby skipjack source catch is missing, not observed zero; assumed uncaught infant stages retain both raw sentinel and explicit effective-zero assumption.','- LME052 pollock replaces biomass weighting with an explicit adult-only assumption. Its numerical cutoff remains unknown. Broader Gadidae/Gadiformes taxonomic weights remain flagged for separate review.','- LME003/014/035/036/038 existing allocations are documented and preserved numerically. Geographic strata, distinct species with size-like common names, ambiguous aliases and unsupported mixed guilds remain unresolved.','- LME026 has mapping evidence but no usable numerical SPPR; no PPR was fabricated.','- Existing model diagnostic problems remain visible in workbooks and the map. Improved coverage does not validate models.','','## Evidence and verification','','Per-pair source proposals and online-search audits are in pacific/, lme_west/ and lme_east/. reviewed_plans.json records normalized adoption inputs. Active candidate ledgers and impact tables live in the regional workbooks. Baseline bytes and source hashes are retained in baseline/ and baseline_manifest.json.','',f"Verified {cells:,} central annual cells against the saved regional outputs, plus NPP, source metadata, selections, all existing diagnosis tables and 343 unselected regional workbooks. FINAL_VERIFICATION.json records resulting hashes. The source-scope recalculation regression has a dedicated passing test.",'','Central workflow updated: tools/skills/original_skill_resources/combined-src/SKILL.md and references/size-stage-allocations.md.']
    (HERE/'RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Consolidated, rebuilt and verified',flush=True)

if __name__=='__main__':main()
