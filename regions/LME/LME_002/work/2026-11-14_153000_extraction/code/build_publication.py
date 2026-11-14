"""Run maintained import/conversion tools and preserve their actual outcomes."""
from pathlib import Path
import json, subprocess,sys,hashlib,shutil,csv,os
RUN=Path(__file__).resolve().parents[1]
ROOT=next(p for p in RUN.parents if (p/'Project.xlsx').exists())
SCRIPTS=ROOT/'tools/skills/paper-to-ppr/resources/extraction/scripts'
OUT=RUN/'outputs'
inp=OUT/'publication_writer_input.json'
d=json.loads(inp.read_text(encoding='utf-8'))
# Retain source review numeric/rule companions supplied by the independent reader.
for f in OUT.glob('source_companion_*.csv'):
    rows=list(csv.reader(f.open(encoding='utf-8',newline='')))
    d['companions'][f.name.removeprefix('source_companion_')]={'description':'Published source evidence from independent prose/table review; unsupported fields have no implied runtime use.','rows':rows}
inp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
outcomes=[]
def run(script,args,log):
    proc=subprocess.run([sys.executable,str(SCRIPTS/script),*map(str,args)],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',env={**os.environ,'PYTHONIOENCODING':'utf-8'})
    (RUN/'qa'/log).write_text(proc.stdout+'\nSTDERR\n'+proc.stderr,encoding='utf-8')
    outcomes.append({'script':str((SCRIPTS/script).relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256((SCRIPTS/script).read_bytes()).hexdigest(),'returncode':proc.returncode,'log':log})
    print(script,proc.returncode,flush=True)
    return proc
p=run('write_outputs.py',[inp,'--outdir',OUT],'publication_writer.log')
if p.returncode:raise SystemExit(p.stdout+p.stderr)
stage=OUT/'Aydin2007_Gulf_of_Alaska_1990-1994'
if not stage.exists():
    candidates=[x for x in OUT.iterdir() if x.is_dir() and (x/'Basic_input.csv').exists()]
    assert len(candidates)==1,candidates
    stage=candidates[0]
tax=OUT/'source_taxonomy.csv'
if tax.exists():
    import openpyxl
    wb=openpyxl.Workbook();ws=wb.active;ws.title='Taxonomy'
    for row in csv.reader(tax.open(encoding='utf-8',newline='')):ws.append(row)
    ws.freeze_panes='A2';ws.auto_filter.ref=ws.dimensions
    ws.column_dimensions['A'].width=8;ws.column_dimensions['B'].width=30;ws.column_dimensions['C'].width=90
    wb.save(stage/'Taxonomy.xlsx')
run('validate.py',[stage],'publication_validate.log')
run('massbalance_check.py',[stage],'publication_massbalance.log')
run('database_json.py',['-d',stage,'--update-report'],'publication_conversion.log')
result={'stage_relative':str(stage.relative_to(ROOT)).replace('\\','/'),'outcomes':outcomes,'source_pdf_sha256':hashlib.sha256((ROOT/'regions/LME/LME_002/papers/GOA-2007/sources/noaa_22894_DS1-9dadd884.pdf').read_bytes()).hexdigest(),'python':sys.version,'scope':'Source-faithful publication extraction; unresolved diets retained; no PPRCalculator or SPPR executed'}
(RUN/'qa/publication_tools.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
