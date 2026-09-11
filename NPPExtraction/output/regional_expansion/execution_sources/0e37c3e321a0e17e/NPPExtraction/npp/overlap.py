"""How much the three Sea Around Us region systems overlap each other.

**This is the single easiest way to get a wrong answer from these data.** The three
systems are not a partition of the ocean:

* 51.6% of total EEZ area lies inside an LME, and the distribution is strongly bimodal --
  continental EEZs are ~100% inside an LME, oceanic island EEZs are 0%. So "LME totals"
  and "EEZ totals" are largely the same water counted twice.
* 5.3% of high-seas area lies inside an LME. The Arctic Sea high-seas area is 99.99%
  inside the Central Arctic Ocean LME, i.e. almost entirely duplicated.
* 24 of 66 LMEs extend past the EEZ limit into water the high-seas system also claims.

Overlap per cell is taken as ``min(coverage_a, coverage_b) * cell_area``. That is exact
wherever one region nests inside the other within a cell, which is the normal case at 4 km
for regions this large; it is an upper bound on the rare cells where two regions occupy
genuinely different parts of the same cell.

The disjoint alternative is **EEZ + high seas**, which is how Sea Around Us defines the
high seas in the first place (FAO area minus EEZs) and which closes to the global total.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .config import Config
from .grids import get_grid
from .log import log
from .regions import Coverage

SYSTEM_LABEL = {"lme": "LME", "highseas": "HighSeas", "eez": "EEZ"}


def _union_field(cov: Coverage, size: int) -> np.ndarray:
    """Per-cell coverage of the union of every region in a layer, clipped to 1."""
    field = np.zeros(size, dtype="float32")
    np.add.at(field, cov.cid, cov.cov.astype("float32"))
    return np.clip(field, 0.0, 1.0, out=field)


def run_overlap(cfg: Config) -> Path:
    grid = get_grid(cfg.baseline_grid)
    covs, unions = {}, {}
    for layer in cfg.layers:
        path = cfg.coverage_path(layer, cfg.baseline_grid)
        if not path.exists():
            raise FileNotFoundError(f"missing {path}; run `npp regions` first")
        covs[layer] = Coverage(path, grid)
        unions[layer] = _union_field(covs[layer], grid.size)

    rows = []
    for layer, cov in covs.items():
        total = cov.sum_by_region(cov.weight)
        area = grid.cell_area_flat(cov.cid)
        rec = {"total": total}
        for other in cfg.layers:
            if other == layer:
                continue
            shared = np.minimum(cov.cov, unions[other][cov.cid]) * area
            rec[other] = cov.sum_by_region(shared)
        for i in range(cov.n):
            row = {"system": SYSTEM_LABEL[layer], "layer": layer,
                   "region_id": int(cov.region_id[i]), "title": cov.title[i],
                   "area_km2": total[i] / 1e6}
            for other in cfg.layers:
                col = f"pct_also_in_{other}"
                row[col] = (100 * rec[other][i] / total[i]) if other != layer and total[i] > 0 else np.nan
                row[f"km2_also_in_{other}"] = rec[other][i] / 1e6 if other != layer else np.nan
            rows.append(row)
    df = pd.DataFrame(rows)
    out = Path(cfg.out_dir) / "region_system_overlap.csv"
    Path(cfg.out_dir).mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    for layer in cfg.layers:
        s = df[df.layer == layer]
        for other in cfg.layers:
            if other == layer:
                continue
            tot = s.area_km2.sum()
            sh = s[f"km2_also_in_{other}"].sum()
            log(f"overlap: {100*sh/tot:5.1f}% of {SYSTEM_LABEL[layer]} area also in {SYSTEM_LABEL[other]}")
    log(f"overlap: -> {out}")
    return out
