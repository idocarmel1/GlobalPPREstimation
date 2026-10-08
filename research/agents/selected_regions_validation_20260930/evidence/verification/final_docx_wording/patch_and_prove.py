"""Bounded, hash-guarded OOXML wording edits; all other raw ZIP entries retained."""
from pathlib import Path
import hashlib, json, re, struct, zlib, zipfile, difflib, copy
from lxml import etree

ROOT = Path(__file__).resolve().parents[5]
EVIDENCE = Path(__file__).resolve().parent
MANIFEST = ROOT / 'original_research_archive/research/selected_regions_validation_20260930/work/final_automatic_draft_text_nodes.json'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
CHANGES = {
    'EEZ_598': ('Papua New Guinea, EEZ_598. Pending alignment draft; regional figures adopted.',
                'Papua New Guinea, EEZ_598. Regional review completed; figures integrated.'),
    'LME_026': ('Mediterranean Sea model validation draft', 'Mediterranean Sea model validation'),
    'LME_036': ('Pending alignment draft for the selected 2000s northern South China Sea model.',
                'Completed regional review for the selected 2000s northern South China Sea model.'),
    'LME_038': ('Pending alignment draft', 'Regional review completed'),
    'LME_049': ('Pending alignment draft', 'Regional review completed'),
    'LME_052': ('Pending alignment draft', 'Regional review completed'),
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def zip_index(data):
    eocd = data.rfind(b'PK\x05\x06')
    assert eocd >= 0 and eocd + 22 + struct.unpack_from('<H', data, eocd + 20)[0] == len(data)
    disk, cd_disk, disk_count, count, cd_size, cd_offset = struct.unpack_from('<HHHHII', data, eocd + 4)
    assert disk == cd_disk == 0 and disk_count == count and cd_offset + cd_size == eocd
    records = []
    pos = cd_offset
    for _ in range(count):
        assert data[pos:pos+4] == b'PK\x01\x02'
        nlen, xlen, clen = struct.unpack_from('<HHH', data, pos+28)
        length = 46+nlen+xlen+clen
        rec = data[pos:pos+length]
        name = rec[46:46+nlen].decode('utf-8')
        offset = struct.unpack_from('<I', rec, 42)[0]
        csize = struct.unpack_from('<I', rec, 20)[0]
        records.append({'name': name, 'raw': rec, 'offset': offset, 'csize': csize})
        pos += length
    assert pos == eocd
    order = sorted(records, key=lambda x: x['offset'])
    assert order[0]['offset'] == 0
    for i, rec in enumerate(order):
        rec['end'] = order[i+1]['offset'] if i+1 < len(order) else cd_offset
        rec['local_raw'] = data[rec['offset']:rec['end']]
    return records, order, cd_offset, eocd

def replace_zip_part(data, part, replacement):
    records, order, cd_offset, eocd = zip_index(data)
    selected = next(x for x in records if x['name'] == part)
    off = selected['offset']
    local = selected['local_raw']
    assert local[:4] == b'PK\x03\x04'
    flags, method = struct.unpack_from('<HH', local, 6)
    assert not flags & 8, 'Data descriptors are not allowed by this exact patcher'
    assert method == 8, 'Expected deflated document.xml'
    nlen, xlen = struct.unpack_from('<HH', local, 26)
    start = 30+nlen+xlen
    assert start+selected['csize'] == len(local), 'Unexpected local suffix'
    compressor = zlib.compressobj(6, zlib.DEFLATED, -15)
    compressed = compressor.compress(replacement)+compressor.flush()
    crc = zlib.crc32(replacement) & 0xffffffff
    header = bytearray(local[:start])
    struct.pack_into('<III', header, 14, crc, len(compressed), len(replacement))
    new_local = bytes(header)+compressed
    delta = len(new_local)-len(local)
    locals_out = b''.join(new_local if rec['name'] == part else rec['local_raw'] for rec in order)
    central_out = []
    for rec in records:
        raw = bytearray(rec['raw'])
        if rec['name'] == part:
            struct.pack_into('<III', raw, 16, crc, len(compressed), len(replacement))
        if rec['offset'] > off:
            struct.pack_into('<I', raw, 42, rec['offset']+delta)
        central_out.append(bytes(raw))
    tail = bytearray(data[eocd:])
    struct.pack_into('<I', tail, 16, cd_offset+delta)
    return locals_out+b''.join(central_out)+bytes(tail)

def proof(old, new, old_xml, new_xml, unit, manifest_item):
    before_records, _, _, _ = zip_index(old)
    after_records, _, _, _ = zip_index(new)
    before_map = {x['name']: x for x in before_records}
    after_map = {x['name']: x for x in after_records}
    assert list(before_map) == list(after_map)
    local_unchanged = []
    central_metadata_unchanged = []
    content_hashes = []
    with zipfile.ZipFile(__import__('io').BytesIO(old)) as bz, zipfile.ZipFile(__import__('io').BytesIO(new)) as az:
        assert bz.testzip() is None and az.testzip() is None
        for part in before_map:
            bd, ad = bz.read(part), az.read(part)
            if part != 'word/document.xml':
                assert bd == ad and before_map[part]['local_raw'] == after_map[part]['local_raw']
                local_unchanged.append(part)
                br, ar = bytearray(before_map[part]['raw']), bytearray(after_map[part]['raw'])
                br[42:46] = ar[42:46] = b'\0'*4
                assert br == ar
                central_metadata_unchanged.append(part)
            content_hashes.append({'part': part, 'before_sha256': sha(bd), 'after_sha256': sha(ad),
                                   'raw_local_before_sha256': sha(before_map[part]['local_raw']),
                                   'raw_local_after_sha256': sha(after_map[part]['local_raw']),
                                   'unchanged': bd == ad})
    bt, at = etree.fromstring(old_xml), etree.fromstring(new_xml)
    btext, atext = bt.findall('.//w:t', NS), at.findall('.//w:t', NS)
    assert len(btext) == len(atext)
    changed_nodes = []
    for i, (b, a) in enumerate(zip(btext, atext)):
        if b.text != a.text:
            assert dict(b.attrib) == dict(a.attrib)
            changed_nodes.append({'text_node_index': i, 'before': b.text, 'after': a.text})
    assert len(changed_nodes) == 1
    before_norm, after_norm = copy.deepcopy(bt), copy.deepcopy(at)
    for tree in (before_norm, after_norm):
        tree.findall('.//w:t', NS)[changed_nodes[0]['text_node_index']].text = '__ONLY_AUTHORIZED_CHANGE__'
    assert etree.tostring(before_norm) == etree.tostring(after_norm)
    # All manual-review XML and scientific caveats are protected by the byte-exact inverse proof.
    old_phrase, new_phrase = CHANGES[unit]
    old_token, new_token = old_phrase.encode(), new_phrase.encode()
    assert new_xml.replace(new_token, old_token, 1) == old_xml
    bh = [etree.tostring(x) for x in bt.findall('.//w:hyperlink', NS)]
    ah = [etree.tostring(x) for x in at.findall('.//w:hyperlink', NS)]
    assert bh == ah
    btables = [etree.tostring(x) for x in bt.findall('.//w:tbl', NS)]
    atables = [etree.tostring(x) for x in at.findall('.//w:tbl', NS)]
    assert len(btables) == len(atables)
    modified_tables = [i for i,(b,a) in enumerate(zip(btables,atables)) if b != a]
    assert modified_tables == ([0] if unit == 'EEZ_598' else [])
    assert [etree.tostring(x) for x in before_norm.findall('.//w:tbl', NS)] == [etree.tostring(x) for x in after_norm.findall('.//w:tbl', NS)]
    brows, arows = bt.findall('.//w:tr', NS), at.findall('.//w:tr', NS)
    manual_rows = []
    for i, (b,a) in enumerate(zip(brows,arows)):
        text = ' | '.join(x.text or '' for x in b.findall('.//w:t', NS))
        if any(term in text.lower() for term in ('researcher','manual','review date','reviewed by','reviewer','signature')):
            raw_b, raw_a = etree.tostring(b), etree.tostring(a)
            assert raw_b == raw_a
            manual_rows.append({'row_index':i,'sha256':sha(raw_b),'text':text,'xml_exact':True})
    pretty_before = old_xml.decode().replace('><', '>\n<').splitlines(True)
    pretty_after = new_xml.decode().replace('><', '>\n<').splitlines(True)
    diff = ''.join(difflib.unified_diff(pretty_before, pretty_after, fromfile=unit+'.before.document.xml', tofile=unit+'.after.document.xml'))
    (EVIDENCE/'xml'/f'{unit}.xml.diff').write_text(diff, encoding='utf-8')
    (EVIDENCE/'xml'/f'{unit}.before.document.xml').write_bytes(old_xml)
    (EVIDENCE/'xml'/f'{unit}.after.document.xml').write_bytes(new_xml)
    return {
        'unit': unit, 'path': manifest_item['path'], 'before_sha256': sha(old), 'after_sha256': sha(new),
        'manifest_sha256_matched_immediately_before_mutation': True,
        'changed_part': 'word/document.xml', 'changed_text_nodes': changed_nodes,
        'inverse_replacement_restores_original_xml_byte_for_byte': True,
        'all_other_xml_including_manual_review_fields_exact': True,
        'all_table_xml_exact_except_authorized_EEZ598_status_text': True, 'table_count': len(btables),
        'modified_table_indices': modified_tables, 'manual_researcher_rows_exact': manual_rows,
        'all_hyperlink_xml_exact': True, 'hyperlink_count': len(bh),
        'all_other_zip_part_bytes_exact': True,
        'all_other_raw_compressed_zip_local_entries_exact': True,
        'all_other_zip_metadata_exact_except_required_offset_adjustment': True,
        'unchanged_local_parts': local_unchanged, 'part_hashes': content_hashes,
        'before_copy': str((EVIDENCE/'before'/f'{unit}.docx').relative_to(ROOT)),
        'exact_xml_diff': str((EVIDENCE/'xml'/f'{unit}.xml.diff').relative_to(ROOT)),
    }

def main():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8-sig'))
    assert len(manifest) == 6 and {x['unit'] for x in manifest} == set(CHANGES)
    (EVIDENCE/'before').mkdir(parents=True, exist_ok=True)
    (EVIDENCE/'xml').mkdir(parents=True, exist_ok=True)
    reports = []
    for item in manifest:
        unit, path = item['unit'], ROOT/item['path']
        original = path.read_bytes()
        assert sha(original) == item['sha256'], f'Stale input for {unit}'
        with zipfile.ZipFile(path) as z:
            original_xml = z.read('word/document.xml')
        body_paras = etree.fromstring(original_xml).findall('.//w:p', NS)
        nodes = body_paras[item['paragraph']].findall('.//w:t', NS)
        assert [x.text or '' for x in nodes] == item['text_nodes']
        old, new = CHANGES[unit]
        old_b, new_b = old.encode(), new.encode()
        assert original_xml.count(old_b) == 1
        # Exact text content only. No XML parser writes or document regeneration.
        updated_xml = original_xml.replace(old_b, new_b, 1)
        updated = replace_zip_part(original, 'word/document.xml', updated_xml)
        report = proof(original, updated, original_xml, updated_xml, unit, item)
        before_path = EVIDENCE/'before'/f'{unit}.docx'
        assert not before_path.exists(), f'Before copy already exists: {before_path}'
        before_path.write_bytes(original)
        assert sha(before_path.read_bytes()) == item['sha256']
        # Re-read for the mandatory immediate freshness gate before each replacement.
        assert sha(path.read_bytes()) == item['sha256'], f'Changed concurrently: {unit}'
        path.write_bytes(updated)
        assert sha(path.read_bytes()) == report['after_sha256']
        reports.append(report)
        print(unit, report['after_sha256'], flush=True)
    output = {
        'scope': 'Six exact automatic-status wording changes only',
        'runtime': r'C:\Users\idoca\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe',
        'operation_marker': 'Already performed once by parent; intentionally not repeated',
        'files': reports,
    }
    (EVIDENCE/'patch_proof.json').write_text(json.dumps(output, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

if __name__ == '__main__':
    main()
