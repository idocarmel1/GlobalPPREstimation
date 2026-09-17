from pathlib import Path
import ast,re,shutil,subprocess,json
ROOT=Path(__file__).resolve().parents[1]
checks=[]
for p in (ROOT/'src').rglob('*.py'):
    ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p));checks.append(str(p.relative_to(ROOT)))
html=(ROOT/'src/report_template.html').read_text(encoding='utf-8');scripts=re.findall(r'<script>(.*?)</script>',html,re.S)
target=ROOT/'verification/report_script.js';target.write_text('\n'.join(scripts),encoding='utf-8')
result=subprocess.run([shutil.which('node'),'--check',str(target)],capture_output=True,text=True)
if result.returncode:raise SystemExit(result.stderr)
(ROOT/'verification/static_checks.json').write_text(json.dumps(dict(python_files=checks,report_script_syntax='passed'),indent=2),encoding='utf-8')
print('Static checks passed:',len(checks),'Python files and report JavaScript')
