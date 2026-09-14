"""OPTIONAL: benthic and macrophyte production, which no ocean-colour algorithm sees.

**This module is off by default and nothing in the main outputs depends on it.** It is a
first-order scoping estimate, not a measurement. Per-region values should be read as
within roughly a factor of two; the global totals are far better constrained than their
distribution across regions.

Ocean colour measures phytoplankton in the water column. It does not see the kelp,
seagrass, salt marsh, mangrove or benthic diatoms growing on the seabed underneath. On
broad sunlit shelves that production is not marginal: on this estimate it adds a quarter
to the pelagic total in the Gulf of Thailand and about a fifth in the South China Sea,
North Australian Shelf and East China Sea. It adds ~9% across the LME system as a whole.

What is in, with sources
    macroalgae         1.32 Pg C/yr over 6.06-7.22 M km2. Duarte et al. 2022,
                       Glob Ecol Biogeogr, doi 10.1111/geb.13515. A NICHE MODEL of where
                       macroalgae could grow given seafloor light and substrate, not an
                       observed extent -- and it is three quarters of the benthic total,
                       so it is the dominant uncertainty here. Areal rates from
                       Pessarrodona et al. 2022, Sci Adv, doi 10.1126/sciadv.abn2465
                       (656 gC/m2/yr subtidal, 1711 intertidal, >400 in-situ sites).
    microphytobenthos  ~0.42 (0.30-0.60) Pg C/yr. Cahoon 1999 review; photic shelf
                       fraction 33% of shelf area from Gattuso et al. 2006, Biogeosciences,
                       doi 10.5194/bg-3-489-2006. NO GLOBAL MAP EXISTS. Weakest link.
    mangrove           218 +/- 72 Tg C/yr. Bouillon et al. 2008, Glob Biogeochem Cycles,
                       doi 10.1029/2007gb003052. Area 0.147 M km2 from Global Mangrove
                       Watch v3, Bunting et al. 2022, doi 10.3390/rs14153657 -- the only
                       one of the five with an observed, annually updated global extent.
    seagrass           ~0.064 (0.045-0.110) Pg C/yr. Area 160 387 km2, possibly 266 562,
                       McKenzie et al. 2020, Environ Res Lett, doi 10.1088/1748-9326/ab7d06;
                       rate ~400 gC/m2/yr, Duarte & Chiscano 1999.
    salt marsh         ~0.066 (0.045-0.120) Pg C/yr. Area 54 951 km2, Mcowen et al. 2017,
                       Biodivers Data J, doi 10.3897/BDJ.5.e11764 -- 43 countries only; the
                       authors flag missing Canada, northern Russia, South America, Africa.

What is deliberately OUT
    coral reefs        Gross production is enormous (~0.7 Pg C/yr) but NET community
                       production is close to zero (Gattuso et al. 1998): almost all of it
                       is recycled inside the reef and never leaves. Adding it to a
                       denominator would be counting energy that does not go anywhere. The
                       gross figure is reported in its own column for context only.
    terrestrial carbon Rivers deliver ~0.9 Pg C/yr to the ocean, but ~70% of the
                       particulate organic fraction is remineralised in estuaries and
                       isotopic tracers find very little terrestrial carbon in marine
                       consumers (Bianchi 2011, PNAS, doi 10.1073/pnas.1017982108). It is a
                       local subsidy in river-plume systems, not a term in a global
                       denominator. Mangrove outwelling is already inside the estimate above.

Allocation, and why it is only first order
    Global habitat totals are distributed across LMEs by shelf area (macroalgae,
    microphytobenthos), inshore fishing area (mangrove, seagrass, salt marsh) or Sea
    Around Us's own coral share, each scaled by a LIGHT INDEX: annual mean top-of-
    atmosphere insolation at that latitude over the global ocean mean, times the ice-free
    lit fraction of the year taken from the pipeline's own retrieval coverage. Without
    that scaling, raw shelf area puts implausible kelp forests on ice-covered Arctic
    shelves -- the first version of this calculation gave the Canadian High Arctic 191% of
    its pelagic NPP. The rigorous replacement is to overlay the actual habitat rasters
    (Global Mangrove Watch, UNEP-WCMC seagrass and salt marsh, the Duarte et al. layer)
    on the same grid, which turns a factor-of-two guess into a measured area times a rate.

Trophic availability
    The five sources are not interchangeable currency. Duarte & Cebrian (1996, Limnol
    Oceanogr, doi 10.4319/lo.1996.41.8.1758) compiled the fate of NPP by autotroph type:
    herbivory takes >40% of microalgal production and 33.6 +/- 4.9% of macroalgal, but
    much less of the vascular plants, whose production is disproportionately buried.
    ``availability`` is the fraction with a plausible route into a metazoan food web.
    NOTE that classical PPR (Pauly & Christensen 1995) uses UNWEIGHTED total NPP as its
    denominator, so adding an availability-weighted benthic term to an unweighted pelagic
    one mixes two conventions. Both columns are provided; pick one.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .config import Config
from .grids import get_grid
from .log import log
from .regions import Coverage
from .solar import monthly_tables

#: habitat -> parameters. ``key`` is the allocation variable, ``lat_weights`` are
#: (tropical, temperate, polar) multipliers, ``light`` says whether the light index applies.
DEFAULT_HABITATS: dict[str, dict] = {
    "macroalgae": dict(npp_pgc=1.32, low=1.00, high=1.80, area_mkm2=6.64,
                       key="shelf", lat_weights=(0.8, 1.0, 1.0), light="linear",
                       lme_share=0.85, availability=0.50),
    "microphytobenthos": dict(npp_pgc=0.42, low=0.30, high=0.60, area_mkm2=8.35,
                              key="shelf", lat_weights=(1.0, 1.0, 1.0), light="linear",
                              lme_share=0.85, availability=0.60),
    "mangrove": dict(npp_pgc=0.218, low=0.146, high=0.290, area_mkm2=0.147,
                     key="ifa", lat_weights=(1.0, 0.0, 0.0), subtropical=0.3, light=None,
                     lme_share=0.75, availability=0.30),
    "seagrass": dict(npp_pgc=0.064, low=0.045, high=0.110, area_mkm2=0.160,
                     key="ifa", lat_weights=(1.2, 1.0, 0.1), light="linear",
                     lme_share=0.70, availability=0.25),
    "saltmarsh": dict(npp_pgc=0.066, low=0.045, high=0.120, area_mkm2=0.055,
                      key="ifa", lat_weights=(0.2, 1.0, 0.5), light="sqrt",
                      lme_share=0.90, availability=0.15),
}


def light_index(cfg: Config, baseline: pd.DataFrame) -> pd.DataFrame:
    """Relative light reaching the seafloor, per LME: insolation ratio x ice-free fraction."""
    grid = get_grid(cfg.baseline_grid)
    q_toa, _ = monthly_tables(cfg.year, grid.ny)
    q_annual = q_toa.mean(axis=0)
    area_row = grid.area_row()
    watermask = np.load(cfg.watermask_path()).ravel()
    cov = Coverage(cfg.coverage_path("lme", cfg.baseline_grid), grid)
    w = cov.cov * area_row[grid.row_of(cov.cid)] * watermask[cov.cid]
    aw = cov.sum_by_region(w)
    qbar = cov.sum_by_region(w * q_annual[grid.row_of(cov.cid)]) / np.maximum(aw, 1.0)
    lat = np.abs(90.0 - (grid.row_of(cov.cid) + 0.5) * grid.dlat)
    abs_lat = cov.sum_by_region(w * lat) / np.maximum(aw, 1.0)
    ocean = watermask.reshape(grid.ny, grid.nx)
    q_global = float((q_annual[:, None] * area_row[:, None] * ocean).sum()
                     / (area_row[:, None] * ocean).sum())
    lme = baseline[baseline.layer == "lme"].set_index("region_id")
    obs_pct = lme.area_obs_pct.reindex(cov.region_id).to_numpy()
    return pd.DataFrame({
        "region_id": cov.region_id,
        "abs_lat": abs_lat,
        "q_ratio": qbar / q_global,
        "ice_free_fraction": obs_pct / 100.0,
        "light_index": (qbar / q_global) * (obs_pct / 100.0),
    })


def run_benthic(cfg: Config, baseline: pd.DataFrame) -> Path:
    """Distribute the literature habitat totals across LMEs. LMEs only, by construction."""
    if not cfg.benthic.enabled:
        raise RuntimeError("benthic.enabled is false in the config; nothing to do")
    habitats = cfg.benthic.habitats or DEFAULT_HABITATS
    sau = cfg.sau_reference_path("lme")
    if not sau.exists():
        raise FileNotFoundError(
            f"benthic needs {sau} for shelf area, inshore fishing area and coral share; "
            "run `npp regions --sau-reference`")
    ref = pd.read_csv(sau).drop(columns=["title"], errors="ignore")
    li = light_index(cfg, baseline)
    lme = baseline[baseline.layer == "lme"][["region_id", "title", "water_area_km2",
                                             "npp_central_tC_yr"]]
    d = lme.merge(ref, on="region_id", how="left").merge(li, on="region_id", how="left")
    d["shelf"] = d.sau_shelf_km2.fillna(0.0)
    d["ifa"] = d.sau_ifa_km2.fillna(0.0)

    trop, temp = cfg.benthic.tropical_lat, cfg.benthic.temperate_lat
    lat = d.abs_lat.to_numpy()
    L = d.light_index.to_numpy()
    names = list(habitats)
    for name in names:
        p = habitats[name]
        w = np.where(lat < trop, p["lat_weights"][0],
                     np.where(lat < temp, p["lat_weights"][1], p["lat_weights"][2]))
        if "subtropical" in p:
            w = np.where((lat >= trop) & (lat < 30.0), p["subtropical"], w)
        key = d[p["key"]].to_numpy() * w
        if p.get("light") == "linear":
            key = key * L
        elif p.get("light") == "sqrt":
            key = key * np.sqrt(np.maximum(L, 0.0))
        share = key / key.sum() if key.sum() > 0 else np.zeros_like(key)
        for tag, field in (("", "npp_pgc"), ("_low", "low"), ("_high", "high")):
            d[f"{name}{tag}_tC"] = share * p[field] * p["lme_share"] * 1e15 / 1e6
        d[f"{name}_available_tC"] = d[f"{name}_tC"] * p["availability"]

    d["benthic_tC"] = d[[f"{n}_tC" for n in names]].sum(axis=1)
    d["benthic_low_tC"] = d[[f"{n}_low_tC" for n in names]].sum(axis=1)
    d["benthic_high_tC"] = d[[f"{n}_high_tC" for n in names]].sum(axis=1)
    d["benthic_available_tC"] = d[[f"{n}_available_tC" for n in names]].sum(axis=1)
    d["coral_reef_gross_tC"] = (d.sau_coral_pct_world.fillna(0) / 100.0
                                * cfg.benthic.coral_reef_gross_pgc * 1e15 / 1e6)
    for col, num in (("pct_of_pelagic", "benthic_tC"), ("pct_of_pelagic_low", "benthic_low_tC"),
                     ("pct_of_pelagic_high", "benthic_high_tC"),
                     ("pct_available_of_pelagic", "benthic_available_tC"),
                     ("coral_gross_pct_of_pelagic", "coral_reef_gross_tC")):
        d[col] = 100 * d[num] / d.npp_central_tC_yr
    d["dominant_habitat"] = d[[f"{n}_tC" for n in names]].idxmax(axis=1).str.replace("_tC", "", regex=False)

    out = Path(cfg.out_dir) / f"benthic_{cfg.year}_by_LME_firstorder.csv"
    Path(cfg.out_dir).mkdir(parents=True, exist_ok=True)
    d.sort_values("pct_of_pelagic", ascending=False).to_csv(out, index=False)
    log(f"benthic: -> {out}")
    log(f"benthic: {d.benthic_tC.sum()/1e9:.2f} Pg C/yr over the LME system "
        f"({100*d.benthic_tC.sum()/d.npp_central_tC_yr.sum():.1f}% of pelagic; "
        f"availability-weighted {100*d.benthic_available_tC.sum()/d.npp_central_tC_yr.sum():.1f}%)")
    return out
