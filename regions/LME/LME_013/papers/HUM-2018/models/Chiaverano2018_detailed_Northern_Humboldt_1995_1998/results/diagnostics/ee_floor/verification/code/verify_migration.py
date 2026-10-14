"""Preservation and displayed-result audit for the authorized EE-floor migration."""
from pathlib import Path
import argparse, copy, gzip, hashlib, itertools, json, sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
from tools.project_core.calculations.coverage import _metadata, validated_identities, _preserved_inputs
from tools.project_core.registry.discovery import discover_regions, region_directory, resolve_model
from tools.project_core.workbooks.workbooks import read_book, records, overview, digest_tables, sha

WORK = Path(__file__).resolve().parents[1]

def saved(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(json.dumps(value, ensure_ascii=False, allow_nan=False).encode(), mtime=0))

def read(path):
    return json.loads(gzip.decompress(path.read_bytes()))

def summaries(book):
    return [r for r in records(book, 'PPR', 'Annual') if r['scope']=='all' and
            r['catch_basis']=='landings' and r['unidentified']=='method' and r['metric']=='ppr']

def independent_project(book, units):
    generated = {'Regions & status','Regional PPR','Regional NPP','Method comparisons',
                 'Diagnostics & sensitivity','Definitions & build'}
    result = {s:copy.deepcopy(t) for s,t in book.items() if s not in generated}
    for s in sorted(generated - {'Definitions & build'}):
        for t, (h, rr) in book.get(s, {}).items():
            if 'unit_id' in h:
                result.setdefault(s,{})[t] = (h,[r for r in rr if r[h.index('unit_id')] not in units])
    # Atlas rank fields are generated from newly published eligible values.
    for h, rr in result.get('Models & coverage',{}).values():
        for j, name in enumerate(h):
            if 'rank' in str(name).lower():
                for r in rr:r[j]=None
    return result

def verify_independent_project(baseline, current, units):
    """Authenticate the capture without depending on random set iteration order.

    The original capture constructed generated-sheet keys by iterating a set.
    digest_tables preserves dictionary insertion order. Reconstruct its exact
    recorded hash from the lossless pre-publication workbook before comparing
    table contents; never replace the recorded baseline with a new hash.
    """
    before=independent_project(read_book(WORK/'qa/Project.before.xlsx'),units)
    after=independent_project(current,units)
    generated={'Regions & status','Regional PPR','Regional NPP','Method comparisons',
               'Diagnostics & sensitivity'}
    fragments={key:json.dumps({key:value},ensure_ascii=False,separators=(',',':'))[1:-1].encode()
               for key,value in before.items()}
    prefix=[key for key in before if key not in generated]
    suffix=[key for key in before if key in generated]
    def ordered_hash(keys):
        digest=hashlib.sha256();digest.update(b'{')
        for i,key in enumerate(keys):
            if i:digest.update(b',')
            digest.update(fragments[key])
        digest.update(b'}');return digest.hexdigest()
    assert ordered_hash(list(before))==digest_tables(before)
    matched=None
    for order in itertools.permutations(suffix):
        if ordered_hash([*prefix,*order])==baseline['independent_project']:
            matched=list(order);break
    assert matched is not None,'Lossless pre-publication workbook does not authenticate the original capture'
    assert before==after,'Unrelated central table content changed'
    stable=hashlib.sha256(json.dumps(before,ensure_ascii=False,sort_keys=True,
                                  separators=(',',':')).encode()).hexdigest()
    result={'original_capture_hash':baseline['independent_project'],
            'authenticated_generated_sheet_order':matched,
            'stable_independent_tables_sha256':stable,'unrelated_central_tables_unchanged':True}
    saved(WORK/'qa/central_preservation.json.gz',result)
    return result

def capture():
    identities=validated_identities(_metadata(ROOT)); units={u for u,_ in identities}
    baseline={'identities':identities,'methods':{},'protected_files':{},'unrelated_regions':{},'models':{}}
    owned=[]
    for unit,mid in identities:
        model=resolve_model(region_directory(ROOT,unit),mid).parent
        path=region_directory(ROOT,unit)/(unit+'.xlsx'); book=read_book(path)
        owned += [model/'sppr_source.xlsx',model/'results']
        settings=overview(book)
        review_settings={k:v for k,v in settings.items() if any(s in k.lower() for s in
            ('researcher','review','exclu','selection','selected_model'))}
        baseline['models'][unit+'/'+mid]={'model':model.relative_to(ROOT).as_posix(),
            'protected_tables':_preserved_inputs(book),'classic':digest_tables(book.get('Classic PPR',{})),
            'review_settings':review_settings,'annual':summaries(book),
            'manifest':json.loads((model/'results/result_manifest.json').read_text(encoding='utf-8'))}
    for unit,path in discover_regions(ROOT).items():
        if unit not in units:baseline['unrelated_regions'][path.relative_to(ROOT).as_posix()]=sha(path)
    paths=[]
    for unit in sorted(units):
        region=region_directory(ROOT,unit)
        paths += [p for p in region.rglob('*') if p.is_file() and
                  not p.is_relative_to(region/'work') and p!=region/(unit+'.xlsx') and
                  not any(p==o or p.is_relative_to(o) for o in owned)]
    paths += [p for p in (ROOT/'common_reference_data').rglob('*') if p.is_file()]
    baseline['protected_files']={p.relative_to(ROOT).as_posix():sha(p) for p in paths}
    baseline['independent_project']=digest_tables(independent_project(read_book(ROOT/'Project.xlsx'),units))
    saved(WORK/'qa/before.json.gz',baseline)
    print(json.dumps({'validated_pairs':len(identities),'protected_files':len(paths),'unrelated_regions':len(baseline['unrelated_regions'])}))

def verify():
    from tools.scientific_helpers.sppr.method_coverage import method_inventory
    baseline=read(WORK/'qa/before.json.gz'); expected=set(method_inventory()); report=[]
    for path,digest in {**baseline['protected_files'],**baseline['unrelated_regions']}.items():
        assert sha(ROOT/path)==digest, 'Protected input changed: '+path
    identities=validated_identities(_metadata(ROOT)); assert [list(v) for v in identities]==baseline['identities']
    units={u for u,_ in identities}
    central=verify_independent_project(baseline,read_book(ROOT/'Project.xlsx'),units)
    for unit,mid in identities:
        old=baseline['models'][unit+'/'+mid]; model=ROOT/old['model']; book=read_book(region_directory(ROOT,unit)/(unit+'.xlsx'))
        assert _preserved_inputs(book)==old['protected_tables'], unit+' scientific tables changed'
        assert digest_tables(book.get('Classic PPR',{}))==old['classic'], unit+' Classic PPR changed'
        settings=overview(book)
        assert {k:settings.get(k) for k in old['review_settings']}==old['review_settings'],unit+' selection or signed review settings changed'
        mf=json.loads((model/'results/result_manifest.json').read_text(encoding='utf-8'))
        flags=mf['effective_flags']; assert flags['constructor']['use_ee_floor'] is True and flags['constructor']['ee_floor']==.1
        assert set(mf['method_coverage']['methods'])==expected,unit+' incomplete method outcomes'
        assert mf['snapshot_sha256']==sha(model/'results/regional_snapshot.xlsx')
        assert mf['coefficient_source_sha256']==sha(model/'sppr_source.xlsx')
        if unit=='LME_013':assert flags['diagnostics']['det_collapse_mode']=='auto'
        current={r['method']:r for r in summaries(book)}
        changes=[]
        for r in old['annual']:
            key=r['method']; after=current[key]; a=r.get('2019',r.get(2019)); b=after.get('2019',after.get(2019))
            changes.append({'method':key,'before_2019_tonnes_wet_weight':a,'after_2019_tonnes_wet_weight':b,
                            'before_2019_tC':a/9 if a is not None else None,
                            'after_2019_tC':b/9 if b is not None else None,
                            'percent_change':100*(b/a-1) if a and b is not None else None,
                            'before_status':r['status'],'after_status':after['status']})
        entry={'unit':unit,'model_id':mid,'all_method_count':len(expected),'preserved':True,
               'ppr_basis':'2019 landings; all sources; all model groups; saved regional Annual ppr is wet-weight equivalent; carbon equivalent divides by 9, as in regional PPR/NPP arithmetic. Researcher display exclusions remain separate.',
               'changes':changes,
               'method_outcomes':{k:{'status':v['status'],'reason':v.get('reason'), 'evidence_kind':v.get('evidence_kind')} for k,v in mf['method_coverage']['methods'].items()}}
        report.append(entry)
        saved(model/'results/diagnostics/ee_floor/publication_verification.json.gz',entry)
    saved(WORK/'qa/after.json.gz',report)
    print(json.dumps([{'unit':r['unit'],'methods':r['all_method_count'],'changes':[v for v in r['changes'] if v['method'] in ('new_GE','new_TE_EEfix','new_WithEgestion')]} for r in report],ensure_ascii=False,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['capture','verify']);a=p.parse_args()
    capture() if a.action=='capture' else verify()
