"""Command line interface.

    npp regions   [--sau-reference]   download polygons and rasterise coverage
    npp fetch     [--source ...]      download the raw monthly product files
    npp watermask                     build the multi-year water mask
    npp baseline                      gap-fill the target year, integrate per region
    npp ensemble                      five-model comparison, scaled onto the baseline
    npp overlap                       quantify overlap between the region systems
    npp benthic                       OPTIONAL benthic estimate (needs benthic.enabled)
    npp workbook                      assemble the Excel deliverable
    npp all                           regions -> fetch -> baseline -> ensemble -> overlap -> workbook

Every command takes ``-c/--config`` and the common overrides ``--year``, ``--layers``,
``--raw-dir``, ``--work-dir``, ``--out-dir``. Stages are resumable: anything already on
disk is reused unless ``--overwrite`` is given.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import log as loglib
from .config import LAYERS, MODELS, Config


def _cache_valid(path: Path, cfg: Config) -> bool:
    marker = path.with_suffix(path.suffix + ".config-key")
    return path.exists() and marker.exists() and marker.read_text(encoding="utf-8") == cfg.cache_key()


def _cache_stamp(path: Path, cfg: Config) -> None:
    path.with_suffix(path.suffix + ".config-key").write_text(cfg.cache_key(), encoding="utf-8")


def _common(p: argparse.ArgumentParser) -> None:
    p.add_argument("-c", "--config", help="YAML config file")
    p.add_argument("--year", type=int, help="target year (overrides config)")
    p.add_argument("--layers", help="comma-separated subset of " + ",".join(LAYERS))
    p.add_argument("--raw-dir")
    p.add_argument("--work-dir")
    p.add_argument("--out-dir")
    p.add_argument("--quiet", action="store_true")


def _config(args) -> Config:
    loglib.set_enabled(not args.quiet)
    overrides = {}
    if args.year:
        overrides["year"] = args.year
        # keep the window centred on the requested year unless the config pins it
        if not args.config:
            overrides["window_years"] = [args.year + d for d in (-2, -1, 0, 1, 2)]
    if args.layers:
        overrides["layers"] = [s.strip() for s in args.layers.split(",") if s.strip()]
    for key, val in (("raw_dir", args.raw_dir), ("work_dir", args.work_dir), ("out_dir", args.out_dir)):
        if val:
            overrides[key] = Path(val)
    return Config.load(args.config, **overrides)


def cmd_regions(args) -> None:
    from .grids import get_grid
    from .regions import build_coverage, download_geojson, download_sau_reference

    cfg = _config(args)
    cfg.ensure_dirs()
    grids = {cfg.baseline_grid, cfg.ensemble.grid}
    for layer in cfg.layers:
        gj = cfg.geojson_path(layer)
        if not gj.exists() or args.overwrite:
            download_geojson(layer, gj, cfg.http_timeout_s, cfg.http_retries)
        for gname in sorted(grids):
            dest = cfg.coverage_path(layer, gname)
            if not dest.exists() or args.overwrite:
                build_coverage(gj, get_grid(gname), dest)
        if (args.sau_reference or cfg.fetch_sau_reference):
            ref = cfg.sau_reference_path(layer)
            if not ref.exists() or args.overwrite:
                download_sau_reference(layer, ref, cfg.http_timeout_s, cfg.http_retries)


def cmd_fetch(args) -> None:
    from .sources import copernicus, osu

    cfg = _config(args)
    cfg.ensure_dirs()
    src = args.source
    if src in ("all", "copernicus"):
        for year in sorted(set(cfg.window_years)):
            copernicus.fetch(cfg.raw_dir, year, cfg.http_timeout_s, cfg.http_retries, args.overwrite)
    if src in ("all", "osu"):
        models = [m for m in cfg.ensemble.models if m in osu.MODELS]
        if models:
            osu.fetch(cfg.raw_dir, cfg.year, models, cfg.http_timeout_s, cfg.http_retries, args.overwrite)


def cmd_watermask(args) -> None:
    from .fill import build_watermask

    cfg = _config(args)
    cfg.ensure_dirs()
    if args.overwrite or not _cache_valid(cfg.watermask_path(), cfg):
        cfg.watermask_path().unlink(missing_ok=True)
    build_watermask(cfg)
    _cache_stamp(cfg.watermask_path(), cfg)


def cmd_baseline(args) -> Config:
    from .aggregate import run_baseline
    from .report import baseline_table

    cfg = _config(args)
    npz = Path(cfg.work_dir) / f"baseline_{cfg.year}_{cfg.baseline_grid}.npz"
    if not _cache_valid(npz, cfg) or args.overwrite:
        cmd_watermask(args)
        npz = run_baseline(cfg)
        _cache_stamp(npz, cfg)
    baseline_table(cfg, npz)
    return cfg


def cmd_ensemble(args) -> None:
    from .ensemble import run_ensemble, scale_to_baseline
    from .report import baseline_table, ensemble_table, summarise

    cfg = _config(args)
    base_npz = Path(cfg.work_dir) / f"baseline_{cfg.year}_{cfg.baseline_grid}.npz"
    if not _cache_valid(base_npz, cfg):
        raise FileNotFoundError(f"missing {base_npz}; run `npp baseline` first")
    base = baseline_table(cfg, base_npz)
    ens_npz = Path(cfg.work_dir) / f"ensemble_{cfg.year}_{cfg.ensemble.grid}.npz"
    if not _cache_valid(ens_npz, cfg) or args.overwrite:
        ens_npz = run_ensemble(cfg)
        _cache_stamp(ens_npz, cfg)
    ens = scale_to_baseline(cfg, base, ens_npz)
    ensemble_table(cfg, ens)
    print(summarise(cfg, base, ens))


def cmd_overlap(args) -> None:
    from .overlap import run_overlap

    run_overlap(_config(args))


def cmd_benthic(args) -> None:
    from .benthic import run_benthic
    from .report import baseline_table

    cfg = _config(args)
    if args.enable:
        cfg.benthic.enabled = True
    base_npz = Path(cfg.work_dir) / f"baseline_{cfg.year}_{cfg.baseline_grid}.npz"
    if not base_npz.exists():
        raise FileNotFoundError(f"missing {base_npz}; run `npp baseline` first")
    run_benthic(cfg, baseline_table(cfg, base_npz))


def cmd_workbook(args) -> None:
    from .workbook import build_workbook

    build_workbook(_config(args))


def cmd_all(args) -> None:
    cmd_regions(args)
    cmd_fetch(args)
    cmd_baseline(args)
    cmd_ensemble(args)
    cmd_overlap(args)
    cfg = _config(args)
    if cfg.benthic.enabled or args.enable:
        cmd_benthic(args)
    cmd_workbook(args)


def cmd_config(args) -> None:
    print(json.dumps(_config(args).as_dict(), indent=2))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="npp", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    specs = [
        ("regions", cmd_regions), ("fetch", cmd_fetch), ("watermask", cmd_watermask),
        ("baseline", cmd_baseline), ("ensemble", cmd_ensemble), ("overlap", cmd_overlap),
        ("benthic", cmd_benthic), ("workbook", cmd_workbook), ("all", cmd_all),
        ("config", cmd_config),
    ]
    for name, fn in specs:
        p = sub.add_parser(name, help=(fn.__doc__ or "").strip().splitlines()[0] if fn.__doc__ else name)
        _common(p)
        p.add_argument("--overwrite", action="store_true", help="recompute even if outputs exist")
        if name in ("fetch", "all"):
            p.add_argument("--source", choices=["all", "copernicus", "osu"], default="all")
        if name in ("regions", "all"):
            p.add_argument("--sau-reference", action="store_true",
                           help="also fetch each region's published SAU metrics")
        if name in ("benthic", "all"):
            p.add_argument("--enable", action="store_true", help="turn the benthic module on for this run")
        p.set_defaults(func=fn)
    args = ap.parse_args(argv)
    for missing, default in (("overwrite", False), ("source", "all"),
                             ("sau_reference", False), ("enable", False)):
        if not hasattr(args, missing):
            setattr(args, missing, default)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
