"""Insert only the requested table; retain every pre-existing DOCX byte part."""
import copy, hashlib, json, os, re, tempfile, zipfile
from pathlib import Path
from lxml import etree as E
from openpyxl import load_workbook

QA = Path(__file__).resolve().parent
ROOT = next(p for p in QA.parents if (p/'Project.xlsx').exists())
REPORT = next((ROOT/'regions/LME_032').glob('Model_validation*.docx'))
BASELINE = QA/('baseline_'+REPORT.name)
REFERENCE = next((ROOT/'regions/LME_036').glob('Model_validation*.docx'))
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
text = lambda e: ''.join(t.text or '' for t in e.iter(W+'t'))
sha = lambda b: hashlib.sha256(b).hexdigest()

groups = [
(['Marine fishes not identified','Perciformes','Marine pelagic fishes not identified','Marine groundfishes not identified'],
 'Unknown fish composition is approximated by compatible harvested bony-fish guilds, water-column pools or benthic pools. A demersal tag does not establish unidentified-fish composition; the legacy Perciformes label is broader than four demersal pools. Whole source-group catch proportions are assumed transferable across regions, years and catch bases.'),
(['Anguilliformes'],
 'Adult eels and morays are approximated by demersal carnivore pools. Eel larvae in Micro Nekton do not represent adult fishery catch; size, diet and depth mixture remain uncertain. Published model catch proportions are an assumed allocation.'),
(['Chondrichthyes'],
 'Sharks and rays fit two source pools, but common metadata also includes chimaeras, absent from the model. The two elasmobranch pools provide an approximation rather than complete containment; model catch proportions supply an assumed split.'),
(['Scombroidei'],
 'The provider label includes tunas, bonitos and billfishes. Tunas plus Large Pelagics approximate those taxa; billfishes are ecological extensions, not source members. Published model catch proportions supply an assumed split.'),
(['Gobiidae'],
 'Unknown goby species and feeding composition are approximated by small benthic carnivory, omnivory and water-column feeding in three source pools. Reef and specialised feeding remain unmatched; model catch proportions supply an assumed split.'),
(['Siganus canaliculatus','Siganidae','Siganus','Crenidens crenidens','Scaridae','Bolbometopon muricatum','Scarus persicus','Acanthurus dussumieri','Siganus sutor','Scarus ghobban','Acanthuridae'],
 'Benthic Omnivores is the closest available bottom-feeding approximation. The model lacks a herbivorous reef-fish pool; specialised algal, seagrass or coral feeding differs materially from its sole and squilla diet.'),
(['Pomacanthus maculosus','Platax orbicularis','Ephippidae','Platax','Chaetodontidae','Pomacentridae','Pomacanthidae'],
 'Benthic Omnivores is the closest available reef or bottom-feeding approximation. Specialised coral and sponge feeding, or mixed reef plankton and algal feeding, is absent from the model; direct source membership is not established.'),
(['Bramidae','Berycidae','Beryx','Brama brama','Gadiformes','Gempylidae','Lampris guttatus','Lepidocybium flavobrunneum','Ruvettus pretiosus'],
 'Large Benthopelagics, represented by ribbonfish and carangids, is the closest available water-column predator approximation. Deep or oceanic feeding and habitat, or coarse gadiform composition, are poorly represented by this shelf model exploited to 200 m.'),
(['Mollusca'],
 'Common metadata includes clams, seasnails, squids and octopuses. Cephalopods and Heterotrophic Benthos form a coarse approximation under an adult-fishery-catch assumption; larval zooplankton is excluded. Model catch proportions supply an assumed split.'),
(['Miscellaneous aquatic invertebrates'],
 'Unidentified demersal invertebrates may span molluscs, crustaceans, epifauna and infauna. Compatible adult pools provide an explicit coarse approximation; fish-bearing pools and pelagic larvae are excluded. Model catch proportions supply an assumed split.'),
(['Malacostraca'],
 'Common metadata includes lobsters, crabs, shrimps and krill. Harvested decapods, squilla, epifaunal crustaceans and large zooplankton approximate this mixture; micro-zooplankton eggs and larvae are excluded under an adult-catch assumption. Model catch proportions supply an assumed split.'),
(['Labridae'],
 'Wrasses vary in size and include benthic invertebrate feeders and planktivores. Medium and small benthic feeders plus the small water-column pool provide an approximation; specialised cleaning and reef habitats remain unmatched. Model catch proportions supply an assumed split.'),
(['Scomber'],
 'The dedicated Rastrelliger kanagurta pool is the closest available mackerel analogue. Scomber is not listed among source members and can differ materially in feeding and habitat.')]

book = load_workbook(ROOT/'regions/LME_032/LME032_taxon_mapping_appendix.xlsx',read_only=True,data_only=True)
very_low = {r[0]:r[6] for r in list(book['Taxon appendix'].values)[5:] if r[5]=='Very low'}
book.close()
names = [n for group,_ in groups for n in group]
assert len(names)==len(set(names))==40 and set(names)==set(very_low)
with zipfile.ZipFile(REFERENCE) as z:
    body = E.fromstring(z.read('word/document.xml')).find(W+'body')
    children = list(body)
    index = next(i for i,n in enumerate(children) if n.tag==W+'p' and text(n)=='Very low decisions')
    heading = copy.deepcopy(children[index]); table = copy.deepcopy(children[index+1])
header, row_template = table.findall(W+'tr')[:2]
for row in table.findall(W+'tr')[1:]: table.remove(row)
for taxa,reason in groups:
    row = copy.deepcopy(row_template)
    for cell,value in zip(row.findall(W+'tc'), ['; '.join(taxa),reason]):
        p = cell.find(W+'p'); ppr = copy.deepcopy(p.find(W+'pPr')); rpr = copy.deepcopy(p.find(W+'r/'+W+'rPr'))
        for child in list(cell):
            if child.tag != W+'tcPr': cell.remove(child)
        p = E.SubElement(cell,W+'p'); p.append(ppr)
        r = E.SubElement(p,W+'r'); r.append(rpr); E.SubElement(r,W+'t').text=value
    table.append(row)
for node in [heading,table]:
    for element in node.iter():
        for attr in list(element.attrib):
            if attr.rsplit('}',1)[-1].startswith('rsid') or attr.rsplit('}',1)[-1] in ['paraId','textId']:
                del element.attrib[attr]
fragment = E.tostring(heading)+E.tostring(table)
with zipfile.ZipFile(BASELINE) as z:
    parts = [(info,z.read(info.filename)) for info in z.infolist()]
original = dict((i.filename,b) for i,b in parts)['word/document.xml']
assert not any(n.tag==W+'p' and text(n)=='Very low decisions' for n in E.fromstring(original).find(W+'body'))
pos = original.index(b'<w:t>Geographic evidence</w:t>')
insertion = list(re.finditer(rb'<w:p(?:\s|>)',original[:pos]))[-1].start()
patched = original[:insertion]+fragment+original[insertion:]
E.fromstring(patched)
assert patched[:insertion]+patched[insertion+len(fragment):] == original
assert REPORT.read_bytes()==BASELINE.read_bytes(), 'Report changed since source snapshot'
fd,tmp = tempfile.mkstemp(suffix='.docx',dir=REPORT.parent); os.close(fd)
try:
    with zipfile.ZipFile(tmp,'w') as z:
        for info,data in parts: z.writestr(info,patched if info.filename=='word/document.xml' else data)
    os.replace(tmp,REPORT)
finally:
    if os.path.exists(tmp): os.unlink(tmp)
with zipfile.ZipFile(REPORT) as z:
    changed = [info.filename for info,data in parts if z.read(info.filename)!=data]
assert changed == ['word/document.xml']
proof = {'baseline_sha256':sha(BASELINE.read_bytes()),'report_sha256':sha(REPORT.read_bytes()),
 'changed_zip_parts':changed,'original_document_xml_restored_by_removing_only_insertion':True,
 'all_original_paragraphs_tables_runs_properties_preserved':True,'very_low_taxa_count':40,
 'very_low_decision_rows':len(groups),'inserted_xml_offset':insertion,'inserted_xml_bytes':len(fragment),
 'rows':[{'taxa':g,'reason':r,'appendix_reasons':{n:very_low[n] for n in g}} for g,r in groups]}
(QA/'word_preservation.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
print('Inserted 13 source-specific rows covering all 40 Very low taxa; only document.xml changed.')
