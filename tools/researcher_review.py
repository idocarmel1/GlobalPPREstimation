"""Store approved researcher review metadata centrally; never change regional science."""
import argparse, copy, hashlib, json, os, re, tempfile, zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as etree

STATUS = 'Validated by researcher'
HEADINGS = ['Model extraction notes', 'GE and TE diagnostics',
            'Groups excluded from displayed PPR', 'Geographic fit', 'Taxon mapping confidence']
NOTE = ('Following researcher review, seabirds, other mammals, pinnipeds and marine turtles '
        'are excluded from displayed PPR. Model loading, diagnostics and saved workbook '
        'calculations retain all groups.')

def exclusion_note(sppr_text):
    """Name only groups explicitly removed in the approved report's SPPR field."""
    removed = sppr_text.partition('Removed groups from calculation:')[2]
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
    selected = fields.get('Selected model', {}).get('text', '')
    if not re.match(re.escape(model_id) + r'(?=$|[.;\s])', selected):
        raise ValueError('Review document identifies a different model')
    manual = fields['Review and reproducibility']['text']
    match = re.search(r'Researcher name:\s*([^|\n]+)\s*\|\s*review date:\s*(\d{2})/(\d{2})/(\d{4})', manual)
    if not match or 'MODEL VALIDATED' not in manual:
        raise ValueError('The report needs an explicit researcher identity, date and validation decision')
    name, day, month, year = match.groups()
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
                   .lower().endswith('_taxon_mapping_appendix.xlsx')
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
         'appendix_path': (report.parent / (report.parent.name.replace('_', '') + '_taxon_mapping_appendix.xlsx')).relative_to(root).as_posix()}],
        'note': exclusion_note(fields['SPPR calculation']['text'])}
    return name.strip(), f'{year}-{month}-{day}', summary

def register_review(project, report, unit_id, model_id, excluded_seq):
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
    regional_path = root / 'regions' / unit_id / (unit_id + '.xlsx')
    with zipfile.ZipFile(regional_path) as archive:
        _, _, _, settings = table_rows(archive, 'Overview', 'Settings')
        settings = {r['field']: r['value'] for _, r in settings}
        _, _, _, groups = table_rows(archive, 'Selected model groups', 'Groups')
    if settings.get('selected_model_id') != model_id:
        raise ValueError('The supplied model is not the current regional selection')
    exclusions = [r['group_name'] for _, r in groups if int(float(r['seq'])) in excluded_seq]
    if len(exclusions) != len(set(excluded_seq)):
        raise ValueError('Approved group exclusion identifiers do not resolve uniquely')
    name, date, summary = read_report(root, report, model_id)
    summary['excluded_group_ids'] = exclusions
    if excluded_seq == []:
        removed = summary['sections'][2]['rows'][0]['text'].partition('Removed groups from calculation:')[2]
        declared = [line.split('(', 1)[0].strip().lstrip('-• ').lower() for line in removed.splitlines()
                    if '(' in line and line.split('(', 1)[0].strip()]
        available = {r['group_name'].strip().lower() for _, r in groups}
        if declared and not any(name in available for name in declared):
            names = declared[0] if len(declared) == 1 else ', '.join(declared[:-1]) + ' and ' + declared[-1]
            summary['note'] = ('The reviewed SPPR notes name ' + names + ' for exclusion, but the selected model '
                               'contains no matching group. No model groups are excluded from displayed PPR. '
                               'Model loading, diagnostics and saved workbook calculations retain all groups.')
    values = dict(zip(FIELDS, [STATUS, name, date, report.resolve().relative_to(root).as_posix(),
                              sha(report), sha(root / model['model_path']),
                              settings['calculation_input_sha256'], json.dumps(summary, ensure_ascii=False, separators=(',', ':'))]))
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
        etree.SubElement(font, f'{{{S}}}color', rgb='FF187344')
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
    if not metadata or metadata.get('researcher_review_status') != STATUS:
        return None
    for key in FIELDS:
        if not metadata.get(key):
            raise ValueError('Incomplete central researcher review: ' + key)
    for field, hashfield in [('validation_report_path', 'validation_report_sha256'), ('model_path', 'reviewed_model_sha256')]:
        path = (root / metadata[field]).resolve()
        if not path.is_relative_to(root) or not path.is_file() or sha(path) != metadata[hashfield]:
            raise ValueError('Researcher review source changed; review and register the current ' + field)
    from workbooks import overview
    if overview(book).get('calculation_input_sha256') != metadata['reviewed_calculation_input_sha256']:
        raise ValueError('Researcher review calculation inputs changed; review the current regional inputs')
    summary = json.loads(metadata['researcher_review_summary'])
    if summary.get('schema_version') != 1 or summary.get('model_id') != metadata['model_id']:
        raise ValueError('Researcher review snapshot identifies another model or schema')
    name, date, source_summary = read_report(root, root / metadata['validation_report_path'], metadata['model_id'])
    if (name, date) != (metadata['researcher_name'], metadata['researcher_review_date']) or source_summary['sections'] != summary.get('sections'):
        raise ValueError('Central researcher review snapshot differs from the reviewed Word source')
    from workbooks import records
    group_ids = {r['group_name'] for r in records(book, 'Selected model groups', 'Groups')}
    if not set(summary.get('excluded_group_ids', [])).issubset(group_ids):
        raise ValueError('Researcher PPR exclusions identify unknown current model groups')
    return {**summary, 'status': STATUS, 'researcher_name': metadata['researcher_name'],
            'review_date': metadata['researcher_review_date'], 'report_path': metadata['validation_report_path'],
            'report_sha256': metadata['validation_report_sha256'], 'model_sha256': metadata['reviewed_model_sha256']}

def reviewed_layout(text):
    """Overlay current review behavior without editing retained historical templates."""
    directory = Path(__file__).parent
    start = text.find('/* Retain the original catch allocations when selecting model groups. */')
    if start < 0:
        return text
    end = text.index('/* Compact preferences shared by the two standalone pages.', start)
    from provisional_display import provisional_layout
    group_source = (directory / 'original_html_layout/calculation_modules/group_metrics.js').read_text(encoding='utf-8')
    text = text[:start] + provisional_layout(group_source) + '\n\n' + text[end:]
    # Group controls always show the effective PPR selection, while retaining
    # the original browser-requested selection for other catch metrics.
    text = text.replace("function selection(){const {model}=current();return new Set(store.data.selections[key()]??model?.group_data.groups.map(g=>g.id)??[]);}",
        "function requestedSelection(){const {model}=current();return new Set(store.data.selections[key()]??model?.group_data.groups.map(g=>g.id)??[]);}\n"
        "    function selection(){const {model}=current();return new Set(PPRGroups.selection(model,store.data.selections[key()]).ids);}")
    text = text.replace("const ids=selection();if(check.checked)", "const ids=requestedSelection();if(check.checked)")
    text = text.replace("check.checked=selected.has(row.id);check.setAttribute", "check.checked=selected.has(row.id);check.disabled=(current().model?.display_ppr_excluded_group_ids||[]).includes(row.id);check.setAttribute")
    text = text.replace("key==='name'?row.name:finite(row[key])", "key==='name'?row.name+((current().model?.display_ppr_excluded_group_ids||[]).includes(row.id)?' · Excluded from displayed PPR by researcher':''):finite(row[key])")
    text = text.replace("if(!model)return;const allIds=model.group_data.groups.map(g=>g.id);", "if(!model)return;if(ids.length)ids=[...new Set([...ids,...(model.display_ppr_excluded_group_ids||[])])];const allIds=model.group_data.groups.map(g=>g.id);")
    text = text.replace("${selected.size} of ${model?.group_data.groups.length||0} groups selected · ${visibleRows().length} matching", "${selected.size} of ${model?.group_data.groups.length||0} groups included in displayed PPR · ${(model?.display_ppr_excluded_group_ids||[]).length} researcher exclusions · ${visibleRows().length} matching")
    text = text.replace("const {unit,model}=current();if(!model)return;const prefs=preferences(),context=getContext();", "const {unit,model}=current();if(!model)return;models.style.color=model.researcher_review?'#187344':'#203c40';models.style.fontWeight=model.researcher_review?'600':'400';const prefs=preferences(),context=getContext();")
    text = text.replace("fill(models,modelList.map(m=>[m.id,m.label||m.id]));", "fill(models,modelList.map(m=>[m.id,m.label||m.id]));for(const option of models.options){const reviewed=modelList.find(m=>m.id===option.value)?.researcher_review;option.style.color=reviewed?'#187344':'#203c40';option.style.fontWeight=reviewed?'600':'400';}")
    # The reviewed model is selected independently of the chosen PPR method.
    text = re.sub(r"  if\(model\?\.review_flags\?\.length\)\{const flag=.*?panel\.appendChild\(flag\);\}\n  if\(model\?\.review_note\)\{const note=.*?panel\.appendChild\(note\);\}\n", "  const reviewModel=modelUnit?.models[idx];\n", text)
    text = text.replace("o.textContent=(m.review_flags?.length?'⚠ ':'')+(m.label||m.id.replaceAll('_',' '));", "o.textContent=m.label||m.id.replaceAll('_',' ');o.style.color=m.researcher_review?'#187344':'#203c40';o.style.fontWeight=m.researcher_review?'600':'400';")
    text = text.replace("const sel=panel.querySelector('select');", "const sel=panel.querySelector('select');if(sel&&reviewModel?.researcher_review){sel.classList.add('researcher-validated-name');}")
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
    text = text.replace("Object.keys(groupStore.data.selections).length?`${Object.keys(groupStore.data.selections).length} models with group selections`:'All model groups included'", "PPRResearcherReview.selectionSummary(typeof network!=='undefined'?network.units:db.units,groupStore.data)")
    script = (directory / 'researcher_review.js').read_text(encoding='utf-8')
    return text.replace('</head>', '<style>'+STYLE+'</style><script>'+script+'</script></head>', 1)

STYLE = '''.researcher-validated-name{color:#187344;font-weight:600}
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
    parser.add_argument('--project', type=Path, default=Path(__file__).resolve().parents[1] / 'Project.xlsx')
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--unit-id', required=True); parser.add_argument('--model-id', required=True)
    parser.add_argument('--exclude-group-seq', type=int, nargs='+', required=True)
    args = parser.parse_args()
    register_review(args.project, args.report, args.unit_id, args.model_id, args.exclude_group_seq)
    print('Registered approved researcher review in central model metadata; regional workbooks unchanged.')
