from pathlib import Path
import hashlib,json
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
QA=Path(__file__).resolve().parents[1]/'qa';records=[]
for p in sorted((ROOT/'research').rglob('README.md')):
    rel=p.relative_to(ROOT)
    if any(x in rel.parts for x in ['inputs','work','node_modules','vendor','.venv','__pycache__']):continue
    before=p.read_bytes();text=before.decode('utf-8-sig')
    depth=len(p.parent.relative_to(ROOT).parts)
    guide='../'*depth+'explainers/structure.md'
    prefix=f'> **Reorganization scope: frozen historical evidence.** This guide retains the original study/release statements, counts, scientific assumptions and execution history. Its former paths or build commands are not the current project workflow. Follow the [current structure contract]({guide}) and resolve retained dependencies through the portable source-path ledger before any separately authorized reproduction. Reorganization does not certify old results as current or authorize reruns.\n\n'
    if 'Reorganization scope: frozen historical evidence' in text:
        # Recover the exact preface/body after an interrupted first Windows
        # newline assertion; the old CRLF was translated a second time.
        encoded_prefix=prefix.replace('\n','\r\n')
        if text.startswith(encoded_prefix):
            text=text[len(encoded_prefix):].replace('\r\r\n','\r\n')
        else:continue
    text=text.replace('\r\n','\n')
    p.write_text(prefix+text,encoding='utf-8',newline='\n')
    after=p.read_text(encoding='utf-8')
    assert after[len(prefix):]==text.replace('\r\n','\n')
    records.append(dict(path=rel.as_posix(),before_sha256=hashlib.sha256(before).hexdigest(),after_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),original_prose_preserved=True))
(QA/'historical_guide_scope.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print('Scoped historical guides:',len(records))
