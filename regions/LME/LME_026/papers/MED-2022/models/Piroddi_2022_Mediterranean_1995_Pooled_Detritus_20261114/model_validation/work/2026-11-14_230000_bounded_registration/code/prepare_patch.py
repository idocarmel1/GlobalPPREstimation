"""Generate a reviewable shared patch; never install or execute it."""
from pathlib import Path
import difflib
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
RUN=Path(__file__).resolve().parents[1]
p=ROOT/'tools/project_core/maps/build_html.py'
old=p.read_text(encoding='utf-8');new=old
new=new.replace('*,model_ids=None):','*,model_ids=None,model_pairs=None,candidate_rows=()):',1)
new=new.replace('directory,model_ids=model_ids,publish=False)','directory,model_ids=model_ids,model_pairs=model_pairs,candidate_rows=candidate_rows,publish=False)',1)
new=new.replace('directory,model_ids=model_ids)','directory,model_ids=model_ids,model_pairs=model_pairs,candidate_rows=candidate_rows)',1)
new=new.replace('*,model_ids=None,publish=True):','*,model_ids=None,model_pairs=None,candidate_rows=(),publish=True):',1)
needle='    reviews={};registrations=[];review_books={}\n    for unit_id in unit_ids:'
replacement='''    if model_pairs is not None:
        if unit_ids or model_ids:raise ValueError('Use exact model_pairs or legacy unit_ids/model_ids, not both')
        pairs=[tuple(pair) for pair in model_pairs]
        if any(len(pair)!=2 or not all(isinstance(v,str) and v for v in pair) for pair in pairs):raise ValueError('Invalid exact review pair')
    else:
        pairs=[(unit,(model_ids or {}).get(unit)) for unit in unit_ids]
    if not pairs or len(set(pairs))!=len(pairs):raise ValueError('Require unique nonempty review scope')
    candidate_keys=[(item['row']['unit_id'],item['row']['model_id']) for item in candidate_rows]
    if len(set(candidate_keys))!=len(candidate_keys) or not set(candidate_keys)<=set(pairs):
        raise ValueError('Candidate insertions must be unique exact reviewed pairs')
    reviews={};registrations=[];review_books={}
    for unit_id,requested_model_id in pairs:'''
assert needle in new;new=new.replace(needle,replacement,1)
new=new.replace("model_id=(model_ids or {}).get(unit_id) or overview(book).get('selected_model_id');key=(unit_id,model_id)","model_id=requested_model_id or overview(book).get('selected_model_id');key=(unit_id,model_id)",1)
needle='        shutil.copyfile(previous_workbook,expected)\n        for report,unit_id,model_id,seq in registrations:'
replacement='''        shutil.copyfile(previous_workbook,expected)
        from tools.project_core.registry.review_candidates import add_review_candidate
        for item in candidate_rows:
            key=(item['row']['unit_id'],item['row']['model_id'])
            if reviews[key].get('status')!='Disqualified by researcher' or reviews[key].get('review_scope')!='model_source':
                raise ValueError('New review-only candidate requires a source-only disqualification')
            add_review_candidate(Path(expected),root,item['row'],item['canonical_sha256'])
        for report,unit_id,model_id,seq in registrations:'''
assert needle in new;new=new.replace(needle,replacement,1)
# Compile only. Actual imports and publication remain coordinator-owned.
compile(new,str(p),'exec')
(RUN/'outputs/build_html.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/tools/project_core/maps/build_html.py',tofile='b/tools/project_core/maps/build_html.py')),encoding='utf-8')
(RUN/'outputs/build_html.proposed.py').write_text(new,encoding='utf-8')
print('Generated patch; no shared files changed')
