import pathlib,json,sys,re,hashlib
p=pathlib.Path(sys.argv[1]);ex=p/'extracted';w=ex/'work'
audit=w/'audit_database.py';a=audit.read_text(encoding='utf-8-sig').replace('12 changed consumer diet columns incomplete','14 affected consumer diets incomplete');a=a.replace("import csv,json,pathlib,sys,re,decimal,hashlib","import csv,json,pathlib,sys,re,decimal,hashlib\nsys.dont_write_bytecode=True");audit.write_text(a,encoding='utf-8')
index=ex/'MASTER_INDEX.md';index.write_text(index.read_text(encoding='utf-8').replace('12 changed consumer diet columns incomplete','14 affected consumer diets incomplete'),encoding='utf-8')
for d in sorted(ex.glob('27_*_Banc*')):
 m=json.loads((d/'model.json').read_text(encoding='utf-8'));variant=m['metadata']['variant'];stem=variant.lower();report=d/'REPORT.md';text=report.read_text(encoding='utf-8')
 text=text.replace('Checked by `ewe_model_json_creator.py`','Checked by the bundled `database_json.py` equations plus the local source-preservation/integrity audit')
 text=text.replace('### Indeterminate (BA unknown)','### Unresolved data and scope')
 text=text.replace('The final section of ewe_conversion.log supersedes its preliminary values/verdict.','The final section of ewe_conversion.log supersedes the preliminary stock-conversion values/verdict; the original pipeline record is also retained under ../work.')
 # Clarify that baseline inheritance is an extraction assumption and not independent source verification.
 if variant!='Base':
  text=text.replace('No post-1991 simulation rates are added.','This inheritance is an explicit extraction assumption limited to the changes described by the authors; these retained cells require checking against the unavailable original variant model file. No post-1991 simulation rates are added.')
 report.write_text(text,encoding='utf-8')
 mb=d/'MASS_BALANCE.md';mt=mb.read_text(encoding='utf-8').replace('Checked by `ewe_model_json_creator.py`','Checked by the bundled `database_json.py` equations plus the local source-preservation/integrity audit').replace('### Indeterminate (BA unknown)','### Unresolved data and scope');mb.write_text(mt,encoding='utf-8')
 # Combine original output records and final adapter decisions without discarding either.
 logfile=d/'ewe_conversion.log';final=logfile.read_text(encoding='utf-8');original=(w/(stem+'_bundled_database_pipeline.txt')).read_text(encoding='utf-8');logfile.write_text('ORIGINAL BUNDLED CONVERSION RECORD — SUPERSEDED BY FINAL SOURCE-PRESERVATION AUDIT BELOW\n\n'+original+'\n\nFINAL SOURCE-PRESERVATION AUDIT — AUTHORITATIVE FINAL OUTPUTS\n\n'+final,encoding='utf-8')
 pv=json.loads((d/'PROVENANCE.json').read_text(encoding='utf-8'));groups={g['n']:g for g in m['groups']}
 for v in pv:
  if variant!='Base' and v['model']=='Base':
   if v['field']=='diet':
    target=m['diet'][str(v['group'])].get(v['prey']);v['variant_usage']='withheld: aggregate share does not resolve variant cell' if target is None else 'inherited baseline assumption; not separately tabulated for variant'
   else:v['variant_usage']='inherited baseline assumption; not separately tabulated for variant'
 (d/'PROVENANCE.json').write_text(json.dumps(pv,ensure_ascii=False,indent=2),encoding='utf-8')
 required=['Basic_input.csv','Diet_composition.csv','Landings.csv','Discards.csv','Detritus_fate.csv','Biomass_accumulation.csv','TL.xlsx','Metadata.xlsx','model.json','REPORT.md','MASS_BALANCE.md','ewe_conversion.log','PROVENANCE.json','SOURCE_DETAILS.json','AUDIT_RESULTS.json']
 for f in required:assert (d/f).is_file() and (d/f).stat().st_size>0,(d,f)
 for f in d.glob('*.csv'):
  b=f.read_bytes();assert not b.startswith(b'\xef\xbb\xbf') and b'"' not in b and b.endswith(b'\r\n') and b'\n' not in b.replace(b'\r\n',b''),f
 assert len(list(d.glob('27_Canary_Current*.json')))==1 and len(list(d.glob('*_reconstructed.xlsx')))==1
 print(variant,len(list(d.iterdir())),'files verified')
inv=json.loads((ex/'SOURCE_INVENTORY.json').read_text(encoding='utf-8'))
for r in inv:assert hashlib.sha256((p/r['file']).read_bytes()).hexdigest()==r['sha256'],r['file']
(ex/'FINAL_VERIFICATION.md').write_text('# Final verification\n\n2026-09-04: three model directories verified; all eight import files plus database JSON, reconstructed workbook, provenance/report and validation artifacts present. All CSVs have CRLF, UTF-8 without BOM and no quotes. Every reconstructed workbook matches all eight source tables cell-for-cell. Database diet values preserve published percentages after exact /100 conversion with no normalization; all unreported habitat/GS/diet components remain -9999. Group classes are 47 consumers, 3 producers and 1 detritus. All 16 source files match pre-extraction hashes; the 13 publication downloads match recorded SHA-256 values. No source file or installed skill source was edited.\n\nKnown failures are reported rather than repaired: source diet totals 0.980331 and 2.2006; incomplete variant diets; missing multi-stanza P/B, habitat, GS, discards and detritus routing. All models are partial; final guarded mass-balance verdict is NOT BALANCED.\n',encoding='utf-8')
print('All source SHA-256 values unchanged')
