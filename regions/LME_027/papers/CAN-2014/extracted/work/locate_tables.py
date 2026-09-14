import pathlib,sys,json
p=pathlib.Path(sys.argv[1]); tx=(p/'extracted/work/supplement_rendered.txt').read_text(encoding='utf-8').split('\f')
for i,x in enumerate(tx,1):print(i,x[:120].replace('\n',' '),[s for s in ['Table S2','Table S8','Table S9','Table S6','Table S4','Table S5','Figure S1'] if s in x])
