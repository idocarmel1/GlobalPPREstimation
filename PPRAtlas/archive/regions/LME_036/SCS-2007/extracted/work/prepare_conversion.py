from pathlib import Path
import re,json,sys
w=Path(r'C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/קוד/PPR_Ecopath_Atlas/archive/regions/LME_036/SCS-2007/extracted/work')
skill=Path(r'C:/Users/idoca/.agents/skills/ecopath-extraction/scripts')
s=(skill/'database_json.py').read_text(encoding='utf-8')
patches=[
('norm_factor = 1.0 / total_diet_sum if needs_normalization else 1.0','norm_factor = 1.0  # Preserve published diet fractions; extraction rule.'),
('Diet Sum is not 1 ({total_diet_sum:.5f}). Normalizing to 1.0','Diet Sum is not 1 ({total_diet_sum:.5f}). Preserving published fractions'),
('"habitat_area": hab_area,','"habitat_area": str(row.iloc[2]) if not pd.isna(row.iloc[2]) else self.NO_DATA,'),
('"vbk": "0",','"vbk": self.NO_DATA,'),
('"shadow_price": "0",','"shadow_price": self.NO_DATA,'),
('"ge": self.NO_DATA,','"ge": get_val(row.iloc[9])[0],'),
('"ge_input": "false",','"ge_input": get_val(row.iloc[9])[1],'),
('"detritus_fate": self._fmt_float(vals["detritus_fate"])','"detritus_fate": self.NO_DATA if vals["detritus_fate"] == 0.0 else self._fmt_float(vals["detritus_fate"])'),
('with open(output_json, \'w\') as f:',"with open(output_json, 'w', encoding='utf-8') as f:"),
('        base = os.path.basename(filename).replace(\'.json\', \'\')', '''        sibling = os.path.join(os.path.dirname(filename), "Metadata.xlsx")
        if os.path.exists(sibling):
            meta = pd.read_excel(sibling, header=None, dtype=str)
            return dict(zip(meta.iloc[:, 0], meta.iloc[:, 1]))
        base = os.path.basename(filename).replace('.json', '')'''),
("'Ecotrophic Efficiency': parse_val(g.get('ee')),", "'Ecotrophic Efficiency': parse_val(g.get('ee')),\n                'Production / consumption': parse_val(g.get('ge')),")
]
for old,new in patches:
 assert old in s,old
 s=s.replace(old,new)
(w/'database_json_preserve_source.py').write_text(s,encoding='utf-8')
import difflib
(w/'converter_changes.patch').write_text(''.join(difflib.unified_diff((skill/'database_json.py').read_text(encoding='utf-8').splitlines(True),s.splitlines(True),fromfile='installed/database_json.py',tofile='work/database_json_preserve_source.py')),encoding='utf-8')
# Cached-text equivalent of the skill's full prose sweep, with all page locations retained.
sys.path.insert(0,str(skill))
from prose_sweep import FAMILIES,sentences
pages=(w/'thesis.txt').read_text(encoding='utf-8').split('\f')
hits=[]
for n,p in enumerate(pages,1):
 for sentence in sentences(p):
  fam=[k for k,patterns in FAMILIES.items() if any(re.search(pattern,sentence,re.I) for pattern in patterns)]
  if fam and (re.search(r'\d',sentence) or 'pointers' in fam):
   hits.append({'pdf_page':n,'printed_page':n-15 if n>15 else 'front matter','families':fam,'text':sentence})
(w/'prose_sweep_all_numbers.json').write_text(json.dumps(hits,indent=2,ensure_ascii=False),encoding='utf-8')
for h in hits:
 if any(f in h['families'] for f in ['assimilation','accumulation']) and (185<=h['pdf_page']<=228 or h['pdf_page']>=337): print(h)
