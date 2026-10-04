"""Create source-supported taxonomy and catch matching review without publication."""
from pathlib import Path
import sys,json,csv,hashlib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];REGION=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book,records,overview
def write_csv(name,fields,rows):
    with (HERE/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def main():
    b=read_book(REGION/'HS_077.xlsx');o=overview(b);groups=json.loads((REGION/o['model_path']).read_text(encoding='utf-8'))['group']
    members={1:'Fregatidae; Sulidae; Laridae; Procellariidae; Stercorariidae',2:'Oceanitidae; Phalaropodidae',3:'Balaenoptera musculus; B. edeni',4:'Tursiops; Grampus; Steno; Globicephala; Peponocephala; Feresa; Pseudorca; Orcinus; Zyphius; Mesoplodon; Kogia; Physeter',5:'Stenella attenuata',6:'Stenella longirostris; Stenella coeruleoalba; Delphinus delphis; Lagenodelphis hosei; Lagenorhynchus obliquidens',7:'Lepidochelys olivacea; Chelonia mydas; Caretta caretta',8:'Thunnus albacares; large >90 cm',9:'Thunnus obesus; large >80 cm',10:'Makaira indica; M. mazara; Tetrapturus audax; large >150 cm',11:'Istiophorus platypterus; large >150 cm',12:'Xiphias gladius; large >150 cm',13:'Coryphaena hippurus; C. equiselis; large >90 cm',14:'Acanthocybium solandri; large >90 cm',15:'Sphyrna spp.; Alopias spp.; Isurus oxyrinchus; Carcharhinus spp. (4 species); Prionace glauca; Nasolamia velox; large >150 cm',16:'Manta birostris',17:'Katsuwonus pelamis',18:'Thunnus alalunga',19:'Auxis thazard; A. rochei',20:'Thunnus orientalis',21:'Thunnus albacares; small <90 cm',22:'Thunnus obesus; small <80 cm',23:'Makaira indica; M. mazara; Tetrapturus audax; small <150 cm',24:'Istiophorus platypterus; small <150 cm',25:'Xiphias gladius; small <150 cm',26:'Coryphaena hippurus; C. equiselis; small <90 cm',27:'Acanthocybium solandri; small <90 cm',28:'Sphyrna spp.; Alopias spp.; Isurus oxyrinchus; Carcharhinus spp. (4 species); Prionace glauca; Nasolamia velox; small <150 cm',29:'Euthynnus lineatus; Sarda orientalis; S. chiliensis; Carangidae; Gempylidae',30:'Primarily: Exocoetus spp.; Hirundichthys spp.; Prognichthys spp.; Oxyporhamphus micropterus',31:'Primarily: Clupeidae; Nomeidae; Balistidae; Ostraciidae; Tetraodontidae; Diodontidae; Scomber japonicus; Scomberomorus sierra; Engraulidae',32:'Primarily: Phosichthyidae; Myctophidae',33:'Primarily: Argonautidae; Octopoteuthidae; Thysanoteuthidae; Ommastrephidae; Enoploteuthidae',34:'Pleuroncodes planipes; Portunus xantusii; Euphylax robustus',35:'Copepods (omnivorous and predatory); larval and juvenile euphausiids; thecosome pteropods; larval fishes; chaetognaths; ctenophores; hydromedusae',36:'Heterotrophic nanoflagellates; heterotrophic dinoflagellates; ciliates; crustacean nauplii',37:'Diatoms; phototrophic dinoflagellates; chlorophytes',38:'Prochlorococcus spp.; Synechococcus spp.; picoeukaryotes; heterotrophic bacteria',39:'Nonliving detritus pool; identified in Table 3a; numeric routing not documented'}
    taxonomy=[{'seq':int(g['group_seq']),'group_name':g['group_name'],'taxon_descr':members[int(g['group_seq'])]} for g in groups]
    assert len(taxonomy)==39
    write_csv('taxonomy.csv',['seq','group_name','taxon_descr'],taxonomy)
    resolved={'Katsuwonus pelamis':'Skipjack tuna','Thunnus alalunga':'Albacore','Thunnus orientalis':'Bluefin tuna','Carangidae':'Miscellaneous piscivores'}
    split={'Thunnus albacares':'Large yellowfin tuna; Small yellowfin tuna','Thunnus obesus':'Large bigeye tuna; Small bigeye tuna','Prionace glauca':'Large sharks; Small sharks','Xiphias gladius':'Large swordfish; Small swordfish','Coryphaena hippurus':'Large dorado; Small dorado','Coryphaena':'Large dorado; Small dorado','Acanthocybium solandri':'Large wahoo; Small wahoo','Carcharhinus falciformis':'Large sharks; Small sharks','Carcharhinus longimanus':'Large sharks; Small sharks','Alopias':'Large sharks; Small sharks','Sphyrna':'Large sharks; Small sharks','Istiophorus platypterus':'Large sailfish; Small sailfish'}
    names={g['group_name'] for g in groups};assert set(resolved.values())<=names
    review=[];total=covered=0
    for r in records(b,'Catch','Catch'):
        if r['catch_basis']!='catch':continue
        taxon=r['taxon'];catch=r[2019] or 0;total+=catch
        if taxon in resolved:
            group=resolved[taxon];weight=1;status='supported assignment; coefficient not admitted';why='Explicit taxon in Table 1a; one model group; no size split.';covered+=catch
        elif taxon in split:
            group='';weight='';status='unresolved allocation';why='Source-supported membership, but catch has no regional size allocation. Candidate groups: '+split[taxon]
        else:
            group='';weight='';status='unresolved membership/allocation';why='Catch label spans groups, source membership does not establish all members, or synonym/species reconciliation remains needed. No invented allocation.'
        review.append({'model_id':o['selected_model_id'],'taxon':taxon,'group':group,'weight':weight,'status':status,'catch_2019_tonnes':catch,'evidence':'Olson & Watters (2003), Table 1a, printed pp.152-153 / PDF22-23','explanation':why})
    write_csv('matching_review_NOT_ADOPTED.csv',list(review[0]),review)
    source_path=REGION/'papers/ETP-2003/Olson_Watters_2003_ETP-c037fcbc.pdf'
    summary={'region':'HS_077','selected_model_id':o['selected_model_id'],'source_admission':'BLOCKED: source diets require repair; historical runtime normalized them and inferred BA','annual_GE_2019_all_source_total_catch_tC':None,'annual_GE_coverage_percent':0,'mapping_review_total_labels':len(review),'mapping_review_supported_labels':len(resolved),'catch_2019_tonnes':total,'supported_mapping_catch_2019_tonnes':covered,'supported_mapping_catch_coverage_percent':100*covered/total,'scientific_note':'Mapping support is not eligible coefficient coverage. GE annual PPR unavailable, never zero. No regional allocation inferred from 1993-1997 model catches or biomass.','source_pdf_sha256':hashlib.sha256(source_path.read_bytes()).hexdigest(),'workbook_untouched':True}
    (HERE/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    d=json.loads((HERE/'direct_diagnostics.json').read_text(encoding='utf-8'))
    (HERE/'DIRECT_DIAGNOSTICS.md').write_text('\n\n'.join('```json\n'+json.dumps({k:v},indent=2)+'\n```' for k,v in d.items()),encoding='utf-8')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
