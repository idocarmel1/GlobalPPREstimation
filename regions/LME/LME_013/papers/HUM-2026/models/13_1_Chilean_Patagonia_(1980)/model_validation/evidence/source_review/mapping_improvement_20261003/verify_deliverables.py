from pathlib import Path
from zipfile import ZipFile
from collections import defaultdict,Counter
from lxml import etree
import json,sys,hashlib,math,re,openpyxl,urllib.parse,shutil,datetime
sys.stdout.reconfigure(encoding='utf-8')
OUT=Path(__file__).parent;ROOT=OUT.parents[4];REG=ROOT/'regions/LME_013';sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book,records,overview,input_hash,finite,numeric_status,YEARS
from regional import result_hash
from ooxml_preserve import package
from validation_percentage_format import verify_report,format_percent
def load(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def normalize(v):return json.loads(json.dumps(v,ensure_ascii=False))
def close(a,b):
    if a is None or b is None:assert a==b,(a,b)
    else:assert math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-8),(a,b)
base=load('baseline_tables.json');final=read_book(REG/'LME_013.xlsx');ledger=load('decision_ledger.json');summary=load('comparison_summary.json');identity=load('baseline_identity.json')
assert normalize(final)==load('adopted_tables.json')
for sheet in ['Catch','Classic PPR','Selected model groups','NPP']:assert normalize(final[sheet])==base[sheet],sheet
for table,block in base['Diagnostics'].items():
    if table!='Taxon mapping validation':assert normalize(final['Diagnostics'][table])==block,table
concurrent=[]
shared_paths={'Project.xlsx','interactive_map/index.html','interactive_map/trends.html','interactive_map/archive/index.html','tools/knowledge_graph/graph.json'}
for p,want in identity['protected_file_hashes'].items():
    got=sha(ROOT/p)
    if p in shared_paths and got!=want:
        concurrent.append({'path':p,'baseline_sha256':want,'current_sha256':got,'last_write_utc':datetime.datetime.fromtimestamp((ROOT/p).stat().st_mtime,datetime.timezone.utc).isoformat(),'bytes':(ROOT/p).stat().st_size})
    else:assert got==want,p
(OUT/'concurrent_protected_file_changes.json').write_text(json.dumps(concurrent,ensure_ascii=False,indent=2),encoding='utf-8')
old_settings=identity['settings'];new_settings=overview(final)
for k,v in old_settings.items():
    if k not in ['source_note','calculation_input_sha256','calculation_result_sha256','calculation_status']:assert new_settings[k]==v,k
assert new_settings['calculation_input_sha256']==input_hash(final)
assert new_settings['calculation_result_sha256']==result_hash(final)
assert new_settings['production_eligible'] is False
assert new_settings['selected_model_id']=='13_1_Chilean_Patagonia_(1980)'
taxa={r['taxon'] for r in records(final,'Catch','Catch')};decisions={r['taxon']:r for r in ledger};assert taxa==set(decisions) and len(taxa)==218
mapping=defaultdict(list)
for r in records(final,'PPR','Matching'):mapping[r['taxon']].append(r)
scores={r['taxon']:r for r in records(final,'Diagnostics','Taxon mapping validation')}
rank={'Unresolved':0,'Very low':1,'Low':2,'Medium':3,'High':4}
for t in taxa:
    row=decisions[t];assert math.isclose(math.fsum(r['weight'] for r in mapping[t]),1,rel_tol=0,abs_tol=1e-9)
    assert sorted((r['group'],r['weight']) for r in mapping[t])==sorted((r['group'],r['weight']) for r in row['new_mappings'] if r['weight']>0)
    assert row['overall_confidence']==min([row['membership_confidence'],row['allocation_confidence']],key=rank.get)
    assert all(r['confidence']==row['overall_confidence'] for r in mapping[t])
    for k in ['membership_rule','membership_confidence','allocation_rule','allocation_confidence','overall_confidence']:assert scores[t][k]==row[k],(t,k)
# Independent saved-coefficient weighting, including unknown and negative values.
groups={(r['group'],r['scope'],r['method']):r['sppr'] for r in records(final,'Selected model groups','Group SPPR')}
coefs={};weighted_count=0
for row in records(final,'PPR','Taxon SPPR'):
    t,s,m=row['taxon'],row['scope'],row['method'];v=[(r['weight'],groups.get((r['group'],s,m))) for r in mapping[t]]
    want=round(math.fsum(w*x for w,x in v),6) if v and all(finite(x) for w,x in v) else None
    close(row['sppr'],want);coefs[t,s,m]=want;weighted_count+=1
catch={(r['taxon'],r['catch_basis']):r for r in records(final,'Catch','Catch')};unidentified={r['taxon']:bool(r.get('unidentified')) for r in records(final,'Catch','Catch')};classic={r['taxon']:r['sppr'] for r in records(final,'Classic PPR','Taxa')}
annual_checks=0
for r in records(final,'PPR','Annual'):
    for y in YEARS:
        pairs=[];allcatch=[]
        for t in taxa:
            c=catch[t,r['catch_basis']][y];v=coefs[t,r['scope'],r['method']]
            if unidentified[t] and r['unidentified']=='zero':v=0
            if unidentified[t] and r['unidentified']=='simple':v=classic.get(t)
            allcatch.append(c)
            if finite(c) and finite(v):pairs.append((c,v))
        if r['metric']=='catch':want=math.fsum(allcatch) if all(finite(v) for v in allcatch) else None
        elif r['metric']=='ppr':want=math.fsum(c*v for c,v in pairs) if pairs and numeric_status(r['status']) else None
        else:want=math.fsum(c for c,v in pairs) if pairs and numeric_status(r['status']) else None
        close(r[y],want);annual_checks+=1
den=math.fsum(catch[t,'landings'][2019]*classic[t]/9 for t in taxa if finite(classic.get(t)))
npp={r['method']:r for r in records(final,'NPP','NPP')}
annual_lookup={(r['scope'],r['method'],r['catch_basis'],r['unidentified']):r for sheet in ['Classic PPR','PPR'] for r in records(final,sheet,'Annual') if r['metric']=='ppr'}
ratio_checks=0
for r in records(final,'PPR–NPP','Ratios'):
    a=annual_lookup[r['scope'],r['method'],r['catch_basis'],r['unidentified']];n=npp[r['npp_method']]
    for y in YEARS:
        p,d=a[y],n[y];want=100*p/9/d if finite(p) and finite(d) and d>0 else None
        close(r[y],want);ratio_checks+=1
unknown=[t for t in taxa if catch[t,'landings'][2019]>0 and not finite(classic.get(t))]
assert not unknown;close(den,summary['total_simple_chain_ppr_tC']);close(den,identity['independent_simple_ppr_tC'])
assert len([t for t in taxa if not finite(classic.get(t))])==34
for key in ['revised_confidence','baseline_confidence']:close(math.fsum(r['ppr_percentage'] for r in summary[key]),100);assert sum(r['taxa'] for r in summary[key])==218
for key in ['membership_summary','allocation_summary']:close(math.fsum(r['ppr_percentage'] for r in summary[key]),100)
# Native appendix contract, numeric ordering and preserved inputs/features.
wb=openpyxl.load_workbook(REG/'LME013_taxon_mapping_appendix.xlsx');old=openpyxl.load_workbook(OUT/'baseline/LME013_taxon_mapping_appendix.xlsx');sh=wb['Taxon mapping'];prior=old['Taxon mapping']
assert sh.max_column==7 and sh.max_row==225 and sh.freeze_panes==prior.freeze_panes
assert [sh.cell(7,i).value for i in range(1,8)]==[prior.cell(7,i).value for i in range(1,8)]
assert sh.tables['HumboldtMappingTable'].ref=='A7:G225'
allkeys=[];numeric=[];vl=[]
for ri in range(8,226):
    for ci in range(1,5):assert sh.cell(ri,ci).value==prior.cell(ri,ci).value,(ri,ci)
    t=sh.cell(ri,1).value;allkeys.append(t);r=decisions[t];assert sh.cell(ri,6).value==r['overall_confidence']
    p=sh.cell(ri,4).value
    if isinstance(p,(int,float)):numeric.append(p)
    else:assert p=='?' and not finite(classic.get(t))
    if r['overall_confidence']=='Very low':vl.append(t)
    display=sh.cell(ri,5).value;weights=[float(v) for v in re.findall(r'\(([-\d.]+)%\)',display)]
    assert len(weights)==len(r['new_mappings']) and abs(sum(weights)-100)<len(weights)*.000001
assert set(allkeys)==taxa and len(allkeys)==len(set(allkeys))==218
assert numeric==sorted(numeric,reverse=True)
assert set(vl)==set(summary['very_low_taxa'])
for name in wb.sheetnames:
    a,b=wb[name],old[name]
    assert a.freeze_panes==b.freeze_panes
    for k,v in b.column_dimensions.items():assert a.column_dimensions[k].width==v.width
    for i,v in b.row_dimensions.items():assert a.row_dimensions[i].height==v.height
# Every repository-local Office hyperlink is relative and can be relocated.
links=[]
for file in [REG/'LME013_taxon_mapping_appendix.xlsx',REG/'Model_validation_13_1_Chilean_Patagonia_(1980).docx']:
    infos,parts=package(file)
    for name,content in parts.items():
        if name.endswith('.rels'):
            for rel in etree.fromstring(content):
                if rel.get('Type','').endswith('/hyperlink'):
                    target=rel.get('Target');parsed=urllib.parse.urlsplit(target)
                    if parsed.scheme in ['http','https','mailto']:continue
                    assert not parsed.scheme and not target.startswith(('/','\\')),target
                    local=(file.parent/urllib.parse.unquote(parsed.path)).resolve();assert local.exists(),(file.name,target)
                    # A root substitution preserves the repository-relative destination.
                    relfile=file.relative_to(ROOT);reldest=local.relative_to(ROOT)
                    virtual=Path('portable_repository')/relfile.parent/urllib.parse.unquote(parsed.path)
                    assert Path(__import__('os').path.normpath(virtual))==Path('portable_repository')/reldest
                    links.append({'file':file.name,'target':target,'resolved_repository_path':reldest.as_posix()})
        elif name in ['docProps/app.xml']:
            x=etree.fromstring(content)
            assert not x.xpath('//*[local-name()="HyperlinkBase"]/text()'),'machine-specific Hyperlink Base'
for name in wb.sheetnames:
    for row in wb[name]:
        for cell in row:
            if cell.hyperlink:assert cell.font.underline=='single' and cell.font.color.type=='rgb' and cell.font.color.rgb[-6:].upper() in ['0000FF','0563C1'],(name,cell.coordinate)
# Main report preservation and exact decision table coverage.
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main';NS={'w':W};q=lambda n:'{'+W+'}'+n
infos,parts=package(REG/'Model_validation_13_1_Chilean_Patagonia_(1980).docx');_,oldparts=package(OUT/'baseline/Model_validation_13_1_Chilean_Patagonia_(1980).docx')
assert set(parts)==set(oldparts)
for name,data in oldparts.items():
    if name not in ['word/document.xml','word/_rels/document.xml.rels']:assert parts[name]==data,name
xml=etree.fromstring(parts['word/document.xml']);oldxml=etree.fromstring(oldparts['word/document.xml']);tables=xml.findall('.//'+q('body')+'/'+q('tbl'));oldtables=oldxml.findall('.//'+q('body')+'/'+q('tbl'))
text=lambda n:''.join(n.xpath('.//w:t/text()',namespaces=NS))
for a,b in zip(tables[0].findall(q('tr')),oldtables[0].findall(q('tr'))):
    if text(a.find(q('tc')))!='Model extraction':assert etree.tostring(a,method='c14n')==etree.tostring(b,method='c14n'),text(a.find(q('tc')))
for rows,data in [(tables[1].findall(q('tr'))[1:],summary['revised_confidence']),(tables[2].findall(q('tr'))[1:],summary['membership_summary']),(tables[3].findall(q('tr'))[1:],summary['allocation_summary'])]:
    assert len(rows)==len(data)
    for row,r in zip(rows,data):
        cells=[text(c) for c in row.findall(q('tc'))];assert cells[-1]==format_percent(r['ppr_percentage'])
wordvl=[t.strip() for row in tables[4].findall(q('tr'))[1:] for t in text(row.find(q('tc'))).split(';')]
assert len(wordvl)==len(set(wordvl)) and set(wordvl)==set(vl)
for hyperlink in xml.findall('.//'+q('hyperlink')):
    for run in hyperlink.findall(q('r')):
        rp=run.find(q('rPr'));assert rp is not None
        c=rp.find(q('color'));u=rp.find(q('u'));assert c is not None and c.get(q('val')).upper() in ['0000FF','0563C1'] and u is not None and u.get(q('val'))=='single'
verify_report(REG/'Model_validation_13_1_Chilean_Patagonia_(1980).docx')
out={'status':'PASS_WITH_CONCURRENT_SHARED_FILE_NOTICE','selected_model':new_settings['selected_model_id'],'reviewed_exact_labels':218,'protected_files_unchanged':len(identity['protected_file_hashes'])-len(concurrent),'concurrent_shared_file_changes':concurrent,'concurrent_change_handling':'No executed authoring path writes these shared files; changes were left intact. Baseline hashes retained; no global unchanged assertion is made.','protected_tables_unchanged':True,'fresh_input_hash':input_hash(final),'fresh_result_hash':result_hash(final),'saved_group_weight_checks':weighted_count,'annual_checks_all_years_scopes_methods_bases_treatments':annual_checks,'npp_ratio_checks':ratio_checks,'independent_2019_simple_chain_tC':den,'missing_coefficients_zero_2019_catch':34,'positive_unknown_ppr_labels':unknown,'confidence_counts':dict(Counter(r['overall_confidence'] for r in ledger)),'portable_local_links':links,'manual_rows_and_nonedited_package_parts_preserved':True,'appendix_native_features_and_numeric_inputs_preserved':True,'exact_very_low_taxa_in_both_outputs':len(vl),'review_gate':'shared update deferred; no researcher approval registered','solver_MC_extraction_execution':False}
(OUT/'verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='portable_local_links'},ensure_ascii=False,indent=2))
