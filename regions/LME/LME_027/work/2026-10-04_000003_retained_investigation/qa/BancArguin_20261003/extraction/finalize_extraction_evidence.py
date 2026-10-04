from pathlib import Path
import json,hashlib,os,re,subprocess,sys,shutil
from decimal import Decimal as D
h=Path(__file__).resolve().parent;root=h.parents[4];models=root/'regions/LME_027/models';skill=Path('C:/Users/idoca/.agents/skills/ecopath-extraction')
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return os.path.relpath(p,h).replace('\\','/')
mapping={'27_1_Banc_d_Arguin_and_Mauritanian_Shelf_(1991)':'Base','27_Canary_Current_27_1_Banc_d_Arguin_and_Mauritanian_Shelf_(1991)':'Base','27_Canary_Current_27_2_Banc_d_Arguin_and_Mauritanian_Shelf_(1991)':'M30','27_Canary_Current_27_3_Banc_d_Arguin_and_Mauritanian_Shelf_(1991)':'P30'}
lineage=[];deltas=[]
for old,v in mapping.items():
 oldp=models/old/'model.json';newp=models/f'Guenette2014_BancArguin_{v}_1991/model.json'
 lineage.append({'old_directory':'regions/LME_027/models/'+old,'canonical_directory':str(newp.parent.relative_to(root)).replace('\\','/'),'old_sha256':sha(oldp) if oldp.exists() else None,'new_sha256':sha(newp),'variant':v,'action':'consolidate_same_published_variant; root coordinator controls cleanup; original sources preserved'})
 if not oldp.exists():continue
 olddata=load(oldp);newdata=load(newp);oldgroups={str(g['group_seq']):g for g in olddata.get('group',[])}
 for ng in newdata['group']:
  seq=ng['group_seq'];og=oldgroups.get(seq,{})
  for f in ['group_name','biomass','pb','qb','ee','z','ge','gs','habitat_area','biomass_accum','biomass_accum_rate','diet_imp','export']:
   if og.get(f)!=ng.get(f):deltas.append({'old_model':old,'variant':v,'group':seq,'field':f,'old':og.get(f),'source_reextracted':ng.get(f),'basis':'original Table1/S2/S8; explicit unknown and source-form preservation; no researcher override evidence supplied'})
  od=(og.get('diet_descr') or {}).get('diet') or [];od=[od] if isinstance(od,dict) else od;od={str(x['prey_seq']):x['proportion'] for x in od}
  for nd in (ng.get('diet_descr') or {}).get('diet') or []:
   prey=nd['prey_seq'];before=od.get(prey)
   if before!=nd['proportion']:deltas.append({'old_model':old,'variant':v,'group':seq,'field':'diet','prey':prey,'old':before,'source_reextracted':nd['proportion'],'basis':'original S2 cell or explicit unpublished variant; no normalization; no researcher correction evidence'})
save(h/'old_to_canonical_mapping.json',lineage);save(h/'old_to_source_cell_changes.json',deltas)
statuses=[]
for v in ['Base','M30','P30']:
 d=models/f'Guenette2014_BancArguin_{v}_1991';e=d/'extracted_tables';m=load(e/'extraction.json');j=load(d/'model.json');status=load(e/'EXTRACTION_STATUS.json');rt=load(e/'ROUNDTRIP_CHECK.json')
 validations=(e/'VALIDATION.txt').read_text(encoding='utf-8');vm=re.findall(r'\d+ error\(s\), \d+ warning\(s\)',validations)[-1]
 mb=(e/'MASS_BALANCE.md').read_text(encoding='utf-8');assert '**Verdict: BALANCED**' not in mb
 unknownpb=[g['n'] for g in m['groups'] if g.get('pb') is None and g['n']<=47];zeropb=[g['n'] for g in m['groups'] if g.get('pb')=='0' and g['n']<=47]
 sourceconf=load(e/'SOURCE_CONFLICTS.json');negative=[{'group':g['n'],'name':g['name'],'rate':g['ba_rate']} for g in m['groups'] if g.get('ba_rate') is not None and D(g['ba_rate'])<0]
 completeba=sum(g.get('ba_rate') is not None for g in m['groups'])
 report=f'''# Banc d'Arguin and Mauritanian Shelf — {v} (1991)

**Source extraction status: partial; not ready as a complete source model.** The published Base diet contains unresolved composition defects and multistanza production fields are incomplete. {'The '+v+' variant additionally has 114 unpublished prey cells across 14 consumers.' if v!='Base' else 'Base source-admission failure must not be presented as a validated ecological model.'} This concerns the published reconstruction; it does not establish that the authors' operational native model was unbalanced.

Source: Guénette, Meissa and Gascuel (2014), *Assessing the Contribution of Marine Protected Areas to the Trophic Functioning of Ecosystems*, PLoS ONE 9:e94742, [DOI](https://doi.org/10.1371/journal.pone.0094742). Original [article](../../../papers/CAN-2014/file-e30dfe50.pdf), [Table 1](../../../papers/CAN-2014/Table_1-f0424c0e.xls), and [supplement](../../../papers/CAN-2014/pone.0094742.s001-eb18ca66.docx).

51 groups: 47 consumers, 3 primary producers, 1 detritus pool. Three reported catch fleets: Artisanal, Industrial demersal, Industrial pelagic. The reference period is 1991, within a 33,224 km² Mauritanian shelf area; the 1991–2006 Ecosim fits and 2056 projections are separate outputs.

## Source tables and field meanings

Table 1 (article pp. 4–5; original XLS Table_1) fixes group IDs/names. Columns C–J map to TL, B, Z, P/B, Q/B, EE, P/Q and BA rate; K–M retain the three fleet catches and N the reported total. XLS stored strings and bold markup were reread independently; fresh page renders and word coordinates were retained. Bold B/rate/EE/PQ values are marked model-estimated, not silently described as author inputs. Z is separate from P/B, P/Q is separate from Q/B, and each source zero is retained.

Supplement S2, physical DOCX tables 2–4 (retained rendered pp. 8–10), is prey rows × consumer columns 1–47 with import row 52. Every printed percentage is divided by exactly 100 using Decimal, retaining source precision. The four original blank cells are predator/prey 14/36, 15/36, 2/39 and 15/39. They stay blank/-9999, distinct from the explicitly unpublished variant cells. A computational structural-zero convention for source blanks requires its own recorded transformation; it cannot fill a diet deficit.

S8 (physical DOCX table 10, retained rendered pp. 15–16) supplies variant B/EE, aggregate Banc invertebrate shares and Ecosim vulnerability values. {'Base keeps the dedicated Table1 input/output parameter set.' if v=='Base' else v+' takes its B/EE directly from S8. Other scalar parameters, catches and unchanged diet components are inherited Base data, not independently published variant values. TL is unknown. Aggregate pBA does not uniquely determine the 114 changing individual prey shares; they remain unknown.'} All original supplementary tables and their additional fields are retained in separate [companion CSVs](companions/manifest.json), including S8 formatting roles and scenario outputs; these evidence CSVs are not asserted to be directly importable by EwE.

## Biomass accumulation and multistanza structure

The supplement's Fish section states that BA values are rates per year derived from pre-1991 biomass trends. {completeba}/51 group BA rates are known; the detritus rate is unreported. Negative rates: {', '.join(str(x['group'])+' '+x['name']+' '+x['rate'] for x in negative)}. Printed zeros remain known zeros. Absolute BA stays unknown in source imports/JSON; B×rate is used only inside the check and retained separately as arithmetic evidence. A steady-state statement for the last projected year does not establish BA=0 for 1991.

Six stocks have juvenile (age 0–1 year) and adult stanzas, with adults leading the native linked equations. Source P/B is explicitly zero for {zeropb} and unreported for {unknownpb}. Table1 provides Z and P/Q separately. P/B=Z is stated only for equilibrium; QB×PQ is a rounded arithmetic reconstruction, not proof of the native stanza solution. VBK is unavailable. No missing P/B or known zero was replaced.

## Values from prose and deliberate blanks

All source documents were swept for BA, assimilation, diets/imports, detritus, fishing, migration and stanza fields. No numeric unassimilated consumption, habitat fractions, detritus routing/import or migration inputs were identified. These remain unknown; EwE/loader defaults would be computational assumptions. The source explicitly reports no discard information. Each fleet catch is retained independently, and total removals stay unknown. The database export field uses an explicit reported-landings scope recorded in metadata; it does not assert zero discards.

## Unresolved source conflicts

- Coastal birds' sum of printed cells is **0.980331**, leaving 0.019669 unexplained; its blank shelf-mollusc cell is not an authorized allocation of the deficit.
- Adult groupers' Banc large-crustacean cell is **134% = 1.34**, and its printed column sum is **2.2006**. The original DOCX and retained render agree. The old **0.1347275** value is not the published literal, and no actual researcher decision authorizing that correction was found. Neither correction nor normalization was adopted.
- {len(sourceconf)} Table1/S8 Base numeric differences are retained in [SOURCE_CONFLICTS.json](SOURCE_CONFLICTS.json). Most reflect rounding, while Banc phytoplankton EE is **0.260 versus 0.40**. Dedicated Table1 remains the Base authority; the disagreement is unresolved.
- Supplement prose says P/Q was fixed at 0.2 for mackerel/sardine/horse mackerels, while Table1 gives 0.150 for mackerel and sardine. The tabulated values are retained and the prose disagreement is not averaged.
- The separately recovered EcoBase 689 native model has different diet, precision, fleet and stanza representations. It is source context, not proof that its cells can replace any of these three published variants.

## Conventions and validation

No source diet or detritus routing was normalized. No project GS, habitat or discard default was inserted. Table percentages were converted to proportions; B remains the source's whole-study-area density. The directory name intentionally supplies a stable unique identity for each published variant.

The eight standard EwE import schemas retain their required headers/order. Extra fields are in 22 purpose-specific companion CSVs. The improved installed writer/converter were run; standard JSON fields were reconciled with fresh source extraction, and all eight import tables plus companions were reopened and checked in [ROUNDTRIP_CHECK.json](ROUNDTRIP_CHECK.json). Workbook standard cells are numeric; JSON/ledgers retain source literals and missing masks. Taxonomy is source-backed and shared by the three variants, with the S1 Hake row-30 conflict retained separately.

`validate.py`: **{vm}**. Base source diet defects, incomplete variant columns, missing routing/GS and rounded S8 zero biomass are retained findings, not repaired inputs. [MASS_BALANCE.md](MASS_BALANCE.md) includes equation arithmetic and completeness guards; its failure/indeterminate findings do not license source repairs. Canonical source admission and any runtime GE/TE/With Egestion experiments are separate stages owned by the regional assessment.

Reproducible source extraction and converter regression evidence: [extraction evidence](../../../validation_reports/BancArguin_20261003/extraction/evidence_index.json). Source-cell provenance: [diet ledger](DIET_CELL_LEDGER.json), [parameter ledger](PARAMETER_CELL_LEDGER.json), and [published CSV companions](companions/manifest.json).
'''
 (e/'REPORT.md').write_text(report,encoding='utf-8');status.update(installed_skill_workflow=True,companion_tables=22,source_admission='incomplete_source_not_ready',validation=vm,canonical_sha256=sha(d/'model.json'),taxonomy_present=(e/'Taxonomy.xlsx').exists())
 save(e/'EXTRACTION_STATUS.json',status);statuses.append(status)
 (d/'MODEL_PROFILE.md').write_text((e/'MODEL_PROFILE.md').read_text(encoding='utf-8').replace('../../../papers/','../../papers/'),encoding='utf-8')
save(h/'extraction_summary.json',statuses)
manifest=[]
for path in sorted(skill.rglob('*')):
 if path.is_file() and str(path.relative_to(skill)).replace('\\','/') in ['SKILL.md','scripts/write_outputs.py','scripts/database_json.py','scripts/source_fidelity.py','references/published-companions.md','references/workflow.md','references/output-formats.md','references/diet-source-runtime.md']:manifest.append({'path':str(path),'sha256':sha(path)})
save(h/'installed_skill_update.json',manifest)
# Applicable stage inventory: a complete extraction handoff may document an incomplete model.
artifacts=[];required=[]
def add(role,p):
 artifacts.append({'role':role,'path':rel(p),'sha256':sha(p),'availability':'present'});required.append(role)
for page in [8,9,10,15,16]:
 src=root/f'regions/LME_027/papers/CAN-2014/extracted/work/supplement_rendered_page_{page}_250dpi.png';dst=h/f'supplement_visual_page_{page}_250dpi.png'
 if src.exists():shutil.copyfile(src,dst);add('supplement_visual_'+str(page),dst)
for name in ['original_source_inventory.json','original_docx_tables.json','original_docx_styles.json','Table_1-f0424c0e.xls.cells.json','article_table1_coordinate_words.json','original_article_page_4_250dpi.png','original_article_page_5_250dpi.png','prose_sweep.json','old_to_canonical_mapping.json','old_to_source_cell_changes.json','installed_skill_update.json','portable_skill_sync.json']:
 add(name,h/name)
for p in (root/'regions/LME_027/papers/CAN-2014').iterdir():
 if p.is_file() and p.suffix.lower() in ['.pdf','.xls','.docx','.tif']:add('original_'+p.name,p)
for v in ['Base','M30','P30']:
 d=models/f'Guenette2014_BancArguin_{v}_1991';e=d/'extracted_tables';add(v+'_canonical',d/'model.json')
 for name in ['extraction.json','Basic_input.csv','Diet_composition.csv','Landings.csv','Discards.csv','Detritus_fate.csv','Biomass_accumulation.csv','TL.xlsx','Metadata.xlsx','Taxonomy.xlsx','taxonomy_evidence.json','DIET_CELL_LEDGER.json','PARAMETER_CELL_LEDGER.json','SOURCE_CONFLICTS.json','STANZAS.json','REPORT.md','MASS_BALANCE.md','ROUNDTRIP_CHECK.json','SOURCE_FIDELITY_CHECK.json','canonical_reconstructed.xlsx']:
  add(v+'_'+name,e/name)
 for p in sorted((e/'companions').glob('*')):add(v+'_companion_'+p.name,p)
 art={'schema_version':1,'run_id':'BancArguin_20261003_source_reextraction','region_id':'LME_027','model_id':'Guenette2014_BancArguin','variant_id':'Base_M30_P30','source_identity':{'doi':'10.1371/journal.pone.0094742','original_inventory':'original_source_inventory.json'},'computational_input_identity':{'stage':'extraction_only','status':'canonical_source; runtime calculations separately owned'},'methods':[],'required_roles':required,'artifacts':artifacts,'reconciliation':{'fresh_source_to_standard_json':True,'eight_standard_schemas_preserved':True,'companion_and_missing_mask_roundtrip':True,'no_source_normalization':True}}
save(h/'evidence_index.json',art)
checker=root/'tools/skills/original_skill_resources/combined-src/scripts/check_evidence.py'
p=subprocess.run([sys.executable,str(checker),str(h/'evidence_index.json'),'--output',str(h/'completeness.json')],capture_output=True,text=True,encoding='utf-8');assert p.returncode==0,p.stdout[-2000:]
(h/'MASTER_INDEX.md').write_text('# Guénette 2014 source re-extraction\n\n| Variant | Year | Groups | Source status |\n|---|---|---|---|\n'+''.join('| '+v+' | 1991 | 51 | Partial; published defects/unknowns retained |\n' for v in ['Base','M30','P30'])+'\nAll three use the improved installed extraction workflow and retain the eight EwE imports, 22 separate source companion CSVs, canonical JSON, numeric reconstructed workbook, source ledgers, taxonomy and verification. The evidence handoff is complete; the source models are not complete validated computational inputs.\n',encoding='utf-8')
print('FINAL source evidence complete',len(artifacts),'artifacts; canonical hashes',[(x['variant'],x['canonical_sha256']) for x in statuses])
