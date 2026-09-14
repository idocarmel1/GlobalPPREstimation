import unittest
from atlas.files import validate_bytes

class FileTests(unittest.TestCase):
    def test_html_masquerading_as_pdf_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_bytes(b'<html>Access denied</html>','.pdf')
    def test_html_masquerading_as_csv_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_bytes(b'<html>error,failed</html>\n1,2','.csv')
    def test_diet_matrix_is_valid_csv(self):
        self.assertEqual(validate_bytes(b'prey,predator\n1,0.2','.csv')['rows'],2)
