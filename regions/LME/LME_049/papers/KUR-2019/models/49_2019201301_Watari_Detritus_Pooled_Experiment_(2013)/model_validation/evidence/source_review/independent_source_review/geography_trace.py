"""Independent source Figure1 graphical trace, deliberately not a new source polygon."""
from pathlib import Path
import io, json, hashlib, zipfile, xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
from scipy.ndimage import binary_closing, binary_fill_holes, label
from shapely.geometry import shape, mapping, box, Point
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[5]
NATIVE = OUT / 'Figure1_native.png'
LAYER = ROOT / 'common_reference_data/geography/LMEs.geojson'
LAND_LAYER = ROOT / 'common_reference_data/geography/basemaps/ne_50m_land.geojson'
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
fc = json.loads(LAYER.read_text(encoding='utf-8'))
feature = next(f for f in fc['features'] if f['properties'].get('region_id') == 49)
target = shape(feature['geometry'])

# Native source image graticule: tick-line intersections, not the labels/figure caption.
x_ticks = [242, 441, 640, 839, 1037]
x_degrees = [130, 135, 140, 145, 150]
y_ticks = [149, 348, 546, 745]
y_degrees = [45, 40, 35, 30]
xfit = np.polyfit(x_ticks, x_degrees, 1)
yfit = np.polyfit(y_ticks, y_degrees, 1)
def lon(x): return float(xfit[0] * x + xfit[1])
def lat(y): return float(yfit[0] * y + yfit[1])
calibration = {'native_image_pixels': [1181, 900],
               'longitude_pixel_controls': list(zip(x_ticks, x_degrees)),
               'latitude_pixel_controls': list(zip(y_ticks, y_degrees)),
               'longitude_linear_fit': xfit.tolist(), 'latitude_linear_fit': yfit.tolist(),
               'maximum_control_residual_degrees': float(max(
                   np.max(np.abs(np.polyval(xfit, x_ticks) - x_degrees)),
                   np.max(np.abs(np.polyval(yfit, y_ticks) - y_degrees)))),
               'source_locator': 'Watari2019 main PDF3/printed296 Figure1; extracted native raster xref18',
               'limits': 'Raster graphical calibration; tick locations are manually read at integer pixels. Source currents/transition oval are schematic overlays, not boundaries.'}

a = np.asarray(Image.open(NATIVE).convert('RGB'))
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
colors = {
    'KC': (r > 220) & (g > 125) & (g < 205) & (b < 80),
    'OYC': (r > 95) & (r < 175) & (g > 175) & (b > 210),
    'OF': (r > 225) & (g > 215) & (b > 75) & (b < 165),
}
roi = np.zeros(a.shape[:2], dtype=bool)
roi[15:834, 110:1166] = True
mask = np.logical_or.reduce(list(colors.values())) & roi
# Restore small internal arrow/text gaps only when bracketed by original colored
# cells and the gap mostly consists of the source's dark/arrow overlay colors.
overlay = ((r < 115) & (g < 115) & (b < 190)) | ((r > 140) & (g < 100) & (b < 100)) | ((r < 100) & (g > 65) & (b < 95))
restored = mask.copy()
restored_gaps = 0
for y in range(15, 834):
    changes = np.diff(np.r_[False, mask[y], False].astype(int))
    starts = np.flatnonzero(changes == 1)
    ends = np.flatnonzero(changes == -1)
    for left, right in zip(ends[:-1], starts[1:]):
        length = right - left
        if 0 < length <= 70 and np.mean(overlay[y, left:right]) >= .70:
            restored[y, left:right] = True
            restored_gaps += 1
restored = binary_fill_holes(binary_closing(restored, structure=np.ones((5, 5)))) & roi
components, component_count = label(restored)
component_sizes = np.bincount(components.ravel())
# Visual inspection identifies disconnected1–3pixel flecks on schematic arrows
# beyond the colored blocks. Keep genuine larger disconnected coastal patches.
noise_components = np.flatnonzero((component_sizes <= 3) & (np.arange(len(component_sizes)) > 0))
discarded_noise_pixels = int(sum(component_sizes[i] for i in noise_components))
restored[np.isin(components, noise_components)] = False
before_edge_repair = restored.copy()
# Native image visually establishes these constant offshore/stepped water edges.
# A current arrow/transition oval crosses them; the colored block continues on
# both sides of each crossing. Restore only the bounded decorative-overlay bites.
edge_repairs = [
    ('OF150E blue-current crossing', 1035, 340, 349),
    ('OF150E upper transition-oval crossing', 1035, 421, 428),
    ('OF150E lower transition-oval crossing', 1035, 481, 489),
    ('KC132E red-current crossing', 320, 698, 712),
    ('KC132.5E red-current crossing', 340, 668, 682),
]
repair_ledger = []
for description, edge_x, first_y, end_y in edge_repairs:
    count_before = int(restored.sum())
    for y in range(first_y, end_y):
        existing = np.flatnonzero(restored[y, edge_x - 70:edge_x + 1])
        assert len(existing), (description, y)
        last = edge_x - 70 + int(existing[-1])
        restored[y, last + 1:edge_x + 1] = True
    repair_ledger.append({'native_edge': description, 'edge_pixel_x': edge_x,
                          'first_pixel_y': first_y, 'end_pixel_y_exclusive': end_y,
                          'restored_pixels': int(restored.sum()) - count_before,
                          'source_support': 'Straight colored edge immediately above/below crossing in native Figure1; only decorative arrow/oval masked water restored'})
horizontal_edge_checks = []
for description, y, left, right in [
    ('KC30N', 743, 245, 320), ('KC31.5N', 683, 324, 340),
    ('KC32N', 663, 344, 378), ('KC32.5N', 643, 383, 518),
    ('KC33N', 623, 523, 598), ('KC33.5N', 603, 603, 717),
    ('OF35N green-current crossing', 543, 722, 1033),
]:
    assert bool(restored[y, left:right].all()), description
    horizontal_edge_checks.append({'edge': description, 'native_interior_row_y': y,
                                   'pixel_x_interval': [left, right], 'all_interior_water_retained': True,
                                   'additional_restoration_needed': False})

def mask_geometry(pixels, simplify_tolerance=.0125):
    # Merge identical horizontal runs vertically before WGS84 union; these are
    # actual georeferenced cell rectangles, never a raw pixel-area comparison.
    active = {}
    rectangles = []
    for y, row in enumerate(pixels):
        changes = np.diff(np.r_[False, row, False].astype(int))
        runs = set(zip(np.flatnonzero(changes == 1), np.flatnonzero(changes == -1)))
        for run in set(active) - runs:
            first, last = active.pop(run)
            rectangles.append(box(lon(run[0] - .5), lat(last + .5), lon(run[1] - .5), lat(first - .5)))
        for run in runs:
            if run in active: active[run][1] = y
            else: active[run] = [y, y]
    for run, (first, last) in active.items():
        rectangles.append(box(lon(run[0] - .5), lat(last + .5), lon(run[1] - .5), lat(first - .5)))
    geom = unary_union(rectangles)
    return geom.simplify(simplify_tolerance, preserve_topology=True) if simplify_tolerance else geom

before_raw_trace = mask_geometry(before_edge_repair)
# Preserve the complete prior coastline/steps exactly; add only repaired cells.
# Independently simplifying the whole after-polygon can shave tiny old corners.
added_edge_geometry = mask_geometry(restored & ~before_edge_repair, simplify_tolerance=0)
raw_trace = before_raw_trace.union(added_edge_geometry)
landfc = json.loads(LAND_LAYER.read_text(encoding='utf-8'))
land = unary_union([geom for f in landfc['features']
                   if (geom := shape(f['geometry'])).intersects(box(119, 20, 157, 50))])
study = raw_trace.difference(land)
before_study = before_raw_trace.difference(land)
assert before_study.equals(shape(json.loads((OUT / 'Figure1_colored_study_trace_draft_before_overlay_edge_repair.geojson').read_text(encoding='utf-8'))['geometry']))
assert before_study.difference(study).is_empty, 'Edge restoration removed prior source geometry'
geod = Geod(ellps='WGS84')
def area(geom):
    if geom.is_empty: return 0.
    if geom.geom_type == 'Polygon':
        return abs(geod.geometry_area_perimeter(orient(geom, sign=1))[0]) / 1e6
    return sum(area(g) for g in geom.geoms)

# Authenticate the same geometry against a single in-memory snapshot of Project.
project_bytes = (ROOT / 'Project.xlsx').read_bytes()
project_sha = hashlib.sha256(project_bytes).hexdigest()
ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile(io.BytesIO(project_bytes)) as z:
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    sheet = next(s for s in wb.find('m:sheets', ns) if s.get('name') == 'Map geography')
    rid = sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
    sheet_path = next(x.get('Target') for x in rels if x.get('Id') == rid).lstrip('/')
    if not sheet_path.startswith('xl/'): sheet_path = 'xl/' + sheet_path
    strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        strings = [''.join(t.text or '' for t in item.findall('.//m:t', ns))
                   for item in ET.fromstring(z.read('xl/sharedStrings.xml'))]
    chunks = []
    for row in ET.fromstring(z.read(sheet_path)).find('m:sheetData', ns):
        vals = []
        for cell in row:
            if cell.get('t') == 'inlineStr':
                value = ''.join(t.text or '' for t in cell.findall('.//m:t', ns))
            else:
                node = cell.find('m:v', ns)
                value = node.text if node is not None else None
                if cell.get('t') == 's': value = strings[int(value)]
            vals.append(value)
        if vals and vals[0] == 'LME_049': chunks.append((int(vals[1]), vals[2]))
    project_geometry = shape(json.loads(''.join(v for _, v in sorted(chunks))))
assert project_geometry.equals(target), 'Canonical layer differs from current Project Map geography'

scenarios = []
for label, buffer_degrees in [('inset_graphical_sensitivity', -.10), ('central_native_color_trace', 0), ('outset_graphical_sensitivity', .10)]:
    geometry = raw_trace.buffer(buffer_degrees).difference(land) if buffer_degrees else study
    overlap = geometry.intersection(target)
    scenarios.append({'name': label, 'buffer_degrees': buffer_degrees,
                      'study_area_km2': area(geometry), 'overlap_km2': area(overlap),
                      'A_overlap_over_target_percent': 100 * area(overlap) / area(target),
                      'B_overlap_over_traced_study_percent': 100 * area(overlap) / area(geometry)})
controls = []
for name, x, y, expected in [
    ('KC coastal water', 134, 33, True), ('OYC coastal water', 141.5, 37.5, True),
    ('OF offshore water', 147, 38, True), ('western water outside colored KC', 128, 34, False),
    ('eastern water beyond150E', 151, 38, False), ('northern water within nominal prose but beyond colored study', 146, 46, False),
    ('southern offshore water within nominal prose but beyond colored study', 146, 32, False),
    ('Honshu land', 135, 35, False), ('Hokkaido land', 143, 43, False),
    ('inside150E blue-current crossing', lon(1034.8), lat(344), True),
    ('inside150E upper-oval crossing', lon(1034.8), lat(424), True),
    ('inside150E lower-oval crossing', lon(1034.8), lat(484), True),
    ('inside KC132E red-current crossing', lon(319.2), lat(705), True),
    ('inside KC132.5E red-current crossing', lon(339.2), lat(675), True),
]:
    actual = bool(study.covers(Point(x, y)))
    controls.append({'name': name, 'longitude': x, 'latitude': y, 'expected_inside_trace': expected,
                     'actual_inside_trace': actual, 'in_target_R': bool(target.covers(Point(x, y)))})
assert all(c['expected_inside_trace'] == c['actual_inside_trace'] for c in controls), controls

for name, geom in [('target_LME049', target), ('Figure1_colored_study_trace_draft', study)]:
    (OUT / (name + '.geojson')).write_text(json.dumps({'type': 'Feature',
        'properties': {'role': name, 'approximate': name != 'target_LME049',
                       'source': 'Watari2019 Figure1/PDF3 printed296 native color trace; graphical draft only'},
        'geometry': mapping(geom)}, ensure_ascii=False, indent=2), encoding='utf-8')
Image.fromarray((restored.astype(np.uint8) * 255)).save(OUT / 'colored_domain_mask.png')

def draw(geom, ax, color, alpha, label):
    parts = list(geom.geoms) if hasattr(geom, 'geoms') else [geom]
    for i, p in enumerate(parts):
        if p.geom_type != 'Polygon': continue
        ax.fill(*p.exterior.xy, color=color, alpha=alpha, label=label if i == 0 else None)
        for ring in p.interiors: ax.fill(*ring.xy, color='#eeeeeb')
fig, ax = plt.subplots(figsize=(9, 7))
draw(land, ax, '#eeeeeb', 1, 'Land (Natural Earth 1:50 million)')
draw(target, ax, '#397c9b', .35, 'Kuroshio Current LME049 R')
draw(study, ax, '#d38f26', .65, 'Source colored-domain trace S (draft)')
for c in controls:
    ax.plot(c['longitude'], c['latitude'], 'o' if c['expected_inside_trace'] else 'x',
            color='#17633d' if c['expected_inside_trace'] else '#a62222', markersize=6)
for name, x, y in [('KC', 134, 32), ('OYC', 142, 38), ('OF', 147, 41), ('Japan', 137, 36)]:
    ax.text(x, y, name, fontsize=10, ha='center')
ax.set_xlim(119, 155); ax.set_ylim(20, 49); ax.set_aspect(1)
ax.set_xlabel('Longitude °E'); ax.set_ylabel('Latitude °N'); ax.grid(alpha=.25)
ax.legend(loc='lower right', fontsize=8)
ax.set_title('Watari2019 colored study blocks and target LME049\nCalibrated graphical draft; currents and nominal prose bounds are separate evidence')
fig.tight_layout(); fig.savefig(OUT / 'target_trace_controls.png', dpi=170); plt.close(fig)

out = {'source_model': 'Published41-group Watari2019/2013 model; selected39-group detritus pooling leaves study domain unchanged',
       'source_main_pdf_sha256': sha(ROOT / 'regions/LME_049/papers/KUR-2019/Watari-Ecosystemmodelingwestern-2019.pdf'),
       'native_figure_sha256': sha(NATIVE), 'canonical_target_layer_sha256': sha(LAYER),
       'land_layer_sha256': sha(LAND_LAYER), 'project_snapshot_sha256': project_sha,
       'canonical_layer_equals_Project_Map_LME049': True, 'target_properties': feature['properties'],
       'reported_source_areas_km2': {'KC': 186220, 'OYC': 186128, 'OF': 540754, 'total': 913102},
       'traced_central_area_km2': area(study), 'target_area_km2': area(target),
       'calibration': calibration, 'restored_internal_overlay_row_gaps': restored_gaps,
       'disconnected_arrow_antialias_noise_pixels_removed': discarded_noise_pixels,
       'bounded_decorative_edge_repair': {'repairs': repair_ledger,
             'horizontal_edge_checks': horizontal_edge_checks,
             'before_area_km2': area(before_study), 'after_area_km2': area(study),
             'added_study_area_km2': area(study) - area(before_study),
             'added_overlap_km2': area(study.intersection(target)) - area(before_study.intersection(target)),
             'added_area_measure_definition': 'Difference of full before/after WGS84 polygon areas; not interchangeable with geodesic area of separately subdivided added clipping pieces.',
             'separately_measured_added_pieces_km2': area(study.difference(before_study)),
             'removed_area_km2': area(before_study.difference(study)),
             'before_mask': 'colored_domain_mask_before_overlay_edge_repair.png',
             'before_geometry': 'Figure1_colored_study_trace_draft_before_overlay_edge_repair.geojson',
             'before_assessment': 'geography_trace_assessment_before_overlay_edge_repair.json',
             'before_overlay': 'target_trace_controls_before_overlay_edge_repair.png'},
       'scenarios': scenarios, 'ordered_water_land_controls': controls,
       'graphical_A_range_percent': [min(s['A_overlap_over_target_percent'] for s in scenarios), max(s['A_overlap_over_target_percent'] for s in scenarios)],
       'graphical_B_range_percent': [min(s['B_overlap_over_traced_study_percent'] for s in scenarios), max(s['B_overlap_over_traced_study_percent'] for s in scenarios)],
       'confidence': 'Low', 'proposal_only': True,
       'limits': ['Figure1 is schematic and coarsely gridded. Color-cell trace is an approximate displayed domain, not author digital study geometry.',
                 'The prose30–50N/150E bounds enclose offshore geography but do not establish a full rectangular offshore domain; colored OF mainly35–45N is distinct.',
                 'Published913102km² is retained separately; differences from traced area expose graphical uncertainty and must not be calibrated away.',
                 '±0.10degree buffers illustrate digitization sensitivity only, not statistical confidence or the full source-area discrepancy.',
                 'Natural Earth1:50million is a generalized coastline. Coastal grid/land-edge differences remain approximate.',
                 'No catch/PPR geographic multiplier, accepted parameter change, new model selection or scientific approval is implied.']}
(OUT / 'geography_trace_assessment.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in out.items() if k not in ['calibration', 'limits']}, ensure_ascii=False, indent=2))
