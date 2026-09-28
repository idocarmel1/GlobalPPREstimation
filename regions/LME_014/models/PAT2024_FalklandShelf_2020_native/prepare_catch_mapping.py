"""Source-reviewed mapping for the selected Falkland shelf native model only."""
from pathlib import Path
import sys,json,csv,math,shutil
MODEL=Path(__file__).resolve().parent;REGION=MODEL.parents[1];ROOT=REGION.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
from regional import set_setting
MID=MODEL.name;E=MODEL/'selection_20260928'

def save_csv(path,header,records_):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f);writer.writerow(header);writer.writerows(records_)

def main():
    path=REGION/'LME_014.xlsx';book=read_book(path)
    assert overview(book)['results_model_id']==MID
    catch=records(book,'Catch','Catch');taxa={r['taxon']:r for r in catch if r['catch_basis']=='catch'}
    totals={t:math.fsum(r[y] or 0 for y in YEARS) for t,r in taxa.items()}
    dictionary=list(csv.DictReader((MODEL/'extracted_tables/taxonomy.csv').open(encoding='utf-8-sig')))
    # Table 2 is explicitly a definition of model groups, not merely a diet-sample list.
    direct={}
    members=[]
    for r in dictionary:
        group=r['group_name']
        for member in r['taxon_descr'].split(';'):
            member=member.strip()
            if member in taxa and member!='Doryteuthis gahi':direct[member]=group
            members.append([member,member,group,'Article Table 2 pp7–8; definition of model groups'])
    # These printed rows include lifecycle qualifiers and are handled explicitly.
    direct.pop('Dissostichus eleginoides',None)
    # Validate bivalve containment using the retained primary taxonomy records.
    taxonomy=json.loads((E/'mapping_taxonomy_evidence.json').read_text())
    bivalves={}
    for r in taxonomy:
        exact=[x for x in r['records'] if x['scientificname']==r['taxon'] and x['class']=='Bivalvia']
        assert len(exact)==1
        bivalves[r['taxon']]=exact[0]['url']
    landings=list(csv.DictReader((MODEL/'extracted_tables/Landings.csv').open(encoding='utf-8-sig')))
    model_landings={r['Group name']:float(r['Total']) for r in landings}
    cohort_groups=['D. gahi ASC','D. gahi SSC']
    cohort_total=math.fsum(model_landings[g] for g in cohort_groups)
    cohort_weights={g:model_landings[g]/cohort_total for g in cohort_groups}
    hake_species={'Merluccius hubbsi':'Hake Common','Merluccius australis':'Hake Austral'}
    hake_total=math.fsum(totals[s] for s in hake_species)
    hake_weights={g:totals[s]/hake_total for s,g in hake_species.items()}
    rows_=[];notes=[]
    important={
      'Dissostichus eleginoides':'The source explicitly excludes adults and longline fisheries (p6); SAU class is Large bathydemersals. Juvenile-only group cannot represent unsplit whole-LME toothfish catches.',
      'Pleoticus muelleri':'Table 2 defines Benthic Crustaceans as Munida gregaria, with no penaeoid shrimp compartment. The shrimp catch is not assigned to lobster krill.',
      'Micropogonias furnieri':'No croaker species or sciaenid guild is defined in Table 2; the Falkland fish groups do not document this northern-LME species.',
      'Engraulis anchoita':'Pelagic Fish is explicitly defined by six other species; no anchovy compartment or source-supported assignment exists.',
      'Rajiformes':'Unsplit regional skates/rays include taxa outside the three Table 2 members; the paper explicitly excludes some deep-water skates (p6). No supported shelf/species fraction is available.',
      'Rajidae':'The regional family record does not distinguish the three modeled shelf species from other and deep-water species; no supported component fraction is available.',
      'Teuthida':'The model separates Illex, both D. gahi cohorts and three other squid species. The whole-LME squid aggregate may include additional species; no composition resolving its modeled fraction was supplied.',
      'Loliginidae':'Table 2 supports only D. gahi cohorts from this family; the family catch has no species composition establishing that it consists of D. gahi.',
      'Marine fishes not identified':'SAU calls this Medium demersals, but many identified regional demersals have no source-supported group. Catch weighting the modeled subset would conceal the unrepresented fraction.',
      'Myctophidae':'The Table 2 group names Gymnoscopelus nicholsi; the family catch does not establish this species or a supported guild extension.',
      'Macrourus carinatus':'Table 2 Grenadier is Coelorinchus fasciatus; some deep-water grenadiers are explicitly excluded (p6). No source-supported assignment to that different species.',
    }
    for t,r in taxa.items():
        assignments=[];confidence='unresolved';evidence='none'
        if t in direct:
            assignments=[(direct[t],1.)];confidence='high';evidence='explicit_member'
            explanation=f'Article Table 2 pp7–8 explicitly places {t} in {direct[t]}; exact native group identifier retained.'
        elif t in bivalves:
            assignments=[('Small Zoobenthos',1.)];confidence='high';evidence='taxonomic_containment'
            explanation=f'Table 2 p8 defines Small Zoobenthos to include scallops and bivalves; {t} is Bivalvia in WoRMS ({bivalves[t]}), retained in mapping_taxonomy_evidence.json. This verifies membership, not whole-LME ecological equivalence.'
        elif t=='Doryteuthis gahi':
            assignments=list(cohort_weights.items());confidence='medium';evidence='composite_split'
            explanation='Both source-defined D. gahi cohorts (Table 2 p7); fixed weights use each cohort native 2020 landings / combined cohort landings, not biomass or equal shares. Transfer of the 2020 cohort mixture to historical catch is an explicit approximation.'
        elif t=='Merluccius':
            assignments=list(hake_weights.items());confidence='medium';evidence='composite_split'
            explanation='Genus-level hakes split between the two source-defined hake groups using identified M. hubbsi and M. australis catch tonnes over 1950–2019 in this regional workbook. This is an inferred constant composition, not a source-stated annual split.'
        else:
            explanation=important.get(t,f'Table 2 pp7–8 does not establish {t} as a member of the Falkland shelf model. No source-supported whole-LME taxonomic/guild assignment or component fraction was found; catch retained as unresolved, not zero PPR.')
        if assignments:
            assert math.isclose(math.fsum(w for g,w in assignments),1.,abs_tol=1e-12)
            for group,weight in assignments:rows_.append([MID,t,group,weight,confidence,evidence,explanation])
        else:rows_.append([MID,t,None,None,confidence,evidence,explanation])
        notes.append([t,r['common_name'],r['functional_group'],r['commercial_group'],' | '.join(g for g,w in assignments) or 'Unresolved',' | '.join(format(w,'.17g') for g,w in assignments),confidence,evidence,explanation,totals[t],r[2019]])
    known={r['group'] for r in records(book,'Selected model groups','Group SPPR')}
    assert all(r[2] is None or r[2] in known for r in rows_)
    assert {r[1] for r in rows_}==set(taxa)
    assert not any(r[2] in ['Phytoplankton','Kelp','Detritus','Discards','diet_import'] for r in rows_)
    for r in rows_:
        if r[1] in direct:assert r[2]==direct[r[1]]
    before=E/f'LME_014_before_mapping_{sha(path)[:12]}.xlsx'
    if not before.exists():shutil.copy2(path,before)
    header=['model_id','taxon','group','weight','confidence','evidence','explanation']
    book['PPR']['Matching']=(header,rows_)
    set_setting(book,'mapping_note','Source-defined groups; no unsupported northern/deep-water taxa forced into Falkland groups. See selected model selection_report.md for catch coverage and cohort/hake weights.')
    write_book(path,book)
    save_csv(E/'mapping_resolved.csv',header,rows_)
    save_csv(E/'mapping_review.csv',['taxon','common_name','functional_group','commercial_group','group','weights','confidence','evidence','explanation','catch_tonnes_1950_2019','catch_tonnes_2019'],sorted(notes,key=lambda r:r[-2],reverse=True))
    save_csv(E/'members.csv',['printed_name','accepted_name','group_name','source_page'],members)
    save_csv(E/'groups.csv',list(dictionary[0]),[list(r.values()) for r in dictionary])
    resolved={r[1] for r in rows_ if r[2]}
    coverage=[]
    for basis in ['landings','catch','discards']:
        subset=[r for r in catch if r['catch_basis']==basis]
        for year in ['1950–2019',2019]:
            v=lambda r: math.fsum(r[y] or 0 for y in YEARS) if isinstance(year,str) else r[year] or 0
            total=math.fsum(v(r) for r in subset);covered=math.fsum(v(r) for r in subset if r['taxon'] in resolved)
            coverage.append([basis,year,total,covered,100*covered/total if total else None,len(resolved),len(taxa)])
    save_csv(E/'mapping_coverage.csv',['catch_basis','years','total_tonnes','mapped_tonnes','mapped_percent','mapped_taxa','total_taxa'],coverage)
    save_csv(E/'split_weights.csv',['taxon','group','weight','basis'],[['Doryteuthis gahi',g,w,'native 2020 cohort landings'] for g,w in cohort_weights.items()]+[['Merluccius',g,w,'regional identified hake catch 1950–2019'] for g,w in hake_weights.items()])
    print(json.dumps({'resolved_taxa':len(resolved),'total_taxa':len(taxa),'coverage':coverage,'cohort_weights':cohort_weights,'hake_weights':hake_weights},indent=2))

if __name__=='__main__':main()
