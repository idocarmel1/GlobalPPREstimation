from pathlib import Path
from pdf2image import convert_from_path
import json,sys
sys.stdout.reconfigure(encoding='utf-8')
p=Path(sys.argv[1]);d=convert_from_path(str(p),dpi=120,thread_count=2)
for i,page in enumerate(d):page.save(p.parent/f'page-{i+1:02}.png')
(p.parent/'render_manifest.json').write_text(json.dumps({'renderer':'independent hidden Word read-only PDF export; bundled Poppler rasterization','pages':len(d),'pdf':p.name,'images':[f'page-{i+1:02}.png' for i in range(len(d))]},indent=2),encoding='utf-8')
print('Rendered pages',len(d))
