# 52_1_Sea_of_Okhotsk_NE_(1980)

Axis: named stocks/families, residual habitat/feeding pools, and juvenile/adult pollock.
Prefixes: NE identifies the detailed Ecopath model contrasted with the Shuntov-Dulepova SD model; it is not a northeastern geographic stratum. The source does not spell out NE as a formal expansion, so keep the label.
Area: the Sea of Okhotsk, stated area about 1,590,000 km² (Chaikina 2020 p.24); no northeastern-only restriction is stated. This corrects the older handoff interpretation.
Period: 1980s annual-average ecosystem; 29 source groups plus the algorithm import group.
Catch-capable: named fish pools, residual bottom/mesopelagic fish and benthic invertebrate groups; exclude mammals, seabirds, zooplankton, primary producers, detritus and import.
Stocks: Walleye pollock and Juv. pollock are one species split by life stage; Pacific herring, Capelin, Pacific Sardine are common-name stocks. No published age/length split or complete species-membership table is supplied.
Membership: Table 1 group definitions and Table 3 diets. Empty members.csv makes the absence of an explicit species inventory clear.
Source verification: Table 1 group sequence and B/PB/QB values checked against the imported JSON. Diet matrix is rounded in publication; model input has unit diet sums and balances after algorithm processing.
Model health: all input catches are zero. GE and egestion converge; TE fails with living spectral radius >1 and negative source results. Use biomass for pollock stage weights, and retain numerical method flags.
