from pathlib import Path
run=Path(__file__).resolve().parents[1];p=run/'code/publish_ices.py';s=p.read_text(encoding='utf-8-sig')
s=s.replace('import argparse, copy, importlib.util, json, re, shutil, sys, tempfile','import argparse, copy, importlib.util, json, re, shutil, sys, tempfile, time')
s=s.replace('from tools.project_core.calculations.coverage import _preserved_inputs','from tools.project_core.workbooks.workbooks import digest_tables')
needle='def authenticate_package():'
helpers='''AUTHORIZED_MAPPING={('Selected model groups','Groups'),('PPR','Matching'),('PPR','Allocation assumptions'),('PPR','Mapping review')}
AUTHORIZED_OUTPUTS={('Overview','Settings'),('Selected model groups','Group SPPR'),('PPR','Annual'),('PPR','Taxon SPPR'),('PPR','Taxon PPR'),('PPR–NPP','Ratios'),*[('Diagnostics',name) for name in ['model_health','EE floor','EE floor groups','Method coverage','Retained adoption']]}

def independent_inputs(book):
    return digest_tables([(sheet,name,data) for sheet,tables in book.items() for name,data in tables.items() if (sheet,name) not in AUTHORIZED_MAPPING|AUTHORIZED_OUTPUTS])

def mapping_identity(book):
    return digest_tables([(sheet,name,book[sheet][name]) for sheet,name in sorted(AUTHORIZED_MAPPING)])

def table_counts(book):
    return {sheet+'/'+name:len(records(book,sheet,name)) for sheet,name in sorted(AUTHORIZED_MAPPING)}

PROGRESS={'stages':[],'started_utc':datetime.now(timezone.utc).isoformat()}
def step(name,action):
    item={'stage':name,'started_utc':datetime.now(timezone.utc).isoformat(),'status':'running'}
    PROGRESS['stages'].append(item);write(RUN/'qa/progress.json',PROGRESS)
    print('['+item['started_utc']+'] '+name,flush=True);started=time.monotonic()
    try:
        result=action();item['status']='passed';return result
    except Exception as error:
        item.update(status='failed',error_type=type(error).__name__,error=str(error));raise
    finally:
        item['elapsed_seconds']=round(time.monotonic()-started,3);write(RUN/'qa/progress.json',PROGRESS)

'''
s=s.replace(needle,helpers+needle)
s=s.replace('_preserved_inputs(current)==_preserved_inputs(book)','independent_inputs(current)==independent_inputs(book)')
s=s.replace("'protected':_preserved_inputs(current),","'protected':independent_inputs(current),'staged_mapping_identity':mapping_identity(book),'old_table_counts':table_counts(current),'staged_table_counts':table_counts(book),")
s=s.replace("require(_preserved_inputs(book)==state['protected'],'Protected regional inputs changed')","require(independent_inputs(book)==state['protected'],'Protected independent/manual tables changed')\n    require(mapping_identity(book)==state['staged_mapping_identity'],'Authorized staged Groups/mapping tables changed')")
s=s.replace("package['module'].apply(publication,PACKAGE)","step('adopt authenticated ICES retained package',lambda:package['module'].apply(publication,PACKAGE))")
s=s.replace("with publication_write(PROJECT):_register_review(PROJECT,REPORT,UNIT,MID,EXCLUDED)","with publication_write(PROJECT):step('register signed ICES review',lambda:_register_review(PROJECT,REPORT,UNIT,MID,EXCLUDED))")
s=s.replace("_refresh_reviews(PROJECT,prior,[UNIT],model_ids={UNIT:MID},publish=False)","step('verify exact bounded review replay',lambda:_refresh_reviews(PROJECT,prior,[UNIT],model_ids={UNIT:MID},publish=False))")
s=s.replace("expected=candidate(ROOT,PROJECT,read_book(REGION))","expected=step('verify installed candidate review and diagnostics',lambda:candidate(ROOT,PROJECT,read_book(REGION)))")
s=s.replace("_update(ROOT,[REGION],False);publication.checkpoint([PROJECT])","step('consolidate only LME022',lambda:_update(ROOT,[REGION],False));publication.checkpoint([PROJECT])")
s=s.replace("_build(PROJECT,only_units={UNIT})","step('build saved-data pages only LME022',lambda:_build(PROJECT,only_units={UNIT}))")
s=s.replace("result=final_checks(state,package,expected)","result=step('final installed bytes sources reviews defaults and diagnostics',lambda:final_checks(state,package,expected))")
s=s.replace("package=authenticate_package();state=initialize(package)","package=step('authenticate and verify frozen retained package',authenticate_package);state=step('check current baseline and staged independent inputs',lambda:initialize(package))\n        write(RUN/'qa/input_preservation.json',{k:state[k] for k in ['protected','staged_mapping_identity','old_table_counts','staged_table_counts']})")
s=s.replace("isolated_preflight(state,package);result=", "step('isolated staged registration replay and candidate preflight',lambda:isolated_preflight(state,package));result=")
p.write_text(s,encoding='utf-8')
compile(s,str(p),'exec')
