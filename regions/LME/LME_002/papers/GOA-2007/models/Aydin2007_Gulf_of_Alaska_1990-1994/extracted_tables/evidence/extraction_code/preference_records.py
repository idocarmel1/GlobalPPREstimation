"""Verbatim pool percentages transcribed from visually checked Appendix C tables.

These are published aggregate diet specifications, not normalized final diets.
Source spelling is retained here; a separate crosswalk resolves model groups.
An asterisk restricts prey to juvenile predators; + to adult predators (C5/C6).
"""
import json
from pathlib import Path

records=[]
def add(table, pages, predator, rows):
    for line in rows.strip().splitlines():
        percent, prey = line.split('|',1)
        preference=percent.endswith('P')
        records.append(dict(table=table,pdf_pages=pages,printed_pages=[p-10 for p in pages],
            predator=predator,percent_literal=percent.rstrip('P'),preference=preference,
            prey=[s.strip() for s in prey.split(';')],source='Aydin et al. 2007 AFSC-178',
            extraction='manual transcription from 200 dpi source page; pools preserved'))

add('C4',[248],'Sea Otters','''
75.0P|Urchins dollars and cucumbers;Misc. crabs
20.0P|W. pollock;W. pollock juv;P. cod juv;Herring;Herring juv;P. halibut juv;Other Sebastes;Capelin;Sand lance;Eulachon;Managed forage;Other pelagic smelt
5.00|Squids
''')
add('C5',[249,250],'West S.S.L. / West S.S.L._Juv','''
39.9P|W. pollock;W. pollock juv*
17.7P|Salmon outgoing;Salmon returning
7.5P|Herring;Herring juv*
6.6|Atka mackerel
5.0|Sand lance
3.6|Misc. shallow fish
3.1P|P. cod;P. cod juv*
2.5P|Arrowtooth;Arrowtooth juv*
2.3|Large sculpins
2.0P|N rock sole;S rock sole
1.3|Managed forage
1.3P|Octopus;Squids
1.1|Greenlings
0.9P|Pacific ocean perch;Sharpchin rockfish;Northern rockfish;Dusky rockfish;Other Sebastes;Shortraker rockfish+;Rougheye rockfish+;Shortspine thornyhead+
0.8|Polychaetes
0.7P|Big skate;Longnose skate;Alaska skate;Bering skate;Aleutian skate
0.7P|Flathead sole;AK plaice;Dover sole;Rex sole;Flathead sole juv*
0.6|Bathylagidae
0.6P|Halibut;Halibut juv*
0.5|Capelin
0.3|Other sculpins
0.3|Other pelagic smelt
0.3|Yellowfin sole
0.2|Misc. flatfish
0.2P|Shearwater;Murre;Kittiwake;Auklet;Puffin;Fulmar;Storm Petrel;Cormorants;Gulls;Albatross Jaeger
0.2|Sablefish+;Sablefish juv*
0.1|Eulachon
''')
add('C5',[249,250],'Central S.S.L. / Central S.S.L._Juv','''
40.4P|W. pollock;W. pollock juv*
20.2P|Salmon outgoing;Salmon returning
16.9P|Arrowtooth;Arrowtooth juv*
3.9|Sand lance
3.0|Other pelagic smelt
2.9|Misc. shallow fish
2.8P|Herring;Herring juv*
2.0P|P. cod;P. cod juv*
1.6P|Octopus;Squids
1.1|Capelin
0.9|Sablefish+;Sablefish juv*
0.8P|Flathead sole;AK plaice;Dover sole;Rex sole;Flathead sole juv*
0.6P|Halibut;Halibut juv*
0.5P|Pacific ocean perch;Sharpchin rockfish;Northern rockfish;Dusky rockfish;Other Sebastes;Shortraker rockfish+;Rougheye rockfish+;Shortspine thornyhead+
0.5P|Big skate;Longnose skate;Alaska skate;Bering skate;Aleutian skate
0.5|Managed forage
0.5|Polychaetes
0.3P|N rock sole;S rock sole
0.3|Eulachon
0.2|Myctophidae
0.2|Large sculpins
''')
add('C6',[251,252],'N. Fur Seal / N. Fur Seal_Juv','''
38.0|Capelin
34.0|Sand lance
8.5P|W. pollock;W. pollock juv*
6.5|Squid
5.5P|P. cod;P. cod juv*;Arrowtooth;Arrowtooth juv*;Halibut;Halibut juv*;Yellowfin sole;Flathead sole;Flathead sole juv*;N rock sole;S rock sole;AK plaice;Dover sole;Rex sole;Misc. flatfish;Sablefish;Sablefish juv;Eelpouts;Atka mackerel;Atka mack juv*;Greenlings;Large sculpins;Other sculpins;Misc. shallow fish;Salmon outgoing;Bathylagidae;Myctophidae;Eulachon;Managed forage;Oth. Pelagic smelt
3.5P|Herring;Herring juv*
2.0|Salmon returning
2.0P|Pacific o. perch;Sharpchin rf.;Northern rockfish;Dusky rockfish;Shortraker rf.;Rougheye rf.;Other Sebastes
''')
add('C6',[251,252],'Resident seals','''
42.6P|W. pollock;W. pollock juv
32.4P|Herring;Herring juv
9.7|Misc. shallow fish
4.0|Salmon returning
2.7P|Eelpouts;Atka mackerel;Atka mack juv;Greenlings
2.1P|Octopus;Squid
1.6P|P. cod;P. cod juv
1.2P|Large sculpins;Other sculpins
1.2P|Arrowtooth;Arrowtooth juv;Halibut;Halibut juv;Yellowfin sole;Flathead sole;Flathead sole juv;N rock sole;S rock sole;AK plaice;Dover sole;Rex sole;Misc. flatfish
1.1P|Pacific o. perch;Sharpchin rf.;Northern rockfish;Dusky rockfish;Shortraker rf.;Rougheye rf.;Other Sebastes
0.8|Sand lance
0.4P|Capelin;Eulachon;Managed forage;Oth. Pelagic smelt
0.2P|Pandalid shrimp;Non-pand. sh.;Tanner crab;King crab;Snow crab;Hermit crab;Misc. crab
''')
add('C7',[253],'Transient Killers','''
100P|Porpoises;Belugas;Gray whales;Humpback whales;Fin whales;Sei whales;Right whales;Minke whales;Bowhead whales;Sea otters;N. fur seal;N. fur seal juv;Steller sea lion;Steller sea lion juv;Resident seals
''')
add('C7',[253],'Sperm and beaked whales','''
85.0|Squid
15.0P|Sleeper sharks;P. cod;Alaska skate;Bering skate;Aleutian skate;Whiteblotched skate;Mud skate;Sablefish;Sablefish juv;Eelpouts;Giant grenadier;Pacific grenadier;Other Macrourids;Misc. deep fish;Pacific o. perch;Sharpchin rf.;Northern rockfish;Dusky rockfish;Shortraker rf.;Rougheye rf.;Sh. thornyhead;Other Sebastes
''')
add('C7',[253],'Resident Killers','''
100P|W. pollock;W. pollock juv;P. cod;P. cod juv;Herring;Herring juv;Arrowtooth;Arrowtooth juv;Kamchatka;Kamchatka juv;Gr. turbot;Gr. turbot juv;P. Halibut;P. Halibut juv;Yellowfin sole;Yellowfin so. juv;Flathead sole;Flathead sold juv;N. rock sole;S. rock sole;Alaska plaice;Dover sole;Rex sole;Misc. flatfish;Squid;Salmon returning;Salmon outgoing;Bathylagidae;Myctophidae;Capelin;Sand lance;Eulachon;Managed forage;Oth pel. smelt
''')
add('C7',[253],'Porpoises','''
69.3|Squid
18.5P|Bathylagidae;Myctophidae;Capelin;Sand lance;Eulachon;Managed Forage;Oth pel. smelt
12.2P|Eelpouts;Other sculpins;Misc. shallow fish
''')

add('C8',[254],'Gray Whales','''
90.0|Benthic amphipods
10.0P|Tanner crab;King crab;Snow crab;Pandalid shrimp;Non-pand. shrimp;Sea star;Brittle star;Urchins dollars and cucumbers;Snails;Hermit crabs;Misc. crabs;Misc. Crustacean;Anemones;Corals;Benth. Hydroid;Benth. Urochordata;Sea Pens;Sponge;Bivalves;Polychaete;Misc. Worm. Etc.
''')
add('C8',[254],'Humpbacks','''
59.9P|Chaetognaths;Euphausiids;Mysids;Pel. amphipods;Pteropods
39.9P|W. pollock juv;Herring juv;Atka mack juv;Misc. shallow fish;Salmon returning;Salmon outgoing;Capelin;Sand lance;Eulachon;Managed Forage;Oth pel. smelt
0.5|Squid
0.5|Copepods
''')
add('C8',[254],'Fin Whales','''
60.0P|Chaetognaths;Euphausiids;Mysids;Pel. amphipods;Pteropods
20.0|Copepods
20.0P|W. pollock juv;Herring juv;Misc. shallow fish;Salmon returning;Salmon outgoing;Capelin;Sand lance;Eulachon;Managed Forage;Oth pel. smelt
''')
add('C8',[254],'Sei whales','''
80.0|Copepods
10.0P|W. pollock juv;Herring juv;Salmon returning;Salmon outgoing;Capelin;Sand lance;Eulachon;Managed Forage;Oth pel. smelt
5.0P|Chaetognaths;Euphausiids;Mysids;Pel. amphipods;Pteropods
5.0|Squid
''')
add('C8',[254],'Right whales','''
95.0|Copepods
5.0P|Chaetognaths;Euphausiids;Mysids;Pel. amphipods;Pteropods
''')
add('C8',[254],'Minke whales','''
56.0P|W. pollock juv;Herring juv;Salmon returning;Salmon outgoing;Capelin;Sand lance;Eulachon;Managed Forage;Oth pel. smelt
40.0P|Chaetognaths;Euphausiids;Mysids;Pel. amphipods;Pteropods
2.0|Squid
2.0|Copepods
''')
add('C9',[255,256],'Sleeper shark','''
67.2|Arrowtooth fl.
12.3|Offal
5.2|W. pollock
4.6|Octopus
4.5|Salmon returning
2.1P|Pacific o. perch;Sharpchin rf.;Northern rockfish;Dusky rockfish;Shortraker rf.;Rougheye rf.;Sh. thornyhead;Other Sebastes
1.1P|Arrowtooth juv;Halibut;Halibut juv;Yellowfin sole;Flathead sole juv;N rock sole;S rock sole;AK plaice;Dover sole;Rex sole;Misc flatfish
1.0|Flathead sole
0.8|Squids
0.7|Snails
0.5|Misc. shallow fish
0.01|Non-Pandalid shrimp
0.01|Hermit crabs
''')
add('C9',[255,256],'Salmon shark','''
39.6|Salmon returning
36.0|Sablefish
11.0|P. halibut juv
7.0|Squids
4.0P|Greenlings;Large sculpins;Other sculpins;Misc. fish shallow
1.0|Dogfish
1.0P|Pacific o. perch;Sharpchin rf.;Northern rockfish;Dusky rockfish;Shortraker rf.;Rougheye rf.;Sh. thornyhead;Other Sebastes
0.4|Herring
''')
add('C9',[255,256],'Dogfish','''
15.4P|W. pollock;W. pollock juv;P. cod;P. cod juv;Misc. shallow fish
14.2|Herring
12.9|Euphausiids
11.2P|Arrowtooth fl.;Arrowtooth juv;Halibut;Halibut juv;Yellowfin sole;Flathead sole;Flathead sole juv;N rock sole;S rock sole;AK plaice;Dover sole;Rex sole;Misc. flatfish
9.1P|Chaetognaths;Mysids;Pel. amphipods;Pteropods;Copepods
7.6|Pandalid shrimp
6.7|Misc. crabs
3.7|Eulachon
2.9P|Tanner crab;King crab;Non Pand. shrimp;Sea star;Brittle star;Snails;Hermit crabs;Anemones;Benth. Hydroid;Bivalves;Polychaete;Misc. Worm. Etc.
2.9|Octopus
2.8P|Pacific o. perch;Sharpchin rf.;Northern rockfish;Dusky rockfish;Shortraker rf.;Rougheye rf.;Sh. thornyhead;Other Sebastes
2.3|Pel. gel. filter feeder
2.0P|Dogfish;Alaska skate;Bering skate;Aleutian skate;Whiteblotched skate;Mud skate;Longnose skate;Big skate
1.8|Squids
1.2|Misc. worm etc.
1.2|Scyphozoid jellies
1.1|Sand lance
0.6|Benthic amphipods
0.3|Urchins dollars and cucumbers
0.1|Misc. Crustacean
''')

add('C10',[257,258],'Alaska skate','''
16.8|Benthic amphipods
12.2|Atka mackerel
12.2|Octopus
11.8|Squids
7.9P|P. cod;P. cod juv;Herring;Herring juv;Arrowtooth fl.;Arrowtooth juv;Halibut;Halibut juv;Yellowfin sole;Flathead sole;Flathead sole juv;N rock sole;S rock sole;AK plaice;Dover sole;Rex sole;Misc. flatfish;Sablefish juv;Eelpouts;Greenlings;Capelin;Sand lance;Eulachon;Managed forage;Oth. pelagic smelt
7.9|Other sculpins
7.9|Tanner crabs
3.9P|W. pollock;W. pollock juv
3.9|Large sculpins
3.9|Misc. shallow fish
3.9|Bathylagidae
3.9|Non-Pandalid shrimp
3.9|Hermit crabs
''')
add('C10',[257,258],'Bering skate','''
80.5|Benthic amphipods
10.5|Misc. worms etc.
2.8|Pandalid shrimp
1.7|Squids
1.1|Non-Pand. shrimp
0.9|Misc. Crustacean
0.9|Polychaetes
0.9|Benthic detritus
0.3|Brittle star
0.2P|W. pollock;W. pollock juv;P. cod;P. cod juv;Herring;Herring juv;Arrowtooth fl.;Arrowtooth juv;Halibut;Halibut juv;Yellowfin sole;Flathead sole;Flathead sole juv;N rock sole;S rock sole;AK plaice;Dover sole;Rex sole;Misc. flatfish;Sablefish juv;Eelpouts;Atka mackerel;Atka mack. juv;Greenlings;Large sculpins;Other sculpins;Misc. shallow fish
0.2|Hermit crabs
''')
add('C10',[257,258],'Aleutian skate','''
26.4|Pandalid shrimp
14.6|Squids
9.8P|W. pollock juv;P. cod;P. cod juv;Herring;Herring juv;Arrowtooth fl.;Arrowtooth juv;Halibut;Halibut juv;Yellowfin sole;Flathead sole;Flathead sole juv;N rock sole;S rock sole;AK plaice;Dover sole;Rex sole;Misc. flatfish;Sablefish;Sablefish juv;Misc. shallow fish;Pacific o. perch;Pacific o. perch juv;Sharpchin rf.;Northern rockfish;Dusky rockfish;Shortraker rf.;Rougheye rf.;Sh. thornyhead;Sh. thornyhead juv;Other Sebastes;Atka mack. juv;Greenlings;Bathylagidae;Myctophidae;Capelin;Sandlance;Eulachon;Managed Forage;Oth pel. smelt
8.8|Tanner crabs
7.7|Other sculpins
6.5|Benthic amphipods
5.4|Misc. shallow fish
4.7|Octopus
4.3|Atka mackerel
3.0|W. pollock
2.5|Misc. worm etc.
2.5|Benthic detritus
1.3|Large sculpins
0.8|Eelpouts
0.4|Bering skate
0.4|Non-Pandalid shrimp
0.4|Hermit crabs
0.4|Polychaetes
''')
add('C10',[257,258],'Other skates','''
26.5|Squids
25.7|Benthic amphipods
10.4P|W. pollock juv;P. cod;P. cod juv;Herring;Herring juv;Arrowtooth fl.;Arrowtooth juv;Halibut;Halibut juv;Yellowfin sole;Flathead sole;Flathead sole juv;N rock sole;S rock sole;AK plaice;Dover sole;Rex sole;Misc. flatfish;Sablefish;Sablefish juv;Misc. shallow fish;Eelpouts;Giant grenadier;Pacific grenadier;Pacific o. perch;Pacific o. perch juv;Sharpchin rf.;Northern rockfish;Dusky rockfish;Rougheye rf.;Sh. thornyhead;Sh. thornyhead juv;Other Sebastes;Atka mack. juv;Greenlings;Capelin;Sandlance;Eulachon;Managed Forage;Oth pel. smelt
9.8|Pandalid shrimp
4.3|Tanner crabs
3.5|Atka mackerel
3.0|Hermit crabs
2.9|Octopus
2.7|Polychaetes
2.7|Benthic detritus
1.8|Misc. worm, etc.
1.5|Other sculpins
1.1|Myctophidae
0.9|W. pollock
0.8|Bathylagidae
0.7|Non-Pandalid shrimp
0.4|Mysids
0.3|Misc. shallow fish
0.2|Shortraker rf.
0.2|Misc. Crustacean
0.1|Other Macrourids
0.1|Large sculpins
0.1|King crabs
0.1|Bivalves
''')
add('C10',[257,258],'Longnose skate','''
47.5P|W. pollock juv;P. cod;P. cod juv;Herring;Herring juv;Sablefish juv;Eelpouts;Atka mackerel;Atka mack. juv;Greenlings;Large sculpins;Other sculpins;Misc. shallow fish;Salmon returning;Salmon outgoing;Bathylagidae;Myctophidae;Capelin;Sandlance;Eulachon;Managed Forage;Oth pel. smelt
25.4|Rex sole
25.0P|Arrowtooth fl.;Arrowtooth juv;Halibut;Halibut juv;Yellowfin sole;Flathead sole;Flathead sole juv;N rock sole;S rock sole;AK plaice;Dover sole;Misc. flatfish
2.1|Non-Pandalid shrimp
''')
add('C10',[257,258],'Big skate','''
44.1|Non-Pandalid shrimp
17.4P|Arrowtooth fl.;Arrowtooth juv;Halibut;Halibut juv;Yellowfin sole;Flathead sole;Flathead sole juv;N rock sole;S rock sole;AK plaice;Misc. flatfish
12.1|Sand lance
11.8P|W. pollock juv;P. cod;P. cod juv;Herring;Herring juv;Sablefish juv;Atka mack. juv;Greenlings;Large sculpins;Other sculpins;Salmon returning;Salmon outgoing;Capelin;Eulachon;Managed Forage;Oth pel. smelt
10.0|Eelpouts
1.3|Benthic detritus
1.0|Mysid
0.9|Misc. shallow fish
0.5|Octopus
0.4|Bivalves
0.2|Misc. Crustacean
0.1|Benthic amphipods
0.1|Misc. crabs
''')

if __name__=='__main__':
    out=Path(__file__).resolve().parents[1]/'qa'/'preference_diets.json'
    out.write_text(json.dumps({'schema_version':1,'records':records},ensure_ascii=False,indent=2),encoding='utf-8')
    print(out)
