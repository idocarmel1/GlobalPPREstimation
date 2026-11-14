import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
import sys
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from tools.project_core.validation.researcher_review import table_rows, sha
RUN=Path(__file__).resolve().parents[1]
PROPOSAL=RUN.parent/'2026-11-14_201300_disqualification_binding/outputs/proposed_central_metadata.json'

class CandidateTests(unittest.TestCase):
    def test_exact_insertion_preserves_every_other_part(self):
        from candidate_row import add_review_candidate
        proposal=json.loads(PROPOSAL.read_text())
        with tempfile.TemporaryDirectory(dir=RUN/'qa') as tmp:
            project=Path(tmp)/'Project.xlsx'
            project.write_bytes((ROOT/'Project.xlsx').read_bytes())
            with zipfile.ZipFile(project) as z:
                before={n:z.read(n) for n in z.namelist()}
            add_review_candidate(project, ROOT, proposal['row'], proposal['provenance']['canonical_sha256'])
            with zipfile.ZipFile(project) as z:
                after={n:z.read(n) for n in z.namelist()}
                rows=[r for _,r in table_rows(z,'Models & coverage','Models')[3]]
            matches=[r for r in rows if r.get('model_id')==proposal['row']['model_id']]
            self.assertEqual(len(matches),1)
            self.assertEqual(matches[0]['selected'],'0')
            self.assertIsNone(matches[0]['production_eligible'])
            changed=[n for n in before if before[n]!=after[n]]
            self.assertEqual(len(changed),2)
            self.assertTrue(any(n.startswith('xl/tables/') for n in changed))
            with self.assertRaises(ValueError):
                add_review_candidate(project,ROOT,proposal['row'],proposal['provenance']['canonical_sha256'])

    def test_rejects_selection_and_bad_hash_without_writes(self):
        from candidate_row import add_review_candidate
        proposal=json.loads(PROPOSAL.read_text())
        with tempfile.TemporaryDirectory(dir=RUN/'qa') as tmp:
            project=Path(tmp)/'Project.xlsx'
            project.write_bytes((ROOT/'Project.xlsx').read_bytes()); before=sha(project)
            for row,digest in [(dict(proposal['row'],selected=True),proposal['provenance']['canonical_sha256']),(proposal['row'],'0'*64),(dict(proposal['row'],production_eligible=True),proposal['provenance']['canonical_sha256'])]:
                with self.assertRaises(ValueError):add_review_candidate(project,ROOT,row,digest)
                self.assertEqual(sha(project),before)

if __name__=='__main__':unittest.main()

