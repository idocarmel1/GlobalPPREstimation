from pathlib import Path
import json,re
w=Path(r'C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/קוד/PPR_Ecopath_Atlas/archive/regions/LME_036/SCS-2007/extracted/work');out=w.parent
(out/'MULTISTANZA.md').write_text('''# Published multi-stanza parameters

Applies to both periods. Source: Appendix Table A6.3, printed p. 330 / PDF p. 345; visually verified at 200 dpi. These fields are outside the eight-file import schema and are preserved here for reconstruction of native stanza linkages.

| Source group | Juvenile group | Adult group | Stanzas | K (/year) | Recruitment power | Wmaturity/Winf | Adult boundary |
|---|---|---|---|---|---|---|---|
| Hairtails (trichiurids) | 16 | 17 | 2 | 0.41 | 1 | 0.0007 | 18 months; printed p. 329 / PDF344 |
| Croakers (>30 cm) | 22 | 23 | 2 | 0.36 | 1 | 0.15 | 24 months; printed p. 334 / PDF349 |
| Demersal fish (>30 cm) | 25 | 26 | 2 | 0.31 | 1 | 0.13 | 18 months initially stated, but later juvenile biomass described as below age2; printed p. 336 / PDF351 |
| Pelagic fish (>30 cm) | 30 | 31 | 2 | 0.59 | 1 | 0.13 | 18 months; printed p. 339 / PDF354 |

Footnotes: hairtail K and Wmaturity/Winf are from FishBase; recruitment power1 is explicitly identified as the default adopted by the author. Croaker K uses26 stocks and maturity ratio uses59 stocks of large croakers. Demersal parameters use33 species and pelagic parameters23 species. Numbers are transcribed, including the unusually small hairtail maturity ratio0.0007.

No native multi-stanza links have been built or tested. The demersal age boundary is conflicting and must be resolved before assigning stanza cutoffs in a native model. The summary table's juvenile/adult biomasses and rates were retained without recomputing them from these settings.
''',encoding='utf-8')
# Improve prose spacing without touching machine-readable source data.
for p in list(out.glob('*.md'))+list(out.glob('*/REPORT.md')):
 s=p.read_text(encoding='utf-8')
 s=re.sub(r'\b(Table|Appendix|Figure|PDF|group|groups|periods|with|for|and|contains|than|all|power|uses|parameters|ratio|is|sum|total|by|of|exactly|including|no|No)(?=\d)',r'\1 ',s)
 s=re.sub(r'(?<=\d)(?=(?:groups|group|consumer|warnings|warning|errors|error|stocks|species)\b)',' ',s)
 s=s.replace('±0.01','±0.01').replace('beyond0.05','beyond 0.05').replace('are0.8500','are 0.8500').replace('is0.8500','is 0.8500').replace('sum0.8501','sum 0.8501').replace('is7.7375','is 7.7375').replace('total7.736','total 7.736').replace('to7.738','to 7.738').replace('range0.','range 0.').replace('No0.35','No 0.35').replace('100%','100%').replace('that100%','that 100%').replace('with3','with 3').replace('including38','including 38').replace('reported410','reported 410').replace('assumption0.2','assumption 0.2').replace('ratio1.30','ratio 1.30').replace('use-9999','use -9999').replace('B0.0002','B 0.0002').replace('P/B0.100','P/B 0.100').replace('production0.00002','production 0.00002').replace('F0.05','F 0.05').replace('imply0.00001','imply 0.00001').replace('F0.01','F 0.01').replace('Some1970s','Some 1970s').replace('Several1970s','Several 1970s')
 p.write_text(s,encoding='utf-8')
print('Supplemental stanza settings and report text finalized.')
