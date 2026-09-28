"""A plain Windows Python invocation must preserve Unicode scientific names."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def test_wrapper_enables_utf8_for_loader_and_workers(tmp_path):
    root = Path(__file__).resolve().parents[1]
    (tmp_path / 'tools').mkdir()
    (tmp_path / 'PPREstimation').mkdir()
    shutil.copy2(root / 'tools/run_sppr.py', tmp_path / 'tools/run_sppr.py')
    (tmp_path / 'PPREstimation/create_PPRS_excel.py').write_text(
        "import json, sys, os\nfrom pathlib import Path\n"
        "def run_directory(json_dir, out_dir, **kwargs):\n"
        " data=json.loads(next(Path(json_dir).glob('*.json')).read_text())\n"
        " data.update(utf8=sys.flags.utf8_mode, worker_env=os.environ.get('PYTHONUTF8'))\n"
        " Path(out_dir,'result.json').write_text(json.dumps(data),encoding='utf-8')\n"
        " return {'n_written':1,'n_models':1}\n", encoding='utf-8')
    source = tmp_path / 'models'
    source.mkdir()
    (source / 'one.json').write_text(json.dumps({'name':'Pelagic fish (≤ 30 cm)'}, ensure_ascii=False), encoding='utf-8')
    out = tmp_path / 'out'
    env = dict(os.environ, PYTHONUTF8='0')
    result = subprocess.run([sys.executable, '-X', 'utf8=0', str(tmp_path / 'tools/run_sppr.py'),
                             '--models','one','--json-dir',str(source),'--out',str(out)], env=env, capture_output=True)
    assert result.returncode == 0, result.stderr.decode('utf-8', errors='replace')
    data = json.loads((out / 'result.json').read_text(encoding='utf-8'))
    assert data['utf8'] == 1
    assert data['worker_env'] == '1'
    assert data['name'] == 'Pelagic fish (≤ 30 cm)'
