# Mapping work order — LME_035

catch years        : 1950-2019
taxa to map        : 247
total catch        : 151,964,195 tonnes over the whole period
Ecopath models     : 1

## Model selection — check `usable` before mapping

| author | title | usable | notes |
| --- | --- | --- | --- |
| From Ecobase 412 (Christensen, 1998) |  | **yes** |  |
| Mala Supongpan (2003) | Trophic Model of the Coastal Fisheries Ecosystem in the Gulf | **unchecked** | NOT CHECKED |

A model marked `no` must not be mapped. Say so and stop.

## Model `35_412_Gulf_of_Thailande_(1963)`

30 groups, 20 SPPR methods. Group names below are verbatim and authoritative — copy them exactly.

| seq | group_name | type | TL | biomass | model catch |
| --- | --- | --- | --- | --- | --- |
| 1 | `M. mammals` | Regular | 4.883 | 0.025 | 0 |
| 2 | `Sharks` | Regular | 4.394 | 0.002 | 0.008 |
| 3 | `Lg. piscivores` | Regular | 3.85 | 0.045 | 0.176 |
| 4 | `Grouper/snapper` | Regular | 3.907 | 0.044 | 0.171 |
| 5 | `Tuna` | Regular | 4.135 | 0.373 | 0.121 |
| 6 | `Med.dem.pisc.` | Regular | 3.38 | 0.164 | 0.64 |
| 7 | `Scomberomorus` | Regular | 3.91 | 0.2861 | 0.127 |
| 8 | `Juv. sharks` | Regular | 3.737 | 0.04662 | 0 |
| 9 | `Juv.Lg.Pisciv.` | Regular | 3.737 | 0.04662 | 0 |
| 10 | `Juv. groupers` | Regular | 3.759 | 0.04662 | 0 |
| 11 | `Scad` | Regular | 3.528 | 0.8136 | 1.006 |
| 12 | `Cephalopods` | Regular | 3.381 | 0.35 | 1.37 |
| 13 | `Sm.dem.pisc.` | Regular | 3.344 | 0.162 | 0.635 |
| 14 | `Med.dem.benth.` | Regular | 3.502 | 0.072 | 0.281 |
| 15 | `Rays` | Regular | 3.389 | 0.007 | 0.028 |
| 16 | `Flatfish` | Regular | 3.354 | 0.006 | 0.022 |
| 17 | `Sm.dem.benth.` | Regular | 3.187 | 0.191 | 0.749 |
| 18 | `Jellyfish` | Regular | 3.053 | 1 | 0 |
| 19 | `Mackerel` | Regular | 2.947 | 1.083 | 0.622 |
| 20 | `Sm. pelagics` | Regular | 2.947 | 1.181 | 0.955 |
| 21 | `Ponyfishes` | Regular | 2.784 | 0.123 | 0.48 |
| 22 | `Crab, lobster` | Regular | 2.78 | 0.042 | 0.245 |
| 23 | `O.fish` | Regular | 2.653 | 0.555 | 2.172 |
| 24 | `Benthos` | Regular | 2.56 | 33 | 0 |
| 25 | `Shrimps` | Regular | 2.417 | 1.36 | 0.901 |
| 26 | `Molluscs` | Regular | 2.211 | 12.62 | 0.955 |
| 27 | `Zooplankton` | Regular | 2.053 | 17.3 | 0 |
| 28 | `Phytoplankton` | PP | 1 | 18.25 | 0 |
| 29 | `Detritus` | DET | 1 | 100 | 0 |
| 30 | `diet_import` | Import | 1 | 1 | 0 |

`taxon_descr` carries membership for 29 of 30 groups — use it before the paper.
- `M. mammals`: Christensen 1998 pp.130-131: generic marine mammals, parameterized from other ecosystems; local species not listed.
- `Sharks`: Christensen 1998 pp.130-131: adult sharks with a separate juvenile compartment; species not listed.
- `Lg. piscivores`: Christensen 1998 p.130 important components: Trichiurus, Muraenesox, Chirocentrus, Sphyraena. This is an illustrative list, not an exhaustive species inventory.
- `Grouper/snapper`: Christensen 1998 p.130 important components: Ephinephelus, Lutjanus. This is an illustrative list, not an exhaustive species inventory.
- `Tuna`: Christensen 1998 p.130 important components: Thunnus tonggol, Euthynnus affinis, Auxis thazard. This is an illustrative list, not an exhaustive species inventory.
- `Med.dem.pisc.`: Christensen 1998 p.130 important components: Saurida, Lactarius, Lethrinus, Sciaenidae, Psettodes. This is an illustrative list, not an exhaustive species inventory.
- `Scomberomorus`: Christensen 1998 p.130 important components: Scomberomorus. This is an illustrative list, not an exhaustive species inventory.
- `Juv. sharks`: Christensen 1998 pp.130-131: juvenile sharks; species and age/length threshold not listed.
- `Juv.Lg.Pisciv.`: Christensen 1998 p.130 important components: Trichiurus, Muraenesox, Chirocentrus, Sphyraena. This is an illustrative list, not an exhaustive species inventory.
- `Juv. groupers`: Christensen 1998 p.130 important components: Ephinephelus, Lutjanus. Juvenile grouper AND snapper compartment; JSON label is shortened. This is an illustrative list, not an exhaustive species inventory.
- `Scad`: Christensen 1998 p.130 important components: Decapterus. This is an illustrative list, not an exhaustive species inventory.
- `Cephalopods`: Christensen 1998 pp.130-131: Cephalopods pool; individual species not listed.
- `Sm.dem.pisc.`: Christensen 1998 p.130 important components: Priacanthus. This is an illustrative list, not an exhaustive species inventory.
- `Med.dem.benth.`: Christensen 1998 p.130 important components: Plectorhynchus, Scolopsis, Upeneus, Pomadasys, Pampus, Arius, Tachysuridea. This is an illustrative list, not an exhaustive species inventory.
- `Rays`: Christensen 1998 pp.130-131: Rays pool; individual species not listed.
- `Flatfish`: Christensen 1998 p.130 important components: Bothidae, Cynoglossidae. This is an illustrative list, not an exhaustive species inventory.
- `Sm.dem.benth.`: Christensen 1998 p.130 important components: Nemipterus, Pentaprion. This is an illustrative list, not an exhaustive species inventory.
- `Jellyfish`: Christensen 1998 pp.130-131: generic jellyfish, included to represent presence; local species not listed.
- `Mackerel`: Christensen 1998 p.130 important components: Rastrelliger. This is an illustrative list, not an exhaustive species inventory.
- `Sm. pelagics`: Christensen 1998 p.130 important components: sardine, anchovy. This is an illustrative list, not an exhaustive species inventory.
- `Ponyfishes`: Christensen 1998 p.130 important components: Leiognathus. This is an illustrative list, not an exhaustive species inventory.
- `Crab, lobster`: Christensen 1998 pp.130-131: Crab, lobster pool; individual species not listed.
- `O.fish`: Christensen 1998 pp.130-131: trash fish; JSON abbreviated residual group. Its diet is 25% each phytoplankton, detritus, zooplankton and benthos. Species composition is not documented.
- `Benthos`: Christensen 1998 pp.130-131: Benthos pool; individual species not listed.
- `Shrimps`: Christensen 1998 pp.130-131: Shrimps pool; individual species not listed.
- `Molluscs`: Christensen 1998 pp.130-131: Molluscs pool; individual species not listed.
- `Zooplankton`: Christensen 1998 pp.130-131: Zooplankton pool; individual species not listed.
- `Phytoplankton`: Christensen 1998 pp.130-131: primary producer group; species not listed.
- `Detritus`: Christensen 1998 pp.130-131: nonliving detritus compartment; no species membership.

## Taxa, by tonnage

`coarse` marks a label above genus: it may legitimately span several groups, which is what the composite syntax is for.

| # | cum % | tonnes | taxon | rank | common name | SAU functional group | SAU commercial group | TL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 9.8 | 14,865,557 | `Nemipteridae` | **family** | Threadfins, whiptail breams | Small demersals (<30 cm) | Perch-likes | 3.51 |
| 2 | 17.7 | 12,027,858 | `Synodontidae` | **family** | Lizardfishes, sauries | Medium demersals (30 - 89 cm) | Other fishes & inverts | 4.30 |
| 3 | 24.6 | 10,490,185 | `Leiognathidae` | **family** | Slipmouths, ponyfishes | Small benthopelagics (<30 cm) | Perch-likes | 3.24 |
| 4 | 30.4 | 8,776,892 | `Rastrelliger kanagurta` | species | Indian mackerel | Medium pelagics (30 - 89 cm) | Perch-likes | 3.19 |
| 5 | 36.0 | 8,571,169 | `Carangidae` | **family** | Jacks, pompanos | Medium pelagics (30 - 89 cm) | Perch-likes | 4.05 |
| 6 | 41.2 | 7,914,679 | `Marine fishes not identified` | **category** | Marine fishes nei | Medium demersals (30 - 89 cm) | Other fishes & inverts | 3.28 |
| 7 | 45.4 | 6,360,940 | `Engraulidae` | **family** | Anchovies, round herrings | Small pelagics (<30 cm) | Anchovies | 3.20 |
| 8 | 49.6 | 6,300,173 | `Sciaenidae` | **family** | Drums, croakers | Medium demersals (30 - 89 cm) | Perch-likes | 3.76 |
| 9 | 53.5 | 5,991,392 | `Sardinella` | genus | Sardinellas | Small pelagics (<30 cm) | Herring-likes | 2.77 |
| 10 | 56.6 | 4,759,039 | `Platycephalidae` | **family** | Flatheads | Medium demersals (30 - 89 cm) | Scorpionfishes | 3.90 |
| 11 | 59.5 | 4,426,594 | `Loliginidae` | **family** | Common pencil squids | Cephalopods | Other fishes & inverts | 3.90 |
| 12 | 61.9 | 3,617,747 | `Perna viridis` | species | Brown mussel | Other demersal invertebrates | Molluscs |  |
| 13 | 64.2 | 3,391,063 | `Penaeus` | genus | Tiger prawns | Shrimps | Crustaceans | 2.70 |
| 14 | 66.3 | 3,199,377 | `Scombridae` | **family** | Mackerels, tunas, bonitos | Medium pelagics (30 - 89 cm) | Perch-likes | 4.26 |
| 15 | 68.1 | 2,761,997 | `Sepiidae` | **family** | Cuttlefishes | Cephalopods | Other fishes & inverts | 3.60 |
| 16 | 69.7 | 2,526,380 | `Priacanthus` | genus | Bigeyes | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.81 |
| 17 | 71.2 | 2,144,516 | `Penaeidae` | **family** | Commercial shrimps and prawns | Shrimps | Crustaceans | 3.31 |
| 18 | 72.6 | 2,143,133 | `Rastrelliger` | genus | Indian mackerels | Medium pelagics (30 - 89 cm) | Perch-likes | 3.10 |
| 19 | 73.9 | 1,991,346 | `Decapterus russelli` | species | Indian scad | Medium pelagics (30 - 89 cm) | Perch-likes | 3.68 |
| 20 | 75.2 | 1,966,533 | `Nemipterus` | genus | Threadfin breams | Small demersals (<30 cm) | Perch-likes | 3.72 |
| 21 | 76.4 | 1,941,136 | `Portunus pelagicus` | species | Blue swimming crab | Lobsters, crabs | Crustaceans | 2.48 |
| 22 | 77.7 | 1,853,315 | `Veneridae` | **family** | Venus clams | Other demersal invertebrates | Molluscs | 2.00 |
| 23 | 78.8 | 1,732,948 | `Saurida` | genus | Lizardfishes | Medium demersals (30 - 89 cm) | Other fishes & inverts | 4.35 |
| 24 | 79.8 | 1,580,033 | `Decapterus` | genus | Scads | Medium pelagics (30 - 89 cm) | Perch-likes | 3.63 |
| 25 | 80.8 | 1,447,770 | `Stolephorus` | genus | Garment anchovies | Small pelagics (<30 cm) | Anchovies | 3.44 |
| 26 | 81.7 | 1,430,940 | `Cephea` | genus | Cepheid jellyfishes | Jellyfish | Other fishes & inverts | 3.46 |
| 27 | 82.6 | 1,361,133 | `Scomberomorus guttatus` | species | Indo-Pacific king mackerel | Medium pelagics (30 - 89 cm) | Perch-likes | 4.28 |
| 28 | 83.5 | 1,241,411 | `Sparidae` | **family** | Porgies, seabreams | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.31 |
| 29 | 84.2 | 1,156,976 | `Megalaspis cordyla` | species | Torpedo scad | Medium pelagics (30 - 89 cm) | Perch-likes | 4.24 |
| 30 | 85.0 | 1,132,474 | `Mugilidae` | **family** | Mullets, grey mullets | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.53 |
| 31 | 85.6 | 993,203 | `Thunnus tonggol` | species | Longtail tuna | Large pelagics (>=90 cm) | Tuna & billfishes | 4.50 |
| 32 | 86.2 | 871,595 | `Selaroides leptolepis` | species | Yellowstripe scad | Small pelagics (<30 cm) | Perch-likes | 3.84 |
| 33 | 86.7 | 859,208 | `Dendrobranchiata` | genus | Shrimps and prawns | Shrimps | Crustaceans | 3.24 |
| 34 | 87.3 | 856,476 | `Ariidae` | **family** | Sea catfishes, coblers | Medium demersals (30 - 89 cm) | Other fishes & inverts | 3.48 |
| 35 | 87.9 | 849,251 | `Scomberomorus` | genus | Spanish mackerels | Large pelagics (>=90 cm) | Perch-likes | 4.35 |
| 36 | 88.4 | 813,216 | `Priacanthidae` | **family** | Bigeyes, catalufas | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.79 |
| 37 | 88.9 | 778,260 | `Octopodidae` | **family** | Octopuses | Cephalopods | Other fishes & inverts | 3.59 |
| 38 | 89.4 | 737,749 | `Clupeidae` | **family** | Herrings, sardines, menhadens | Small pelagics (<30 cm) | Herring-likes | 3.16 |
| 39 | 89.9 | 684,728 | `Sergestidae` | **family** | Sergestid shrimp | Shrimps | Crustaceans | 2.93 |
| 40 | 90.2 | 594,151 | `Alepes` | genus | Crevalles | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.32 |
| 41 | 90.6 | 581,883 | `Selar crumenophthalmus` | species | Bigeye scad | Medium pelagics (30 - 89 cm) | Perch-likes | 3.81 |
| 42 | 91.0 | 556,590 | `Penaeus merguiensis` | species | Banana prawn | Shrimps | Crustaceans | 3.77 |
| 43 | 91.3 | 529,365 | `Metapenaeus` | genus | Indo-Pacific prawns | Shrimps | Crustaceans | 2.70 |
| 44 | 91.7 | 515,699 | `Apogonidae` | **family** | Cardinalfishes | Small reef assoc. fish (<30 cm) | Perch-likes | 3.54 |
| 45 | 92.0 | 493,895 | `Mollusca` | genus | Clams, seasnails, squids, octopuses | Other demersal invertebrates | Molluscs | 2.10 |
| 46 | 92.3 | 490,184 | `Trichiurus lepturus` | species | Largehead hairtail | Large benthopelagics (>=90 cm) | Perch-likes | 4.42 |
| 47 | 92.6 | 469,544 | `Euthynnus affinis` | species | Kawakawa | Large pelagics (>=90 cm) | Tuna & billfishes | 4.50 |
| 48 | 92.9 | 440,058 | `Mullidae` | **family** | Goatfishes | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.46 |
| 49 | 93.2 | 438,943 | `Batoidea` | **superfamily** | Batoids, skates, rays, sawfishes | Large rays (>=90 cm) | Sharks & rays | 3.72 |
| 50 | 93.5 | 436,421 | `Sphyraena` | genus | Barracudas, sennets | Large pelagics (>=90 cm) | Perch-likes | 4.40 |
| 51 | 93.8 | 423,639 | `Modiolus` | genus | Horse mussels | Other demersal invertebrates | Molluscs | 2.00 |
| 52 | 94.0 | 357,626 | `Scombroidei` | **suborder** | Tunas, bonitos, billfishes | Large pelagics (>=90 cm) | Tuna & billfishes | 4.20 |
| 53 | 94.2 | 342,076 | `Lutjanidae` | **family** | Snappers | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.02 |
| 54 | 94.5 | 340,723 | `Saurida tumbil` | species | Greater lizardfish | Medium demersals (30 - 89 cm) | Other fishes & inverts | 4.40 |
| 55 | 94.7 | 330,520 | `Scolopsis` | genus | Monocle breams | Small reef assoc. fish (<30 cm) | Perch-likes | 3.30 |
| 56 | 94.9 | 314,475 | `Sepia` | genus | Sepia cuttlefishes | Cephalopods | Other fishes & inverts | 3.69 |
| 57 | 95.1 | 305,193 | `Portunus` | genus | Swimmer crabs | Lobsters, crabs | Crustaceans | 3.26 |
| 58 | 95.3 | 267,982 | `Parastromateus niger` | species | Black pomfret | Medium benthopelagics (30 - 89 cm) | Perch-likes | 2.93 |
| 59 | 95.4 | 262,477 | `Himantura` | genus | Whiprays | Large rays (>=90 cm) | Sharks & rays | 3.85 |
| 60 | 95.6 | 255,918 | `Acetes` | genus | Acetes shrimps | Shrimps | Crustaceans | 2.70 |
| 61 | 95.8 | 238,182 | `Pennahia` | genus | Pennah croakers | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.73 |
| 62 | 95.9 | 236,153 | `Metapenaeus tenuipes` | species | Stork shrimp | Shrimps | Crustaceans | 3.39 |
| 63 | 96.1 | 233,563 | `Metapenaeus affinis` | species | Jinga shrimp | Shrimps | Crustaceans | 3.44 |
| 64 | 96.2 | 230,384 | `Atule mate` | species | Yellowtail scad | Small pelagics (<30 cm) | Perch-likes | 4.22 |
| 65 | 96.4 | 210,170 | `Chirocentrus dorab` | species | Dorab wolf-herring | Large benthopelagics (>=90 cm) | Herring-likes | 4.20 |
| 66 | 96.5 | 205,203 | `Elasmobranchii` | genus | Sharks, rays, skates | Large sharks (>=90 cm) | Sharks & rays | 4.05 |
| 67 | 96.6 | 191,560 | `Sillago` | genus | Smelt-whitings | Medium demersals (30 - 89 cm) | Perch-likes | 3.33 |
| 68 | 96.8 | 187,671 | `Psettodes erumei` | species | Indian halibut | Small to medium flatfishes (<90 cm) | Flatfishes | 4.39 |
| 69 | 96.9 | 185,152 | `Serranidae` | **family** | Basses, groupers, hinds | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.98 |
| 70 | 97.0 | 184,085 | `Chirocentrus` | genus | Wolf herrings | Large pelagics (>=90 cm) | Herring-likes | 4.30 |
| 71 | 97.1 | 178,163 | `Epinephelus` | genus | Seabasses, hinds | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.84 |
| 72 | 97.2 | 174,080 | `Portunidae` | **family** | Swimming crabs | Lobsters, crabs | Crustaceans | 3.56 |
| 73 | 97.3 | 161,848 | `Lutjanus malabaricus` | species | Malabar blood snapper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes |  |
| 74 | 97.4 | 161,200 | `Muraenesox cinereus` | species | Daggertooth pike conger | Large demersals (>=90 cm) | Other fishes & inverts | 4.38 |
| 75 | 97.5 | 147,415 | `Upeneus` | genus | Upeneid goatfishes | Small reef assoc. fish (<30 cm) | Perch-likes | 3.54 |
| 76 | 97.6 | 142,750 | `Gobiidae` | **family** | Gobies | Small reef assoc. fish (<30 cm) | Perch-likes | 3.11 |
| 77 | 97.7 | 135,192 | `Penaeus latisulcatus` | species | Western king prawn | Shrimps | Crustaceans | 2.70 |
| 78 | 97.8 | 133,557 | `Sepioteuthis lessoniana` | species | Bigfin reef squid | Cephalopods | Other fishes & inverts | 3.98 |
| 79 | 97.9 | 131,359 | `Pomadasys` | genus | Grunters | Medium demersals (30 - 89 cm) | Perch-likes | 3.59 |
| 80 | 98.0 | 125,460 | `Scylla serrata` | species | Indo-Pacific swamp crab | Lobsters, crabs | Crustaceans | 3.17 |
| 81 | 98.1 | 117,054 | `Balistidae` | **family** | Triggerfishes | Medium reef assoc. fish (30 - 89 cm) | Other fishes & inverts | 3.25 |
| 82 | 98.1 | 103,715 | `Trichiurus` | genus | Hairtails | Large benthopelagics (>=90 cm) | Perch-likes | 4.42 |
| 83 | 98.2 | 101,727 | `Penaeus semisulcatus` | species | Green tiger prawn | Shrimps | Crustaceans | 2.00 |
| 84 | 98.3 | 101,649 | `Carcharhinus` | genus | Sharp-nosed sharks | Large sharks (>=90 cm) | Sharks & rays | 4.26 |
| 85 | 98.3 | 89,077 | `Katsuwonus pelamis` | species | Skipjack tuna | Large pelagics (>=90 cm) | Tuna & billfishes | 4.43 |
| 86 | 98.4 | 81,876 | `Thenus orientalis` | species | Flathead lobster | Lobsters, crabs | Crustaceans | 2.50 |
| 87 | 98.4 | 80,795 | `Penaeus monodon` | species | Giant tiger prawn | Shrimps | Crustaceans | 2.60 |
| 88 | 98.5 | 77,932 | `Terapon` | genus | Terapons | Medium demersals (30 - 89 cm) | Perch-likes | 3.50 |
| 89 | 98.5 | 77,894 | `Polynemidae` | **family** | Threadfins | Small demersals (<30 cm) | Perch-likes | 3.62 |
| 90 | 98.6 | 72,493 | `Cynoglossus` | genus | Tonguesoles | Small to medium flatfishes (<90 cm) | Flatfishes | 3.36 |
| 91 | 98.6 | 71,930 | `Leiognathus` | genus | Ponyfishes | Small benthopelagics (<30 cm) | Perch-likes | 3.22 |
| 92 | 98.7 | 71,255 | `Tetraodontidae` | **family** | Puffers, tobies | Large reef assoc. fish (>=90 cm) | Other fishes & inverts | 3.50 |
| 93 | 98.7 | 70,748 | `Seriolina nigrofasciata` | species | Blackbanded trevally | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.17 |
| 94 | 98.8 | 66,280 | `Miscellaneous aquatic invertebrates` | **category** | Aquatic invertebrates | Other demersal invertebrates | Other fishes & inverts | 2.43 |
| 95 | 98.8 | 62,355 | `Parapenaeopsis` | genus | Leafy-legged shrimps | Shrimps | Crustaceans | 2.72 |
| 96 | 98.8 | 60,526 | `Lutjanus` | genus | Snappers | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.02 |
| 97 | 98.9 | 60,321 | `Cephalopoda` | **class** | Squids, cuttlefishes, octopuses | Cephalopods | Other fishes & inverts | 3.81 |
| 98 | 98.9 | 58,554 | `Pristipomoides` | genus | Jobfishes | Medium demersals (30 - 89 cm) | Perch-likes | 3.91 |
| 99 | 99.0 | 56,415 | `Lutjanus quinquelineatus` | species | Five-lined snapper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.68 |
| 100 | 99.0 | 55,888 | `Siganus` | genus | Spinefoots | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.11 |
| 101 | 99.0 | 54,848 | `Nemipterus japonicus` | species | Japanese threadfin bream | Small demersals (<30 cm) | Perch-likes | 3.77 |
| 102 | 99.1 | 54,179 | `Mugil` | genus | Grey mullets | Medium demersals (30 - 89 cm) | Perch-likes | 2.26 |
| 103 | 99.1 | 54,147 | `Ilisha elongata` | species | Elongate ilisha | Medium pelagics (30 - 89 cm) | Herring-likes | 3.79 |
| 104 | 99.1 | 49,887 | `Carangoides` | genus | Trevallies | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.34 |
| 105 | 99.2 | 49,448 | `Tegillarca granosa` | species | Granular ark | Other demersal invertebrates | Molluscs | 2.00 |
| 106 | 99.2 | 45,887 | `Acanthurus` | genus | Surgeonfishes | Small reef assoc. fish (<30 cm) | Perch-likes | 2.03 |
| 107 | 99.2 | 44,489 | `Mierspenaeopsis sculptilis` | species | Rainbow shrimp | Shrimps | Crustaceans | 2.71 |
| 108 | 99.2 | 42,452 | `Ozius guttatus` | species | Spottedbelly rock crab | Lobsters, crabs | Crustaceans | 3.70 |
| 109 | 99.3 | 42,037 | `Marine groundfishes not identified` | **category** | Groundfishes | Medium demersals (30 - 89 cm) | Other fishes & inverts | 3.22 |
| 110 | 99.3 | 41,840 | `Bothidae` | **family** | Lefteye flounders | Small to medium flatfishes (<90 cm) | Flatfishes | 3.77 |
| 111 | 99.3 | 40,244 | `Thunnus albacares` | species | Yellowfin tuna | Large pelagics (>=90 cm) | Tuna & billfishes | 4.41 |
| 112 | 99.4 | 39,896 | `Rachycentron canadum` | species | Cobia | Large pelagics (>=90 cm) | Perch-likes | 3.96 |
| 113 | 99.4 | 39,415 | `Penaeus japonicus` | species | Kuruma prawn | Shrimps | Crustaceans | 2.70 |
| 114 | 99.4 | 39,400 | `Melicertus canaliculatus` | species | Witch prawn | Shrimps | Crustaceans | 3.77 |
| 115 | 99.4 | 38,255 | `Plectorhinchus` | genus | Sweetlips | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.43 |
| 116 | 99.5 | 35,650 | `Pampus argenteus` | species | Silver pomfret | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.30 |
| 117 | 99.5 | 34,677 | `Muraenesox` | genus | Congers | Large demersals (>=90 cm) | Other fishes & inverts | 3.99 |
| 118 | 99.5 | 34,093 | `Scomberomorus commerson` | species | Narrow-barred Spanish mackerel | Large pelagics (>=90 cm) | Perch-likes | 4.50 |
| 119 | 99.5 | 33,185 | `Clupeiformes` | **order** | Herrings, shads, anchovies | Small pelagics (<30 cm) | Other fishes & inverts | 3.24 |
| 120 | 99.5 | 31,660 | `Sphyraena obtusata` | species | Obtuse barracuda | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.50 |
| 121 | 99.6 | 28,427 | `Scyris indica` | species | Indian threadfish | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.09 |
| 122 | 99.6 | 27,954 | `Anodontostoma chacunda` | species | Chacunda gizzard shad | Small pelagics (<30 cm) | Herring-likes | 2.84 |
| 123 | 99.6 | 27,602 | `Auxis thazard` | species | Frigate tuna | Medium pelagics (30 - 89 cm) | Tuna & billfishes | 4.37 |
| 124 | 99.6 | 25,751 | `Malacostraca` | genus | Lobsters, crabs, shrimps, krill | Shrimps | Crustaceans | 3.00 |
| 125 | 99.6 | 24,155 | `Lutjanus johnii` | species | John's snapper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.20 |
| 126 | 99.6 | 21,900 | `Gerreidae` | **family** | Mojarras, silverbellies | Small benthopelagics (<30 cm) | Perch-likes | 3.03 |
| 127 | 99.7 | 21,658 | `Caesionidae` | **family** | Fusiliers | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.39 |
| 128 | 99.7 | 21,432 | `Charybdis` | genus | Whirlpool swimming crabs | Lobsters, crabs | Crustaceans | 2.70 |
| 129 | 99.7 | 21,150 | `Scorpaenidae` | **family** | Scorpionfishes, rockfishes | Large reef assoc. fish (>=90 cm) | Scorpionfishes | 3.92 |
| 130 | 99.7 | 19,954 | `Podophthalmus vigil` | species | Periscope crab | Lobsters, crabs | Crustaceans | 3.36 |
| 131 | 99.7 | 19,705 | `Charybdis feriatus` | species | Crucifix crab | Lobsters, crabs | Crustaceans | 3.51 |
| 132 | 99.7 | 19,300 | `Scomberoides` | genus | Queenfishes | Medium pelagics (30 - 89 cm) | Perch-likes | 4.47 |
| 133 | 99.7 | 19,033 | `Caesio` | genus | Caesios | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.40 |
| 134 | 99.8 | 18,953 | `Charybdis anisodon` | species | Twospined arm swimming crab | Lobsters, crabs | Crustaceans | 3.42 |
| 135 | 99.8 | 18,848 | `Mierspenaeopsis hardwickii` | species | Spear shrimp | Shrimps | Crustaceans |  |
| 136 | 99.8 | 18,765 | `Plotosidae` | **family** | Eeltail catfishes | Medium reef assoc. fish (30 - 89 cm) | Other fishes & inverts | 3.49 |
| 137 | 99.8 | 18,571 | `Dussumieria` | genus | Rainbow sardines | Small pelagics (<30 cm) | Herring-likes | 3.40 |
| 138 | 99.8 | 16,391 | `Paralichthyidae` | **family** | Largetooth flounders | Small to medium flatfishes (<90 cm) | Flatfishes | 4.06 |
| 139 | 99.8 | 15,573 | `Siganus canaliculatus` | species | White-spotted spinefoot | Small reef assoc. fish (<30 cm) | Perch-likes | 2.76 |
| 140 | 99.8 | 15,389 | `Plotosus` | genus | Eel catfishes | Medium reef assoc. fish (30 - 89 cm) | Other fishes & inverts | 3.49 |
| 141 | 99.8 | 14,752 | `Siganidae` | **family** | Rabbitfishes | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.11 |
| 142 | 99.8 | 13,718 | `Panulirus longipes` | species | Longlegged spiny lobster | Lobsters, crabs | Crustaceans | 2.60 |
| 143 | 99.8 | 13,127 | `Solenocera crassicornis` | species | Coastal mud shrimp | Shrimps | Crustaceans | 2.20 |
| 144 | 99.9 | 12,440 | `Rhizostomeae` | genus | Oral arm jellyfishes | Jellyfish | Other fishes & inverts | 3.46 |
| 145 | 99.9 | 12,020 | `Elagatis bipinnulata` | species | Rainbow runner | Large pelagics (>=90 cm) | Perch-likes | 4.27 |
| 146 | 99.9 | 11,854 | `Istiophorus` | genus | Sailfishes | Large pelagics (>=90 cm) | Tuna & billfishes | 4.50 |
| 147 | 99.9 | 11,259 | `Thunnus obesus` | species | Bigeye tuna | Large pelagics (>=90 cm) | Tuna & billfishes | 4.49 |
| 148 | 99.9 | 10,870 | `Lates calcarifer` | species | Barramundi | Large demersals (>=90 cm) | Perch-likes | 4.35 |
| 149 | 99.9 | 10,084 | `Monacanthidae` | **family** | Filefishes | Medium reef assoc. fish (30 - 89 cm) | Other fishes & inverts | 3.00 |
| 150 | 99.9 | 9,400 | `Thunnus` | genus | Tunas | Large pelagics (>=90 cm) | Tuna & billfishes |  |
| 151 | 99.9 | 8,165 | `Bivalvia` | genus | Clams | Other demersal invertebrates | Molluscs |  |
| 152 | 99.9 | 8,012 | `Scarus` | genus | Parrots | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.00 |
| 153 | 99.9 | 7,902 | `Lactarius lactarius` | species | False trevally | Medium pelagics (30 - 89 cm) | Perch-likes | 3.97 |
| 154 | 99.9 | 7,584 | `Drepane` | genus | Sicklefishes | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.32 |
| 155 | 99.9 | 7,266 | `Lethrinus` | genus | Emperors | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.75 |
| 156 | 99.9 | 7,124 | `Dussumieria elopsoides` | species | Slender rainbow sardine | Small pelagics (<30 cm) | Herring-likes | 3.40 |
| 157 | 99.9 | 6,248 | `Rastrelliger brachysoma` | species | Short mackerel | Medium pelagics (30 - 89 cm) | Perch-likes | 2.72 |
| 158 | 99.9 | 6,242 | `Photopectoralis bindus` | species | Orangefin ponyfish | Large reef assoc. fish (>=90 cm) | Perch-likes | 2.93 |
| 159 | 99.9 | 6,152 | `Istiophoridae` | **family** | Billfishes | Large pelagics (>=90 cm) | Tuna & billfishes | 4.48 |
| 160 | 99.9 | 6,131 | `Palinuridae` | **family** | Spiny lobsters | Lobsters, crabs | Crustaceans | 3.14 |
| 161 | 100.0 | 5,502 | `Gazza minuta` | species | Toothpony | Small demersals (<30 cm) | Perch-likes | 4.19 |
| 162 | 100.0 | 5,338 | `Sardinella fimbriata` | species | Fringescale sardinella | Small pelagics (<30 cm) | Herring-likes | 2.70 |
| 163 | 100.0 | 5,058 | `Terapon theraps` | species | Largescaled terapon | Small pelagics (<30 cm) | Perch-likes | 3.49 |
| 164 | 100.0 | 4,664 | `Psettodidae` | **family** | Turbots, Indian halibuts | Small to medium flatfishes (<90 cm) | Flatfishes | 3.83 |
| 165 | 100.0 | 4,279 | `Pampus chinensis` | species | Chinese silver pomfret | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.60 |
| 166 | 100.0 | 3,693 | `Perciformes` | **order** | Perch-likes | Medium demersals (30 - 89 cm) | Perch-likes | 3.53 |
| 167 | 100.0 | 3,690 | `Priacanthus tayenus` | species | Purple-spotted bigeye | Small pelagics (<30 cm) | Perch-likes | 3.79 |
| 168 | 100.0 | 3,356 | `Eubleekeria splendens` | species | Splendid ponyfish | Small pelagics (<30 cm) | Perch-likes | 2.94 |
| 169 | 100.0 | 3,118 | `Scyllaridae` | **family** | Slipper lobsters | Lobsters, crabs | Crustaceans | 2.87 |
| 170 | 100.0 | 3,068 | `Sphyraenidae` | **family** | Barracudas | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.40 |
| 171 | 100.0 | 2,957 | `Gerres` | genus | Silver biddies | Small benthopelagics (<30 cm) | Perch-likes | 3.27 |
| 172 | 100.0 | 2,801 | `Xiphias gladius` | species | Swordfish | Large pelagics (>=90 cm) | Tuna & billfishes | 4.53 |
| 173 | 100.0 | 2,653 | `Haemulidae` | **family** | Grunts, sweetlips, bonnetmouths | Medium demersals (30 - 89 cm) | Perch-likes | 3.36 |
| 174 | 100.0 | 2,597 | `Thryssa` | genus | Thryssas | Small pelagics (<30 cm) | Anchovies | 3.34 |
| 175 | 100.0 | 2,398 | `Hilsa kelee` | species | Kelee shad | Small pelagics (<30 cm) | Herring-likes | 3.25 |
| 176 | 100.0 | 2,191 | `Octopus` | genus | Octopuses, pikas | Cephalopods | Other fishes & inverts | 3.80 |
| 177 | 100.0 | 1,992 | `Lethrinidae` | **family** | Emperors, scavengers | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.59 |
| 178 | 100.0 | 1,990 | `Pampus` | genus | Silver pomfrets | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.41 |
| 179 | 100.0 | 1,824 | `Platycaranx malabaricus` | species | Malabar trevally | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.88 |
| 180 | 100.0 | 1,677 | `Crassostrea` | genus | Cupped oysters | Other demersal invertebrates | Molluscs |  |
| 181 | 100.0 | 1,594 | `Gnathanodon speciosus` | species | Golden trevally | Large reef assoc. fish (>=90 cm) | Perch-likes | 3.84 |
| 182 | 100.0 | 1,370 | `Aluterus` | genus | Aluterid filefishes | Large reef assoc. fish (>=90 cm) | Other fishes & inverts | 2.81 |
| 183 | 100.0 | 1,295 | `Scatophagus` | genus | Scats | Medium demersals (30 - 89 cm) | Perch-likes | 2.75 |
| 184 | 100.0 | 1,295 | `Panulirus polyphagus` | species | Mud spiny lobster | Lobsters, crabs | Crustaceans | 2.94 |
| 185 | 100.0 | 1,283 | `Makaira mazara` | species | Indo-Pacific blue marlin | Large pelagics (>=90 cm) | Tuna & billfishes | 4.46 |
| 186 | 100.0 | 1,138 | `Miscellaneous marine crustaceans` | **category** | Marine crabs, shrimps, lobsters nei | Shrimps | Crustaceans | 2.70 |
| 187 | 100.0 | 1,000 | `Platycephalus indicus` | species | Bartail flathead | Medium demersals (30 - 89 cm) | Scorpionfishes | 3.60 |
| 188 | 100.0 | 931 | `Holothuriidae` | **family** | Fleshy sea cucumbers | Other demersal invertebrates | Other fishes & inverts |  |
| 189 | 100.0 | 851 | `Istiompax indica` | species | Black marlin | Large pelagics (>=90 cm) | Tuna & billfishes | 4.50 |
| 190 | 100.0 | 666 | `Menidae` | **family** | Moonfishes | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.45 |
| 191 | 100.0 | 605 | `Hyporhamphus` | genus | Sea garfishes | Small reef assoc. fish (<30 cm) | Other fishes & inverts | 3.30 |
| 192 | 100.0 | 539 | `Caranx sexfasciatus` | species | Bigeye trevally | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.50 |
| 193 | 100.0 | 422 | `Megalops cyprinoides` | species | Indo-Pacific tarpon | Large pelagics (>=90 cm) | Other fishes & inverts | 3.48 |
| 194 | 100.0 | 393 | `Spratelloides` | genus | Round herrings | Small reef assoc. fish (<30 cm) | Herring-likes |  |
| 195 | 100.0 | 331 | `Marine pelagic fishes not identified` | **category** | Pelagic fishes | Medium pelagics (30 - 89 cm) | Other fishes & inverts |  |
| 196 | 100.0 | 263 | `Makaira` | genus | Blue marlins | Large pelagics (>=90 cm) | Tuna & billfishes | 4.47 |
| 197 | 100.0 | 249 | `Thunnus alalunga` | species | Albacore | Large pelagics (>=90 cm) | Tuna & billfishes | 4.30 |
| 198 | 100.0 | 174 | `Scatophagus argus` | species | Spotted scat | Medium demersals (30 - 89 cm) | Perch-likes | 2.99 |
| 199 | 100.0 | 170 | `Panulirus` | genus | Spiny lobsters | Lobsters, crabs | Crustaceans |  |
| 200 | 100.0 | 164 | `Istiophorus platypterus` | species | Indo-Pacific sailfish | Large pelagics (>=90 cm) | Tuna & billfishes |  |
| 201 | 100.0 | 153 | `Ostreidae` | **family** | True oysters | Other demersal invertebrates | Molluscs | 2.00 |
| 202 | 100.0 | 132 | `Stromateidae` | **family** | Butterfishes | Small benthopelagics (<30 cm) | Perch-likes |  |
| 203 | 100.0 | 89 | `Aluterus monoceros` | species | Unicorn leatherjacket filefish | Medium reef assoc. fish (30 - 89 cm) | Other fishes & inverts | 3.84 |
| 204 | 100.0 | 84 | `Chondrichthyes` | genus | Sharks, rays, chimaeras | Large sharks (>=90 cm) | Sharks & rays | 4.00 |
| 205 | 100.0 | 45 | `Echinodermata` | genus | Sea urchins, stars, cucumbers | Other demersal invertebrates | Other fishes & inverts | 2.30 |
| 206 | 100.0 | 40 | `Caranx` | genus | Jacks | Medium reef assoc. fish (30 - 89 cm) | Perch-likes |  |
| 207 | 100.0 | 30 | `Pellona ditchela` | species | Indian pellona | Small pelagics (<30 cm) | Herring-likes | 3.37 |
| 208 | 100.0 | 23 | `Carcharhinus falciformis` | species | Silky shark | Large sharks (>=90 cm) | Sharks & rays |  |
| 209 | 100.0 | 22 | `Scyphozoa` | **phylum** | True jellyfishes | Jellyfish | Other fishes & inverts |  |
| 210 | 100.0 | 22 | `Coryphaena hippurus` | species | Common dolphinfish | Large pelagics (>=90 cm) | Perch-likes |  |
| 211 | 100.0 | 5 | `Labridae` | **family** | Wrasses, gropers, tuskfishes | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.46 |
| 212 | 100.0 | 4 | `Decapoda` | genus | Crabs, lobsters, shrimps | Lobsters, crabs | Crustaceans | 3.43 |
| 213 | 100.0 | 4 | `Netuma thalassina` | species | Giant catfish | Large demersals (>=90 cm) | Other fishes & inverts | 3.54 |
| 214 | 100.0 | 3 | `Sardinella lemuru` | species | Bali sardinella | Small pelagics (<30 cm) | Herring-likes | 2.48 |
| 215 | 100.0 | 3 | `Teuthida` | genus | Squids | Cephalopods | Other fishes & inverts | 4.13 |
| 216 | 100.0 | 3 | `Acetes japonicus` | species | Akiami paste shrimp | Shrimps | Crustaceans | 2.54 |
| 217 | 100.0 | 3 | `Lutjanus argentimaculatus` | species | Mangrove red snapper | Large reef assoc. fish (>=90 cm) | Perch-likes |  |
| 218 | 100.0 | 3 | `Penaeus indicus` | species | Indian white prawn | Shrimps | Crustaceans | 2.70 |
| 219 | 100.0 | 2 | `Nemipterus hexodon` | species | Ornate threadfin bream | Small demersals (<30 cm) | Perch-likes | 3.93 |
| 220 | 100.0 | 1 | `Cephalopholis boenak` | species | Chocolate hind | Small reef assoc. fish (<30 cm) | Perch-likes | 4.07 |
| 221 | 100.0 | 1 | `Dussumieria acuta` | species | Rainbow sardine | Small pelagics (<30 cm) | Herring-likes | 3.40 |
| 222 | 100.0 | 1 | `Sphyrna lewini` | species | Scalloped hammerhead | Large sharks (>=90 cm) | Sharks & rays |  |
| 223 | 100.0 | 0 | `Trichiuridae` | **family** | Cutlassfishes | Large benthopelagics (>=90 cm) | Perch-likes | 4.15 |
| 224 | 100.0 | 0 | `Auxis rochei` | species | Bullet tuna | Medium pelagics (30 - 89 cm) | Tuna & billfishes |  |
| 225 | 100.0 | 0 | `Hemiramphus` | genus | Halfbeaks | Medium pelagics (30 - 89 cm) | Other fishes & inverts | 3.05 |
| 226 | 100.0 | 0 | `Tetrapturus angustirostris` | species | Shortbill spearfish | Large pelagics (>=90 cm) | Tuna & billfishes |  |
| 227 | 100.0 | 0 | `Kajikia audax` | species | Striped marlin | Large pelagics (>=90 cm) | Tuna & billfishes |  |
| 228 | 100.0 | 0 | `Dasyatidae` | **family** | Whiptail stingrays | Large rays (>=90 cm) | Sharks & rays | 3.38 |
| 229 | 100.0 | 0 | `Prionace glauca` | species | Blue shark | Large sharks (>=90 cm) | Sharks & rays | 4.35 |
| 230 | 100.0 | 0 | `Cypselurus poecilopterus` | species | Yellowing flyingfish | Small pelagics (<30 cm) | Other fishes & inverts | 3.40 |
| 231 | 100.0 | 0 | `Latidae` | **family** | Lates perches | Large demersals (>=90 cm) | Perch-likes |  |
| 232 | 100.0 | 0 | `Hemiramphidae` | **family** | Halfbeaks, garfishes | Medium pelagics (30 - 89 cm) | Other fishes & inverts | 2.82 |
| 233 | 100.0 | 0 | `Carcharhinus longimanus` | species | Oceanic whitetip shark | Large sharks (>=90 cm) | Sharks & rays | 4.16 |
| 234 | 100.0 | 0 | `Octopoda` | **class** | Octopuses, argonauts | Cephalopods | Other fishes & inverts |  |
| 235 | 100.0 | 0 | `Pleuronectiformes` | **order** | Flatfishes | Small to medium flatfishes (<90 cm) | Flatfishes |  |
| 236 | 100.0 | 0 | `Congridae` | **family** | Conger, garden eels | Large demersals (>=90 cm) | Other fishes & inverts |  |
| 237 | 100.0 | 0 | `Isurus` | genus | Mako sharks | Large sharks (>=90 cm) | Sharks & rays |  |
| 238 | 100.0 | 0 | `Isurus oxyrinchus` | species | Shortfin mako | Large sharks (>=90 cm) | Sharks & rays | 4.50 |
| 239 | 100.0 | 0 | `Alopias` | genus | Thresher sharks | Large sharks (>=90 cm) | Sharks & rays |  |
| 240 | 100.0 | 0 | `Pomadasys argenteus` | species | Silver grunt | Medium demersals (30 - 89 cm) | Perch-likes | 3.47 |
| 241 | 100.0 | 0 | `Exocoetidae` | **family** | Flyingfishes | Small pelagics (<30 cm) | Other fishes & inverts | 3.57 |
| 242 | 100.0 | 0 | `Tenualosa toli` | species | Toli shad | Medium pelagics (30 - 89 cm) | Herring-likes |  |
| 243 | 100.0 | 0 | `Sphyrnidae` | **family** | Hammer, bonnet, scoophead sharks | Large sharks (>=90 cm) | Sharks & rays |  |
| 244 | 100.0 | 0 | `Trochus niloticus` | species | Commercial top | Other demersal invertebrates | Molluscs |  |
| 245 | 100.0 | 0 | `Sphyraena barracuda` | species | Great barracuda | Large pelagics (>=90 cm) | Perch-likes |  |
| 246 | 100.0 | 0 | `Seriola` | genus | Amberjacks | Large benthopelagics (>=90 cm) | Perch-likes |  |
| 247 | 100.0 | 0 | `Sphyrna` | genus | Hammerhead sharks | Large sharks (>=90 cm) | Sharks & rays |  |

## Where the difficulty is

68 of 247 labels sit above genus and together carry **95,185,513 tonnes (62.6 % of the catch)**.
Leaving these unresolved is what caps coverage near 78 %. Read `references/coarse-taxa-playbook.md` before deciding any of them.

The ten largest:

- `Nemipteridae` — 14,865,557 t (9.8 %), SAU: Small demersals (<30 cm) / Perch-likes
- `Synodontidae` — 12,027,858 t (7.9 %), SAU: Medium demersals (30 - 89 cm) / Other fishes & inverts
- `Leiognathidae` — 10,490,185 t (6.9 %), SAU: Small benthopelagics (<30 cm) / Perch-likes
- `Carangidae` — 8,571,169 t (5.6 %), SAU: Medium pelagics (30 - 89 cm) / Perch-likes
- `Marine fishes not identified` — 7,914,679 t (5.2 %), SAU: Medium demersals (30 - 89 cm) / Other fishes & inverts
- `Engraulidae` — 6,360,940 t (4.2 %), SAU: Small pelagics (<30 cm) / Anchovies
- `Sciaenidae` — 6,300,173 t (4.1 %), SAU: Medium demersals (30 - 89 cm) / Perch-likes
- `Platycephalidae` — 4,759,039 t (3.1 %), SAU: Medium demersals (30 - 89 cm) / Scorpionfishes
- `Loliginidae` — 4,426,594 t (2.9 %), SAU: Cephalopods / Other fishes & inverts
- `Scombridae` — 3,199,377 t (2.1 %), SAU: Medium pelagics (30 - 89 cm) / Perch-likes
