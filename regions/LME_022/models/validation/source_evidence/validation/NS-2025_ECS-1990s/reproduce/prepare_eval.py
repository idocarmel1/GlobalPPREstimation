from pathlib import Path
import shutil, hashlib, json
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/run_sppr.py').is_file() and (p/'PPRAtlas/archive').is_dir())
BASE=ROOT/'data/LME_022/validation/NS-2025_ECS-1990s'
EVAL=BASE/'evaluation'
files=['SeaAroundUsExtraction/data/catch_by_taxon_year/LME_022.csv.gz','SeaAroundUsExtraction/global_output/tables/regions/LME_022/species.csv','PPRAtlas/data/regions.csv','data/LME_022/npp.json','tools/build_model_workbook.py','tools/ppr_scopes.py','tools/verify_model_workbook.py']
for p in (ROOT/'skills/claude/ewe-species-to-group-mapper/scripts').glob('*.py'):files.append(str(p.relative_to(ROOT)))
manifest=[]
for rel in files:
    p=ROOT/rel;dst=EVAL/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
    manifest.append({'source':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(BASE/'EVALUATION_INPUT_HASHES.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(EVAL/'data/LME_022/mapping').mkdir(parents=True,exist_ok=True)
(EVAL/'PPREstimation/output/top10').mkdir(parents=True,exist_ok=True)
print(EVAL)
