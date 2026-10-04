from pathlib import Path
from lxml import etree
from copy import deepcopy
import json,re,sys,hashlib
from ooxml_preserve import package,save_package
sys.stdout.reconfigure(encoding='utf-8')
OUT=Path(__file__).parent;REG=OUT.parents[2]
def load(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def save(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
updates=load('appendix_updates.json')
source_cells={
'B10':'65 cm; coastal/near-coastal pelagic; 0–500 m. Fits the explicit small/medium pelagic definition at High confidence. The genus also contains the two named Other demersal fish species; genus-level allocation remains assumed.',
'A13':'FAO_Dory: FAO Cephalopods of the World Vol2, Doryteuthis gahi account printed p59 (Figure88)',
'B13':'Medium neritic shelf squid; maximum 400 mm mantle length. Full primary catalogue account reviewed. Mantle length is not fish total length. Retained Small pelagic fish is a Very low active-nekton analogue, not explicit fish membership.',
'B15':'Regional 2019/2020 assessment and age/size evidence reviewed. Counts and spawning-survey population percentages do not establish complete caught-mass proportions at age three. Retain the historical source catch proxy at Medium allocation confidence.',
'B16':'Historical complete-candidate allocation audit. Missing native catches invalidate a whole-set catch proxy; loader defaults are not observed zeros. Hoki retains 0.006/0.062 and 0.056/0.062. Current adopted candidate sets and proportions are in the reassessment ledger below.',
'B17':'Historical complete 218-label audit, including all 16 source/recipient candidates. Current retained and changed decisions, component ratings and every included/excluded candidate are in the reassessment ledger below; overall confidence uses the weaker component.',
'B20':'Paper/canonical/runtime layers, temporal/geographic transfer limits and weak-analogue exposure remain. This update stops for researcher review; shared LME_013 integration and approval registration are deferred.'}
updates['Sources'].update(source_cells)
for address in source_cells:updates['Sources']['D'+re.search(r'\d+$',address).group()]='2026-10-03'
# Keep evidence records literal; improve only the human-facing concise reasons.
def readable(s):
    for number,name in [('13','Southern hake'),('12','Skates'),('10','Southern blue whiting'),('9','Hoki adult'),('8','Hoki juvenile'),('7','Other demersal fish'),('6','Small pelagic fish'),('5','Benthos'),('4','Macrozooplankton')]:
        s=re.sub(r'(?i)\b(?:source\s*group|source|group)\s*'+number+r'\b',name,s)
        s=re.sub(r'(?i)\b(gives|supports|fits|select|change\s*to|weak)'+number+r'\b',lambda m:m.group(1)+' '+name,s)
    s=re.sub(r'(\d)(cm|mm|mTL|cmTL|cmFL)\b',r'\1 \2',s)
    s=s.replace('forage-fish definition','small/medium pelagic-fish definition')
    return s
ledger=load('decision_ledger.json');review=load('reconciled_decisions.json')
for r in ledger:
    r['appendix_reason']=readable(r.get('appendix_reason',r['reason']))
    review[r['taxon']]['appendix_reason']=r['appendix_reason']
for address,reason in list(updates['Taxon mapping'].items()):
    if address.startswith('G'):updates['Taxon mapping'][address]=readable(reason)
save('decision_ledger.json',ledger);save('reconciled_decisions.json',review);save('appendix_updates.json',updates)
doc=REG/'Model_validation_13_1_Chilean_Patagonia_(1980).docx';before=hashlib.sha256(doc.read_bytes()).hexdigest()
infos,parts=package(doc);W='http://schemas.openxmlformats.org/wordprocessingml/2006/main';NS={'w':W};q=lambda n:'{'+W+'}'+n
xml=etree.fromstring(parts['word/document.xml']);body=xml.find(q('body'));tables=body.findall(q('tbl'));text=lambda n:''.join(n.xpath('.//w:t/text()',namespaces=NS))
vl_reasons={
'Dosidicus gigas':'Large oceanic predatory squid uses Small pelagic fish as a weak active-nekton analogue. Squid taxonomy, body size and feeding differ from the source’s small/medium pelagic fish pool; the selected model has no cephalopod group.',
'Lampris guttatus; Lepidocybium flavobrunneum':'Unrepresented deep-water fish use the pelagic fish pool as a weak analogue. Lampris is pelagic; Lepidocybium also uses slopes and near-bottom waters. Size, depth and feeding differ from the source pool.',
'Carangidae':'Unknown family composition spans pelagic and bottom/reef-associated fish. The Seriolella-defined demersal pool is an analogue. Complete model biomass proportions supply an assumed regional composition proxy.',
'Coelorinchus chilensis':'The focal model has no grenadier group. The Hoki union offers a weak morphology/habitat analogue with different biology. Historical Hoki catch proportions divide surrogate coefficients; they do not measure grenadier stage composition.',
'Gadiformes':'Unknown cod-like species composition and unrepresented grenadiers require a broad-category approximation. Complete source catches for Hoki, blue whiting and Southern hake supply proxy weights; they do not establish regional composition.',
'Galaxias maculatus':'This diadromous fish has marine planktonic larvae/juveniles and freshwater adults. Small pelagic fish supplies a weak marine-life-phase analogue. The caught-stage mixture is unknown and the provider’s large-reef tag conflicts with primary evidence.',
'Hoplostethus atlanticus':'Primary evidence describes deep seamount/bottom-associated aggregations, often beyond 800 m. The Seriolella-defined Other demersal fish group is a weak depth/habitat analogue. A bathypelagic provider tag does not establish small-pelagic membership.',
'Larimus pacificus':'Regional primary evidence places Pacific drum over coastal bottoms at 40–60 m and in demersal/coastal catches. Retain a weak Seriolella-pool analogue; taxonomy differs. These observations override the provider’s simplified small-pelagic tag.',
'Macrouridae':'Unknown grenadier composition has no named focal pool. Hoki morphology/habitat provides a weak broad-category analogue. Transferred Hoki catch weights are not observed grenadier ages.',
'Mobula birostris':'Pelagic zooplankton feeding provides a closer ecological connection to the pelagic fish pool than to benthic predatory Skates. Giant body size, cartilaginous taxonomy and life history remain outside the source’s small/medium fish scope.',
'Rajiformes':'Historical provider/FAO reporting includes skates, rays, stingrays and mantas. It does not establish a modern skate-only composition. The specifically named Skates stock remains a weak broad-category analogue.',
'Salilota australis':'Primary regional evidence describes a southern benthopelagic gadiform in demersal fisheries. Southern hake supplies a weak unsplit predator analogue. The source does not name Salilota, and its ecology differs from the source Hoki/blue-whiting alternatives.',
'Selene peruviana':'Primary regional evidence describes sandy-bottom demersal habitat at 1–50 m and sizes up to 85 cm. The Seriolella-defined pool remains a weak analogue. The provider’s small-pelagic tag cannot define exclusive ecological membership.',
'Thyrsites atun':'Chile diet observations and the primary catalogue support shelf/midwater schooling and pelagic prey. Small pelagic fish is retained as a weak food-web analogue; observed large size and bottom association remain mismatches.'}
changes=[]
for row in tables[4].findall(q('tr'))[1:]:
    cells=row.findall(q('tc'));label=text(cells[0])
    if label in vl_reasons:
        cell=cells[1];old=text(cell);p=cell.find(q('p'));rp=p.find('w:r/w:rPr',NS)
        for n in list(p):
            if n.tag!=q('pPr'):p.remove(n)
        r=etree.SubElement(p,q('r'))
        if rp is not None:r.append(deepcopy(rp))
        etree.SubElement(r,q('t')).text=vl_reasons[label]
        for extra in cell.findall(q('p'))[1:]:cell.remove(extra)
        changes.append({'labels':label,'old_reason':old,'new_reason':vl_reasons[label]})
for p in body.findall(q('p')):
    for h in p.findall(q('hyperlink')):
        previous=h.getprevious()
        if previous is not None and previous.tag==q('r'):
            for t in previous.findall(q('t')):
                if t.text and not t.text.strip():t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
parts['word/document.xml']=etree.tostring(xml,encoding='utf-8',xml_declaration=True,standalone=True)
assert hashlib.sha256(doc.read_bytes()).hexdigest()==before,'concurrent Word edit'
save_package(doc,infos,parts)
save('presentation_corrections.json',{'input_document_sha256':before,'source_cells':source_cells,'very_low_reason_clarifications':changes,'scope':'presentation/evidence descriptions only; adopted numerical mappings, ratings and scientific inputs unchanged'})
print('Human-facing explanations, historical source descriptions and link spacing corrected.')
