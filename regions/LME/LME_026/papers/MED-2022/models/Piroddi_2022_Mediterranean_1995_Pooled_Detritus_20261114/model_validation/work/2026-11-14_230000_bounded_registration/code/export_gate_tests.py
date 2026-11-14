from pathlib import Path
run=Path(__file__).resolve().parents[1]
src=(run/'code/test_review_candidate_gate.py').read_text(encoding='utf-8-sig')
a=src.index('RUN=Path(__file__)');b=src.index('from tools.workflow_checks',a)
src=src[:a]+'''sys.path.insert(0,str(ROOT))
from tools.project_core.registry import review_candidates as candidate_row
from tools.project_core.maps import build_html as build
'''+src[b:]
src=src.replace("tempfile.TemporaryDirectory(dir=RUN/'qa')","tempfile.TemporaryDirectory()")
src=src.replace('Copy into shared checks after replacing proposed module loader with normal import.','Install in tools/workflow_checks/validation/test_review_candidate_gate.py.')
compile(src,'test_review_candidate_gate.py','exec')
(run/'outputs/test_review_candidate_gate.installable.py').write_text(src,encoding='utf-8')
print('Installable regression module generated')
