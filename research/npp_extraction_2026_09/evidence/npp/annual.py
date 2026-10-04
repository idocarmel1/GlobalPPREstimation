"""Archive/catch-year extraction. Run ``python -m npp.annual --help``.

Canonical numbers use the supplied gap-filled baseline and coverage-matched ratios.
Only complete source years are processed; no target-year extrapolation is performed.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import json
import math
import re
import shutil
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin, urlencode
import xml.etree.ElementTree as ET

from .config import Config, MODELS, EnsembleConfig
from .http import download, get_json, get_text
from .sources import copernicus, osu

METHOD = "gap-filled Antoine-Morel baseline; common-mask model ratios, own-coverage fallback"
PREFIXES = {"lme": "LME", "eez": "EEZ", "highseas": "HS"}
FIELDS = ["unit_id", "year"] + [f"npp_{m}_tC_yr" for m in MODELS] + [
    "ens_median_tC_yr", "ens_min_tC_yr", "ens_max_tC_yr", "status", "reason", "provenance",
    "n_models", "available_models", "ensemble_basis", "method", "window_years", "config_key",
    "model_status", "water_area_km2"]
OSU_PAGES = {
    "vgpm": "2160.by.4320.monthly.hdf.vgpm.m.chl.m.sst.php",
    "eppley": "2160.by.4320.monthly.hdf.eppley.m.chl.m.sst.php",
    "cbpm": "2160.by.4320.monthly.hdf.cbpm2.m.php",
    "cafe": "2160.by.4320.monthly.hdf.cafe.m.php",
}


def atomic_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".part")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    tmp.replace(path)


def archive_grid(root: Path, missing: list | None = None) -> list[tuple[str, int]]:
    rows = []
    missing = missing if missing is not None else []
    for p in sorted((Path(root) / "PPRAtlas/archive/regions").iterdir()):
        if not p.is_dir() or not re.fullmatch(r"(?:LME|EEZ|HS)_\d+", p.name):
            continue
        catch = Path(root) / "SeaAroundUsExtraction/data/catch_by_taxon_year" / (p.name + ".csv.gz")
        if not catch.exists():
            missing.append({"unit_id": p.name, "status": "no_catch", "reason": "catch file absent"})
            continue
        years = set()
        with gzip.open(catch, "rt", encoding="utf-8-sig", newline="") as fh:
            for rec in csv.DictReader(fh):
                if rec["unit_id"] != p.name:
                    raise ValueError(f"catch identity mismatch in {catch}: {rec['unit_id']}")
                years.add(int(rec["year"]))
        if not years:
            missing.append({"unit_id": p.name, "status": "no_catch", "reason": "catch file has no rows"})
        rows.extend((p.name, y) for y in sorted(years))
    return rows


def full_years(months):
    return sorted(int(y) for y, mm in months.items() if {int(m) for m in mm} == set(range(1, 13)))


def bounded_window(year, years, radius=2):
    if year not in years:
        raise ValueError(f"no complete reference source year {year}")
    return [y for y in years if year - radius <= y <= year + radius]


def parse_osu_links(html, page_url):
    months = {}
    matches = re.findall(r'''href\s*=\s*["']([^"']+\.hdf\.gz)["']''', html, flags=re.I)
    for href in matches:
        match = re.search(r"\.([12]\d{3})(\d{3})\.hdf\.gz$", href)
        if match:
            y, doy = map(int, match.groups())
            day = dt.date(y, 1, 1) + dt.timedelta(days=doy - 1)
            if day.day == 1 and day.year == y:
                months.setdefault(str(y), {})[str(day.month)] = urljoin(page_url, href)
    return months


def discover_sources(out: Path, timeout=60, retries=2):
    """Discover every listed monthly file, recording errors separately from no coverage."""
    catalog = {m: {} for m in MODELS}
    meta = {"retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(), "errors": {}}
    try:
        product_url = f"{copernicus.STAC_ROOT}/{copernicus.PRODUCT_ID}/product.stac.json"
        product = get_json(product_url, timeout, retries)
        link = next(l for l in product["links"] if copernicus.DATASET_PREFIX in l.get("href", ""))
        dataset_url = urljoin(product_url, link["href"])
        ds = get_json(dataset_url, timeout, retries)
        root = ds["assets"]["native"]["href"].split("?")[0].rstrip("/")
        bucket, _, key = root.partition("/native/")
        prefix = "native/" + key + "/"
        token = None
        meta["copernicus"] = {"stac": dataset_url, "native_root": root, "bytes": {}}
        while True:
            query = {"list-type": 2, "prefix": prefix, "max-keys": 1000}
            if token:
                query["continuation-token"] = token
            xml = ET.fromstring(get_text(bucket + "?" + urlencode(query), timeout, retries))
            for entry in xml.findall("{*}Contents"):
                k = entry.findtext("{*}Key")
                match = re.match(r"(\d{4})(\d{2})\d{2}-\d{8}_" + re.escape(copernicus.DATASET_PREFIX) + r"\.nc$", k.rsplit("/", 1)[-1])
                if match:
                    y, m = match.groups()
                    catalog["antoinemorel"].setdefault(y, {})[str(int(m))] = bucket + "/" + k
                    meta["copernicus"]["bytes"][k.rsplit("/", 1)[-1]] = int(entry.findtext("{*}Size"))
            token = xml.findtext("{*}NextContinuationToken")
            if not token:
                break
    except Exception as exc:
        meta["errors"]["antoinemorel"] = str(exc)
    for model, page in OSU_PAGES.items():
        page_url = "https://orca.science.oregonstate.edu/" + page
        try:
            html = get_text(page_url, timeout, retries)
            catalog[model] = parse_osu_links(html, page_url)
            if not catalog[model]:
                raise ValueError("source page contained no monthly HDF links")
            meta[model] = {"page": page_url}
        except Exception as exc:
            meta["errors"][model] = str(exc)
    meta["full_years"] = {m: full_years(v) for m, v in catalog.items()}
    atomic_json(out / "source_catalog.json", {"sources": catalog, "metadata": meta})
    return catalog, meta


def number(value):
    try:
        v = float(value)
        return v if math.isfinite(v) else None
    except (ValueError, TypeError):
        return None


def write_annual(path, grid, values, catalog, errors=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".csv.part")
    supported = set(full_years(catalog.get("antoinemorel", {})))
    with tmp.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        for unit, year in grid:
            rec = dict(values.get((unit, year), {}))
            rec.update(unit_id=unit, year=year)
            if not rec.get("status"):
                rec["status"] = "pending" if year in supported else ("source_error" if (errors or {}).get("antoinemorel") else "unsupported")
                rec["reason"] = "complete source year available; not yet extracted" if year in supported else "reference source has no complete twelve-month year"
            vals = []
            models = []
            for m in MODELS:
                field = f"npp_{m}_tC_yr"
                rec[field] = number(rec.get(field))
                if rec[field] is not None:
                    vals.append(rec[field]); models.append(m)
            rec["n_models"] = len(vals)
            rec["available_models"] = ";".join(models)
            for label, fn in (("median", statistics.median), ("min", min), ("max", max)):
                rec[f"ens_{label}_tC_yr"] = fn(vals) if vals else None
            rec.setdefault("method", METHOD)
            writer.writerow(rec)
    tmp.replace(path)


def prepare_regions(root, grid, raw, work):
    from .regions import download_geojson, build_coverage
    from .grids import get_grid
    wanted = {u for u, _ in grid}
    layers = []
    for layer, prefix in PREFIXES.items():
        ids = {int(u.split("_")[1]) for u in wanted if u.startswith(prefix + "_")}
        if not ids:
            continue
        layers.append(layer)
        full = raw / f"sau_{layer}_full.geojson"
        if not full.exists():
            download_geojson(layer, full)
        fc = json.loads(full.read_text(encoding="utf-8"))
        fc["features"] = [f for f in fc["features"] if int(f["properties"]["region_id"]) in ids]
        present = {int(f["properties"]["region_id"]) for f in fc["features"]}
        if present != ids:
            raise ValueError(f"source polygons missing archived {layer} IDs: {sorted(ids-present)}")
        dest = raw / f"sau_{layer}.geojson"
        encoded = json.dumps(fc, sort_keys=True).encode()
        if not dest.exists() or dest.read_bytes() != encoded:
            dest.write_bytes(encoded)
        digest = hashlib.sha256(encoded).hexdigest()[:12]
        for g in ("4km", "12th"):
            cached = work / "coverage" / f"{layer}_{g}_{digest}.npz"
            if not cached.exists():
                build_coverage(dest, get_grid(g), cached)
    return layers


def fetch_year(cfg, catalog, workers, out):
    previous = {}
    for saved in sorted(out.glob("downloads_*.json")):
        for rec in json.loads(saved.read_text(encoding="utf-8")):
            if rec.get("status") == "downloaded":
                previous[Path(rec["path"]).name] = rec
    jobs = []
    for y in sorted(set(cfg.window_years) | set(cfg.donor_years())):
        for month in range(1, 13):
            jobs.append(("antoinemorel", y, month, catalog["antoinemorel"][str(y)][str(month)], copernicus.local_path(cfg.raw_dir, y, month)))
    for model in cfg.ensemble.models:
        if model != "antoinemorel":
            for month in range(1, 13):
                jobs.append((model, cfg.year, month, catalog[model][str(cfg.year)][str(month)], osu.local_path(cfg.raw_dir, model, cfg.year, month)))
    manifest = []
    failures = []
    def one(job):
        model, y, month, url, dest = job
        rec = {"model": model, "year": y, "month": month, "url": url, "path": str(dest)}
        try:
            known = previous.get(dest.name, {})
            reuse = False
            if dest.exists() and known.get("url") == url:
                with dest.open("rb") as fh:
                    reuse = hashlib.file_digest(fh, "sha256").hexdigest() == known.get("sha256")
            download(url, dest, cfg.http_timeout_s, cfg.http_retries, overwrite=not reuse)
            with dest.open("rb") as fh:
                digest = hashlib.file_digest(fh, "sha256").hexdigest()
            rec.update(status="downloaded", bytes=dest.stat().st_size, sha256=digest)
        except Exception as exc:
            rec.update(status="failed", reason=str(exc))
        return rec
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for fut in as_completed([pool.submit(one, j) for j in jobs]):
            rec = fut.result(); manifest.append(rec)
            if rec["status"] == "failed":
                failures.append(rec)
    atomic_json(out / f"downloads_{cfg.year}.json", sorted(manifest, key=lambda r: (r["model"], r["year"], r["month"])))
    if failures:
        raise RuntimeError(f"{len(failures)} monthly downloads failed; see downloads_{cfg.year}.json: {failures[0]['reason']}")
    return manifest


def extract_year(cfg, work_root, output, manifest):
    from .aggregate import run_baseline
    from .ensemble import run_ensemble, scale_to_baseline
    from .report import baseline_table, ensemble_table
    key = completion_key(cfg, manifest)
    cfg.work_dir = work_root / "years" / str(cfg.year) / key
    cfg.out_dir = output / "years" / str(cfg.year) / key
    cfg.ensure_dirs()
    for layer in cfg.layers:
        digest = hashlib.sha256(cfg.geojson_path(layer).read_bytes()).hexdigest()[:12]
        for g in ("4km", "12th"):
            dst = cfg.coverage_path(layer, g)
            if not dst.exists():
                shutil.copyfile(work_root / "coverage" / f"{layer}_{g}_{digest}.npz", dst)
    done = cfg.out_dir / "annual_records.json"
    if done.exists():
        return json.loads(done.read_text(encoding="utf-8"))
    baseline = cfg.work_dir / f"baseline_{cfg.year}_{cfg.baseline_grid}.npz"
    if not baseline.exists():
        baseline = run_baseline(cfg)
    base = baseline_table(cfg, baseline)
    ens_path = cfg.work_dir / f"ensemble_{cfg.year}_{cfg.ensemble.grid}.npz"
    if not ens_path.exists():
        ens_path = run_ensemble(cfg)
    ens = scale_to_baseline(cfg, base, ens_path)
    ensemble_table(cfg, ens)
    records = []
    for row in ens.to_dict("records"):
        unit = f"{PREFIXES[row['layer']]}_{int(row['region_id']):03d}"
        rec = {"unit_id": unit, "year": cfg.year, "ensemble_basis": row["ensemble_basis"],
               "method": METHOD, "window_years": ";".join(map(str, cfg.window_years)), "config_key": key,
               "water_area_km2": number(row["water_area_km2"]),
               "provenance": f"NPPExtraction/output/years/{cfg.year}/{key}/provenance.json"}
        statuses = {}
        for m in MODELS:
            value = number(row.get(f"scaled_{m}_tC_yr"))
            # A region never retrieved by any source is missing, not a measured zero.
            if not rec["water_area_km2"]:
                value = None
            rec[f"npp_{m}_tC_yr"] = value
            statuses[m] = "available" if value is not None else ("unsupported_year" if m not in cfg.ensemble.models else "no_regional_retrieval")
        count = sum(v == "available" for v in statuses.values())
        rec["status"] = "complete" if count == len(MODELS) else ("partial" if count else "missing")
        rec["reason"] = "; ".join(f"{m}: {v}" for m, v in statuses.items() if v != "available")
        rec["model_status"] = json.dumps(statuses, sort_keys=True)
        records.append(rec)
    atomic_json(cfg.out_dir / "provenance.json", {"config": cfg.as_dict(), "method": METHOD,
                "config_key": key, "completed_at": dt.datetime.now(dt.timezone.utc).isoformat(), "downloads": manifest})
    atomic_json(done, records)
    # Expanded HDFs are disposable; retaining every year's copies wastes ~2 GB/year.
    for plain in cfg.work_dir.glob("*.hdf"):
        plain.unlink()
    return records


def completion_key(cfg, manifest):
    payload = {"config": cfg.cache_key(), "sources": sorted((r["url"], r["sha256"]) for r in manifest)}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def complete_year_records(records, grid, year, provenance):
    records = list(records)
    present = {r["unit_id"] for r in records}
    for unit, y in grid:
        if y == year and unit not in present:
            records.append({"unit_id":unit, "year":year, "status":"missing",
                            "reason":"no usable region geometry after repair", "provenance":provenance})
    return records


def snapshot_code(output):
    import zipfile
    files = sorted(Path(__file__).parent.rglob("*.py"))
    hashes = {str(p.relative_to(Path(__file__).parent)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    key = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()[:16]
    dest = output / "reproducibility" / f"code_{key}.zip"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
            for p in files:
                z.write(p, "npp/" + p.relative_to(Path(__file__).parent).as_posix())
    return {"snapshot": f"NPPExtraction/output/reproducibility/{dest.name}", "sha256": hashes}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["plan", "probe", "run"])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--years", help="comma-separated years or inclusive start:end; default every catch year")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--refresh-sources", action="store_true")
    parser.add_argument("--config", type=Path, help="optional scientific configuration; annual bounds remain enforced")
    args = parser.parse_args(argv)
    root = args.root.resolve(); project = root / "NPPExtraction"; output = project / "output"
    output.mkdir(parents=True, exist_ok=True)
    runtime_code = snapshot_code(output)
    catalog_path = output / "source_catalog.json"
    if args.action == "probe" or args.refresh_sources or not catalog_path.exists():
        catalog, meta = discover_sources(output)
    else:
        saved = json.loads(catalog_path.read_text(encoding="utf-8")); catalog, meta = saved["sources"], saved["metadata"]
    print(json.dumps({"source_full_years": meta.get("full_years"), "errors": meta.get("errors")}), flush=True)
    if args.action == "probe":
        return 1 if meta["errors"] else 0
    missing = []
    grid = archive_grid(root, missing=missing)
    atomic_json(output / "archive_without_catch.json", missing)
    selected = sorted({y for _, y in grid})
    if args.years:
        selected = ([int(v) for v in args.years.split(",")] if ":" not in args.years else list(range(int(args.years.split(":")[0]), int(args.years.split(":")[1]) + 1)))
    values = {}
    canonical = output / "annual_npp.csv"
    if canonical.exists():
        with canonical.open(encoding="utf-8", newline="") as fh:
            values = {(r["unit_id"], int(r["year"])): r for r in csv.DictReader(fh) if r["status"] not in ("pending", "unsupported", "source_error")}
    write_annual(canonical, grid, values, catalog, meta["errors"])
    supported = full_years(catalog["antoinemorel"])
    years = [y for y in selected if y in supported]
    plan = {"archive_units": len({u for u, _ in grid}), "catch_year_rows": len(grid), "selected_supported_years": years,
            "unsupported_selected_years": [y for y in selected if y not in supported], "method": METHOD,
            "free_disk_bytes": shutil.disk_usage(project).free}
    atomic_json(output / "run_plan.json", plan); print(json.dumps(plan), flush=True)
    if args.action == "plan":
        return 0
    raw = project / "data/raw"; work = project / "data/work"
    raw.mkdir(parents=True, exist_ok=True); work.mkdir(parents=True, exist_ok=True)
    failures = []
    try:
        layers = prepare_regions(root, grid, raw, work)
    except Exception as exc:
        atomic_json(output / "failed_jobs.json", [{"stage": "regions", "reason": str(exc)}])
        raise
    for year in years:
        try:
            models = [m for m in MODELS if year in full_years(catalog[m])]
            cfg = Config.load(args.config, year=year, window_years=bounded_window(year, supported), layers=layers,
                              raw_dir=raw, work_dir=work, out_dir=output, fetch_sau_reference=False)
            cfg.ensemble.models = models
            if cfg.ensemble.reference_model != "antoinemorel" or cfg.baseline_grid != "4km":
                raise ValueError("annual runner requires the supplied native Antoine-Morel 4km baseline")
            cfg.validate()
            if shutil.disk_usage(project).free < 8 * 1024**3:
                raise RuntimeError("fewer than8GiB free; resume after making space")
            print(f"Extracting {year}: models={models}; window={cfg.window_years}", flush=True)
            manifest = fetch_year(cfg, catalog, args.workers, output)
            records = extract_year(cfg, work, output, manifest)
            provenance = f"NPPExtraction/output/years/{year}/{completion_key(cfg, manifest)}/provenance.json"
            if records:
                provenance = records[0]["provenance"]
                provenance_path = root / provenance
                detail = json.loads(provenance_path.read_text(encoding="utf-8"))
                detail["runtime_code"] = runtime_code
                atomic_json(provenance_path, detail)
            for rec in complete_year_records(records, grid, year, provenance):
                values[(rec["unit_id"], year)] = rec
        except Exception as exc:
            failure = {"year": year, "status": "failed", "reason": str(exc)}
            failures.append(failure)
            for unit, y in grid:
                if y == year:
                    values[(unit, year)] = {**failure, "provenance": f"NPPExtraction/output/downloads_{year}.json"}
            print(f"FAILED {year}: {exc}", flush=True)
        write_annual(canonical, grid, values, catalog, meta["errors"])
        atomic_json(output / "failed_jobs.json", failures)
    return 1 if failures or meta["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
