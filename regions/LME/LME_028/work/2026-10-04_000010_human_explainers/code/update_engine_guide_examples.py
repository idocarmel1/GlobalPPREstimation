"""Replace unavailable example data paths; preserve equations and method settings."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
QA = Path(__file__).resolve().parent.parent / 'qa'
path = ROOT / 'explainers/PPREstimation/USER_GUIDE.md'
changes = [
    ('| `model_input` | `int` | **Legacy API**: a model number; data is pulled from the bundled `real_models/SpeciesGroups.json` / diet data. |',
     '| `model_input` | `int` | Integer-registry API, requiring separately supplied registry/diet data. Those datasets are unavailable in this checkout; use a canonical JSON path for current project models. |'),
    ('> **Project ownership:** current regional models live under the grouped region/paper/model or regional EcoBase layout in structure.md. Shared engine source models under real_models/ are reference inputs; toy-model examples are engine tests, not regional candidates.',
     '> **Project model inputs:** current models live under the grouped region/paper/model or regional EcoBase layout in [project layout](../structure.md). Use the canonical `model.json` path from the selected model. The engine\'s integer registry and old Iceland/Humboldt example datasets are not supplied here. Toy models illustrate the API; they are not regional candidates.'),
    ('model = PPRCalculator(model_number)        # e.g. PPRCalculator(227)\r\nmodel = PPRCalculator("real_models/EwE_jsons/227_227_Iceland_(1950).json")',
     '# model_json: string path to the chosen canonical model.json.\r\n# audited_settings: actual recorded loader/calculator settings for that model.\r\nmodel = PPRCalculator(model_json, **audited_settings)'),
    ('md = ModelData("real_models/EwE_jsons/13_10013_Humboldt_Current_(1995-2004).json")\r\n  model = PPRCalculator.from_modeldata(md)',
     'md = ModelData(model_json)\r\n  model = PPRCalculator.from_modeldata(md, **audited_settings)'),
    ('# 1. Load and complete a model.\r\nmodel = PPRCalculator(227)',
     '# 1. Use the chosen canonical JSON and its actual audited settings.\r\nmodel = PPRCalculator(model_json, **audited_settings)'),
    ('## 9. End-to-end example\r\n\r\n```python',
     '## 9. End-to-end example\r\n\r\nThis is a library illustration covering several scientific methods. Supply `model_json` and `audited_settings` as described in section 4. Apply only the methods/configurations appropriate to the model and your research scope; openness sensitivity and Monte Carlo are separate from an ordinary regional refresh. Construction can fail, as explained in [current limitations](../limitations.md). This example does not adopt results into regional workbooks.\r\n\r\n```python'),
]
raw = path.read_bytes()
for before, after in changes:
    assert raw.count(before.encode('utf8')) == 1, before
    raw = raw.replace(before.encode('utf8'), after.encode('utf8'))
path.write_bytes(raw)
proof = {'source': path.relative_to(ROOT).as_posix(), 'changes': [{'before': a, 'after': b} for a,b in changes],
         'scope': 'Unavailable example dataset paths and input applicability only; no scientific equations, diagnostic thresholds, solver options or numerical execution changed.'}
(QA / 'engine_guide_example_changes.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print('Six precise API-context/example replacements; original remaining bytes preserved.')
