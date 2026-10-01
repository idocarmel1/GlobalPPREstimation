"""Independent, source-image-only review. Outputs remain in this directory."""
from pathlib import Path
import csv
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
SOURCE = ROOT / 'regions/LME_028/validation_reports/28_646_Guinea_(1998)/geography/original_figure1_crop.png'
NATIVE = OUT / 'source_embedded_figure1.png'
arr = np.array(Image.open(NATIVE).convert('L'))

def fit(name, rect):
    x0, x1, y0, y1 = rect
    yy, xx = np.where(arr[y0:y1 + 1, x0:x1 + 1] == 74)
    xx, yy = xx + x0, yy + y0
    xs = np.unique(xx)
    ys = np.array([np.mean(yy[xx == x]) for x in xs])
    coeff = np.polyfit(xs, ys, 1)
    return coeff, {'label': name, 'native_pixel_rectangle': rect,
                   'y_equals_mx_plus_b': coeff.tolist(),
                   'centerline_RMS_native_pixels': float(np.sqrt(np.mean((ys - np.polyval(coeff, xs)) ** 2))),
                   'number_of_sampled_columns': len(xs)}

specs = [('north_offshore', (85, 250, 135, 255)),
         ('north_near_coast', (280, 314, 97, 121)),
         ('west_short_segment', (59, 75, 276, 299)),
         ('southwest_long_segment', (88, 179, 308, 375)),
         ('south_diagonal', (207, 437, 249, 373))]
fits = [fit(name, rect) for name, rect in specs]
n1, n2, w, sw, s = [x[0] for x in fits]

def intersection(a, b):
    x = (b[1] - a[1]) / (a[0] - b[0])
    return float(x), float(np.polyval(a, x))

def native_to_geography(x, y):
    # Least squares fit of native raster graticule border transitions.
    # x anchors at -18,-16,-14: 78.5,234.5,392.5 (zero-based pixels).
    # y anchors at 12,10,8: 19.0,177.5,336.5.
    return -16 + (x - 235.1666666667) / 78.5, 10 - (y - 177.6666666667) / 79.375

def native_to_crop(x, y):
    # PDF image matrix 240.06 x 204.48 at 285.66,112.56;
    # image514 x438, PDF top474.96; crop(290,470) with3x render.
    return x * 240.06 / 514 * 3 - 13.02, y * 204.48 / 438 * 3 + 14.88

points = [('W', 'Western principal corner', intersection(n1, w), .05),
          ('N', 'Northern coastal endpoint', (315.5, float(np.polyval(n2, 315.5))), .08),
          ('S', 'Southern coastal endpoint', (446.0, float(np.polyval(s, 446.0))), .08),
          ('SW', 'Southern offshore corner', intersection(sw, s), .05),
          ('WE', 'Western closing-edge elbow', intersection(w, sw), .05),
          ('NB', 'Northern maritime-edge bend', intersection(n1, n2), .05)]
table = []
for short, label, p, tolerance in points:
    lon, lat = native_to_geography(*p)
    crop = native_to_crop(*p)
    table.append({'id': short, 'label': label, 'native_x': p[0], 'native_y': p[1],
                  'crop_x': crop[0], 'crop_y': crop[1], 'longitude': lon, 'latitude': lat,
                  'image_interpretation_bound_degrees': tolerance,
                  'longitude_bound': [lon - tolerance, lon + tolerance],
                  'latitude_bound': [lat - tolerance, lat + tolerance]})

review = {'source': 'Guénette and Diallo2004 Figure1, printed124 / PDF128',
          'source_raster_dimensions': [514, 438],
          'rendered_crop_dimensions': [714, 708],
          'pixel_convention': 'Zero-based x fromleft, y fromtop. Pixel transition anchors use midpoint of adjacent raster pixels.',
          'graticule_anchors_native': {'longitude': [[-18,78.5],[-16,234.5],[-14,392.5]],
                                       'latitude': [[12,19.0],[10,177.5],[8,336.5]]},
          'native_pixels_per_degree': {'longitude':78.5,'latitude':79.375},
          'line_fits': [x[1] for x in fits], 'vertices': table,
          'recommended_maritime_boundary_order': ['N','NB','W','WE','SW','S'],
          'review_scope': 'Read-only source-figure calibration; no regional files, database, landmask or GIS boundaries changed.',
          'uncertainty': 'Bounds are conservative image interpretation bounds, not statisticalconfidence intervals. Offshore points include~3pixels endpoint/line interpretation plus~1pixel graticule uncertainty(~0.05degrees). Coastal points allow~6pixels source-coast/black-stroke occlusion plus~1pixel graticule uncertainty(~0.08degrees). Geographic reconstruction with a modern coarse coast should still report~0.1-0.2degrees and distinct coastline uncertainty; source artwork doesnot provide authoritative GIS.',
          'visual_concerns': ['A real bend is visible on the western closing edge near18.00W,8.42N. A straight W-to-SW chord misses it.',
                             'The northern maritime boundary has two visible straight segments and a bend near15.58W,10.66N.',
                             'Open circles sometimes obscure or sit off the thick gray line; circle centers alone are not reliable polygon vertex anchors.',
                             'Black bathymetry contours and the black coastline must not be mistaken for the thick gray domain outline.',
                             'The coast between N and S must follow the source coastal margin; a direct chord or inland closure is not itself source evidence.',
                             'The earlier W(-18.35,9.15) is about0.31degrees too far north; its geographic uncertainty range doesnot overlap the image-calibrated western latitude bound.']}
(OUT / 'graticule_polygon_review.json').write_text(json.dumps(review, indent=2, ensure_ascii=False), encoding='utf-8')
with (OUT / 'pixel_coordinate_table.csv').open('w', newline='', encoding='utf-8') as file:
    fields = ['id','label','native_x','native_y','crop_x','crop_y','longitude','latitude','image_interpretation_bound_degrees']
    writer = csv.DictWriter(file, fieldnames=fields, extrasaction='ignore')
    writer.writeheader(); writer.writerows(table)

source = Image.open(SOURCE).convert('RGB')
canvas = Image.new('RGB', (1200,708),'white'); canvas.paste(source,(0,0))
draw = ImageDraw.Draw(canvas)
font_path = Path('C:/Windows/Fonts/arial.ttf')
font = ImageFont.truetype(str(font_path),16)
small = ImageFont.truetype(str(font_path),13)
big = ImageFont.truetype(str(font_path),20)
by_id = {x['id']:x for x in table}
line_order = review['recommended_maritime_boundary_order']
draw.line([(by_id[k]['crop_x'],by_id[k]['crop_y']) for k in line_order],fill=(0,140,150),width=2)
offsets = {'W':(9,8),'N':(8,-23),'S':(8,10),'SW':(-26,-22),'WE':(-31,8),'NB':(-28,-24)}
for v in table:
    x,y = v['crop_x'],v['crop_y'];draw.ellipse((x-4,y-4,x+4,y+4),outline=(0,110,130),width=2)
    ox,oy=offsets[v['id']];draw.text((x+ox,y+oy),v['id'],font=font,fill=(0,90,110))
old_native=(235.1666666667+(-18.35+16)*78.5,177.6666666667-(9.15-10)*79.375)
ox,oy=native_to_crop(*old_native)
draw.line((ox-5,oy-5,ox+5,oy+5),fill=(190,40,40),width=2);draw.line((ox-5,oy+5,ox+5,oy-5),fill=(190,40,40),width=2)
draw.text((ox+10,oy-18),'Prior W',font=small,fill=(190,40,40))
draw.line((ox,oy,by_id['W']['crop_x'],by_id['W']['crop_y']),fill=(190,40,40),width=1)
draw.text((732,18),'Independent Figure1 calibration',font=big,fill='black')
draw.text((732,51),'Teal: source gray-line center trace; red: prior W.',font=small,fill='black')
draw.text((732,78),'Coordinates are image-derived approximations.',font=small,fill='black')
y=118
for v in table:
    draw.text((732,y),f"{v['id']}: {v['label']}",font=font,fill=(0,90,110))
    draw.text((732,y+23),f"({v['longitude']:.3f}, {v['latitude']:.3f}) +/-{v['image_interpretation_bound_degrees']:.2f} deg",font=small,fill='black')
    draw.text((732,y+43),f"Crop px ({v['crop_x']:.1f}, {v['crop_y']:.1f}); native ({v['native_x']:.1f}, {v['native_y']:.1f})",font=small,fill='black')
    y+=76
draw.text((732,603),'Anchors in native514x438 raster:',font=font,fill='black')
draw.text((732,628),'Lon -18,-16,-14 at x78.5,234.5,392.5',font=small,fill='black')
draw.text((732,650),'Lat12,10,8 at y19.0,177.5,336.5',font=small,fill='black')
draw.text((732,674),'Bounds are image interpretation, not GIS confidence.',font=small,fill='black')
canvas.save(OUT / 'calibrated_source_annotations.png')
print(json.dumps(table,indent=2))
