from pathlib import Path
import json,re
Q=Path(__file__).parent;ROOT=Q.parents[4];MID='38_38003_Java_Sea_normalized_BA_completed_(mid1970s)';E=ROOT/'regions/LME_038/validation_reports'/MID
p=E/'appendix_sources.json';rows=json.loads(p.read_text(encoding='utf-8'))
facts={
'fao1974_pentapodidae':('FAO1974 species sheets, historical Pentapodidae','PDF2–4: Pentapodus, Gnathodentex, Monotaxis and Gymnocranius are included; Scolopsis is absent. Supports historical Pentapodus source8bridge, not a whole-modern-family synonym or a Scolopsis SAF assignment.'),
'fao1974_nemipteridae':('FAO1974 species sheets, historical Nemipteridae','PDF2–3: Nemipterus, Parascolopsis and Scolopsis are separate from Pentapodidae. Supports source Small demersals connection; representative regional family contents remain incomplete.'),
'fao1990_nemipteridae_intro':('FAO1990 catalogue, Nemipteridae introduction','PDF4–6: modern Nemipteridae includes Nemipterus/Scolopsis and Pentapodus; benthic/reef habitats vary. Supports coarse family21/8boundary and partial Scolopsis fit without proving living-structure dependence or actual catch proportions.'),
'fao1993_cephalopholis':('FAO1993 groupers catalogue, Cephalopholis overview','Genus/habitat context for the historical Serranidae source family. Genus ecology is representative; the species-specific C.boenak account carries the relevant size/habitat evidence.'),
'fao1993_cephalopholis_species':('FAO1993 groupers catalogue, Cephalopholis boenak','PDF6/printed38: maximum TL26cm,4–30m silty dead reefs in protected waters, trawled to64m. Supports source<40cm Small demersals. Dead-reef occurrence alone does not prove source SAF living-structure dependence.'),
'fao1999_haemulidae':('FAO Western Central Pacific guide, Pomadasys argenteus','PDF7/printed2983: maximum about60cm, common40cm; coastal bays and estuaries. Positively supports source40–60cm Medium demersals; source average-or-maximum convention and unobserved landed size leave a Small alternative uncertain.'),
'fao_wcp_megalops':('FAO Western Central Pacific guide, Megalops cyprinoides','Printed1622: maximum TL55cm, common30cm; coastal lagoons/estuaries and open-water swimming. Supports Misc. pelagics analogy and contradicts automatic placement from provider>=90cm tag. Lineage and estuarine migration differ.'),
'fao_pakistan_flatheads':('FAO Pakistan guide, Platycephalidae','Printed30: bottom-associated flathead species have maxima25,50and100cm. Supports family size diversity and explicit21/22/23/26demersal analogues; does not observe Java Sea size or catch composition.'),
'fao_maldives_plotosus':('FAO Maldives account, Plotosus lineatus','Species maximum32cm supports a small constituent; reef/coastal occurrence. A species account cannot establish genus/family-wide small-only membership or caught-stage proportions.'),
'fao_wcp_plotosidae':('FAO Western Central Pacific guide, Plotosidae','Printed1883: P.lineatus maximum about30cm; P.canius common<=80cm. Historical maximum150cm is questioned and is not measured Java Sea composition. Supports small-through-large catfish analogues, with Very low membership.'),
'fao1993_scombroidei_intro':('FAO1993 catalogue, historical scombroid scope','Historical scombroid fisheries concept includes tunas, bonitos, mackerels, billfish and barracudas. Supports provider-category interpretation and actual source scombrid/barracuda connections; modern order identity and local species composition differ.')}
def readable(v):
 v=re.sub(r'(?<=[A-Za-z])(?=\d)',' ',v);v=re.sub(r'(?<=\d)(?=[A-Za-z])',' ',v);return v
for r in rows:
 if r['id']in facts:r['title'],r['supports']=facts[r['id']];r['title']=readable(r['title']);r['supports']=readable(r['supports'])
p.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
ledger=json.loads((E/'independent_review/primary_source_ledger.json').read_text(encoding='utf-8'))
for r in ledger['sources']:
 for key in ['path','extracted_text_path']:
  if r.get(key)and 'independent_source_review/primary_sources/'in r[key]:r[key]='regions/LME_038/validation_reports/'+MID+'/supporting_sources/'+Path(r[key]).name
ledger['portability_note']='Original reviewer ledger retained unmodified alongside this permanent-artifact crosswalk. Recovered native PDF/text bytes remain identical.'
(E/'primary_source_ledger_portable.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2),encoding='utf-8')
print('Descriptive native FAO sources and permanent crosswalk enriched')
