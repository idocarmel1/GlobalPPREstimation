"""Assemble `ecopath-paper-to-ppr` from the two skills it combines, then package it.

The combined skill is *derived*, never edited in place. Its extraction workflow is
`ecopath-extraction/SKILL.md` with its front matter stripped; its mapping workflow is
`ewe-species-to-group-mapper/SKILL.md` the same way; the scripts and references are copied
from both. Only the router and the taxonomy stage are hand-written, and those live in
`skills/combined-src/`.

Forking the two would have been quicker and would have rotted within a month: a fix to the
mapping playbook would land in one copy and not the other, and nothing would notice. Here,
`python skills/build_combined_skill.py` regenerates the combination and the packages, and a
divergence shows up as a diff.

    python skills/build_combined_skill.py            # assemble and package all three
    python skills/build_combined_skill.py --check    # fail if the tree is out of date
"""
from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
import zipfile
from pathlib import Path

SKILLS = Path(__file__).resolve().parent
EXTRACTION = SKILLS / "ecopath-extraction"
MAPPER = SKILLS / "ewe-species-to-group-mapper"
SRC = SKILLS / "combined-src"
OUT = SKILLS / "ecopath-paper-to-ppr"

# Excluded from every package. `artifact-template.json` and `agents/` are packaging
# scaffolding for other hosts that a Claude skill never reads; they stay in the source
# tree for the later GPT adaptation.
EXCLUDE_NAMES = {"artifact-template.json", ".DS_Store"}
EXCLUDE_DIRS = {"agents", "__pycache__", ".pytest_cache"}


def strip_front_matter(text: str) -> str:
    """Drop the YAML front matter. A reference file must not carry a second skill header."""
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    return text[end + 4:].lstrip("\n") if end != -1 else text


def copy_tree(src: Path, dest: Path, rename=None) -> list:
    """Copy every included file under `src` into `dest`. Returns the relative names."""
    written = []
    for p in sorted(src.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(src)
        if any(part in EXCLUDE_DIRS for part in rel.parts) or p.name in EXCLUDE_NAMES:
            continue
        if p.name.startswith("~$"):
            continue
        newrel = rename(rel) if rename else rel
        if newrel is None:          # the renamer drops this file from the combination
            continue
        target = dest / newrel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
        written.append(target.relative_to(dest).as_posix())
    return written


def assemble(out: Path) -> list:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    notes = []

    # the hand-written parts: router SKILL.md, the taxonomy stage, write_taxonomy.py
    copy_tree(SRC, out)

    # the two workflows, demoted to references
    (out / "references").mkdir(exist_ok=True)
    (out / "references" / "extraction.md").write_text(
        strip_front_matter((EXTRACTION / "SKILL.md").read_text(encoding="utf-8")),
        encoding="utf-8")
    mapping = strip_front_matter((MAPPER / "SKILL.md").read_text(encoding="utf-8"))
    # The mapper's own paths do not survive the move: its scripts sit at the combined
    # skill's top level, its output-format reference is renamed to avoid reading as
    # extraction's `output-formats.md`, and its examples are not carried over.
    for old, new in [
        ("skills/ewe-species-to-group-mapper/scripts/", "scripts/"),
        ("references/output-format.md", "references/mapping-output-format.md"),
        ("`examples/`", "`skills/ewe-species-to-group-mapper/examples/`"),
        ("skills/ewe-species-to-group-mapper`", "the mapper skill`"),
    ]:
        mapping = mapping.replace(old, new)
    (out / "references" / "mapping.md").write_text(mapping, encoding="utf-8")
    notes.append("workflows: extraction.md + mapping.md, front matter stripped")

    # extraction's references, scripts and templates, unchanged
    def ext_rename(rel: Path):
        if rel.parts[0] == "SKILL.md" or rel.as_posix() == "SKILL.md":
            return None
        return rel
    copy_tree(EXTRACTION, out, rename=ext_rename)

    # the mapper's references and scripts. `output-format.md` would collide with
    # extraction's `output-formats.md` in a reader's mind, so it is renamed on the way in
    # and the router refers to it by the new name.
    def map_rename(rel: Path):
        if rel.as_posix() == "SKILL.md":
            return None
        if rel.as_posix().startswith("examples/") or rel.as_posix().startswith("assets/"):
            return None
        if rel.as_posix() == "references/output-format.md":
            return Path("references/mapping-output-format.md")
        return rel
    copy_tree(MAPPER, out, rename=map_rename)

    files = sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file())
    return files


def package(src_dir: Path, dest: Path) -> int:
    files = []
    for p in sorted(src_dir.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(src_dir)
        if any(part in EXCLUDE_DIRS for part in rel.parts) or p.name in EXCLUDE_NAMES:
            continue
        if p.name.startswith("~$"):
            continue
        files.append(p)
    dest.unlink(missing_ok=True)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in files:
            zf.write(p, (Path(src_dir.name) / p.relative_to(src_dir)).as_posix())
    return len(files)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="fail if the assembled tree differs from what the sources imply")
    a = ap.parse_args()

    for d in (EXTRACTION, MAPPER, SRC):
        if not d.is_dir():
            raise SystemExit(f"missing source directory {d}")

    if a.check:
        tmp = SKILLS / "_check_ecopath-paper-to-ppr"
        assemble(tmp)
        match, mismatch, errors = filecmp.cmpfiles(
            tmp, OUT, [p.relative_to(tmp).as_posix() for p in tmp.rglob("*") if p.is_file()],
            shallow=False)
        stale = sorted(mismatch + errors)
        extra = sorted({p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file()}
                       - {p.relative_to(tmp).as_posix() for p in tmp.rglob("*") if p.is_file()})
        shutil.rmtree(tmp)
        if stale or extra:
            print("ecopath-paper-to-ppr is out of date; run this script without --check")
            for f in stale:
                print(f"  differs : {f}")
            for f in extra:
                print(f"  orphan  : {f}")
            return 1
        print(f"ecopath-paper-to-ppr matches its sources ({len(match)} files)")
        return 0

    files = assemble(OUT)
    print(f"assembled {OUT.name}/ from {EXTRACTION.name}/ + {MAPPER.name}/ + {SRC.name}/")
    for f in files:
        print("   ", f)

    for d in (OUT, MAPPER, EXTRACTION):
        n = package(d, SKILLS / f"{d.name}.skill")
        print(f"packaged {d.name}.skill  ({n} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
