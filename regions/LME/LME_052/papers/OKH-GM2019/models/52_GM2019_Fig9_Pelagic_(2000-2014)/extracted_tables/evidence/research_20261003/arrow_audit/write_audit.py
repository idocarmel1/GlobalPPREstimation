from pathlib import Path
from PIL import Image, ImageChops
import hashlib
import json
import runpy

BASE = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SOURCE = BASE / 'audit' / 'figure9_original.png'
PDF = BASE.parents[1] / 'papers' / 'OKH-GM2019' / 'gorbatenko_melnikov_2019.pdf'


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


source = {
    'article': 'Gorbatenko and Melnikov (2019), Figure 9',
    'source_pdf': str(PDF),
    'pdf_page_1_based': 15,
    'printed_page': 157,
    'source_pdf_sha256': sha(PDF),
    'source_image': str(SOURCE),
    'source_image_sha256': sha(SOURCE),
    'source_image_dimensions': [1318, 1627],
    'coordinates': 'Original raster x/y pixels, origin at top left; crop bounds use PIL exclusive right/bottom.',
}

proposals = [
    {
        'flow_id': 'F77',
        'change_type': 'source_endpoint_correction',
        'adopted': {'prey_id': 19, 'consumer_id': 20, 'routing_status': 'tentative'},
        'proposed': {'prey_id': 15, 'consumer_id': 20, 'routing_status': 'clear'},
        'literal': '0,01',
        'value': '0.01',
        'confidence': 'high',
        'justification': 'The green shaft leaves the bottom of medium pollock around (295,1163), bows left through (284,1235), then passes through (300,1320) and (327,1384). It crosses the large-pollock box as a shaft, with no green arrowhead there. Beyond the label gap it continues through (390,1449), (450,1474), and (513,1485), ending in the green arrowhead at the left edge of predatory fish around (559,1484). Thus the large-pollock box is a crossing, not the origin of this curve.',
        'path_checkpoints': [[295,1163],[284,1235],[300,1320],[327,1384],[390,1449],[450,1474],[513,1485],[559,1484]],
        'source_crop': 'F77_unannotated_source_crop.png',
        'source_crop_bounds': [140,1080,820,1525],
        'diagnostics': ['F77_annotated_path_x3.png', 'F77_green_reading_aid_x3.png'],
        'adoption': 'Proposal only in this audit. Root independently reviewed the crop and communicated agreement; root owns any adoption in a new variant.',
    },
    {
        'flow_id': 'F22',
        'change_type': 'routing_confidence_upgrade_without_endpoint_change',
        'adopted': {'prey_id': 5, 'consumer_id': 18, 'routing_status': 'tentative'},
        'proposed': {'prey_id': 5, 'consumer_id': 18, 'routing_status': 'clear'},
        'literal': '0,141',
        'value': '0.141',
        'confidence': 'high',
        'justification': 'The inner thin blue curve leaves the euphausiid lower/right attachment, follows the readable 0,141 label near (1260,989), turns left beneath predatory salmon, and ends in the blue arrowhead near (786,1287) at the right edge of the baleen-whale box. The outer blue 0,0075 curve is separate. No blue junction or arrowhead sends the 0,141 curve into jellyfish.',
        'source_crop': 'F22_entire_route_source_native.png',
        'source_crop_bounds': [540,400,1318,1340],
        'endpoint_crop': 'F22_whale_endpoint_source_native.png',
        'endpoint_crop_bounds': [710,1200,960,1340],
        'diagnostics': ['F22_entire_route_blue_reading_aid_x2.png'],
        'adoption': 'Proposal only; baseline ledger is not edited.',
    },
    {
        'flow_id': 'F13',
        'change_type': 'routing_confidence_upgrade_without_endpoint_change',
        'adopted': {'prey_id': 5, 'consumer_id': 6, 'routing_status': 'tentative'},
        'proposed': {'prey_id': 5, 'consumer_id': 6, 'routing_status': 'clear'},
        'literal': '0,283',
        'value': '0.283',
        'confidence': 'high',
        'justification': 'The thin blue curve begins at the upper/left euphausiid attachment around (804,416), descends left through its 0,283 label near (473,532), crosses the thick copepod-to-chaetognath curve, and ends at the blue arrowhead near (216,766) at the hyperiid top edge. Color and curvature distinguish it from the thick 1,5 and 4,4 euphausiid routes below.',
        'adoption': 'Proposal only; baseline ledger is not edited.',
    },
]

unresolved = [
    {'flow_ids':['F26','F47'], 'issue':'Duplicate 6->9 hypothesis', 'result':'Unresolved. The upper 0,241 arch and lower 0,021 bow are separate displayed curves. Dense upper/right crossings prevent a secure common squid-III endpoint. Do not treat the duplicate adopted pair as visually validated or replace its endpoint using balance.'},
    {'flow_ids':['F41','F42'], 'issue':'Duplicate 10->15 hypothesis', 'result':'Unresolved. Around 0,685 an apparent down/right red tip lies near (193,1013), above the medium-pollock box. A shaft can be followed upward through the herring area toward hyperiids, but crossings and detached-looking placement prevent a secure origin/destination substitution. The 0,139 curve descends toward medium pollock; the two adopted herring routes are not independently confirmed as the same pair.', 'diagnostics':['F41_F42_origins_source_x4.png','F41_F42_pixel_nearest.png']},
    {'flow_ids':['F52','F57'], 'issue':'Duplicate 13->15 hypothesis', 'result':'Unresolved. 0,57 and 0,024 are visibly distinct labels beside crossing/overlapping lower curves. The 0,024 arrowhead is at the right side of medium pollock, while the 0,57 neighborhood also contains a red diagonal pointing up/right toward capelin and another bow near squid IV. A unique source/endpoint assignment cannot be proven from this crossing.', 'diagnostics':['F52_F57_origins_source_x4.png']},
    {'flow_ids':['F23'], 'issue':'Outer 0,0075 blue curve', 'result':'General outer euphausiid-to-large-pollock path is supported, but its terminal region overlaps a green shaft/red arrowheads. Retain tentative rather than upgrade the obscured exact attachment.'},
    {'flow_ids':['F24','F27','F28','F31','F38','F39','F48','F50','F56','F58','F59','F60','F61','F63','F64','F65','F66','F68','F69','F70','F71','F72'], 'issue':'Priority red routes around squid III, herring, smelt, capelin, squid IV and large pollock', 'result':'No exact replacement route is proposed. The reviewed source has numerous crossings, white label knockouts, close parallel segments and arrowhead overlaps. Some automated trace aids join two differently labelled curves, so they cannot establish endpoints. Retain the original tentative/overprinted routing status for these cases.'},
    {'flow_ids':['F78'], 'issue':'0,05 green diagonal and overlap near predatory fish', 'result':'Retain adopted 15->21 as tentative. A shallower green diagonal from medium pollock continues across the predatory-fish box to the separate arrowhead entering the mammal box near (902,1523). A steeper green bow from squid IV ends in the green tip entering predatory fish near (569,1454). The close crossing/head overlap makes the assignment of the 0,05 diagonal insufficient for an upgrade to clear; a 15->20 interpretation would be an explicit alternative only.', 'diagnostics':['F78_label_and_heads_source_x4.png','F78_continuation_source_x4.png']},
]

literals = [
    {'flow_id':'F62','visual_literal':'0,02X','visual_reading_status':'final digit overprinted','preferred_human_reading':'0.023','human_alternative':'0.025','human_provenance':'Root conveyed direct user reading on 2026-10-03: 0.02X with final digit 3 or 5, preference 0.023, alternative 0.025 for sensitivity.','numeric_adoption_recommendation':'Keep these as preferred/alternative human readings, not an exact independent visual reading.','route_recommendation':'Keep route tentative independently of numeric choice.','diagnostics':['F62_label_source_x4.png','F62_literal_source_x3.png']},
    {'flow_id':'F67','visual_literal':'0,05','visual_reading_status':'partly overprinted; compatible with human reading','human_confirmed_reading':'0.05','human_provenance':'Root conveyed direct user confirmation F67=0.05 on 2026-10-03.','numeric_adoption_recommendation':'The new variant can use 0.05 with human-confirmed numeric provenance.','route_recommendation':'The endpoint/source route remains tentative; numeric confirmation does not resolve it.','diagnostics':['F67_label_source_x4.png','F67_literal_source_x3.png']},
    {'flow_id':'F78','visual_literal':'0,05','value':'0.05','confidence':'high','justification':'The apparent trailing vertical stroke is the right edge/drop shadow of the white label box, not a printed 1. The original crop contains only 0,05.','diagnostics':['F78_label_and_heads_source_x4.png']},
]

negative = {
    'question':'Is a drawn blue incoming arrow to jellyfish omitted from the adopted ledger?',
    'result':'No blue arrowhead entering jellyfish was found in the original source.',
    'confidence':'high for the visible local diagram; bounded negative visual finding, not proof of a complete author diet',
    'observations':'Blue arrowheads in the local region enter squid III and capelin. The two thin outer blue curves pass outside the jellyfish box and continue downward; the inner 0,141 route ends at baleen whales. No unlabelled blue incoming edge to jellyfish was identified.',
    'source_crop':'jellyfish_blue_incoming_check_source_native.png',
    'source_crop_bounds':[800,740,1318,1020],
    'diagnostic':'jellyfish_blue_incoming_check_blue_reading_aid_x2.png',
    'convention':'A genuinely drawn unlabelled arrow must be unknown, not a missing-arrow zero. This audit found no such blue jellyfish edge.',
}

dump('proposed_route_changes.json', {
    'audit_date':'2026-10-03', 'source':source,
    'status':'Separate source audit; no baseline model or ledger edited',
    'method':'Direct visual inspection of original raster, unannotated crops, nearest-neighbor enlargements, and analytical color isolation. Coordinates/dashed annotations are diagnostic overlays. No numerical balance was used as route evidence. Supporting thesis Figure 8.2 was viewed for context only and its extra arrows were not imported.',
    'scope':'All 22 node production labels; targeted feeding-route review, especially duplicate pairs and priority balance-failure groups. This is a bounded audit, not a claim that all 78 routes have been independently resolved.',
    'proposals':proposals, 'unresolved_route_findings':unresolved,
    'literal_findings':literals, 'jellyfish_blue_incoming_check':negative,
})

# Independent manual node readings, entered before comparison with adopted values.
node_values = ['694,8','101,1','35,1','117,2','56,1','4,752','12,78','0,105','0,105','0,119','0,06','0,197','0,03','0,144','0,59','0,1','0,002','0,001','0,009','0,004','0,001',None]
groups = runpy.run_path(str(BASE/'figure9_data.py'))['GROUPS']
nodes = []
for group, literal in zip(groups,node_values):
    gid,en,ru,adopted,bounds,tier = group
    value = literal.replace(',','.') if literal is not None else None
    assert value == adopted, (gid,value,adopted)
    nodes.append({'group_id':gid,'group':en,'source_literal':literal,'production_million_tC_per_year':value,'source_crop_bounds':list(bounds),'confidence':'high','matches_adopted_value':True,'note':'No numeric production is displayed in the detritus box.' if gid==22 else 'Direct Figure 9 box reading; not harmonized to Table 3.'})
dump('production_node_audit.json',{'source':source,'groups':nodes,'finding':'All 21 living box values match adopted Figure 9 values. Detritus displays no number. Large pollock is unambiguously 0,009, with no visual support for 0,001.','montage':'production_node_source_montage.png'})

im=Image.open(SOURCE).convert('RGB')
crop_checks=[]
for name,bounds in [('F77_unannotated_source_crop.png',(140,1080,820,1525)),('F22_entire_route_source_native.png',(540,400,1318,1340)),('F22_whale_endpoint_source_native.png',(710,1200,960,1340)),('jellyfish_blue_incoming_check_source_native.png',(800,740,1318,1020)),('F78_label_and_heads_source_native.png',(470,1370,650,1495)),('F78_continuation_source_native.png',(510,1400,1045,1580))]:
    crop=Image.open(OUT/name).convert('RGB')
    same=ImageChops.difference(crop,im.crop(bounds)).getbbox() is None
    assert same,name
    crop_checks.append({'file':name,'bounds':list(bounds),'exact_native_source_pixels':same,'sha256':sha(OUT/name)})
dump('audit_verification.json',{'source':source,'node_count':len(nodes),'living_values_verified':21,'detritus_number_absent':True,'native_crop_checks':crop_checks,'baseline_ledger_sha256_at_audit_end':sha(BASE/'audit'/'flow_readings.json'),'baseline_data_script_sha256_at_audit_end':sha(BASE/'figure9_data.py'),'write_scope':'Only research_20261003/arrow_audit. No baseline source, ledger, model, CSV, workbook or report was edited.'})

findings = '''Independent Figure 9 source audit - 2026-10-03

Main finding: change F77 source from large pollock (19) to medium pollock (15), retaining predatory fish (20), literal 0,01. The original green shaft starts at medium pollock and passes through the large-pollock box before its arrowhead enters predatory fish. This is source evidence, not a balance repair.

F22 (0,141): euphausiids -> baleen whales is visually supported through the entire inner blue curve to its blue arrowhead. Recommend upgrading route confidence to clear. No blue feeding arrowhead enters jellyfish, and no omitted drawn/unlabelled blue jellyfish edge was found in the local source check. F13 (0,283): euphausiids -> hyperiids is also visually supported; recommend upgrading confidence to clear.

F78: literal is 0,05, not 0,051; the apparent final vertical stroke is the label-box shadow. Retain medium pollock -> predatory mammals as tentative. The diagonal continues across the predatory-fish box, but the nearby squid-IV bow and green predatory-fish arrowhead overlap closely enough to prevent a confidence upgrade.

All 21 living production boxes were read directly and match the adopted Figure 9 ledger. Detritus displays no number. Large-pollock production is clearly 0,009, not 0,001. Figure/Table-3 disagreements were not harmonized.

The duplicated pairs F26/F47, F41/F42 and F52/F57 remain unresolved. No exact replacement is proposed for the dense red priority routes, including F66. White numeric-label knockouts, crossing curves, close parallel segments and overlapping heads prevent secure endpoint recovery. Automatic trace aids occasionally connect differently labelled curves and cannot be treated as source confirmation.

Numeric provenance stays separate from route confidence. The root conveyed the user's F62 reading as 0.02X, preference 0.023 and alternative 0.025; the last digit remains overprinted visually. The root conveyed user confirmation F67=0.05, which can be entered with human-confirmed numeric provenance. F62/F67 routing remains tentative.

Source: Gorbatenko and Melnikov (2019), original Figure 9 raster, PDF page 15 / printed page 157. Supporting dissertation Figure 8.2 was viewed for context only; its extra arrows were not added. All files from this audit are confined to research_20261003/arrow_audit; the baseline is preserved.

Review proposed_route_changes.json for precise justifications and crop bounds. production_node_audit.json carries all node readings; audit_verification.json checks that the native diagnostic crops contain exact source pixels.
'''
(OUT/'audit_findings.txt').write_text(findings,encoding='utf-8')
print(f'Saved audit: {OUT}')
print(f'{len(proposals)} proposals; {len(nodes)} node checks; {len(crop_checks)} exact native-crop checks')
