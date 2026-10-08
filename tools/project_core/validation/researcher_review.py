from tools.project_core.registry.discovery import project_root, region_directory, discover_regions, discover_models, resolve_model
"""Store approved researcher review metadata centrally; never change regional science."""
import argparse, copy, hashlib, json, os, re, tempfile, zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as etree

STATUS = 'Validated by researcher'
DISQUALIFIED_STATUS = 'Disqualified by researcher'
HEADINGS = ['Model extraction notes', 'GE and TE diagnostics',
            'Groups excluded from displayed PPR', 'Geographic fit', 'Taxon mapping confidence']
NOTE = ('Following researcher review, seabirds, other mammals, pinnipeds and marine turtles '
        'are excluded from displayed PPR. Model loading, diagnostics and saved workbook '
        'calculations retain all groups.')

def removed_groups_text(sppr_text):
    """Preserve signed wording while accepting calculation/calculations headings."""
    match = re.search(r'Removed groups from calculations?:\s*(.*)', sppr_text, re.S)
    return match.group(1) if match else ''

def exclusion_note(sppr_text):
    """Name only groups explicitly removed in the approved report's SPPR field."""
    removed = removed_groups_text(sppr_text)
    groups = [line.split('(', 1)[0].strip().lower() for line in removed.splitlines()
              if '(' in line and line.split('(', 1)[0].strip()]
    # Preserve the original registered closing note for its existing snapshot.
    if set(groups) == {'seabirds', 'other mammals', 'pinnipeds', 'marine turtles'}:
        return NOTE
    if not groups:
        return ('Following researcher review, no model groups are excluded from displayed PPR. '
                'Model loading, diagnostics and saved workbook calculations retain all groups.')
    names = groups[0] if len(groups) == 1 else ', '.join(groups[:-1]) + ' and ' + groups[-1]
    return ('Following researcher review, ' + names + ' are excluded from displayed PPR. '
            'Model loading, diagnostics and saved workbook calculations retain all groups.')
FIELDS = ['researcher_review_status', 'researcher_name', 'researcher_review_date',
          'validation_report_path', 'validation_report_sha256', 'reviewed_model_sha256',
          'reviewed_calculation_input_sha256', 'researcher_review_summary']
S = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
NS = {'s': S, 'w': W}
etree.register_namespace('', S)
etree.register_namespace('r', R)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def column(index):
    result = ''
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result

def column_index(address):
    result = 0
    for character in re.match(r'[A-Z]+', address)[0]:
        result = 26 * result + ord(character) - 64
    return result

def sheet_xml(archive, name):
    workbook = etree.fromstring(archive.read('xl/workbook.xml'))
    sheet = next(s for s in workbook.findall(f'{{{S}}}sheets/{{{S}}}sheet') if s.get('name') == name)
    relationships = etree.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
    target = next(r.get('Target') for r in relationships if r.get('Id') == sheet.get(f'{{{R}}}id'))
    target = target.lstrip('/') if target.startswith('/') else 'xl/' + target
    return target, etree.fromstring(archive.read(target))

def table_rows(archive, name, table):
    _, sheet = sheet_xml(archive, name)
    shared = []
    if 'xl/sharedStrings.xml' in archive.namelist():
        shared = [''.join(si.itertext()) for si in etree.fromstring(archive.read('xl/sharedStrings.xml'))]
    current = None
    headers = None
    output = []
    header_row = None
    for row in sheet.findall(f'{{{S}}}sheetData/{{{S}}}row'):
        values = {}
        for cell in row:
            value = cell.find(f'{{{S}}}v')
            value = value.text if value is not None else None
            if cell.get('t') == 'inlineStr':
                value = ''.join(t.text or '' for t in cell.findall(f'.//{{{S}}}t'))
            elif cell.get('t') == 's':
                value = shared[int(value)]
            values[column_index(cell.get('r')) - 1] = value
        if values.get(0) == '@table':
            current = values.get(1)
            headers = None
        elif current == table and values:
            if headers is None:
                headers = [values.get(i) for i in range(max(values) + 1)]
                header_row = row
            else:
                output.append((row, dict(zip(headers, [values.get(i) for i in range(len(headers))]))))
    return sheet, headers, header_row, output

def read_report(root, report, model_id):
    """Preserve exact reviewed text, rounded values and original hyperlink anchors."""
    report = report.resolve()
    with zipfile.ZipFile(report) as archive:
        document = etree.fromstring(archive.read('word/document.xml'))
        relationships = etree.fromstring(archive.read('word/_rels/document.xml.rels'))
        targets = {r.get('Id'): r.get('Target') for r in relationships}
    def text(element):
        return ''.join(part.text or '' if part.tag == f'{{{W}}}t' else
                       '\n' if part.tag in {f'{{{W}}}br', f'{{{W}}}cr'} else
                       '\t' if part.tag == f'{{{W}}}tab' else ''
                       for part in element.iter())
    def paragraphs(cell):
        result = []
        for paragraph in cell.findall(f'{{{W}}}p'):
            segments = []
            for child in paragraph:
                value = text(child)
                if not value:
                    continue
                segment = {'text': value}
                if child.tag == f'{{{W}}}hyperlink':
                    target = targets.get(child.get(f'{{{R}}}id'), '')
                    anchor = child.get(f'{{{W}}}anchor')
                    if target and not urlsplit(target).scheme:
                        local_target, separator, fragment = target.partition('#')
                        local = (report.parent / unquote(local_target)).resolve()
                        if not local.is_relative_to(root) or not local.exists():
                            raise ValueError('Review hyperlink is missing or outside the repository: ' + target)
                        target = local.relative_to(root).as_posix() + separator + fragment
                    if anchor:
                        target = target.split('#')[0] + '#' + anchor
                    if target:
                        segment['href'] = target
                segments.append(segment)
            result.append(segments)
        return result
    fields = {}
    confidence = None
    confidence_table = None
    for table in document.findall(f'.//{{{W}}}body/{{{W}}}tbl'):
        rows = [[cell for cell in row.findall(f'{{{W}}}tc')] for row in table.findall(f'{{{W}}}tr')]
        if rows and text(rows[0][0]) == 'Overall confidence':
            confidence = [[text(cell) for cell in row] for row in rows]
            confidence_table = table
        for cells in rows:
            if len(cells) == 2:
                fields[text(cells[0])] = {'text': '\n'.join(text(p) for p in cells[1].findall(f'{{{W}}}p')),
                                          'paragraphs': paragraphs(cells[1])}
    identities = [fields[label]['text'] for label in ['Selected model', 'Candidate model'] if label in fields]
    if not identities or any(not re.match(re.escape(model_id) + r'(?=$|[.;\s])', value) for value in identities):
        raise ValueError('Review document identifies a different model')
    manual = fields['Review and reproducibility']['text']
    match = re.search(r'Researcher name:\s*([^|\n]+)\s*\|\s*review date:\s*(\d{2})/(\d{2})/(\d{4})', manual)
    decisions = list(re.finditer(r'\bMODEL (VALIDATED|DISQUALIFIED)\b', manual))
    if not match or len(decisions) != 1:
        raise ValueError('The report needs an explicit researcher identity, date and one unambiguous decision')
    name, day, month, year = match.groups()
    if decisions[0].group(1) == 'DISQUALIFIED':
        reason = manual[decisions[0].end():].strip()
        if not re.match(r'Reason\s*[–—:-]\s*\S', reason):
            raise ValueError('A disqualified report needs its explicit Reason directly below the verdict')
        # A rejection registers its signed verdict only. Diagnostic/mapping
        # notes are evidence, not approval to adopt group-removal suggestions.
        return name.strip(), f'{year}-{month}-{day}', {
            'schema_version': 1, 'model_id': model_id,
            'status': DISQUALIFIED_STATUS, 'verdict': 'MODEL DISQUALIFIED',
            'reason': reason, 'sections': [], 'note': ''}
    references = []
    capture = False
    # Walk body children in order: a paragraph-only scan skips the boundary
    # table and leaks later rule summaries and geographic evidence into the map.
    for element in document.find(f'{{{W}}}body'):
        if capture and element is confidence_table:
            break
        if element.tag != f'{{{W}}}p':
            continue
        value = text(element)
        if value == 'Taxon mapping and coverage':
            capture = True
        elif capture:
            # The map supplies its own appendix link. Identify the Word link
            # by its target, since its visible label varies between reports.
            if any(unquote(urlsplit(targets.get(link.get(f'{{{R}}}id'), '')).path)
                   .lower().endswith(('_taxon_mapping_appendix.xlsx','taxon_mapping.xlsx'))
                   for link in element.findall(f'{{{W}}}hyperlink')):
                continue
            references.append(value)
    if not confidence or len(confidence) != 6:
        raise ValueError('Expected the reviewed five-category confidence table')
    summary = {'schema_version': 1, 'model_id': model_id, 'sections': [
        {'heading': HEADINGS[0], 'rows': [fields['Model extraction']]},
        {'heading': HEADINGS[1], 'rows': [dict(fields['GE diagnostics'], label='GE'), dict(fields['TE diagnostics'], label='TE')]},
        {'heading': HEADINGS[2], 'rows': [fields['SPPR calculation']]},
        {'heading': HEADINGS[3], 'rows': [fields['Geographic fit']]},
        {'heading': HEADINGS[4], 'reference': references, 'table': confidence,
         'appendix_path': (report.parent / 'taxon_mapping.xlsx').relative_to(root).as_posix()}],
        'note': exclusion_note(fields['SPPR calculation']['text'])}
    return name.strip(), f'{year}-{month}-{day}', summary

def register_review(project, report, unit_id, model_id, excluded_seq):
    from tools.project_core.registry.writes import central_lock
    with central_lock(Path(project).resolve().parent):return _register_review(project,report,unit_id,model_id,excluded_seq)

def calculation_review_book(root, metadata, book):
    """Resolve this model's saved inputs independently of the map default."""
    from tools.project_core.workbooks.workbooks import overview
    settings = overview(book)
    identity = settings.get('results_model_id') or settings.get('selected_model_id')
    if identity == metadata['model_id']:
        if not settings.get('calculation_input_sha256'):
            raise ValueError('Review calculation inputs lack their fingerprint')
        if settings.get('results_model_sha256') and settings['results_model_sha256'] != sha(root / metadata['model_path']):
            raise ValueError('Review calculation inputs identify a changed canonical model')
        return book
    snapshot = (root / metadata['model_path']).resolve().parent / 'results/regional_snapshot.xlsx'
    if not snapshot.is_relative_to(root) or not snapshot.is_file():
        raise ValueError('The reviewed model requires its own saved calculation inputs')
    saved = {}
    with zipfile.ZipFile(snapshot) as archive:
        for sheet, table in [('Overview', 'Settings'), ('Selected model groups', 'Groups')]:
            _, headers, _, rows = table_rows(archive, sheet, table)
            headers = list(rows[0][1]) if rows else (headers or [])
            saved.setdefault(sheet, {})[table] = (headers, [[r.get(h) for h in headers] for _, r in rows])
    settings = overview(saved)
    identity = settings.get('results_model_id') or settings.get('selected_model_id')
    if identity != metadata['model_id'] or not settings.get('calculation_input_sha256'):
        raise ValueError('Saved review calculation inputs identify another model or lack their fingerprint')
    if settings.get('results_model_sha256') and settings['results_model_sha256'] != sha(root / metadata['model_path']):
        raise ValueError('Saved review calculation inputs identify a changed canonical model')
    return saved

def _register_review(project, report, unit_id, model_id, excluded_seq):
    """Extend only the central Models table XML and its native table definition."""
    root = project.resolve().parent
    with zipfile.ZipFile(project) as archive:
        sheet, headers, header_row, rows = table_rows(archive, 'Models & coverage', 'Models')
        original_headers = headers[:]
        matches = [(row, data) for row, data in rows if data.get('unit_id') == unit_id and data.get('model_id') == model_id]
        if len(matches) != 1:
            raise ValueError('Register exactly one central region/model record before reviewing it')
        row, model = matches[0]
        sheet_path, _ = sheet_xml(archive, 'Models & coverage')
        parts = [(info, archive.read(info.filename)) for info in archive.infolist()]
    regional_path = region_directory(root,unit_id) / (unit_id + '.xlsx')
    with zipfile.ZipFile(regional_path) as archive:
        _, _, _, settings = table_rows(archive, 'Overview', 'Settings')
        settings = {r['field']: r['value'] for _, r in settings}
        _, _, _, groups = table_rows(archive, 'Selected model groups', 'Groups')
    name, date, summary = read_report(root, report, model_id)
    status = summary.get('status', STATUS)
    input_model_id = settings.get('results_model_id') or settings.get('selected_model_id')
    source_only = input_model_id != model_id and status == DISQUALIFIED_STATUS
    if input_model_id != model_id and not source_only:
        from tools.project_core.workbooks.workbooks import overview, records
        saved = calculation_review_book(root, model, {})
        settings = overview(saved)
        groups = [(None, r) for r in records(saved, 'Selected model groups', 'Groups')]
    if source_only:
        summary['review_scope'] = 'model_source'
    exclusions = [r['group_name'] for _, r in groups if int(float(r['seq'])) in excluded_seq]
    if len(exclusions) != len(set(excluded_seq)):
        raise ValueError('Approved group exclusion identifiers do not resolve uniquely')
    if status == DISQUALIFIED_STATUS and excluded_seq:
        raise ValueError('Disqualification does not authorize group exclusions')
    summary['excluded_group_ids'] = exclusions
    if excluded_seq == [] and status == STATUS:
        removed = removed_groups_text(summary['sections'][2]['rows'][0]['text'])
        declared = [line.split('(', 1)[0].strip().lstrip('-• ').lower() for line in removed.splitlines()
                    if '(' in line and line.split('(', 1)[0].strip()]
        available = {r['group_name'].strip().lower() for _, r in groups}
        if declared and not any(name in available for name in declared):
            names = declared[0] if len(declared) == 1 else ', '.join(declared[:-1]) + ' and ' + declared[-1]
            summary['note'] = ('The reviewed SPPR notes name ' + names + ' for exclusion, but the selected model '
                               'contains no matching group. No model groups are excluded from displayed PPR. '
                               'Model loading, diagnostics and saved workbook calculations retain all groups.')
    values = dict(zip(FIELDS, [status, name, date, report.resolve().relative_to(root).as_posix(),
                              sha(report), sha(root / model['model_path']),
                              '' if source_only else settings['calculation_input_sha256'], json.dumps(summary, ensure_ascii=False, separators=(',', ':'))]))
    if any(len(str(value)) > 32767 for value in values.values()):
        raise ValueError('Review metadata exceeds Excel cell text limit')
    def put(target, index, value, style):
        address = column(index) + target.get('r')
        cell = next((c for c in target if c.get('r') == address), None)
        if cell is None:
            cell = etree.SubElement(target, f'{{{S}}}c', r=address)
        cell.clear(); cell.set('r', address); cell.set('t', 'inlineStr')
        if style:
            cell.set('s', style)
        string = etree.SubElement(etree.SubElement(cell, f'{{{S}}}is'), f'{{{S}}}t')
        string.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve'); string.text = str(value)
        ordered = sorted(list(target), key=lambda c: column_index(c.get('r')))
        target[:] = ordered
    for field, value in values.items():
        if field not in headers:
            headers.append(field)
        index = headers.index(field) + 1
        put(header_row, index, field, header_row[0].get('s'))
        put(row, index, value, None)
    columns = sheet.find(f'{{{S}}}cols')
    if columns is not None:
        for field in FIELDS:
            index = headers.index(field) + 1
            for existing in list(columns):
                if int(existing.get('min')) == index and int(existing.get('max')) == index:
                    columns.remove(existing)
            hidden = field.endswith('sha256') or field == 'researcher_review_summary'
            width = 65 if field == 'validation_report_path' else 28
            etree.SubElement(columns, f'{{{S}}}col', min=str(index), max=str(index), width=str(width), customWidth='1', hidden='1' if hidden else '0')
        columns[:] = sorted(list(columns), key=lambda c: int(c.get('min')))
    replacements = {sheet_path: etree.tostring(sheet, encoding='utf-8')}
    # Match the HTML model-name treatment in Excel, extending existing styles.
    styles = etree.fromstring(dict((info.filename, data) for info, data in parts)['xl/styles.xml'])
    fonts = styles.find(f'{{{S}}}fonts'); formats = styles.find(f'{{{S}}}cellXfs')
    for field in ['model_id', 'researcher_review_status']:
        cell = next(c for c in row if column_index(c.get('r')) == headers.index(field) + 1)
        base = copy.deepcopy(formats[int(cell.get('s', '0'))])
        font = copy.deepcopy(fonts[int(base.get('fontId', '0'))])
        for color in list(font.findall(f'{{{S}}}color')):
            font.remove(color)
        etree.SubElement(font, f'{{{S}}}color', rgb='FFB42318' if status == DISQUALIFIED_STATUS else 'FF187344')
        if font.find(f'{{{S}}}b') is None:
            etree.SubElement(font, f'{{{S}}}b', val='1')
        base.set('fontId', str(len(fonts))); base.set('applyFont', '1')
        fonts.append(font); cell.set('s', str(len(formats))); formats.append(base)
    fonts.set('count', str(len(fonts))); formats.set('count', str(len(formats)))
    replacements['xl/styles.xml'] = etree.tostring(styles, encoding='utf-8')
    replacements[sheet_path] = etree.tostring(sheet, encoding='utf-8')
    for info, data in parts:
        if info.filename.startswith('xl/tables/') and info.filename.endswith('.xml'):
            table = etree.fromstring(data)
            existing = table.find(f'{{{S}}}tableColumns')
            if [c.get('name') for c in existing] != original_headers:
                continue
            ref = table.get('ref'); endrow = re.search(r'\d+$', ref)[0]
            newref = ref.split(':')[0] + ':' + column(len(headers)) + endrow
            table.set('ref', newref)
            filter_node = table.find(f'{{{S}}}autoFilter')
            if filter_node is not None:
                filter_node.set('ref', newref)
            existing[:] = [etree.Element(f'{{{S}}}tableColumn', id=str(i), name=h) for i, h in enumerate(headers, 1)]
            existing.set('count', str(len(headers)))
            replacements[info.filename] = etree.tostring(table, encoding='utf-8')
    before = sha(project)
    fd, temporary = tempfile.mkstemp(suffix='.xlsx', dir=project.parent); os.close(fd)
    try:
        with zipfile.ZipFile(temporary, 'w') as archive:
            for info, data in parts:
                archive.writestr(info, replacements.get(info.filename, data))
        if sha(project) != before:
            raise ValueError('Project workbook changed during review registration')
        os.replace(temporary, project)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return values

def approved_review(root, metadata, book):
    """Require matching source identities before exposing a review or PPR exclusions."""
    if not metadata or metadata.get('researcher_review_status') not in {STATUS, DISQUALIFIED_STATUS}:
        return None
    summary = json.loads(metadata.get('researcher_review_summary') or '{}')
    source_only = summary.get('review_scope') == 'model_source'
    if source_only and (metadata['researcher_review_status'] != DISQUALIFIED_STATUS
                        or metadata.get('reviewed_calculation_input_sha256') or summary.get('excluded_group_ids')):
        raise ValueError('A source-only rejection cannot approve calculations or group exclusions')
    for key in FIELDS:
        if source_only and key == 'reviewed_calculation_input_sha256':
            continue
        if not metadata.get(key):
            raise ValueError('Incomplete central researcher review: ' + key)
    for field, hashfield in [('validation_report_path', 'validation_report_sha256'), ('model_path', 'reviewed_model_sha256')]:
        path = (root / metadata[field]).resolve()
        if not path.is_relative_to(root) or not path.is_file() or sha(path) != metadata[hashfield]:
            raise ValueError('Researcher review source changed; review and register the current ' + field)
    from tools.project_core.workbooks.workbooks import overview
    if not source_only:
        book = calculation_review_book(root, metadata, book)
        if overview(book).get('calculation_input_sha256') != metadata['reviewed_calculation_input_sha256']:
            raise ValueError('Researcher review calculation inputs changed; review the current regional inputs')
    if summary.get('schema_version') != 1 or summary.get('model_id') != metadata['model_id']:
        raise ValueError('Researcher review snapshot identifies another model or schema')
    name, date, source_summary = read_report(root, root / metadata['validation_report_path'], metadata['model_id'])
    status = source_summary.get('status', STATUS)
    if (name, date) != (metadata['researcher_name'], metadata['researcher_review_date']) or source_summary['sections'] != summary.get('sections') or status != metadata['researcher_review_status']:
        raise ValueError('Central researcher review snapshot differs from the reviewed Word source')
    if status == DISQUALIFIED_STATUS and (
            any(summary.get(key) != source_summary[key] for key in ['status', 'verdict', 'reason'])
            or summary.get('excluded_group_ids')):
        raise ValueError('Central researcher review snapshot differs from the reviewed Word source')
    from tools.project_core.workbooks.workbooks import records
    group_ids = {r['group_name'] for r in records(book, 'Selected model groups', 'Groups')}
    if not set(summary.get('excluded_group_ids', [])).issubset(group_ids):
        raise ValueError('Researcher PPR exclusions identify unknown current model groups')
    return {**summary, 'status': status, 'researcher_name': metadata['researcher_name'],
            'review_date': metadata['researcher_review_date'], 'report_path': metadata['validation_report_path'],
            'report_sha256': metadata['validation_report_sha256'], 'model_sha256': metadata['reviewed_model_sha256']}

def unavailable_review_model(metadata, review):
    """Expose a reviewed source in model controls without inventing calculations."""
    if review.get('status') not in {STATUS, DISQUALIFIED_STATUS}:
        raise ValueError('Adding a review-only model requires a verified signed decision')
    return {'id': metadata['model_id'], 'label': metadata['model_id'], 'verified': False,
            'scopes': {}, 'source': metadata['model_path'],
            'researcher_review': copy.deepcopy(review), 'display_ppr_excluded_group_ids': review['excluded_group_ids'][:]}

def attach_payload_review(root, metadata, book, model, review, pending=None):
    """Bind positive signoff to the exact workbook behind displayed calculations."""
    if review and review.get('status') == STATUS and (
            model.get('verified') or model.get('scopes') or model.get('group_data') or model.get('values')):
        from tools.project_core.workbooks.workbooks import overview
        settings = overview(book)
        identity = settings.get('results_model_id') or settings.get('selected_model_id')
        workbook = (region_directory(root, metadata['unit_id']) / (metadata['unit_id'] + '.xlsx')
                    if identity == metadata['model_id'] else
                    (root / metadata['model_path']).resolve().parent / 'results/regional_snapshot.xlsx')
        if not workbook.is_file() or model.get('workbook_sha256') != sha(workbook):
            review = None
            pending = recorded_review_pending(metadata, 'Displayed calculations do not match the reviewed model workbook')
    for field in ['researcher_review', 'recorded_review_pending', 'display_ppr_excluded_group_ids']:
        model.pop(field, None)
    if review:
        model['researcher_review'] = copy.deepcopy(review)
        model['display_ppr_excluded_group_ids'] = review['excluded_group_ids'][:]
    if pending:
        model['recorded_review_pending'] = copy.deepcopy(pending)

def recorded_review_pending(metadata, reason):
    return {'recorded_status': metadata.get('researcher_review_status'),
            'researcher_name': metadata.get('researcher_name'),
            'review_date': metadata.get('researcher_review_date'),
            'report_path': metadata.get('validation_report_path'), 'reason': str(reason)}

def review_display(root, metadata, book):
    """Preserve a recorded decision while exposing only currently verified approval."""
    try:return approved_review(root,metadata,book),None
    except ValueError as error:
        # The approval gate remains strict. A stale decision is visible evidence,
        # with no active exclusions, green eligibility or implied new signoff.
        return None,recorded_review_pending(metadata,error)

def reviewed_layout(text):
    """Overlay current review behavior without editing retained historical templates."""
    directory = project_root(Path(__file__))/'tools/project_core/maps'
    start = text.find('/* Retain the original catch allocations when selecting model groups. */')
    if start < 0:
        return text
    # Map visibility follows the currently chosen model's registered human
    # review, independently of calculation availability or the displayed metric.
    text = text.replace('<option value="all" selected>All</option><option value="custom">Other number</option>',
        '<option value="all" selected>All</option><option value="validated">Validated by researcher</option><option value="custom">Other number</option>')
    text = text.replace("limit:['10','25','50','all','custom']", "limit:['10','25','50','all','validated','custom']")
    text = text.replace('  if(!PPRMapRanking.visible(r,rankState.limit,rankState.custom))return false;',
        "  const reviewedOnly=rankState.limit==='validated';\n"
        "  if(reviewedOnly&&!PPRResearcherReview.isValidated(network.units[r.unit_id]?.models[chosenModels[r.unit_id]]))return false;\n"
        "  if(!PPRMapRanking.visible(r,reviewedOnly?'all':rankState.limit,rankState.custom))return false;")
    # Re-resolve offsets after the map-only additions above.
    start = text.index('/* Retain the original catch allocations when selecting model groups. */')
    end = text.index('/* Compact preferences shared by the two standalone pages.', start)
    from tools.project_core.maps.provisional_display import provisional_layout
    group_source = (directory / 'original_html_layout/calculation_modules/group_metrics.js').read_text(encoding='utf-8')
    # Signed exclusions are the initial display policy. Explicit browser/URL
    # selections override that policy without changing the recorded review.
    selection_start = group_source.index('  function selection(model,ids){')
    selection_end = group_source.index('  const active=', selection_start)
    group_source = group_source[:selection_start] + '''  function selection(model,ids){
    const list=model?.group_data?.groups||[],manual=Array.isArray(ids);
    const excluded=new Set(model?.display_ppr_excluded_group_ids||[]);
    const names=new Set(manual?ids:list.filter(g=>!excluded.has(g.id)).map(g=>g.id));
    const indices=list.flatMap((g,i)=>names.has(g.id)?[i]:[]);
    const catch_indices=manual?indices:list.map((g,i)=>i);
    return {ids:indices.map(i=>list[i].id),indices,count:indices.length,total:list.length,
      catch_indices,requested_ids:catch_indices.map(i=>list[i].id),
      researcher_excluded:list.filter(g=>excluded.has(g.id)).map(g=>g.id),
      manual_active:manual&&indices.length<list.length,
      active:list.length>0&&indices.length<list.length,empty:indices.length===0};
  }
''' + group_source[selection_end:]
    text = text[:start] + provisional_layout(group_source) + '\n\n' + text[end:]
    # Checkbox and bulk actions persist exact user choices, including All.
    text = text.replace("function selection(){const {model}=current();return new Set(store.data.selections[key()]??model?.group_data.groups.map(g=>g.id)??[]);}",
        "    function selection(){const {model}=current();return new Set(PPRGroups.selection(model,store.data.selections[key()]).ids);}")
    text = text.replace("key==='name'?row.name:finite(row[key])", "key==='name'?row.name+((current().model?.display_ppr_excluded_group_ids||[]).includes(row.id)?' · Excluded from displayed PPR by researcher':''):finite(row[key])")
    text = text.replace("if(ids.length===allIds.length&&allIds.every(id=>ids.includes(id)))", "if(!model.display_ppr_excluded_group_ids?.length&&ids.length===allIds.length&&allIds.every(id=>ids.includes(id)))")
    text = text.replace("if(ids.size===model.group_data.groups.length)", "if(!model.display_ppr_excluded_group_ids?.length&&ids.size===model.group_data.groups.length)")
    text = text.replace("prefs.ranges={};delete store.data.selections[key()];notify();loadModel();",
        "prefs.ranges={};const {model}=current();setSelection(model.group_data.groups.map(g=>g.id));loadModel();")
    text = text.replace("${selected.size} of ${model?.group_data.groups.length||0} groups selected · ${visibleRows().length} matching", "${selected.size} of ${model?.group_data.groups.length||0} groups included in displayed PPR · ${(model?.display_ppr_excluded_group_ids||[]).length} researcher exclusions · ${visibleRows().length} matching")
    text = text.replace("const {unit,model}=current();if(!model)return;const prefs=preferences(),context=getContext();", "const {unit,model}=current();if(!model)return;PPRResearcherReview.decorateName(models,model);const prefs=preferences(),context=getContext();")
    text = text.replace("fill(models,modelList.map(m=>[m.id,m.label||m.id]));", "fill(models,modelList.map(m=>[m.id,m.label||m.id]));for(const option of models.options){PPRResearcherReview.decorateName(option,modelList.find(m=>m.id===option.value));}")
    # The reviewed model is selected independently of the chosen PPR method.
    text = re.sub(r"  if\(model\?\.review_flags\?\.length\)\{const flag=.*?panel\.appendChild\(flag\);\}\n  if\(model\?\.review_note\)\{const note=.*?panel\.appendChild\(note\);\}\n", "  const reviewModel=modelUnit?.models[idx];\n", text)
    text = text.replace("o.textContent=(m.review_flags?.length?'⚠ ':'')+(m.label||m.id.replaceAll('_',' '));", "o.textContent=m.label||m.id.replaceAll('_',' ');PPRResearcherReview.decorateName(o,m);")
    text = text.replace("o.textContent=m.label||m.id.replaceAll('_',' ');o.selected=i===idx;", "o.textContent=m.label||m.id.replaceAll('_',' ');PPRResearcherReview.decorateName(o,m);o.selected=i===idx;")
    text = text.replace("const sel=panel.querySelector('select');", "const sel=panel.querySelector('select');PPRResearcherReview.decorateName(sel,reviewModel);PPRResearcherReview.decorateName(panel.querySelector('label[for=\"modelFilter\"]'),reviewModel);")
    text = text.replace("</div><p class=\"network-status\">${escapeMetric(result.status)}</p>`;\n  const reviewModel", "</div>`;\n  const reviewModel")
    # Replace the entire legacy prose area with the current review presentation.
    notes_start = text.find("  const notes=document.createElement('p');notes.className='network-note';")
    notes_end = text.find('  old.replaceWith(panel);', notes_start)
    if notes_start >= 0 and notes_end >= 0:
        text = text[:notes_start] + ("  PPRResearcherReview.append(panel,reviewModel);\n"
            "  panel.appendChild(trendLink());\n"
            "  appendResultDownload(panel,r,model,result,unit);\n") + text[notes_end:]
    text = re.sub(r"  if\(!unit\)\{panel\.innerHTML=[^\n]+\n", "  if(!unit){PPRResearcherReview.append(panel,modelUnit?.models[chosenModels[r.unit_id]]);panel.appendChild(trendLink());old.replaceWith(panel);return}\n", text)
    # Keep the chosen model when linking an independent simple-chain estimate.
    text = text.replace("const model=independent?null:modelUnit?.models[chosenModels[r.unit_id]];", "const model=modelUnit?.models[chosenModels[r.unit_id]];")
    # Trends expose the same review state, including model-independent methods.
    text = text.replace("if(!nppOnly&&(relevantMethods().some(id=>methodInfo(id)?.kind==='model')||result.series.some(series=>series.model_ids?.[id]))){", "if(!nppOnly){")
    text = text.replace("li.appendChild(document.createTextNode(' · '+(model?.label||model?.id||'No model')));", "PPRResearcherReview.appendName(li,model);\n        PPRResearcherReview.append(li,model);")
    text = re.sub(r"        if\(model\?\.review_flags\?\.length\)li\.appendChild\([^\n]+\);\n", '', text)
    text = re.sub(r"        if\(model\?\.review_note\)li\.appendChild\([^\n]+\);\n", '', text)
    text = re.sub(r"        if\(model\?\.workbook\)\{li\.appendChild[^\n]+\n", '', text)
    text = text.replace("if(unit.sources?.workbook){li.appendChild", "if(nppOnly&&unit.sources?.workbook){li.appendChild")
    text = re.sub(r"      if\(!nppOnly\)\{\n      const audit=[\s\S]*?      \}\n      list\.appendChild\(li\);", "      list.appendChild(li);", text)
    text = text.replace("single?('Retained selection rationale: '+(db.units[state.units[0]]?.note||'')):", "single?'':")
    text = text.replace("Object.keys(groupStore.data.selections).length?`${Object.keys(groupStore.data.selections).length} models with group selections`:'All model groups included'", "PPRResearcherReview.selectionSummary(typeof network!=='undefined'?network.units:db.units,groupStore.data,typeof network!=='undefined'?undefined:state.units)")
    script = (directory / 'researcher_review.js').read_text(encoding='utf-8')
    return text.replace('</head>', '<style>'+STYLE+'</style><script>'+script+'</script></head>', 1)

STYLE = '''.researcher-validated-name{color:#187344;font-weight:600}
.researcher-disqualified-name{color:#b42318;font-weight:600}
.researcher-review-pending{color:#b42318;font-size:12px;line-height:1.5;margin:12px 0}
.researcher-review{margin:12px 0;color:#203c40;font-size:12px;line-height:1.5}
.researcher-review h4{font-size:13px;margin:16px 0 5px;color:#174c58}
.researcher-review p{white-space:pre-wrap;margin:4px 0 8px}
.researcher-review table{width:100%;border-collapse:collapse;font-size:11px;margin:8px 0}
.researcher-review th,.researcher-review td{border:1px solid #d8e2e1;padding:5px;text-align:left;overflow-wrap:anywhere}
.researcher-review th{background:#eef4f2;font-weight:600}
.researcher-review .researcher-note{border-top:1px solid #d8e2e1;padding-top:10px;margin-top:14px}
.researcher-review .researcher-review-links{display:flex;flex-wrap:wrap;gap:8px}
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=project_root(Path(__file__)) / 'Project.xlsx')
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--unit-id', required=True); parser.add_argument('--model-id', required=True)
    parser.add_argument('--exclude-group-seq', type=int, nargs='+', required=True)
    args = parser.parse_args()
    register_review(args.project, args.report, args.unit_id, args.model_id, args.exclude_group_seq)
    print('Registered approved researcher review in central model metadata; regional workbooks unchanged.')
