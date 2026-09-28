from pathlib import Path
import sys,shutil,json
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book,write_book,overview,sha
from regional import set_setting
from run_region import prepare_selection
P=ROOT/'regions/LME_050/LME_050.xlsx';D=Path(__file__).resolve().parent
selected='50_502013_Coastal_Kyoto_Inoue_(2013)';comparison='50_501985_Coastal_Kyoto_Inoue_(1985)'
b=read_book(P);old=overview(b)
archive=P.parent/'models/previous_results';archive.mkdir(exist_ok=True)
before=archive/f'LME_050_before_user_2013_selection_{sha(P)[:12]}.xlsx';shutil.copy2(P,before)
rationale='User selected the 2013 model because it is newer; the 1985 model is also a good model for comparison. This is a temporal preference, not a finding that 2013 is numerically superior. Source SOJ-2023 was specified because it is the only available paper. Both years retain the unresolved year-specific diet-matrix ambiguity and documented loader transformations; direct GE, TE and With Egestion diagnostics remain WARN.'
set_setting(b,'selected_model_id',selected);set_setting(b,'model_path',f'models/{selected}/model.json');set_setting(b,'selection_rationale',rationale)
set_setting(b,'selected_paper_ids','SOJ-2023__LME_050')
set_setting(b,'source_note',f'1985 retained as an explicitly good comparison candidate: {comparison}. Coastal Kyoto model (2230 km²), partial LME coverage. One published diet matrix for both years despite year-specific diet prose. Missing source GS, BA, migration and routing are documented separately from loaded defaults/completions. Exact source admission remains unverified; selection does not remove these caveats.')
prepare_selection(b,P);write_book(P,b)
check=overview(read_book(P));assert check['selected_model_id']==selected and check['selection_rationale']==rationale
for sheet in ['Catch','Classic PPR','NPP']:assert read_book(before)[sheet]==read_book(P)[sheet],sheet
(D/'USER_SELECTION_CONFIRMATION.md').write_text(f'''# LME050 user selection recorded

Selected: **{selected}**, because **2013 is newer**.

Retained good comparison candidate: **{comparison}**. This does not claim numerical superiority for 2013. The GE group-comparison report is independently verified and complete.

The regional Overview now owns this selection and rationale. Previous workbook retained at `{before.relative_to(P.parent).as_posix()}`. `prepare_selection` cleared model-dependent results and left this selection pending its selected-model workflow. Catch, Classic PPR and NPP blocks were verified unchanged.

Both candidates' diet-matrix uncertainty, source-admission limits and loader transformations remain explicit; all three direct GE/TE/With Egestion statuses remain WARN. No central workbook changes made.
''',encoding='utf8')
print(json.dumps(check,ensure_ascii=False,indent=2))
