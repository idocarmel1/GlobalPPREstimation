"""ppr-npp: satellite net primary production aggregated to Sea Around Us regions.

Produces, for a chosen year, annual NPP for every Large Marine Ecosystem, high-seas area
and EEZ, from five independent ocean-colour algorithms, with a switchable gap-fill so the
annual total covers the whole year rather than only the months a satellite happened to
see. Built as the denominator for primary-production-required (PPR) work.

Quick start (see README.md):

    npp regions
    npp fetch
    npp baseline --year 2019
    npp ensemble --year 2019
    npp overlap
    npp workbook

Or programmatically:

    from npp.config import Config
    from npp.aggregate import run_baseline
    from npp.report import baseline_table

    cfg = Config.load("config.yaml", year=2019)
    table = baseline_table(cfg, run_baseline(cfg))
"""

__version__ = "1.0.0"

from .config import LAYERS, MODEL_LABELS, MODELS, Config  # noqa: F401
