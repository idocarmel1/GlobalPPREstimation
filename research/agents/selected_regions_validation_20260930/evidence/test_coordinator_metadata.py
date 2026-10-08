"""Guard reviewed article-footprint insertion against stale or unrelated writes."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('reviewed_metadata',HERE/'apply_reviewed_metadata.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)

class GeometryInsertionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'reviewed.geojson'
        self.geometry={'type':'Polygon','coordinates':[[[0,0],[1,0],[1,1],[0,1],[0,0]]]}
        self.path.write_text(json.dumps({'type':'Feature','properties':{},'geometry':self.geometry}),encoding='utf-8')
        self.rows=M.chunks('region:LME_024',{'type':'Polygon','coordinates':[[[-2,0],[-1,0],[-1,1],[-2,0]]]})
        self.book={'Map geography':{'Geometry':(['key','part','json'],copy.deepcopy(self.rows))}}
        self.patch={'key':'article:reviewed','action':'insert','expected_old_geometry_sha256':None,
                    'replacement_geojson':str(self.path),'replacement_file_sha256':M.sha(self.path),
                    'replacement_geometry_sha256':hashlib.sha256(json.dumps(self.geometry,sort_keys=True,separators=(',',':')).encode()).hexdigest()}

    def test_absent_reviewed_article_is_added_without_changing_region_chunks(self):
        checks={};M.apply_geometry_patches(self.book,[self.patch],checks)
        rows=self.book['Map geography']['Geometry'][1]
        self.assertEqual([r for r in rows if r[0]=='region:LME_024'],self.rows)
        self.assertEqual(M.unchunks(rows)['article:reviewed'],self.geometry)
        self.assertEqual(checks[self.path],self.patch['replacement_file_sha256'])

    def test_concurrent_existing_article_rejects_insertion_without_mutation(self):
        self.book['Map geography']['Geometry'][1].extend(M.chunks('article:reviewed',self.geometry))
        before=copy.deepcopy(self.book)
        with self.assertRaises(ValueError):M.apply_geometry_patches(self.book,[self.patch],{})
        self.assertEqual(self.book,before)

    def test_insert_requires_explicit_absence_precondition(self):
        for value in ['missing','unexpected_hash']:
            patch=copy.deepcopy(self.patch)
            if value=='missing':patch.pop('expected_old_geometry_sha256')
            else:patch['expected_old_geometry_sha256']=value
            before=copy.deepcopy(self.book)
            with self.assertRaises(ValueError):M.apply_geometry_patches(self.book,[patch],{})
            self.assertEqual(self.book,before)

    def test_changed_source_and_non_article_key_rejected_without_mutation(self):
        for field,value in [('replacement_file_sha256','stale'),('key','region:new')]:
            patch={**self.patch,field:value};before=copy.deepcopy(self.book)
            with self.assertRaises(ValueError):M.apply_geometry_patches(self.book,[patch],{})
            self.assertEqual(self.book,before)

    def test_existing_replace_and_remove_keep_other_chunks(self):
        rows=self.book['Map geography']['Geometry'][1]
        old={'type':'Polygon','coordinates':[[[5,5],[6,5],[6,6],[5,5]]]}
        rows.extend(M.chunks('article:reviewed',old))
        patch={**self.patch,'action':'replace','expected_old_geometry_sha256':M.geometry_digest(old)}
        M.apply_geometry_patches(self.book,[patch],{})
        self.assertEqual(M.unchunks(self.book['Map geography']['Geometry'][1])['article:reviewed'],self.geometry)
        patch={'key':'article:reviewed','action':'remove','expected_old_geometry_sha256':M.geometry_digest(self.geometry)}
        M.apply_geometry_patches(self.book,[patch],{})
        self.assertEqual(self.book['Map geography']['Geometry'][1],self.rows)

if __name__=='__main__':unittest.main()
