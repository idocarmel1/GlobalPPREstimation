"""Guard reviewed article replacements against stale or collateral changes."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import apply_reviewed_metadata as subject


class ReviewedGeometry(unittest.TestCase):
    def test_replace_remove_preserve_other_chunks_and_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old_root = subject.ROOT
            subject.ROOT = root
            try:
                old = {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]]}
                new = {"type": "Polygon", "coordinates": [[[0, 0], [2, 0], [2, 1], [0, 0]]]}
                source = root / "review.geojson"
                source.write_text(json.dumps({"type": "Feature", "geometry": new, "properties": {}}), encoding="utf-8")
                header = ["key", "chunk", "json"]
                rows = subject.chunks("region", old, 30) + subject.chunks("article:replace", old, 30) + subject.chunks("article:remove", old, 30)
                book = {"Map geography": {"Geometry": (header, copy.deepcopy(rows))}}
                patches = [
                    {"key": "article:replace", "action": "replace", "expected_old_geometry_sha256": subject.geometry_digest(old),
                     "replacement_geojson": "review.geojson", "replacement_file_sha256": subject.sha(source),
                     "replacement_geometry_sha256": subject.geometry_digest(new)},
                    {"key": "article:remove", "action": "remove", "expected_old_geometry_sha256": subject.geometry_digest(old)},
                ]
                checks = {}
                receipt = subject.apply_geometry_patches(book, patches, checks)
                actual = subject.unchunks(book["Map geography"]["Geometry"][1])
                self.assertEqual(actual, {"region": old, "article:replace": new})
                self.assertEqual([r for r in book["Map geography"]["Geometry"][1] if r[0] == "region"], [r for r in rows if r[0] == "region"])
                self.assertEqual(checks[source], subject.sha(source))
                self.assertEqual(len(receipt), 2)
                untouched = copy.deepcopy(book)
                with self.assertRaisesRegex(ValueError, "Geometry changed"):
                    subject.apply_geometry_patches(book, patches, {})
                self.assertEqual(book, untouched)
            finally:
                subject.ROOT = old_root

    def test_reject_non_article_key(self):
        with self.assertRaisesRegex(ValueError, "article"):
            subject.apply_geometry_patches({"Map geography": {"Geometry": (["key", "chunk", "json"], [])}}, [{"key": "LME_003"}], {})


if __name__ == "__main__":
    unittest.main()
