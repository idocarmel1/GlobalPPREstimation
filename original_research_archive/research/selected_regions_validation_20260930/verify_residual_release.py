"""Coordinator verification after an explicitly released bounded reporting-scope review."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'));import workbooks as W;import regional as R
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
U=sys.argv[1];assert U in ['LME_014','LME_026','LME_036']
r=json.loads((BASE/f'work/qa_residual_fish_scope/{U}_release.json').read_text(encoding='utf-8'))
for k in ['final_workbook','final_report','final_appendix','final_handoff']:assert sha(ROOT/r[k]['path'])==r[k]['sha256']
p=ROOT/r['final_workbook']['path'];book=W.read_book(p);o=W.validate_region(book,p);assert R.result_hash(book)==o['calculation_result_sha256'];ev=(ROOT/r['final_handoff']['path']).parent
groups={g['group_name']:int(g['seq']) for g in W.records(book,'Selected model groups','Groups')};matching=W.records(book,'PPR','Matching')
excluded={'LME_014':{4,27,28},'LME_026':{13,43,44,45,46,47},'LME_036':{32,33}}[U]
checks=[]
for t in ['Marine fishes not identified','Marine finfishes not identified','Marine groundfishes not identified','Marine pelagic fishes not identified']:
 rows=[x for x in matching if x['taxon']==t];ids={groups[x['group']] for x in rows if x.get('group')};assert not(ids & excluded),(U,t,ids & excluded)
 if U=='LME_014' and rows and t!='Marine groundfishes not identified':
  assert any(groups[x['group']]==18 and x['weight']==0 for x in rows),'Genuine source-zero candidate lost'
 checks.append({'taxon':t,'candidate_ids':sorted(ids),'excluded_cartilaginous_ids':sorted(excluded),'weight_sum':sum(x['weight'] or 0 for x in rows)})
input_path=BASE/f'verification/final_{U}_residual_scope_input_check.json';inp=json.loads(input_path.read_text(encoding='utf-8'));assert all(x['all_checked_protected_inputs_preserved'] for x in inp)
links=BASE/f'verification/office_links_{U}.json';assert links.exists()
follow=ev/'residual_fish_scope_followup.json';j=json.loads(follow.read_text(encoding='utf-8'));assert j['Office_QA']['status']=='PASS'
proof={'unit_id':U,'released_identities':r,'current_freshness_verified':True,'source_group_membership_checks':checks,'protected_inputs':{'path':input_path.relative_to(ROOT).as_posix(),'sha256':sha(input_path)},'method_exposure':{'path':f'original_research_archive/research/selected_regions_validation_20260930/verification/method_exposure_{U}.json'},'Office_link_check':{'path':links.relative_to(ROOT).as_posix(),'sha256':sha(links)},'regional_followup':{'path':follow.relative_to(ROOT).as_posix(),'sha256':sha(follow)},'root_visual_check':'Representative current Word page and changed appendix row inspected separately in coordinator turn; all pages/changed rows/Sources inspection retained by QA agent.','shared_numeric_freshness_browser':'pending coordinator'}
write(BASE/f'verification/{U}_residual_scope_coordinator_release.json',proof)
progress=BASE/'verification/review_package_progress.json';j=json.loads(progress.read_text(encoding='utf-8'));row=next(x for x in j['regions'] if x['unit_id']==U)
for key,v in [('workbook','final_workbook'),('report','final_report'),('appendix','final_appendix'),('handoff','final_handoff')]:row[key]=r[v]
row['phase']='regional review and bony-fish follow-up complete; shared final reconciliation pending';row['followup']='closed with protected-input/numerical/Office/relocation proof';j['open_followup_regions']=[u for u in j['open_followup_regions'] if u!=U];j['current_packages_fully_released']=j['regional_reviews_released']-len(set(j['open_followup_regions']) | set(j.get('additional_candidate_review_regions', [])));j['status_note']=f"{j['regional_reviews_released']} regional reviews released; {len(j['open_followup_regions'])} bony-fish follow-ups open. Shared final/browser/graph/commit/push verification incomplete; see each region phase for lead progress.";write(progress,j)
print(json.dumps({'unit_id':U,'source_scope_checks':checks,'current_released_packages':j['current_packages_fully_released'],'open_followups':j['open_followup_regions']}))
