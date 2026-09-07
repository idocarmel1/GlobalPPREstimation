"""Regenerate SPPR workbooks for named models, without touching the rest.

Do not run `PPREstimation/create_PPRS_excel.py` from a shell. Its `__main__` block ignores
the command line entirely -- `raise SystemExit(main())` is commented out, and the block
above it hardcodes

    json_dir = real_models/global_cover_jsons
    out_dir  = output/top10

so *any* invocation, with any arguments, regenerates all sixteen models over the committed
outputs. `python create_PPRS_excel.py --help` does it too. That has already cost this
project two accidental overwrites.

This wrapper calls `run_directory()` directly with explicit paths, stages only the model
JSONs asked for, and refuses to write into `PPREstimation/output/top10` unless told to in
so many words.

    python tools/run_sppr.py --models 35_412_Gulf_of_Thailande_(1963) --out <dir>
    python tools/run_sppr.py --models 52_1_Sea_of_Okhotsk_NE_(1980) --json-dir <patched>
    python tools/run_sppr.py --models ... --in-place      # overwrite output/top10

Regenerating is not free of consequence: the Monte-Carlo methods draw samples, so
`MC_new_GE` and `MC_new_TE_EEfix` will not reproduce exactly. Compare before replacing
anything, which is what `--compare` is for.
"""
from __future__ import annotations

import argparse
import math
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PPREST = ROOT / "PPREstimation"
JSON_DIR = PPREST / "real_models" / "global_cover_jsons"
LIVE_OUT = PPREST / "output" / "top10"


def compare(old: Path, new: Path) -> int:
    """Report where a regenerated workbook differs from the committed one."""
    import openpyxl

    def sppr(p):
        wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
        if "sppr_all" not in wb.sheetnames:
            wb.close()
            return None, {}
        rows = list(wb["sppr_all"].iter_rows(values_only=True))
        wb.close()
        methods = [str(h) for h in rows[0][2:]]
        return methods, {str(r[1]): list(r[2:]) for r in rows[1:] if len(r) > 1 and r[1]}

    ma, a = sppr(old)
    mb, b = sppr(new)
    if ma != mb:
        print(f"  method lists differ: {set(ma or []) ^ set(mb or [])}")
        return 1
    worst = {}
    for g in sorted(set(a) & set(b)):
        for i, m in enumerate(ma):
            x, y = a[g][i], b[g][i]
            if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                continue
            if math.isnan(x) or math.isnan(y):
                continue
            denom = max(abs(x), abs(y), 1e-12)
            rel = abs(x - y) / denom
            if rel > worst.get(m, (0.0, ""))[0]:
                worst[m] = (rel, g)
    changed = {m: v for m, v in worst.items() if v[0] > 1e-9}
    print(f"  groups compared: {len(set(a) & set(b))}")
    if not changed:
        print("  identical to the committed workbook across every method")
        return 0
    print(f"  {len(changed)} of {len(ma)} methods differ:")
    for m, (rel, g) in sorted(changed.items(), key=lambda kv: -kv[1][0]):
        note = "  (Monte Carlo, expected)" if m.startswith("MC_") else ""
        print(f"      {m:<26} max relative change {rel:.3e}  worst group {g!r}{note}")
    return 0


def main() -> int:
    # The unchanged algorithm loader uses locale-default open(). Windows cp1255
    # silently corrupts group names such as ≤. Enable UTF-8 in this interpreter
    # and every worker before importing the algorithm or loading model JSON.
    os.environ['PYTHONUTF8'] = '1'
    if not sys.flags.utf8_mode:
        return subprocess.run([sys.executable, '-X', 'utf8', str(Path(__file__).resolve()),
                               *sys.argv[1:]], env=os.environ.copy()).returncode
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", nargs="+", required=True,
                    help="model stems, e.g. 35_412_Gulf_of_Thailande_(1963)")
    ap.add_argument("--json-dir", type=Path, default=JSON_DIR,
                    help="where the model JSONs live (default: the committed ones)")
    ap.add_argument("--out", type=Path, help="directory to write workbooks into")
    ap.add_argument("--in-place", action="store_true",
                    help="write into PPREstimation/output/top10, replacing what is there")
    ap.add_argument("--compare", action="store_true",
                    help="report differences against the committed workbook afterwards")
    ap.add_argument("--timeout", type=float, default=None,
                    help="per-method wall-clock budget in seconds")
    a = ap.parse_args()

    if a.in_place and a.out:
        raise SystemExit("--in-place and --out are mutually exclusive")
    out = LIVE_OUT if a.in_place else a.out
    if out is None:
        raise SystemExit("pass --out DIR, or --in-place to overwrite the committed workbooks")
    out = Path(out).resolve()
    if out == LIVE_OUT.resolve() and not a.in_place:
        raise SystemExit("refusing to write into output/top10 without --in-place")

    missing = [m for m in a.models if not (a.json_dir / f"{m}.json").exists()]
    if missing:
        raise SystemExit(f"no JSON for {missing} under {a.json_dir}")

    sys.path.insert(0, str(PPREST))
    import create_PPRS_excel as cpe  # noqa: E402

    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        staged = Path(tmp) / "jsons"
        staged.mkdir()
        for m in a.models:
            shutil.copy2(a.json_dir / f"{m}.json", staged / f"{m}.json")
        print(f"regenerating {len(a.models)} model(s) into {out}")
        kwargs = {} if a.timeout is None else {"method_timeout": a.timeout}
        summary = cpe.run_directory(json_dir=str(staged), out_dir=str(out), silent=False,
                                    **kwargs)
    print(f"wrote {summary['n_written']}/{summary['n_models']} workbook(s)")
    if summary.get("n_timeout"):
        print(f"{summary['n_timeout']} method run(s) hit the time budget and are empty")
    if summary.get("n_failed"):
        print(f"{summary['n_failed']} model(s) failed -- see {summary.get('report')}")

    if a.compare:
        for m in a.models:
            new, old = out / f"{m}.xlsx", LIVE_OUT / f"{m}.xlsx"
            print(f"\n--- {m}")
            if not old.exists():
                print("  no committed workbook to compare against")
            elif not new.exists():
                print("  nothing was written")
            else:
                compare(old, new)
    return 1 if summary.get('n_failed') or summary['n_written'] != summary['n_models'] else 0


if __name__ == "__main__":
    raise SystemExit(main())
