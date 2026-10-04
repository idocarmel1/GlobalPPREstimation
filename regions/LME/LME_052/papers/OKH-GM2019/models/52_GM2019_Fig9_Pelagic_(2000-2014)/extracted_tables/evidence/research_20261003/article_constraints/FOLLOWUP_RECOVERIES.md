# Bounded recovery of salmon and jellyfish consumption

These are independently recovered supporting-source targets. No Figure 9 arrow was added, rescaled or reassigned, and no model parameter was fitted. The original dissertation tables on pp.124–125 and 169 were visually checked. Exact page text, scope and calculations are saved in `followup_original_page_text.json`, `followup_salmon_recovery.json` and `followup_jellyfish_recovery.json`.

## Salmon: a period-matched independent target exists

Dissertation Table 4.52, printed/PDF p.169, reports mean **2000–2014** whole-Sea salmon food consumption **1837.0 thousand wet tonnes/year** and stock **758.0 thousand tonnes**. Species Q values are pink 1273.2, chum 453.34, sockeye 70.4, Chinook 5.6, coho 20.8 and masu 13.7 thousand tonnes/year. Their summed Q is 1837.04, a source-rounding discrepancy of 0.04 thousand tonnes.

The 2019 article p.155 and dissertation p.318 explicitly attribute tierIII salmon production to **pink+chum+sockeye**. This supports a species-based aggregate Q **1796.94 thousand wet tonnes/year** and matching dissertation stock **740.2 thousand tonnes**. Their Q/B is **2.427641178/year**; using the 2019 Table 3 stock 800 kt instead gives **2.246175/year**. These are labelled derivations from independent source Q, not Figure 9 outputs.

Chinook+coho+masu yield Q **40.1 kt/year**, B **17.8 kt** and Q/B **2.252808989/year**. Matching them to the Figure 9 predatory-salmon group is plausible from nekton-feeding and the approximately 20 kt group stock, but remains a crosswalk interpretation. Using the 2019 stock 20 kt gives 2.005/year. Do not assign total salmon Q 1837 kt to the tierIII group or invent a proportional split.

These consumption calculations already cover the **period of presence in the Okhotsk Sea**: dissertation p.163 says so explicitly. Pink-salmon Table 4.43 p.164 uses summer **2 months** and autumn **3 months**. The seasonal stock construction is not a time-weighted year-round mean: p.318 sums summer 483.2 kt and autumn 272.4 kt as 755.6 kt. Do not extrapolate residence consumption to 365 days or claim the seasonal sums are annual steady-state stock estimates.

The source supplies species-specific prey masses, but includes pteropods, decapods, appendicularians, gelatinous organisms, squid and unspecified fish. Several lack exact Figure 9 nodes or prey conversion factors; squid/fish require group allocation. Thus no exact complete carbon Q for Figure 9 salmon can be recovered without further assumptions. Consumer factor 8.2 cannot convert total prey wet Q. The recovered Q can test the existing reconstruction; replacing its Q/B while preserving its diet fractions would rescale the source arrows and is not authorized by this recovery.

## Jellyfish: useful food composition, different scope

Dissertation Tables 4.15 and 4.16, printed/PDF p.125, report **2006–2014** whole-Sea feeding by large>20 mm and small<20 mm jellyfish. Large Q is **772.7 kt/year** (prose p.124:772.8); small Q is **2404.4 kt/year**; combined Q is **3177.1 kt/year**. Small-jellyfish estimates are explicitly mainly expert calculations because feeding is insufficiently studied (pp.124–125).

The directly linked stock Table 4.13 p.124 gives seasonal large B 1022,2539,1618,1329 kt and small B 1185,11230,555,912 kt. Equal-quarter averaging yields large 1627 kt, small 3470.5 kt, combined **5097.5 kt**, and combined Q/B **0.623266307/year**. This differs from 2019 Table 3 jellyfish B **4100 kt**, PB 10/year and P **41000 kt/year**. A mixed-scope 3177.1/4100=.774902439/year is computable but is not a source-aligned Ecopath parameter. No matching annual production for the two 2006–2014 feeding subsets was recovered. Dissertation Table 3.9 p.88 also differs internally in small-jellyfish stocks; the feeding-linked Table 4.13 is preserved separately.

The broad biological aggregate overlaps the 2019 jellyfish group, but the period and stock do **not** match exactly. The 2019 article provides no independent jellyfish annual Q beyond its displayed flows. Retain the dissertation values as alternate targets.

The feeding tables allow independent partial carbon conversion using matched prey factors, without rescaling Figure 9:

| Prey | Combined wet Q, kt/year | Wet/carbon factor | Carbon Q, million tC/year |
|---|---:|---:|---:|
| Copepods |2477.3|14|.17695|
| Euphausiids |332.2|10.6|.031339622642|
| Chaetognaths |25.9|20|.001295|

These three prey alone supply **at least.209584622642 million tC/year**. Full carbon Q remains unknown because other prey lack exact factor/group matches. Compared illustratively with 2019 P=.144, these known prey alone give R=.8 Q−P **≥+.023667698113 million tC/year**. Even the source calculation's 70% assimilation yields a positive partial residual of+.002709235849. This mixed-period comparison demonstrates why the existing Figure 9 jellyfish failure does not establish a universal physiological impossibility. It does not validate a period-matched model.

Dissertation pp.120 and 123 explicitly use **70% assimilation** to calculate jellyfish rations via an energy balance; this is a methodological assumption, not an independent assimilation measurement. It is retained as source context; the user-default GS=.2 variant is unchanged. The prey composition contains major copepod and euphausiid flows absent from the adopted Figure 9 jellyfish diet. Importing those feeding flows would therefore create a distinct supporting-source network, not repair the original missing-arrow-zero reconstruction while preserving its numbers.

## Microbial inputs remain unresolved

No independent separate whole-Sea 2000–2014 annual bacterial or protozoan B/PB was recovered. Dissertation pp.59–60 gives local summer bacterial stocks and PB.2–.9 adjacent to daily production; section 8.1 pp.313–314 discusses seasonal-production assumptions and Table 8.2 p.316 retains the pooled B 64.0 million/PB 20 row. These do not identify annual separate stocks. Converting the local daily rates to annual values would require unreported seasonality and spatial averaging. The earlier factor 9.4 recovery stands; it does not solve the missing microbial B/PB split.

All original evidence remains unchanged. The bounded recovery does not adopt new source targets into any existing model.
