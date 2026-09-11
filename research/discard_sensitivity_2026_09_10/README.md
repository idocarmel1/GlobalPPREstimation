# Discard routing and primary production required

This study tests how allocating a fraction of each source model's existing catch
to different discard routes changes its SPPR coefficients. It is an isolated
experiment, followed by the separately authorized landings-only atlas integration.

The frozen source set contains 197 files (46,166,147 bytes). Every file's size and
SHA-256 were verified before copying. `input_manifest.json` records the original
source paths and revision; `verification/input_hashes.json` records the initial
check. Its manifest-file checksum is historical; `verification/summary.json`
records the current manifest checksum. All 197 frozen input bytes still match
the current manifest. Scoped Git attributes preserve their exact line endings,
and four manifested converter logs are deliberately exempt from the log ignore rule.
The `inputs/` tree is immutable. Experimental engine changes belong exclusively
in `src/experimental_engine/` and will not replace the live calculator.

The controlling specification is `EXECUTION_PLAN.md`. Original native catch H is
fixed. Designated discards are D=fH and retained landings are L=(1-f)H, using
f=0, .01, .05, .10, .20, .30, .40, .50, .75 and 1. The last two fractions are stress
tests. Primary comparisons multiply perturbed coefficients by the same H. A
separate retained-catch evaluation uses L, exposing the direct boundary change
and its interaction with the coefficient response.

Source evidence, numerical conservation, numerical convergence and ecological
plausibility are distinct. Unsupported or invalid scenarios retain their reasons.
Scenario ranges are sensitivity envelopes, not confidence intervals. Native
model units and any optional fixed-2019 regional application remain separate.

Execution responsibilities: the numerical agent owns baseline reproduction,
explicit routing ledgers, private engine adapters and paired scenarios; the source
review agent owns primary-publication evidence and model inventory; the primary
agent owns the standalone report, independent checks, reporting protocol and
coordinated atlas integration. The existing NPP agent continues extraction and
will coordinate the final canonical-data refresh before shared exports run.

The numerical study and source review are complete: 3,936 scenario records,
85,960 group coefficient rows and 59 passing saved-baseline comparisons. Start
with [report.html](report.html), [METHODS_AND_FINDINGS.md](METHODS_AND_FINDINGS.md),
[NUMERICAL_NOTES.md](NUMERICAL_NOTES.md) and the [source audit](results/source_evidence.md).
The report embeds its data and scripts; CSV/JSON downloads require no remote service.
Its renderer, script syntax and actual-data runtime checks passed. Direct local-file
navigation was blocked by the embedded browser security policy, so visual browser
verification is explicitly not claimed; see `verification/report_data.json`.

## Reproduce the study

From this directory, using Python 3.13 (tested with 3.13.9):

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-verified.txt
.venv/Scripts/python -X utf8 src/external_audit.py
.venv/Scripts/python -X utf8 src/run_study.py
.venv/Scripts/python -X utf8 src/uncertainty.py
.venv/Scripts/python -X utf8 -m pytest tests -q
.venv/Scripts/python -X utf8 src/render_report.py
```

On other operating systems use `.venv/bin/python`. The existing verified versions
are pinned in `requirements-verified.txt`; no production calculator export is run.
The UTF-8 switch is required for the frozen legacy loader on Windows, including
French group names and the Unicode checkout path. Public group labels are checked
by immutable group sequence against the verified source workbook; original loaded
labels remain in provenance.
The source audit retains primary PDF pages and supplement cell transcriptions so
its conclusions can be checked without rerunning an extraction. All numerical
inputs required by these commands are in the immutable `inputs/` tree.

The standalone study is separate from production exports. The latter consume its
versioned group responses and the current annual data, preserving their source
hashes. [INTEGRATION_PROPOSAL.md](INTEGRATION_PROPOSAL.md) defines catch-basis controls,
compatible sensitivity bands and the coordinated final NPP rebuild.
