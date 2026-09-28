import tempfile
import threading
import unittest
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from open_map import make_server, matching_server, find_or_start


class MapServerTests(unittest.TestCase):
    def test_local_read_only_files_and_source_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ['interactive_map', 'regions', '.git', 'tools']:
                (root / name).mkdir()
            (root / 'interactive_map/index.html').write_text('map')
            (root / 'regions/paper.pdf').write_bytes(b'paper')
            (root / 'regions/folder').mkdir()
            (root / 'regions/folder/index.html').write_text('implicit index must not be served')
            (root / '.git/config').write_text('private')
            (root / 'tools/private.txt').write_text('private')
            server = make_server(root, 0)
            self.assertEqual(server.server_address[0], '127.0.0.1')
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            base = f'http://127.0.0.1:{server.server_port}'
            try:
                self.assertTrue(matching_server(root, server.server_port))
                self.assertFalse(matching_server(root / 'other', server.server_port))
                # An earlier available port must not create a second hidden server.
                reused, port = find_or_start(root, [0, server.server_port])
                self.assertIsNone(reused)
                self.assertEqual(port, server.server_port)
                with urlopen(base + '/') as response:
                    self.assertEqual(response.read(), b'map')
                    self.assertEqual(response.headers['Referrer-Policy'], 'strict-origin-when-cross-origin')
                with urlopen(base + '/regions/paper.pdf') as response:
                    self.assertEqual(response.read(), b'paper')
                for route in ['/regions/', '/regions/folder/', '/.git/config', '/tools/private.txt',
                              '/regions/%2e%2e/.git/config', '/regions/%5c..%5c.git/config']:
                    with self.assertRaises(HTTPError) as error:
                        urlopen(base + route)
                    self.assertEqual(error.exception.code, 404, route)
                with self.assertRaises(HTTPError) as error:
                    urlopen(Request(base + '/regions/paper.pdf', data=b'changed', method='POST'))
                self.assertEqual(error.exception.code, 501)
                with self.assertRaises(HTTPError) as error:
                    urlopen(Request(base + '/', headers={'Host': 'external.example'}))
                self.assertEqual(error.exception.code, 403)
                self.assertEqual((root / 'regions/paper.pdf').read_bytes(), b'paper')
            finally:
                server.shutdown()
                worker.join()
                server.server_close()
