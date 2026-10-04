import tempfile,unittest
from pathlib import Path
from io import BytesIO
from unittest.mock import patch
from requests import Response
from pypdf import PdfWriter
from atlas.files import validate_bytes
import download_sources

class ArchivedPDFTests(unittest.TestCase):
    def test_archived_headers_are_removed_and_original_is_preserved(self):
        writer=PdfWriter();writer.add_blank_page(width=72,height=72)
        stream=BytesIO();writer.write(stream);pdf=stream.getvalue()
        prefix=b'HTTP/1.1 200 OK\r\nContent-Type: application/pdf\r\n\r\n'
        response=Response();response._content=prefix+pdf
        with tempfile.TemporaryDirectory() as temp,patch.object(download_sources,'ROOT',Path(temp)):
            evidence=download_sources.unwrap_archived_pdf(response)
            self.assertEqual(response.content,pdf)
            self.assertEqual((Path(temp)/evidence['raw_response_path']).read_bytes(),prefix+pdf)
            self.assertEqual(validate_bytes(response.content,'.pdf')['pages'],1)

    def test_html_with_embedded_pdf_marker_is_not_accepted(self):
        response=Response();response._content=b'<html>%PDF-1.4 fake %%EOF</html>'
        self.assertEqual(download_sources.unwrap_archived_pdf(response),{})
        with self.assertRaises(ValueError):validate_bytes(response.content,'.pdf')

if __name__=='__main__':unittest.main()
