"""Bounded caller runs one requested candidate/configuration; retain basal detail missing from workbook."""
from pathlib import Path
import sys,shutil,json
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
OUT=ROOT/'regions/LME_049/models'/sys.argv[1];te=sys.argv[2]
sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
from create_PPRS_excel import load_model,HEALTH_DET_CONFIG
p=OUT/'evidence'/f'{OUT.name}.json';p.parent.mkdir(exist_ok=True);shutil.copy2(OUT/'model.json',p)
m,_=load_model(str(p));sppr,*_=m.SPPR_new(TE_option=te,**HEALTH_DET_CONFIG)
sppr.to_csv(OUT/'evidence'/f'source_coefficients_{te.replace(" ","_")}.csv')
print(sppr.loc[(sppr<0).any(axis=1)].to_string())
