"""Read-only current-document link/API audit, excluding frozen study content."""
from pathlib import Path
import ast,hashlib,json,re,urllib.parse
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
QA=Path(__file__).resolve().parents[1]/'qa'
docs=[ROOT/'README.md',ROOT/'AGENTS.md',ROOT/'common_reference_data/atlas_source_context/README.md',ROOT/'tools/scientific_code/NPPExtraction/README.md']
for part in ['explainers','tools/skills/paper-to-ppr','tools/skills/ecopath-model-validation','tools/templates']:
    docs.extend(p for p in (ROOT/part).rglob('*.md') if not any(x in p.parts for x in ['__pycache__','node_modules']))
docs=sorted(set(docs));links=[];broken=[];dependencies=[]
for p in docs:
    t=p.read_text(encoding='utf-8-sig')
    # Markdown links may contain model IDs with literal parentheses.
    t=re.sub(r'^```.*?^```[^\n]*',lambda m:'\n'*m.group(0).count('\n'),t,flags=re.M|re.S)
    for m in re.finditer(r'(?<!!)\[[^\]\n]*\]\(',t):
        pos=m.end();target='';angle=pos<len(t) and t[pos]=='<'
        if angle:
            end=t.find('>',pos+1)
            if end!=-1:target=t[pos+1:end]
        else:
            start=pos;depth=1;escaped=False
            while pos<len(t) and depth:
                c=t[pos]
                if escaped:escaped=False
                elif c=='\\':escaped=True
                elif c=='(':depth+=1
                elif c==')':depth-=1
                pos+=1
            if depth==0:target=t[start:pos-1]
        target=target.strip();line=t[:m.start()].count('\n')+1
        if not target:continue
        if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target) or target.startswith('#'):
            continue
        raw=target.split('#',1)[0].split(' "',1)[0]
        if '<' in raw or '>' in raw:continue
        resolved=(p.parent/urllib.parse.unquote(raw)).resolve()
        item={'document':p.relative_to(ROOT).as_posix(),'line':line,'target':target,'resolved':resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else str(resolved),'exists':resolved.exists()}
        links.append(item)
        if not resolved.is_relative_to(ROOT) or not resolved.exists():broken.append(item)
        else:dependencies.append({'from':item['document'],'to':item['resolved'],'kind':'markdown_link'})

imports=[]
for part in ['tools/skills/paper-to-ppr/scripts','tools/skills/paper-to-ppr/resources/extraction/scripts','tools/skills/paper-to-ppr/resources/mapping/scripts']:
    for p in (ROOT/part).glob('*.py'):
        tree=ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
        for n in ast.walk(tree):
            if isinstance(n,ast.Import):names=[x.name for x in n.names]
            elif isinstance(n,ast.ImportFrom):names=[n.module or '']
            else:continue
            for name in names:
                local=p.parent/(name.split('.')[0]+'.py')
                imports.append({'script':p.relative_to(ROOT).as_posix(),'module':name,'local_dependency':local.relative_to(ROOT).as_posix() if local.is_file() else None})

skills=sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/'tools/skills').rglob('SKILL.md'))
required={'tools/skills/paper-to-ppr/SKILL.md','tools/skills/ecopath-model-validation/SKILL.md'}
must_reads={}
for skill in sorted(required):
    t=(ROOT/skill).read_text(encoding='utf-8')
    must_reads[skill]={name:name in t for name in ['AGENTS.md#project_contract','README.md','explainers/structure.md','explainers/workflow.md']}
assert set(skills)==required,skills
assert all(all(v.values()) for v in must_reads.values()),must_reads
report={'schema_version':1,'scope':'Current README/AGENTS, all explainers, two active skills/resources, template instructions. Frozen studies are historical evidence, not current command documentation. Scientific values/engine algorithms were not reassessed or changed.','documents':len(docs),'local_links_checked':len(links),'broken_links':broken,'active_skills':skills,'must_reads':must_reads,'dependencies':dependencies,'script_import_dependencies':imports,'source_hashes':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in docs}}
(QA/'current_contract_verification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'documents':len(docs),'local_links':len(links),'broken':broken,'active_skills':skills},indent=2,ensure_ascii=False))
raise SystemExit(bool(broken))
