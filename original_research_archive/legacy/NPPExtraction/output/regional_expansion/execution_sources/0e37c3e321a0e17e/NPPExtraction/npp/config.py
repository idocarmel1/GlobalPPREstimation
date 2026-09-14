"""Run configuration: one YAML file drives every stage."""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

LAYERS = ("lme", "highseas", "eez")
MODELS = ("antoinemorel", "vgpm", "eppley", "cbpm", "cafe")

MODEL_LABELS = {
    "antoinemorel": "Antoine-Morel",
    "vgpm": "VGPM",
    "eppley": "Eppley-VGPM",
    "cbpm": "CbPM2",
    "cafe": "CAFE",
}


@dataclass
class FillConfig:
    """How to complete the year where the satellite returned nothing.

    Stages are applied in order and each only sees pixel-months the previous ones could
    not supply. Turning them all off reproduces a plain sum over observed months, which
    is what most published regional NPP numbers actually are.
    """

    #: Treat a pixel-month with no sunrise as a real zero rather than a gap.
    dark_is_zero: bool = True
    #: Fill from the pixel's own monthly mean over ``climatology_years``.
    use_climatology: bool = True
    #: Years pooled for that climatology. ``null`` means "the window minus the target year".
    climatology_years: list[int] | None = None
    #: Rescale the climatology fill by the region-month ratio of target year to climatology.
    anomaly_rescale: bool = True
    #: Clamp on that ratio, so a poorly sampled region cannot produce a wild fill.
    anomaly_clip: tuple[float, float] = (0.5, 2.0)
    #: Fill from the nearest pixel that has a value, scaled by TOA insolation ratio.
    use_nearest_neighbour: bool = True
    #: Distance splitting a trustworthy near fill from a pack-ice far fill, km.
    nn_split_km: float = 200.0
    #: Include the far (pack-ice) fills in the headline number. Off: they are an upper bound.
    nn_far_in_central: bool = False
    #: Longitude columns wrapped on each side before the distance transform.
    nn_wrap_pad: int = 240
    #: Ceiling applied to any filled value, mg C m-2 d-1 (the product's own valid_max).
    value_max: float = 10000.0

    def central_categories(self) -> list[str]:
        cats = ["obs"]
        if self.dark_is_zero:
            cats.append("dark")
        if self.use_climatology:
            cats.append("clim")
        if self.use_nearest_neighbour:
            cats.append("nn_near")
            if self.nn_far_in_central:
                cats.append("nn_far")
        return cats


@dataclass
class EnsembleConfig:
    models: list[str] = field(default_factory=lambda: list(MODELS))
    #: Grid the cross-model comparison runs on. Must be reachable from every model's native grid.
    grid: str = "12th"
    #: Model the ratios are taken against, and the model whose gap-filled total is the baseline.
    reference_model: str = "antoinemorel"
    #: Below this common-mask share of a region's water area, fall back to own-coverage ratios.
    min_common_mask_pct: float = 5.0


@dataclass
class BenthicConfig:
    """Optional and OFF by default. Nothing in the main outputs depends on it."""

    enabled: bool = False
    #: Global NPP (Pg C/yr), global area (M km2), allocation key, latitude weights and the
    #: fraction with a route into metazoan food webs. See METHODS.md for every citation.
    habitats: dict[str, dict[str, Any]] = field(default_factory=dict)
    #: Gross reef production, Pg C/yr, reported for context only -- net community production
    #: is near zero so it must not be added to a denominator.
    coral_reef_gross_pgc: float = 0.70
    tropical_lat: float = 23.5
    temperate_lat: float = 60.0


@dataclass
class Config:
    year: int = 2019
    #: Years read for the water mask and the fill climatology (must contain ``year``).
    window_years: list[int] = field(default_factory=lambda: [2017, 2018, 2019, 2020, 2021])
    layers: list[str] = field(default_factory=lambda: list(LAYERS))
    baseline_grid: str = "4km"
    raw_dir: Path = Path("data/raw")
    work_dir: Path = Path("data/work")
    out_dir: Path = Path("data/out")
    fill: FillConfig = field(default_factory=FillConfig)
    ensemble: EnsembleConfig = field(default_factory=EnsembleConfig)
    benthic: BenthicConfig = field(default_factory=BenthicConfig)
    #: Also fetch each region's published Sea Around Us primary-production value.
    fetch_sau_reference: bool = True
    http_timeout_s: int = 180
    http_retries: int = 4

    # ---------------------------------------------------------------- loading
    @classmethod
    def load(cls, path: str | Path | None = None, **overrides) -> "Config":
        raw: dict[str, Any] = {}
        if path is not None:
            raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        raw.update({k: v for k, v in overrides.items() if v is not None})
        if "year" in raw and "window_years" not in raw:
            raw["window_years"] = list(range(raw["year"] - 2, raw["year"] + 3))
        sub = {
            "fill": FillConfig(**(raw.pop("fill", None) or {})),
            "ensemble": EnsembleConfig(**(raw.pop("ensemble", None) or {})),
            "benthic": BenthicConfig(**(raw.pop("benthic", None) or {})),
        }
        for key in ("raw_dir", "work_dir", "out_dir"):
            if key in raw:
                raw[key] = Path(raw[key])
        known = {f.name for f in dataclasses.fields(cls)}
        unknown = set(raw) - known
        if unknown:
            raise ValueError(f"unknown config keys: {sorted(unknown)}")
        cfg = cls(**{**raw, **sub})
        cfg.validate()
        return cfg

    def validate(self) -> None:
        bad = set(self.layers) - set(LAYERS)
        if bad:
            raise ValueError(f"unknown layers {sorted(bad)}; known: {list(LAYERS)}")
        bad = set(self.ensemble.models) - set(MODELS)
        if bad:
            raise ValueError(f"unknown models {sorted(bad)}; known: {list(MODELS)}")
        if self.year not in self.window_years:
            raise ValueError(f"window_years {self.window_years} must contain year {self.year}")
        if self.ensemble.reference_model not in self.ensemble.models:
            raise ValueError("ensemble.reference_model must be one of ensemble.models")

    # ---------------------------------------------------------------- paths
    def donor_years(self) -> list[int]:
        """Years pooled for the fill climatology."""
        if self.fill.climatology_years is not None:
            return [y for y in self.fill.climatology_years if y != self.year]
        return [y for y in self.window_years if y != self.year]

    def ensure_dirs(self) -> None:
        for d in (self.raw_dir, self.work_dir, self.out_dir):
            Path(d).mkdir(parents=True, exist_ok=True)

    def coverage_path(self, layer: str, grid: str) -> Path:
        return Path(self.work_dir) / f"coverage_{layer}_{grid}.npz"

    def watermask_path(self) -> Path:
        years = "-".join(str(y) for y in sorted(self.window_years))
        return Path(self.work_dir) / f"watermask_{self.ensemble.reference_model}_{self.baseline_grid}_{years}.npy"

    def cache_key(self) -> str:
        """Invalidate computed results whenever settings, source files or code change."""
        import hashlib
        import json
        payload = self.as_dict()
        for key in ("work_dir", "out_dir", "http_timeout_s", "http_retries"):
            payload.pop(key, None)
        payload["code"] = {
            str(p.relative_to(Path(__file__).parent)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(__file__).parent.rglob("*.py"))
        }
        payload["geometries"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in sorted(Path(self.raw_dir).glob("*.geojson"))}
        source_years = set(self.window_years) | set(self.donor_years()) | {self.year}
        payload["inputs"] = [(str(p.relative_to(self.raw_dir)), p.stat().st_size, p.stat().st_mtime_ns)
                             for p in sorted(Path(self.raw_dir).rglob("*"))
                             if p.is_file() and p.suffix not in (".part", ".hdf")
                             and (p.suffix == ".geojson" or any(str(y) in p.name for y in source_years))]
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]

    def geojson_path(self, layer: str) -> Path:
        return Path(self.raw_dir) / f"sau_{layer}.geojson"

    def sau_reference_path(self, layer: str) -> Path:
        return Path(self.raw_dir) / f"sau_{layer}_metrics.csv"

    def as_dict(self) -> dict[str, Any]:
        def enc(o):
            if dataclasses.is_dataclass(o):
                return {k: enc(v) for k, v in dataclasses.asdict(o).items()}
            if isinstance(o, Path):
                return str(o)
            if isinstance(o, (list, tuple)):
                return [enc(x) for x in o]
            if isinstance(o, dict):
                return {k: enc(v) for k, v in o.items()}
            return o

        return enc(self)
