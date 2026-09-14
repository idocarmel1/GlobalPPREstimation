"""Validate source files and recover ZIP members using short, generated paths."""
from pathlib import Path
from io import BytesIO
import csv, hashlib, json, zipfile
from pypdf import PdfReader

def validate_bytes(content, suffix):
    suffix = suffix.lower()
    if suffix in ('.png','.jpg','.jpeg','.tif','.tiff'):
        from PIL import Image
        with Image.open(BytesIO(content)) as im:
            size=im.size;im.verify()
        return {'validation':'Supplement image decoded','image_size':size}
    if suffix in ('.doc','.xls','.mdb'):
        import olefile
        if not olefile.isOleFile(BytesIO(content)):raise ValueError('Not a structured Office compound file')
        with olefile.OleFileIO(BytesIO(content)) as doc:
            streams=doc.listdir()
            if suffix=='.doc' and not doc.exists('WordDocument'):raise ValueError('Missing WordDocument stream')
            if suffix=='.xls' and not (doc.exists('Workbook') or doc.exists('Book')):raise ValueError('Missing Excel workbook stream')
        return {'validation':'Office compound-file structure checked; content not load-tested','streams':len(streams)}
    if suffix == '.pdf':
        if not content.lstrip().startswith(b'%PDF-'):
            raise ValueError('Response is not a PDF')
        reader = PdfReader(BytesIO(content))
        pages = len(reader.pages)
        if not pages:
            raise ValueError('PDF has no pages')
        return {'validation':'PDF parsed','pages':pages}
    if suffix in ('.xlsx','.docx','.zip'):
        with zipfile.ZipFile(BytesIO(content)) as z:
            bad = z.testzip()
            if bad:
                raise ValueError(f'Corrupt member: {bad}')
            if suffix=='.xlsx' and 'xl/workbook.xml' not in z.namelist():
                raise ValueError('Missing XLSX workbook')
            if suffix=='.docx' and 'word/document.xml' not in z.namelist():
                raise ValueError('Missing DOCX document')
        return {'validation':'ZIP structure and CRC checked'}
    if suffix == '.csv':
        encoding='utf-8-sig'
        try:text = content.decode(encoding)
        except UnicodeDecodeError:
            encoding='cp1252';text=content.decode(encoding)
        if '<html' in text[:1000].lower() or '<!doctype' in text[:1000].lower():
            raise ValueError('HTML response instead of CSV')
        rows = list(csv.reader(text.splitlines()))
        if len(rows)<2 or max(map(len,rows))<2:
            raise ValueError('CSV lacks tabular data')
        return {'validation':'CSV parsed','encoding':encoding,'rows':len(rows)}
    raise ValueError(f'Unvalidated source file format: {suffix}')

def save_material(root, content, suffix):
    details = validate_bytes(content,suffix)
    digest = hashlib.sha256(content).hexdigest()
    relative = Path('archive/files')/(digest[:20]+suffix.lower())
    destination = root/relative
    destination.parent.mkdir(parents=True,exist_ok=True)
    if not destination.exists():
        destination.write_bytes(content)
    return dict(relative_path=relative.as_posix(),sha256=digest,size_bytes=len(content),status='downloaded_verified',**details)

def recover_archive(root, source_zip, catalog):
    lookup = {f['relative_path']:f for f in catalog['files']}
    records, members = [], []
    with zipfile.ZipFile(source_zip) as z:
        for number, info in enumerate(z.infolist()):
            if info.is_dir():
                continue
            relative = info.filename.split('/',1)[-1]
            content = z.read(info)
            original = lookup.get(relative)
            if original:
                try:
                    record = save_material(root,content,Path(info.filename).suffix)
                except Exception as exc:
                    digest = hashlib.sha256(content).hexdigest()
                    destination = f'archive/files/{digest[:20]}{Path(info.filename).suffix}'
                    (root/destination).parent.mkdir(parents=True,exist_ok=True)
                    (root/destination).write_bytes(content)
                    record = {'relative_path':destination,'sha256':digest,'size_bytes':len(content),'status':'validation_failed','validation_error':str(exc)}
                if record['sha256'] != original['sha256']:
                    raise ValueError(f'Source hash mismatch: {relative}')
                record.update({k:v for k,v in original.items() if k not in record})
                record['original_relative_path'] = relative
                records.append(record)
                destination = record['relative_path']
            else:
                destination = f'inputs/legacy/{number:04d}{Path(info.filename).suffix}'
                path = root/destination
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(content)
            members.append({'original_path':info.filename,'recovered_path':destination,'size_bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()})
    if len(records)!=len(lookup):
        raise ValueError('Not all original verified material records were recovered')
    (root/'inputs/zip_recovery.json').write_text(json.dumps(members,indent=2),encoding='utf-8')
    (root/'inputs/recovered_files.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    return {'members':len(members),'recovered_material_records':len(records),'verified_material_records':sum(f['status']=='downloaded_verified' for f in records),'max_extracted_path_length':max(len(str(root/m['recovered_path'])) for m in members)}
