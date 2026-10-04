## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 27_Canary_Current_999_Independent_adversarial_fixture_(1991), EE tolerance 0.05.

**Verdict: NOT BALANCED** - 3 error(s), 5 indeterminate, 2 warning(s), 3 note(s).

Biomass accumulation is unknown (-9999) for 2 of 5 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 2.200, group 1 (Fish A).

Groups with recomputed EE > 1: 1 (Fish A, 2.700).

P/Q outside 0.02-0.5: none.

BA: carried for 3 group(s) from `Biomass_accumulation.csv`, so the check accounts for it - 1 (Fish A, +1), 2 (Fish B, -2.5), 4 (Det A, +0). The remaining 2 group(s) carry -9999 and are undecided where their EE does not reconcile without BA.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Errors

- group 1 (Fish A): recomputed EE = 2.700 > 1 - catch+BA+predation (2.7) exceeds production (1)
- detritus consumption (5) exceeds detritus inflow (2.7) - the pools cannot balance as extracted
- group 2: complete source diet plus import sum 0.91 is below one

### Indeterminate (BA unknown)

- group 1: diet/import has unknown cells; known subtotal 0.9 is not a complete composition
- group 2: source P/B is missing or nonpositive; native/stanza production cannot be verified
- group 2: unassimilated fraction unknown; indicative checks use a software assumption
- group 4: discard removals unknown; reported catch does not establish complete removals
- group 5: discard removals unknown; reported catch does not establish complete removals

### Warnings

- group 1 (Fish A): printed EE 0.500 vs recomputed 2.700 (diff 2.200), BA 1.0 carried (absolute or derived internally from source BA rate)
- group 3 (Producer): only 1 of B/P-B/Q-B/EE given (P/B) - Ecopath needs three

### Notes

- 1 consumer(s) lack B or Q/B, so predation on their prey is under-counted and every recomputed EE below is a lower bound: 2 (Fish B)
- 1 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Fish A)
- detritus pools (2): inflow ~2.7, consumption ~5 t/km^2/year, implied EE ~1.852 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Fish A | 5 | 0.2 | 2 | 0.5 | 2.7 | 0.1 | 1.7 | 1 |
| 2 | Fish B | 0 | 0 | 0 | - | - | - | 0 | -2.5 |
| 3 | Producer | - | 9 | - | - | - | - | 0 | unknown |
| 4 | Det A | 1 | - | - | - | - | - | 0 | 0 |
| 5 | Det B | - | - | - | - | - | - | 0 | unknown |
