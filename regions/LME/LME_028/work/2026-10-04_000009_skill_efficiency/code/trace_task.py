"""Record actual isolated skill-trial reads; no scientific/project mutation."""
import argparse, hashlib, json, sys, time
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').exists())
sys.path.insert(0, str(ROOT))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trace', type=Path, required=True)
    sub = parser.add_subparsers(dest='operation', required=True)
    read = sub.add_parser('read'); read.add_argument('path', type=Path)
    book = sub.add_parser('book'); book.add_argument('path', type=Path)
    book.add_argument('--sheet', required=True); book.add_argument('--table', required=True)
    book.add_argument('--selective', action='store_true')
    docx = sub.add_parser('docx'); docx.add_argument('path', type=Path)
    args = parser.parse_args(); path = args.path.resolve(); started = time.perf_counter()
    data = path.read_bytes(); fingerprint = hashlib.sha256(data).hexdigest()
    if args.operation == 'read':
        output = data.decode('utf-8-sig'); parses = 0
    elif args.operation == 'docx':
        import zipfile
        from xml.etree import ElementTree as E
        with zipfile.ZipFile(path) as archive:
            document = E.fromstring(archive.read('word/document.xml'))
            paragraphs = [''.join(n.itertext()) for n in document.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')]
            links = [node.attrib for node in E.fromstring(archive.read('word/_rels/document.xml.rels'))
                     if node.get('Type', '').endswith('/hyperlink')]
        output = json.dumps({'text_segments': paragraphs, 'hyperlinks': links}, ensure_ascii=False)
        parses = 0
    else:
        from tools.project_core.workbooks.workbooks import read_book
        tables = read_book(path, sheets=[args.sheet]) if args.selective else read_book(path)
        if args.table not in tables.get(args.sheet, {}): raise ValueError('Requested table is absent')
        output = json.dumps(tables[args.sheet][args.table], ensure_ascii=False, allow_nan=False)
        parses = 1
    display_path = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()
    event = {'operation': args.operation, 'path': display_path,
             'sha256': fingerprint, 'bytes': len(data), 'workbook_parses': parses,
             'selected_sheets': [args.sheet] if args.operation == 'book' and args.selective else None,
             'elapsed_seconds': time.perf_counter() - started,
             'engine_calls': 0, 'render_calls': 0, 'project_writes': 0}
    args.trace.parent.mkdir(parents=True, exist_ok=True)
    with args.trace.open('a', encoding='utf-8') as target:
        target.write(json.dumps(event, ensure_ascii=False) + '\n')
    print(output)

if __name__ == '__main__': main()
