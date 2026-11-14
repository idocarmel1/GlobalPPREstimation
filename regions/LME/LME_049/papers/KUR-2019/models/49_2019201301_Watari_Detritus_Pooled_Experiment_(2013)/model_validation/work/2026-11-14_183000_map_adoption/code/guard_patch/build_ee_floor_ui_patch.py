"""Build narrow presentation candidates and reviewable diffs; no live writes."""
import sys, difflib, hashlib, json
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent
mode=sys.argv[1]
def replace_once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new,1)
active='The signed researcher review applies to the model, diagnostics and calculation conditions recorded in its report. Other method results retain their own diagnostic status.'
pending='The recorded researcher review is awaiting current verification.'
unreviewed='No verified researcher review is recorded for this model.'
if mode=='js':
    path=ROOT/'tools/project_core/maps/ee_floor.js';original=path.read_text('utf-8')
    old="""    let note='The floor assumes a hypothetical external nonfishery mortality sink, excluded from catch and fishery PPR.';
    if(finite(provenance.affected_group_count))note+=' '+provenance.affected_group_count+' affected groups.';
    if(finite(provenance.external_mortality_export_total))note+=' External mortality export: '+number(provenance.external_mortality_export_total)+' in saved model flow units.';
    wrap.appendChild(element('p',note));
    wrap.appendChild(element('p',model.researcher_review||model.recorded_review_pending
      ?'The signed researcher review retains its original scope and does not approve this changed calculation assumption or transformed diagnostics.'
      :'This calculation assumption and its transformed diagnostics require separate researcher review.'));"""
    new="""    let note='No EE floor is applied in this saved calculation.';
    if(provenance.use_ee_floor){
      note='The floor assumes a hypothetical external nonfishery mortality sink, excluded from catch and fishery PPR.';
      if(finite(provenance.affected_group_count))note+=' '+provenance.affected_group_count+' affected groups.';
      if(finite(provenance.external_mortality_export_total))note+=' External mortality export: '+number(provenance.external_mortality_export_total)+' in saved model flow units.';
    }
    wrap.appendChild(element('p',note));
    wrap.appendChild(element('p',model.researcher_review
      ?'"""+active+"""'
      :model.recorded_review_pending
        ?'"""+pending+"""'
        :'"""+unreviewed+"""'));"""
    (OUT/'ee_floor_ui_candidate.js').write_text(replace_once(original,old,new),encoding='utf-8',newline='\n')
elif mode=='source':
    path=ROOT/'tools/project_core/maps/ee_floor_layout.py';original=path.read_text('utf-8')
    old="""            parts.append('<p><b>'+escape(model.get('label') or model['id'])+'</b> · '+escape(setting)+'. '
                         +'Hypothetical external nonfishery mortality sink; excluded from catch and fishery PPR. '
                         +'Existing signed researcher reviews retain their original scope and do not approve this changed calculation assumption or transformed diagnostics.'
                         +(' '+ ' · '.join(links) if links else '')+'</p>')"""
    new="""            assumption = ('Hypothetical external nonfishery mortality sink; excluded from catch and fishery PPR.'
                          if enabled else 'No EE floor is applied in this saved calculation.')
            review_note = ('"""+active+"""'
                           if model.get('researcher_review') else
                           '"""+pending+"""'
                           if model.get('recorded_review_pending') else
                           '"""+unreviewed+"""')
            parts.append('<p><b>'+escape(model.get('label') or model['id'])+'</b> · '+escape(setting)+'. '
                         +assumption+' '+review_note
                         +(' '+ ' · '.join(links) if links else '')+'</p>')"""
    (OUT/'ee_floor_layout_candidate.py').write_text(replace_once(original,old,new),encoding='utf-8',newline='\n')
elif mode=='patches':
    pairs=[
      ('tools/project_core/maps/ee_floor.js','ee_floor_ui_candidate.js'),
      ('tools/project_core/maps/ee_floor_layout.py','ee_floor_layout_candidate.py'),
      ('tools/workflow_checks/maps/check_ee_floor_views.js','check_ee_floor_views_candidate.js'),
      ('tools/workflow_checks/maps/test_ee_floor_views.py','test_ee_floor_views_candidate.py')]
    chunks=[]
    for native,candidate in pairs:
        before=(ROOT/native).read_text('utf-8');after=(OUT/candidate).read_text('utf-8')
        chunks.append(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+native,tofile='b/'+native)))
    (OUT/'ee_floor_ui_source_only.patch').write_text(chunks[0],encoding='utf-8',newline='\n')
    (OUT/'ee_floor_presentation_source_only.patch').write_text(''.join(chunks[:2]),encoding='utf-8',newline='\n')
    (OUT/'ee_floor_presentation_with_tests.patch').write_text(''.join(chunks),encoding='utf-8',newline='\n')
    print(json.dumps({'production_hashes':{native:hashlib.sha256((ROOT/native).read_bytes()).hexdigest() for native,_ in pairs},'candidate_hashes':{candidate:hashlib.sha256((OUT/candidate).read_bytes()).hexdigest() for _,candidate in pairs}},indent=2))
else: raise ValueError(mode)

