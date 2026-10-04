import json, tempfile, unittest
from pathlib import Path
from tools.project_core.registry.discovery import discover_regions, discover_models, resolve_model

class DiscoveryTests(unittest.TestCase):
    def test_grouped_regions_and_model_ownership(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for kind in ['LME','EEZ','HS']:
                unit=kind+'_001'; region=root/'regions'/kind/unit;region.mkdir(parents=True)
                (region/(unit+'.xlsx')).write_bytes(b'workbook')
                (region/'appendix.xlsx').write_bytes(b'appendix')
                for rel in ['papers/P/models/A/model.json','papers/P/models/B/model.json','ecobase/C/model.json','work/run/model.json']:
                    p=region/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('{}')
                self.assertEqual(set(discover_models(region)),{'A','B','C'})
                self.assertEqual(resolve_model(region,'B'),region/'papers/P/models/B/model.json')
            self.assertEqual(set(discover_regions(root)),{'LME_001','EEZ_001','HS_001'})
    def test_duplicate_ids_and_path_escape_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=Path(tmp)
            for rel in ['papers/P/models/A/model.json','ecobase/A/model.json']:
                p=r/rel;p.parent.mkdir(parents=True);p.write_text('{}')
            with self.assertRaisesRegex(ValueError,'Duplicate model'):discover_models(r)
            with self.assertRaisesRegex(ValueError,'identity'):resolve_model(r,'../outside')
