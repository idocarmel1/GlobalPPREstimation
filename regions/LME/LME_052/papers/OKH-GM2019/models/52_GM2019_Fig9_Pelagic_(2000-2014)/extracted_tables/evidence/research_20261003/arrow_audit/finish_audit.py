from pathlib import Path
from PIL import Image, ImageChops
import json
import numpy as np

OUT = Path(__file__).resolve().parent
BASE = OUT.parents[1]
im = Image.open(BASE/'audit'/'figure9_original.png').convert('RGB')
a = np.asarray(im)
blue = (a[:,:,2]>170)&(a[:,:,0]<120)&(a[:,:,1]>80)&(a[:,:,1]<210)
black = a.max(axis=2)<130
aid = np.ones(a.shape,dtype=np.uint8)*255
aid[blue|black] = a[blue|black]
aid = Image.fromarray(aid)
checks=[]
for name,bounds,scale in [
    ('copepod_smelt_context',(90,390,1090,990),2),
    ('smelt_blue_heads',(260,820,500,1000),4),
]:
    raw=im.crop(bounds)
    raw.save(OUT/(name+'_source_native.png'))
    raw.resize((raw.width*scale,raw.height*scale),Image.Resampling.NEAREST).save(OUT/(name+f'_source_x{scale}.png'))
    aid.crop(bounds).resize((raw.width*scale,raw.height*scale),Image.Resampling.NEAREST).save(OUT/(name+f'_blue_reading_aid_x{scale}.png'))
    assert ImageChops.difference(Image.open(OUT/(name+'_source_native.png')).convert('RGB'),raw).getbbox() is None
    checks.append({'file':name+'_source_native.png','bounds':list(bounds),'exact_native_source_pixels':True})

finding={
    'question':'Does Figure 9 draw a copepod -> deep-sea-smelt feeding arrow, including an unlabelled arrow?',
    'source':'Original Figure 9, Gorbatenko and Melnikov 2019, PDF p.15 / printed p.157',
    'result':'No drawn copepod -> smelt blue feeding shaft terminating in a smelt arrowhead was found.',
    'confidence':'high within the visible original raster; bounded negative visual finding',
    'copepod_blue_outgoing_inventory':[
        {'flow_id':'F12','label':'1,1','route':[4,10],'observation':'Outer-left blue curve starts near (249,441), goes around the hyperiid box, and ends at herring near (177,894).'},
        {'flow_id':'F10','label':'4,1','route':[4,6],'observation':'Blue curve starts near (255,465), bows left through its 4,1 label, and ends at the hyperiid top near (212,766).'},
        {'flow_id':'F11','label':'20,1','route':[4,7],'observation':'Thick blue shaft leaves copepods near (377,474), bows left and then down/right, and ends at the chaetognath upper-left corner near (382,771).'},
        {'flow_id':'F18','label':'0,736','route':[4,12],'observation':'Thin blue curve leaves copepods near (500,464), travels down/right past 0,736, and ends at small pollock near (641,894).'},
    ],
    'smelt_blue_arrowhead_inventory':[
        {'flow_id':'F17','label':'0,448','route':[5,11],'observation':'The visible blue feeding head at the smelt top near (379,893) belongs to the thin 0,448 curve, whose upper shaft can be followed to the euphausiid bottom attachment near (929,471). It does not start at copepods.'},
    ],
    'passing_shaft':{'flow_id':'F15','label':'4,4','route':[5,15],'observation':'A thick blue euphausiid curve passes across/through the left part of the smelt box, then continues below it and ends at medium pollock around (299,1097). No blue arrowhead attaches this passing shaft to smelt. A shaft crossing a box is not independently a feeding endpoint.'},
    'unlabelled_edge_check':'No extra unlabelled blue head entering smelt, and no extra blue branch leaving copepods toward smelt, was identified.',
    'relationship_to_prose':'The article p.155 prose diet percentages and annual wet consumption motivated this location check only. They were not used to reroute a drawn line. The diagram-only missing-arrow zero for 4->11 is consistent with this bounded visual absence finding; any prose-derived supplementation should carry separate provenance and scope.',
    'source_crops':checks,
    'reading_aids':['copepod_smelt_context_blue_reading_aid_x2.png','smelt_blue_heads_blue_reading_aid_x4.png'],
    'raw_vs_aid':'*_source_native.png contains exact unmodified source pixels. *_source_xN.png is a nearest-neighbor enlargement. *_blue_reading_aid_xN.png analytically isolates blue and dark text pixels and is not source evidence on its own.',
    'model_edits':'None',
}
(OUT/'copepod_smelt_finding.json').write_text(json.dumps(finding,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'copepod_smelt_finding.txt').write_text('Figure 9 copepod -> smelt bounded visual check\n\nNo drawn blue feeding arrow from copepods to smelt was found, labelled or unlabelled. Four blue shafts leave copepods: 1,1 to herring, 4,1 to hyperiids, 20,1 to chaetognaths and 0,736 to small pollock. The blue head at smelt belongs to 0,448 from euphausiids. The thick 4,4 euphausiid shaft passes through the smelt box without a head there and continues to medium pollock. This supports genuine diagram absence within the visible raster, rather than a swapped copepod/smelt route. The p.155 prose values did not determine this finding. No model or baseline ledger was edited.\n\nExact native source crops: copepod_smelt_context_source_native.png [90,390,1090,990]; smelt_blue_heads_source_native.png [260,820,500,1000]. Analytical blue-only aids and nearest-neighbor enlargements are separate files.\n',encoding='utf-8')

audit=json.loads((OUT/'proposed_route_changes.json').read_text(encoding='utf-8'))
decisions={
    'source':audit['source'],
    'scope':'Source audit recommendations only. Parent creates any derivative numerical variant. Original baseline is preserved.',
    'decisions':[
        {'flow_id':'F77','decision':'Recommend 15->20, replacing adopted 19->20','routing_confidence':'high','numeric_literal':'0,01','value':'0.01','evidence':audit['proposals'][0]},
        {'flow_id':'F22','decision':'Confirm same route 5->18','routing_confidence':'high','numeric_literal':'0,141','value':'0.141','evidence':audit['proposals'][1]},
        {'flow_id':'F78','decision':'Retain adopted 15->21 tentative; no endpoint change','routing_confidence':'tentative','numeric_literal':'0,05','numeric_confidence':'high; label shadow is not a trailing 1','evidence':audit['unresolved_route_findings'][-1]},
        {'flow_ids':['F26','F47','F41','F42','F52','F57'],'decision':'Keep duplicated-pair hypotheses unresolved; no exact substitute endpoint','routing_confidence':'tentative','evidence':audit['unresolved_route_findings'][:3]},
        {'flow_ids':['F62','F67'],'decision':'Separate human numeric readings from unresolved route confidence','routing_confidence':'tentative','evidence':audit['literal_findings'][:2]},
        {'flow_id':'F13','decision':'Confirm same route 5->6; confidence upgrade recommended','routing_confidence':'high','numeric_literal':'0,283','value':'0.283','evidence':audit['proposals'][2]},
    ],
    'jellyfish_blue_incoming':audit['jellyfish_blue_incoming_check'],
    'copepod_smelt_blue_check':finding,
    'raw_vs_annotated':'Unannotated *_source_native.png crops preserve source pixels. *_source_xN.png enlarge those pixels. Color-only *_reading_aid_* files and F77_annotated_path_x3.png are diagnostic aids, not independently authoritative source reconstructions.',
}
(OUT/'route_decisions.json').write_text(json.dumps(decisions,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

(OUT/'FINDINGS.md').write_text('''# Figure 9 source audit

**F77 supports medium pollock -> predatory fish (15 -> 20), replacing 19 -> 20.** Its green shaft starts at medium pollock, passes through the large-pollock box without an arrowhead there, and ends at predatory fish. Confidence: high. Review [unannotated native source crop](F77_unannotated_source_crop.png), bounds `[140,1080,820,1525]`, beside the [annotated diagnostic path](F77_annotated_path_x3.png).

**F22 confirms euphausiids -> baleen whales (5 -> 18).** The inner blue `0,141` curve can be followed to its blue arrowhead at the whale box. Confidence: high. See [whole-route source crop](F22_entire_route_source_native.png), bounds `[540,400,1318,1340]`, and [endpoint crop](F22_whale_endpoint_source_native.png), bounds `[710,1200,960,1340]`. No omitted blue feeding arrowhead into jellyfish was found in the [local source check](jellyfish_blue_incoming_check_source_native.png), bounds `[800,740,1318,1020]`. This is a bounded negative visual finding.

**F78 remains tentative 15 -> 21.** Its literal is `0,05`; the apparent trailing `1` is the white label box's dark shadow. The shallower green diagonal continues across the predatory-fish box toward mammals, while the steeper squid-IV bow ends at a nearby predatory-fish head. Their close crossing/head overlap prevents a confidence upgrade. See [label and heads](F78_label_and_heads_source_native.png) and [continuation](F78_continuation_source_native.png).

**No drawn copepod -> smelt blue feeding arrow was found, labelled or unlabelled.** The four visible copepod blue shafts lead to herring (`1,1`), hyperiids (`4,1`), chaetognaths (`20,1`) and small pollock (`0,736`). The blue smelt head belongs to `0,448` from euphausiids. The thick `4,4` euphausiid shaft passes through the smelt box without a head and continues to medium pollock. See [source context](copepod_smelt_context_source_native.png), bounds `[90,390,1090,990]`, and [smelt heads](smelt_blue_heads_source_native.png), bounds `[260,820,500,1000]`. Confidence: high within the visible raster. The p.155 prose diet figures prompted inspection but were not used to reroute a line; prose-derived supplementation requires separate provenance.

F13 (`0,283`) also supports its existing euphausiid -> hyperiid route with high confidence. F26/F47, F41/F42, F52/F57 and the dense red priority routes remain unresolved; no exact substitute endpoints are proposed. Numeric F62 (`0.023` preferred, `0.025` alternative) and F67 (`0.05` confirmed) are user readings conveyed by the parent, recorded separately from route confidence.

All 21 living production box values match the adopted Figure 9 ledger. Detritus displays no number. Large pollock clearly reads `0,009`, not `0,001`. Figure/Table 3 differences remain preserved.

[route_decisions.json](route_decisions.json) carries concise decisions and confidence. [proposed_route_changes.json](proposed_route_changes.json) retains detailed visual justifications. [production_node_audit.json](production_node_audit.json) holds every node reading; [audit_verification.json](audit_verification.json) verifies exact native source crops.

Native source crops contain unmodified source pixels. Enlargements use nearest-neighbor resampling. Color-only reading aids and annotated paths are diagnostic overlays. The source is Gorbatenko and Melnikov (2019), Figure 9, PDF p.15 / printed p.157. The supporting thesis was viewed only for context; its extra arrows were not imported. No baseline source, ledger, model, CSV, workbook or report was edited.
''',encoding='utf-8')
print('Saved FINDINGS.md, route_decisions.json, and copepod/smelt source crops and finding.')
