import csv
from pathlib import Path

class SourcePaths:
    """Resolve historical references without rewriting scientific source workbooks."""
    def __init__(self,root):
        self.root=Path(root);self.paths={}
        for file,old,new in [
            ('common_reference_data/provenance/source_paths.csv','original_path','retained_path')]:
            path=self.root/file
            if path.exists():
                with path.open(encoding='utf-8-sig',newline='') as source:
                    self.paths.update({r[old]:r[new] or None for r in csv.DictReader(source)})

    def resolve(self,value):
        normalized=value.replace('\\','/')
        candidates=[normalized,normalized.removeprefix('../'),'PPRAtlas/'+normalized]
        match=next((p for p in candidates if p in self.paths),None)
        if match is None:
            return value
        seen=set()
        while match in self.paths:
            target=self.paths[match]
            if target is None:return None
            if target==match:return target
            if match in seen:raise ValueError(f'cyclic source relocation: {value}')
            seen.add(match);match=target
        return match

    def rewrite(self,value,key=None):
        if isinstance(value,dict):return {k:self.rewrite(v,k) for k,v in value.items()}
        if isinstance(value,list):
            rewritten=[self.rewrite(v,key) for v in value]
            # Removed interface artifacts retain their audit record, but are not links.
            return [v for v in rewritten if not isinstance(v,dict) or 'relative_path' not in v or v['relative_path'] is not None]
        if not isinstance(value,str):return value
        path=self.resolve(value)
        if path is not None and path!=value and key=='relative_path':return '../'+path.removeprefix('../')
        return path
