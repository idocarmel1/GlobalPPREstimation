from pathlib import Path
import hashlib,json
h=Path(__file__).resolve().parent;t=Path('C:/Users/idoca/.agents/skills/ecopath-extraction/scripts');stage=h/'skill_update/scripts'
base=(t/'database_json.py').read_text(encoding='utf-8')
needle='            ba_val = self._num(g.get("biomass_accum"))\n            ba_known = ba_val is not None'
replacement='            ba_val = self._num(g.get("biomass_accum"))\n            if ba_val is None and b is not None:\n                source_ba_rate = self._num(g.get("biomass_accum_rate"))\n                if source_ba_rate is not None:\n                    ba_val = b * source_ba_rate  # arithmetic only; canonical source form unchanged\n            ba_known = ba_val is not None'
assert needle in base;base=base.replace(needle,replacement)
base=base.replace('f"{g[\'biomass_accum\']} carried")','f"{ba_val} carried (absolute or derived internally from source BA rate)")')
(stage/'database_json.py').write_text(base,encoding='utf-8');(stage/'source_fidelity.py').write_bytes((h/'source_fidelity.py').read_bytes())
for name in ['database_json.py','source_fidelity.py']:(t/name).write_bytes((stage/name).read_bytes())
print('Updated TL source precision and internal rate-form BA arithmetic')
