# Northern Humboldt Current, 1995–1998 static baseline

Source axis: taxonomy, plankton size classes, fish feeding guilds, and hake size stages. No spatial prefixes.

Domain: 4–16°S, extending 111 km offshore, with a reported area of 165,000 km². Biomass uses wet-weight densities. Regionwide catch extrapolation is a separate applicability assumption.

Exact source nodes are 1–41. The operational stock representation uses 1–39, with 33 feeding consumers (3–35) and two producers (1–2). Source prose lists 36 living groups, including Anchovy eggs 36, and three detritus pools (37–39). Tables encode eggs 36 as a nonfeeding routing pool. Fleet nodes 40 and 41 remain separate Artisanal and Commercial fisheries evidence. The operational detritus convention includes 36–39 and is explicitly recorded.

The hake species inherited from Tam et al. (2008) is Merluccius gayi peruanus: small <29 cm, medium 30–49 cm, and large >50 cm. Printed gaps and the unspecified length convention remain unresolved. These are separately tabulated static groups; no native multistanza links, transition ages, growth curve, or stanza equations were recovered. Inherited plankton size classes are 20–200 µm, 200–2000 µm, and 2–20 mm.

Single taxa include Chrysaora plocamia, Sardinops sagax, Engraulis ringens, Dosidicus gigas, Trachurus murphyi, Scomber japonicus, Prionotus stephanophrys, Galeichtys peruvianus, Chelonia mydas, and Dermochelys coriacea. Historical source spellings are retained. Lists marked “e.g.” are representative examples; donor parameter analogues were not promoted to local group members.

All stocks 1–35 have B/PB/EE, and all 33 consumers have QB/AE/PQ. Source TL, BA, habitat fraction, migration, and external detritus import are unavailable. BA=0 and other conventions appear only in the explicit computational input; raw imports remain blank. Positive catches and real zero rows survive in GROUP_CATCH_BIOMASS.csv. Large hake has zero landings but positive discards.

Fleet discards go entirely to Offal 37 in Table C. The simplified calculator input retains donor removals but cannot preserve internal discard-return ancestry. The runtime loader also replaces eight native detritus-fate cells with self-identity routing and omits the Export destination. These translation losses are explicit; scientific production adoption remains ineligible.
