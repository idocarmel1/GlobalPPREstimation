## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for Chilean Patagonia, EE tolerance 0.05.

**Verdict: INDETERMINATE** - 0 error(s), 1 indeterminate, 1 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 15 of 15 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.090, group 12 (Skates).

Groups with recomputed EE > 1: none.

P/Q outside 0.02-0.5: 14 (Sea lions, 0.014).

BA: not stated for any group. Every EE below is recomputed without a BA term, as a diagnostic with unreported terms omitted. It is not a bound because BA may be positive or negative.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Indeterminate (BA unknown)

- group 12 (Skates): printed EE 0.09 vs recomputed 0.000 (diff 0.090) with BA unknown - a BA of +0.0009855 t/km^2/year (+0.09 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed

### Warnings

- group 14 (Sea lions): P/Q = 0.014 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 13 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 2 (Microzooplankton), 3 (Mesozooplankton), 4 (Macrozooplankton), 5 (Benthos), 6 (Small pelagic fish), 7 (Other demersal fish), 8 (Hoki (j)), 9 (Hoki (a)) ...
- detritus pools (1): inflow ~1.948e+04, consumption ~419.2 t/km^2/year, implied EE ~0.022 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Phytoplankton | 146.2 | 137 | - | 0.05 | 0.052 | - | 0 | unknown |
| 2 | Microzooplankton | 0.67 | 534 | 1476 | 0.95 | 0.95 | 0.362 | 0 | unknown |
| 3 | Mesozooplankton | 7.271 | 14.6 | 40.15 | 0.95 | 0.95 | 0.364 | 0 | unknown |
| 4 | Macrozooplankton | 8.331 | 5.48 | 17.52 | 0.95 | 0.95 | 0.313 | 0 | unknown |
| 5 | Benthos | 11.64 | 2.7 | 36 | 0.24 | 0.239 | 0.075 | 0 | unknown |
| 6 | Small pelagic fish | 8.427 | 1.15 | 10 | 0.95 | 0.95 | 0.115 | 0 | unknown |
| 7 | Other demersal fish | 0.774 | 0.7 | 3.5 | 0.95 | 0.95 | 0.2 | 0 | unknown |
| 8 | Hoki (j) | 2.927 | 1.2 | 6.24 | 0.81 | 0.808 | 0.192 | 0.006 | unknown |
| 9 | Hoki (a) | 2.722 | 0.7 | 3.11 | 0.04 | 0.0388 | 0.225 | 0.056 | unknown |
| 10 | Southern blue whiting | 1.4 | 0.42 | 3.6 | 0.91 | 0.908 | 0.117 | 0.011 | unknown |
| 11 | Kingklip | 0.197 | 0.39 | 1.4 | 0.21 | 0.206 | 0.279 | 0.013 | unknown |
| 12 | Skates | 0.073 | 0.15 | 1.24 | 0.09 | 0 | 0.121 | 0 | unknown |
| 13 | Southern hake | 3.14 | 0.19 | 0.68 | 0.66 | 0.661 | 0.279 | 0.125 | unknown |
| 14 | Sea lions | 0.035 | 0.2 | 14.36 | 0 | 0 | 0.0139 | 0 | unknown |
| 15 | Detritus | - | - | - | 0.02 | - | - | 0 | unknown |


### Source-fidelity and completeness limits

These findings were recomputed from the final, unnormalized JSON. Known-flow EE checks omit unknown catch/BA/migration. The checker uses GS=0.2 internally for missing GS in respiration/detritus diagnostics only; the JSON retains -9999. Unstated detritus routing prevents pool-specific validation.

Diet columns outside +/-0.01: none.

The physiological check derives P/B divided by Q/B; any differently rounded stated P/Q is preserved separately in ge and Basic_input.csv.
