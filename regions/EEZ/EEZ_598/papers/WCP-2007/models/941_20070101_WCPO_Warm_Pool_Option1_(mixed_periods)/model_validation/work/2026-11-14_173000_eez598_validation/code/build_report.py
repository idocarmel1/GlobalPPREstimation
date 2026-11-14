"""Fill current template, retaining requested donor cells and regional evidence."""
from pathlib import Path
from copy import deepcopy
from zipfile import ZipFile, ZIP_DEFLATED
from urllib.parse import unquote, urlsplit
import hashlib, json, os, posixpath, sys
from lxml import etree as E
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path.cwd().resolve()
MODEL = '941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)'
OUT = ROOT/'regions/EEZ/EEZ_598/papers/WCP-2007/models'/MODEL/'model_validation'
RUN = OUT/'work/2026-11-14_173000_eez598_validation'
TEMPLATE = ROOT/'tools/templates/validation.docx'
DONOR = ROOT/'regions/EEZ/EEZ_941/papers/WCP-2007/models'/MODEL/'model_validation/validation.docx'
SOURCE = RUN/'inputs/validation_before.docx'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
REL='http://schemas.openxmlformats.org/package/2006/relationships'
CT='http://schemas.openxmlformats.org/package/2006/content-types'
WP='http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
NS={'w':W,'r':R,'a':A,'wp':WP}
def q(n): return '{'+W+'}'+n
def text(node): return ''.join(node.itertext()) if False else ''.join(node.xpath('.//w:t/text()',namespaces=NS))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def xml(b): return E.fromstring(b)
def ser(x): return E.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
def package(p):
    with ZipFile(p) as z: return {n:z.read(n) for n in z.namelist()}
if not SOURCE.exists(): SOURCE.write_bytes((OUT/'validation.docx').read_bytes())
parts=package(TEMPLATE); doc=xml(parts['word/document.xml']); body=doc.find(q('body'))
rels=xml(parts['word/_rels/document.xml.rels']); types=xml(parts['[Content_Types].xml'])
sources={p:(package(p)) for p in [SOURCE,DONOR]}
source_dirs={SOURCE:OUT,DONOR:DONOR.parent}
cache={}
def add_rel(target,typ,external=True):
    rid='rIdFilled'+str(len(rels)+1)
    r=E.SubElement(rels,'{'+REL+'}Relationship',Id=rid,Type=R+'/'+typ,Target=target)
    if external:r.set('TargetMode','External')
    return rid
def local_link(p):return os.path.relpath(p,OUT).replace('\\','/')
def import_node(node,source):
    result=deepcopy(node)
    sr={e.get('Id'):e for e in xml(sources[source]['word/_rels/document.xml.rels'])}
    for el in result.iter():
        for attr in list(el.attrib):
            if not attr.startswith('{'+R+'}'): continue
            old=el.get(attr); key=(str(source),old)
            if key not in cache:
                rr=sr[old]; target=rr.get('Target'); typ=rr.get('Type').split('/')[-1]
                if rr.get('TargetMode')=='External':
                    if not urlsplit(target).scheme and not target.startswith('#'):
                        base,sep,frag=target.partition('#')
                        resolved=(source_dirs[source]/unquote(base)).resolve()
                        # Repair two stale navigation links without changing their meaning.
                        if typ=='hyperlink' and '/EEZ_598/raw' in str(resolved).replace('\\','/'):
                            resolved=ROOT/'regions/EEZ/EEZ_598/raw/catch'
                        target=local_link(resolved)+(sep+frag if sep else '')
                    new=add_rel(target,typ)
                else:
                    original=posixpath.normpath('word/'+target)
                    assert typ=='image', (typ,target)
                    ext=Path(target).suffix.lower().lstrip('.')
                    newname=f'media/filled_{len(cache)+1}.{ext}'
                    parts['word/'+newname]=sources[source][original]
                    if not any(x.get('Extension')==ext for x in types):
                        E.SubElement(types,'{'+CT+'}Default',Extension=ext,ContentType='image/'+('jpeg' if ext in ('jpg','jpeg') else ext))
                    new=add_rel(newname,typ,False)
                cache[key]=new
            el.set(attr,cache[key])
    return result
def fields(source):
    result={}
    for row in xml(sources[source]['word/document.xml']).xpath('.//w:tbl/w:tr',namespaces=NS):
        cells=row.findall(q('tc'))
        if len(cells)==2: result[text(cells[0])]=cells[1]
    return result
oldfields=fields(SOURCE); donorfields=fields(DONOR)
paras=body.findall(q('p')); tables=body.findall(q('tbl'))
def run(value,bold=False):
    r=E.Element(q('r')); pr=E.SubElement(r,q('rPr'))
    if bold:E.SubElement(pr,q('b'))
    t=E.SubElement(r,q('t'));t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=str(value)
    return r
def setp(p,value):
    for el in list(p):
        if el.tag!=q('pPr'):p.remove(el)
    p.append(run(value));return p
def para(value=''):
    return setp(deepcopy(paras[3]),value)
def setcell(cell,values):
    pattern=cell.find(q('p'))
    for el in list(cell):
        if el.tag!=q('tcPr'):cell.remove(el)
    for value in values if isinstance(values,list) else [values]:
        p=deepcopy(pattern) if pattern is not None else E.Element(q('p'))
        cell.append(setp(p,value))
def link(p,label,target):
    h=E.SubElement(p,q('hyperlink'));h.set('{'+R+'}id',add_rel(target,'hyperlink'))
    rr=run(label);pr=rr.find(q('rPr'));E.SubElement(pr,q('color')).set(q('val'),'0563C1');E.SubElement(pr,q('u')).set(q('val'),'single');h.append(rr)
def replace_cell(target,source,cell):
    copy=import_node(cell,source)
    target.getparent().replace(target,copy)
def tablerows(t,rows):
    prototype=deepcopy(t.findall(q('tr'))[1])
    for row in t.findall(q('tr'))[1:]:t.remove(row)
    for vals in rows:
        row=deepcopy(prototype)
        for cell,val in zip(row.findall(q('tc')),vals):setcell(cell,str(val))
        t.append(row)
def pct(value):
    from tools.project_core.validation.validation_percentage_format import format_percent
    return format_percent(value)
sys.path.insert(0,str(ROOT))
summary=json.loads((OUT/'evidence/mapping/mapping_summary.json').read_text('utf-8'))

for row in tables[0].findall(q('tr'))[1:]:
    label,entry=row.findall(q('tc')); name=text(label)
    src=DONOR if name in ['SPPR calculation','Review and reproducibility','GE diagnostics','TE diagnostics','Other','Model extraction'] else SOURCE
    cells=donorfields if src==DONOR else oldfields
    if name in cells:replace_cell(entry,src,cells[name])
main={text(r.findall(q('tc'))[0]):r.findall(q('tc'))[1] for r in tables[0].findall(q('tr'))[1:]}
main['Other'].append(para('The copied SPPR sensitivity table reports EEZ_941 regional totals.'))
setp(paras[0],'Papua New Guinea model validation')
setcell(main['Region'],'Papua New Guinea, EEZ_598. ')
link(main['Region'].find(q('p')),'Regional workbook','../../../../../EEZ_598.xlsx')
# The selected-JSON label previously pointed to notes about removed evidence.
for h in main['Selected model'].xpath('.//w:hyperlink',namespaces=NS):
    if text(h)=='Selected JSON':
        rid=h.get('{'+R+'}id')
        next(r for r in rels if r.get('Id')==rid).set('Target','../model.json')
setcell(main['Geographic fit'],['A. Region covered by study: approximately 100%.','B. Study area covered by region: approximately 8.9–10%.'])
link(main['Geographic fit'].findall(q('p'))[-1],' Boundary estimate','evidence/source_review/source_geography_review_20261114.json')
# The requested cells are copied intact; decision provenance is kept in evidence.
for name in ['SPPR calculation','Review and reproducibility']:
    assert text(main[name])==text(donorfields[name])

setp(paras[3],'Reference: 2019 landings; all catch labels and source groups, including zero catch and unidentified categories.')
setp(paras[4],f"31 source ecological groups (+1 computational import); {summary['n_taxa']} catch labels.")
setp(paras[5],f"Simple-chain PPR totals {summary['simple_chain_ppr_tC']:,.2f} t C in 2019.")
setp(paras[6],'47 labels lack a saved TL/coefficient. All have zero 2019 landings and therefore zero annual contribution; their missing inputs remain unknown.')
setp(paras[7],'Method: independent simple trophic chain using saved classic taxon coefficients.')
setp(paras[8],'');link(paras[8],'Taxon mapping appendix','taxon_mapping.xlsx');paras[8].append(run(' and '));link(paras[8],'descriptive Sources sheet','taxon_mapping.xlsx#Sources!A1')
tablerows(tables[1],[(r['label'],r['taxa'],pct(r['catch_percentage']),pct(r['ppr_percentage'])) for r in summary['confidence_summary']])
mrules={
 'Explicit source assignment':'Taxon explicitly assigned to the source model group or stage pair.',
 'Assumed eligible group set':'A supported eligible group set requires a composition assumption.',
 'Closest represented analogue':'Closest represented taxonomic or ecological analogue, with substantial mismatch.',
 'Broad-category approximation':'Broad catch category approximated by compatible named and pooled groups.',
 'Partial or conflicting ecological fit':'Group fit is partial or conflicts with habitat, feeding or source scope.',
 'Unambiguous documented group fit':'Source group criteria give an unambiguous documented fit.',
 'Verified synonym':'Verified taxonomic synonym connects the taxon to a named source member.',
 'Supported ecological assignment':'Ecology supports membership without an explicit source assignment.',
 'No meaningful assignment':'No meaningful source group or feeding analogue is available.',
 'Extension from listed representatives':'Membership extends from listed source representatives with a stated assumption.'}
wrules={
 'Source-model catch proportions':'Source model catches determine proportions, assumed transferable across region and years.',
 'Approved model-biomass fallback':'Complete model biomass proportions replace unusable catch proportions, with a catch-composition assumption.',
 'No split required':'All catch is assigned to one eligible group; no allocation split is required.',
 'No usable allocation':'No meaningful group assignment supports a numerical allocation.'}
tablerows(tables[2],[(mrules[r['label']],r['confidence'],pct(r['ppr_percentage'])) for r in summary['membership_summary']])
tablerows(tables[3],[(wrules[r['label']],r['confidence'],pct(r['ppr_percentage'])) for r in summary['allocation_summary']])
setp(paras[11],'Membership evidence: ');link(paras[11],'source group definitions and reporting-scope review','evidence/source_review/source_review.md#membership-and-reporting-scope')
setp(paras[13],'Weights and assumptions: source catch or biomass proportions are held fixed across catch years and bases. ');link(paras[13],'Allocation evidence','evidence/mapping/taxon_mapping_audit.json')
setp(paras[15],'Unresolved: Bivalvia, Pinctada, Tridacna gigas, Echinodermata and Holothuriidae lack a meaningful feeding or taxonomic group. Bivalvia and Pinctada have positive 2019 catch; the other three have zero. The 47 Very low decisions account for 5.3% of landings and 1.2% of simple-chain PPR.')
brief={
 'Thunnus alalunga':'Unlisted albacore/bluefins use the bigeye stage pair as a weak analogue; species, temperature and maturation differ. Historical source catch proportions are transferred.',
 'Scombridae':'Unknown family composition spans named tuna and residual scombrid groups. Complete biomass proportions proxy the regional catch composition.',
 'Lutjanidae':'Coastal, reef or demersal fish use Epi fish and its small stage as mixed-fish analogues. Depth, feeding, stage and taxonomic mismatches remain; weights use biomass proportions.',
 'Marine fishes not identified':'Residual bony-fish composition is unknown. All 17 compatible named and pooled bony-fish groups are included; mixed bathyal pools also contain invertebrates. Complete biomass proportions are transferred across years and bases.',
 'Marine pelagic fishes not identified':'Residual bony-fish composition is unknown. All 17 compatible named and pooled bony-fish groups are included; mixed bathyal pools also contain invertebrates. Complete biomass proportions are transferred across years and bases.',
 'Gastropoda':'Pelagic gastropod pools proxy sea snails and reef-grazing Trochus, with substantial habitat/feeding mismatch. Weights use biomass proportions.',
 'Penaeus merguiensis':'Coastal/benthic penaeids use the sole M Bathy forage taxonomic analogue; bathypelagic depth and feeding differ substantially.',
 'Elasmobranchii':'Shark groups proxy a reporting category that also includes rays/skates, which are unrepresented. Chimaeras are outside this category. Historical shark catch proportions are transferred.',
 'Lates calcarifer':'Large estuarine/demersal barramundi uses Piscivorous fish as the sole predator analogue, with substantial habitat and taxonomic mismatch.',
 'Malacostraca':'Broad crustacean categories include benthic adults beyond the compatible pelagic/deep-water crustacean pools. Biomass proportions proxy unknown composition.',
 'Miscellaneous marine crustaceans':'Reported crabs, shrimps and lobsters use mixed pelagic/deep-water pools containing lobster taxa, crab stages and shrimps. Adult habitat/stage and other-taxon content remain mismatched; weights use biomass.',
 'Scylla serrata':'Benthic adult mud crab uses Epi crust, containing megalopa-stage crustaceans, as the sole larval analogue. Habitat and stage mismatch are substantial.',
 'Chondrichthyes':'Shark pools proxy sharks, rays/skates and chimaeras; the latter components are unrepresented. Historical shark catch proportions are transferred.',
 'Mollusca':'Broad mollusc reporting includes unrepresented benthic taxa. Pelagic mollusc and mollusc-bearing bathyal pools provide a partial composite weighted by biomass.',
 'Octopoda':'Surface, mesopelagic and bathypelagic octopod pools proxy a category also containing unrepresented benthic octopuses. Four compatible pools use biomass weights.',
 'Perciformes':'Regional species composition is unknown. Epi fish and its small stage proxy a broad demersal category, with omitted taxa and habitat mismatch; weights use biomass.',
 'Sepia':'Neritic/benthic cuttlefish use Epi mollusc and its small stage as muscular-cephalopod analogues. Habitat and taxonomy differ; Sepiolidae is not Sepiidae. Weights use biomass.',
 'Teuthida':'Unknown squid depth/species composition spans epi-, meso- and bathypelagic mollusc-bearing pools. Octopod-only Bathy forage is excluded; compatible pools use biomass weights.'}
groups=[]
for row in summary['very_low_decisions']:
    reason=brief[row['taxa'][0]]
    if groups and reason==groups[-1][1]:groups[-1][0].extend(row['taxa'])
    else:groups.append([list(row['taxa']),reason])
tablerows(tables[4],[('; '.join(taxa),reason) for taxa,reason in groups])
assert sorted(t for taxa,_ in groups for t in taxa)==sorted(summary['confidence_summary'][3]['taxon_labels'])
setp(paras[19],'Target region R and selected model study area S. The fixed published bounds are reconstructed below; approximate overlap uses a consistent land mask and a published-area denominator sensitivity.')
setp(paras[21],'Papua New Guinea EEZ and reported study bounds; repository Sea Around Us boundary and Natural Earth land. ')
link(paras[21],'Boundary evidence','evidence/source_review/source_geography_review_20261114.json')
setp(paras[23],'Allain et al. (2007), Figure 1, PDF page 3: warm-pool/cold-tongue context. The fixed model domain is stated on PDF page 7; this contextual figure is not a precise model polygon. ')
link(paras[23],'Original article','../../../sources/download-0adcf55e.pdf#page=3')
body.remove(paras[24])
def picture(path,template_cell,width_inches=6.65):
    # Use source drawing structure; set exact aspect and a new embedded relationship.
    srcdoc=xml(sources[SOURCE]['word/document.xml'])
    p=srcdoc.xpath('.//w:p[.//w:drawing]',namespaces=NS)[0]
    p=import_node(p,SOURCE)
    ext=path.suffix.lstrip('.'); name='media/'+path.name
    parts['word/'+name]=path.read_bytes();rid=add_rel(name,'image',False)
    for blip in p.xpath('.//a:blip',namespaces=NS):blip.set('{'+R+'}embed',rid)
    with Image.open(path) as im: ww,hh=im.size
    cx=int(width_inches*914400);cy=int(cx*hh/ww)
    for ex in p.xpath('.//wp:extent|.//a:xfrm/a:ext',namespaces=NS):ex.set('cx',str(cx));ex.set('cy',str(cy))
    for el in list(template_cell):
        if el.tag!=q('tcPr'):template_cell.remove(el)
    template_cell.append(p)
picture(OUT/'evidence/geography/region_study_domain.png',tables[5].findall(q('tr'))[1].find(q('tc')))
picture(OUT/'evidence/geography/article_figure1_crop.png',tables[6].findall(q('tr'))[1].find(q('tc')))
setcell(tables[6].findall(q('tr'))[0].find(q('tc')),'Article Figure 1 regional context')
for i,pr in enumerate(doc.xpath('.//wp:docPr',namespaces=NS),1):pr.set('id',str(i))
for h in doc.xpath('.//w:hyperlink',namespaces=NS):
    for r in h.findall(q('r')):
        pr=r.find(q('rPr'))
        if pr is None:pr=E.SubElement(r,q('rPr'))
        for tag,val in [('color','0563C1'),('u','single')]:
            e=pr.find(q(tag))
            if e is None:e=E.SubElement(pr,q(tag))
            e.set(q('val'),val)
# Drop unused placeholder/source relationships, preserve other template package parts.
used={v for el in doc.iter() for k,v in el.attrib.items() if k.startswith('{'+R+'}')}
for r in list(rels):
    if r.get('Type').endswith(('/hyperlink','/image')) and r.get('Id') not in used:rels.remove(r)
links=[]
for r in rels:
    target=r.get('Target')
    if r.get('TargetMode')=='External' and not urlsplit(target).scheme and not target.startswith('#'):
        path=(OUT/unquote(target.split('#',1)[0])).resolve()
        links.append({'target':target,'exists':path.exists()})
        assert path.exists(),target
parts['word/document.xml']=ser(doc);parts['word/_rels/document.xml.rels']=ser(rels);parts['[Content_Types].xml']=ser(types)
with ZipFile(OUT/'validation.docx','w',ZIP_DEFLATED) as z:
    for n,b in parts.items():z.writestr(n,b)
from tools.project_core.validation.validation_percentage_format import verify_report
verify_report(OUT/'validation.docx')
from tools.project_core.validation.researcher_review import read_report
name,date,parsed=read_report(ROOT,OUT/'validation.docx',MODEL)
evidence={'template_sha256':sha(TEMPLATE),'source_before_sha256':sha(SOURCE),'donor_report':local_link(DONOR),'donor_sha256':sha(DONOR),'output_sha256':sha(OUT/'validation.docx'),'copied_fields':['SPPR calculation','Review and reproducibility'],'user_authorization':'User explicitly requested copying both named fields from another region using this already validated model and automatic validation for EEZ_598. Exact donor name, signed date and decision were retained; no new signature was invented.','reviewer':name,'review_date':date,'status':parsed.get('status','Validated by researcher'),'local_links':links,'preserved_template_parts':[n for n,b in package(TEMPLATE).items() if parts.get(n)==b],'taxa':102,'very_low_taxa_exactly_once':True,'unresolved':5,'report_reference':'2019 landings','floor':{'use_ee_floor':True,'ee_floor':0.1,'diagnostics':'Reused from identical EEZ_941 source; verification certificate linked in evidence.'}}
(OUT/'evidence/source_review/report_production_20261114.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
(RUN/'qa/report_checks.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(OUT/'validation.docx'),'reviewer':name,'date':date,'status':parsed.get('status','Validated by researcher'),'links':len(links),'tables':len(tables)},ensure_ascii=False))
