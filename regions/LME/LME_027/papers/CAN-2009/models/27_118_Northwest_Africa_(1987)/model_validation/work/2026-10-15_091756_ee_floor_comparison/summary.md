# LME_027 EE-floor diagnostic comparison

The specific concern of excessive living-compartment recycling still holds with
EE floor 0.1 and selection threshold 0.1. TE rho_living is 0.9907169786465047
both OFF and ON, and TE remains WARN. It converges mathematically (<1), but
remains close to divergence and above both the default 0.7 warning threshold
and the signed report's stated 0.9 concern.

| Method | OFF status | ON status | OFF rho_living | ON rho_living |
|---|---|---|---:|---:|
| GE | WARN | OK | 0.16615874785448084 | 0.16615874785448084 |
| TE | WARN | WARN | 0.9907169786465047 | 0.9907169786465047 |
| With Egestion | WARN | OK | 0.13292699828358467 | 0.13292699828358467 |

The returned TE A[13,13] equals the dominant living-network eigenvalue in both
cases. Group 13 (Mesopelagic predators) consumes itself at diet fraction 0.016;
its pre-floor EE is 0.117029533, exceeding the strict selection threshold 0.1.
Its self-loop therefore stays unchanged. The numerical concern persists, but
attributing the dominant loop solely to the EE<0.1 compartments is unsupported.

Coastal tunas (17) no longer triggers the near-zero TE warning. However,
previously zero-EE groups now have nonzero TE; five remain below the diagnostic
TE threshold 0.001: Seabirds (11), Killer whales (9), Sperm whales (8), Beaked
whales (7) and Sei whales (5). Maximum total group TE SPPR rises from about
2.774 million (Mesopelagic predators) to 85.413 million (Beaked whales).
These are group coefficients, not regional catch-weighted totals.

All six SPPR matrices are finite and have no negative contributions. The floor
affects 15 groups, records 10.828832010005804 model flow units as hypothetical
external nonfishery mortality export, and introduces no negative detritus stock
residual. The strict source model balance flag remains false in both cases.
The TE SPPR balance flag changes from false to true; its relative budget gap
falls from 2.1399011940631314e-5 to 7.664274280832692e-6. Budget improvement
does not remove the near-divergent living loop.

The archived loader reproduces the retained completed runtime within 1e-12.
The OFF matrices reproduce historical matrices within the recorded 1e-10
tolerance. Both cases use the same audited initialization, diet normalization,
detritus options and current calculation engine; only the floor Boolean changes.
Threshold and floor are explicitly 0.1. Canonical inputs, living biological
flows and catch remain protected. Full returns, ordered matrices, nonfinite
masks, source-scope coefficients and provenance are adjacent in outputs/.

The original signed review and all protected existing files remain byte-identical.
The registered disqualification, regional workbooks, saved results and map were
not changed. This run creates diagnostic evidence only and supplies no renewed
researcher approval. No extraction, mapping, regional arithmetic or Monte Carlo
was performed.

Reproduction: run code/compare.py from the repository (or with an available
scientific Python), then code/finalize.py and the project's evidence checker.
The archived loader temporarily requires a period-bearing filename; its input
is a byte-identical canonical copy removed immediately after parsing.

- [Comparison values and warnings](outputs/comparison.json)
- [Independent matrix verification](qa/independent_matrix_verification.json)
- [Reconciliation checks](qa/reconciliation.json)
- [Original signed review, preserved](../../validation.docx)
- [Portable evidence inventory](evidence_index.json)
