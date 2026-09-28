from extract_candidates import *
pdf=REG/'papers/LME022-Mackinson-2007/tech142-ead77c0e.pdf'
tax=json.loads((OUT/'mackinson_taxonomy.json').read_text(encoding='utf-8'))
mapping={'Infaunal macrobenthos':57,'Small infauna':60,'Epifaunal macrobenthos':56,'Small mobile epifauna':59,'Shrimp':58,'Large crabs':54,'Sessile epifauna':61,'Meiofauna':62}
members=[]
for page in [118,119,120]:
    lines=get_words(str(pdf),page,merge_gap=.4)
    hs=next(c for l in lines for c in l.cells if c.text=='Species')
    hc=next(c for l in lines for c in l.cells if c.text.startswith('Common/Phylum'))
    last=None
    for line in lines:
        if line.y<=hs.yc:continue
        gg=norm(' '.join(c.text for c in line.cells if 50<c.x0<hs.x0-2))
        ss=norm(' '.join(c.text for c in line.cells if hs.x0-2<=c.x0<hc.x0-2))
        if gg in mapping:
            last={'group_seq':mapping[gg],'printed_group':gg,'printed_taxon':ss,'pdf_page':page,'table':'11.8','scope':'main-species biomass contribution, not exhaustive inventory'};members.append(last)
        elif last and not gg and ss:
            last['printed_taxon']+=' '+ss
for n in mapping.values():
    mm=[r for r in members if r['group_seq']==n]
    tax[str(n)]=tax[str(n)].replace('Table11.7','Table11.8')+' Main contributing taxa in Table11.8 printed pp116–118: '+'; '.join(r['printed_taxon'] for r in mm)+'. These are reported principal biomass contributors, not an exhaustive inventory.'
tax['57']='Bivalves and gastropods mostly >2mm, filter feeders and grazers [Table11.6 printed p115; PDF117]. '+tax['57']
tax['60']='Mostly polychaetes and small sediment-dwelling crustaceans; filter feeders and predators [Table11.6 printed p115]. '+tax['60']
tax['56']='Free-living surface macrobenthos; mostly echinoderms, small crabs, gastropods and scallops [Table11.6 p115]. '+tax['56']
tax['59']='Crustaceans, molluscs and polychaetes at benthic interface plus mysids, gammarids and amphipods swarming off bottom [Table11.6 p115]. '+tax['59']
tax['61']='Suspension/filter feeders including anemones, sponges, corals, tunicates, gorgonians, hydroids, anthozoans, pelecypods, barnacles, bryozoans, attached bivalves, crinoids, ascidians and oysters [Table11.6 p115]. '+tax['61']
dump(OUT/'mackinson_taxonomy.json',tax);dump(OUT/'mackinson_table11_8_members.json',members)
csvout(OUT/'mackinson_table11_8_members.csv',list(members[0]),[list(r.values()) for r in members])
# Preserve detailed 12-fleet input ledger and its disagreements with the 8-fleet summary.
ledger={}
for page in range(163,171):
    ls=get_words(str(pdf),page,merge_gap=.4)
    ledger[str(page)]=[[{'text':c.text,'x0':c.x0,'x1':c.x1,'y0':c.y0,'y1':c.y1} for c in l.cells] for l in ls]
dump(OUT/'mackinson_tables14_7_14_8_coordinates.json',ledger)
print('Captured principal benthic taxa',len(members),'by group', {n:sum(r['group_seq']==n for r in members) for n in mapping.values()})
# Source bundle hashes and current unchanged regional workbook hash.
sources=[]
for folder in ['NS-2025','LME022-Mackinson-2007']:
    for p in (REG/'papers'/folder).iterdir():
        if p.suffix in ['.pdf','.xlsx','.docx']:
            sources.append({'path':str(p.relative_to(ROOT)),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'role':'published source retained unchanged'})
dump(OUT/'source_hashes.json',sources)
