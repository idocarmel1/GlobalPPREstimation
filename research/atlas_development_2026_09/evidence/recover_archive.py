from pathlib import Path
import json, shutil
from atlas.files import recover_archive

root=Path(__file__).resolve().parent
source=root.parent/'article_map_version_1'
for original,destination in [('ecopath_all84_interactive_map.html','original_map.html'),('generate_ecopath_all84_map.py','original_generator.py'),('Ecopath_all84_summary.xlsx','Ecopath_all84_summary.xlsx')]:
    shutil.copy2(source/original,root/'inputs'/destination)
catalog=json.loads((root/'inputs/original_catalog.json').read_text(encoding='utf-8'))
print(json.dumps(recover_archive(root,source/'Ecopath_all84_source_library.zip',catalog)))
