"""Open the atlas through a read-only server reachable only on this computer."""
from __future__ import annotations

import argparse
import hashlib
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import URLError
from urllib.parse import unquote, urlsplit
from urllib.request import urlopen
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
PORT = 8877
ALLOWED = {'interactive_map', 'regions', 'common_reference_data',
           'original_research_archive', 'Project.xlsx'}


def project_id(root: Path) -> str:
    return hashlib.sha256(str(root.resolve()).encode('utf-8')).hexdigest()


class MapHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory, **kwargs):
        self.project_root = Path(directory).resolve()
        super().__init__(*args, directory=str(self.project_root), **kwargs)

    def log_message(self, *args):
        pass

    def list_directory(self, path):
        self.send_error(404, 'Directory listing is disabled')
        return None

    def send_head(self):
        if self.headers.get('Host', '').split(':', 1)[0].lower() not in {'127.0.0.1', 'localhost'}:
            self.send_error(403, 'Localhost access only')
            return None
        route = unquote(urlsplit(self.path).path)
        if route == '/__map_health':
            payload = json.dumps({'project': project_id(self.project_root)}).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            import io
            return io.BytesIO(payload)
        if route == '/':
            self.send_response(302)
            self.send_header('Location', '/interactive_map/index.html')
            self.end_headers()
            return None
        parts = route.strip('/').split('/')
        resolved = (self.project_root / Path(*parts)).resolve()
        retained_parts = resolved.relative_to(self.project_root).parts if resolved.is_relative_to(self.project_root) else ()
        if (not parts or parts[0] not in ALLOWED
                or any(p.startswith('.') or ':' in p or '\\' in p for p in parts)
                or not resolved.is_relative_to(self.project_root)
                or not retained_parts or retained_parts[0] not in ALLOWED
                or any(p.startswith('.') for p in retained_parts)
                or (parts[0] == 'original_research_archive'
                    and (len(parts) < 2 or parts[1] != 'research'))):
            self.send_error(404, 'Not a published project file')
            return None
        # Require explicit filenames; implicit index selection would bypass the
        # checks above if a directory's index were a link to another location.
        if resolved.is_dir():
            self.send_error(404, 'Use an explicit project filename')
            return None
        return super().send_head()

    def end_headers(self):
        # A real localhost origin is sent for normal interactive OSM tile requests.
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()


def matching_server(root: Path, port: int) -> bool:
    try:
        with urlopen(f'http://127.0.0.1:{port}/__map_health', timeout=1) as response:
            return json.load(response).get('project') == project_id(root)
    except (OSError, URLError, ValueError):
        return False


def make_server(root: Path, port: int = PORT) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(('127.0.0.1', port),
                               partial(MapHandler, directory=str(root)))


def find_or_start(root: Path, ports):
    # Search all candidate ports before binding: a previously occupied earlier
    # port may now be free while this project's server still runs on a later one.
    for port in ports:
        if port and matching_server(root, port):
            return None, port
    for port in ports:
        try:
            server = make_server(root, port)
            return server, server.server_port
        except OSError:
            continue
    raise OSError('No free local map port; use --port with another starting port')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=PORT)
    parser.add_argument('--no-browser', action='store_true', help='Serve without opening a browser')
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error('port must be between 0 and 65535')
    ports = list(range(args.port, min(args.port + 10, 65536))) if args.port else [0]
    server, port = find_or_start(ROOT, ports)
    url = f'http://127.0.0.1:{port}/interactive_map/index.html'
    print('Map available at ' + url, flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    if server is None:
        return
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
