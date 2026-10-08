# Size-split catch allocation: evidence reviewed 2026-09-29

The user asked whether all catch could be assigned to the large/adult group, and specifically asked to investigate fishing methods and mesh sizes. No new size allocation has been adopted from this exploratory question.

## Findings

- Gear affects catch size, but does not establish an all-adult rule. Gillnet mesh size selects a size range; trawl mesh affects retention. Selection also depends on fish morphology, gear operation and encounter/availability. FAO: https://www.fao.org/4/x7788e/X7788E03.htm and https://www.fao.org/4/Y3427E/y3427e04.htm
- For eastern Pacific bigeye, IATTC describes longlines targeting large fish and floating-object purse seines targeting small fish. The latter replaced longlines as the dominant bigeye fishery since 1996 in the cited historical account. This contradicts a blanket large-only assignment for HS_077: https://iattc.org/GetAttachment/6aff9a86-590c-4f24-b13b-a929eb4065df/IATTC-100-01
- HS_077's selected Olson and Watters model separates yellowfin at 90 cm and bigeye at 80 cm. These model size definitions must be matched explicitly; the word adult is not a substitute for the model cutoff. Table 1a, printed p.152: https://www.iattc.org/GetAttachment/e121271c-ffc6-4fbd-9451-b95b6cd5163b/Vol-22-No-3-2003-OLSON%2C-ROBERT-J-%2C-and-GEORGE-W-WATTERS_A-model-of-the-pelagic-ecosystem-in-the-eastern-tropical-Pacific-Ocean.pdf
- IATTC reports length-frequency sampling and catch-size distributions by gear, purse-seine set type and area; the 2023 fishery report includes 2018–2023 distributions: https://iattc.org/GetAttachment/5f3054db-560e-4b4a-b417-456226a275e0/IATTC-102-01
- Public IATTC downloads provide catch by species/gear/year, purse-seine catch with spatial/set-type detail, and longline catch with spatial detail. These are a route to investigating fleet mixture, not sufficient on their own to establish stage weights for the HS_077 polygon: https://www.iattc.org/en-us/Data/Public-domain

## Proposed allocation rule (not yet implemented)

Prefer catch-size composition for the taxon, region, year and gear. For a threshold L*, compute the large-group catch-mass fraction f = sum(n_l * mean_weight_l for l > L*) / sum(n_l * mean_weight_l). Representative sampling and fleet expansion weights are needed; sample counts alone are not total catch composition. Match the paper's exact boundary convention before use.

The taxon coefficient is f * SPPR_large + (1-f) * SPPR_small. If landings and discards have different size distributions, estimate each separately before summing total catch. Do not transfer one year's or fleet's fraction across all years/regions without a recorded assumption and uncertainty analysis.

An all-large assignment (f=1) can be a clearly labeled sensitivity scenario, or an approximation supported by the relevant catch-size evidence. It should not silently become the default mapping. Coverage gained by assumed size allocation should remain distinguishable from coverage with supported allocations. The all-large scenario is not automatically an upper PPR bound: the actual two coefficients determine direction, and failed signed SPPR outputs have no validated ecological interpretation.
