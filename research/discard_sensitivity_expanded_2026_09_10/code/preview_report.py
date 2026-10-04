"""Private loopback-only preview on a dynamically assigned unused port."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import json,os
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    state=dict(pid=os.getpid(),host='127.0.0.1',port=server.server_port,url=f'http://127.0.0.1:{server.server_port}/report.html')
    (ROOT/'verification/preview_server.json').write_text(json.dumps(state,indent=2),encoding='utf-8')
    print(state,flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
