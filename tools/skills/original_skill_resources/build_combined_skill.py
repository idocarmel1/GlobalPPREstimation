"""Build equivalent Claude and Codex distributions of the three PPR skills.

Edit shared domain resources in claude/ecopath-extraction and
claude/ewe-species-to-group-mapper, the combined router in combined-src,
and Codex entry points/UI metadata in codex-src. Everything else is derived.

    python skills/build_combined_skill.py
    python skills/build_combined_skill.py --check

--check compares every distributed file and archive without writing anything.
"""
from __future__ import annotations

import argparse
import io
from pathlib import Path
import zipfile

SKILLS = Path(__file__).resolve().parent
NAMES = ("ecopath-extraction", "ewe-species-to-group-mapper", "ecopath-paper-to-ppr")
EXCLUDE_DIRS = {"__pycache__", ".pytest_cache"}
EXCLUDE_NAMES = {".DS_Store"}


def read_tree(folder: Path) -> dict[str, bytes]:
    """Read portable files, ignoring runtime caches and Excel lock files."""
    return {p.relative_to(folder).as_posix(): p.read_bytes()
            for p in sorted(folder.rglob("*")) if p.is_file()
            and not any(part in EXCLUDE_DIRS for part in p.relative_to(folder).parts)
            and p.name not in EXCLUDE_NAMES and not p.name.startswith("~$")}


def strip_front_matter(content: bytes) -> bytes:
    text = content.decode("utf-8").replace("\r\n", "\n")
    if text.startswith("---\n"):
        _, _, text = text[4:].partition("\n---\n")
    return text.lstrip("\n").encode("utf-8")


def distributions() -> dict[tuple[str, str], dict[str, bytes]]:
    """Assemble in memory so verification cannot rewrite the source tree."""
    result = {}
    for name in NAMES[:2]:
        source = read_tree(SKILLS / "claude" / name)
        if "SKILL.md" not in source:
            raise ValueError(f"missing Claude source: {name}/SKILL.md")
        if any(p.startswith("agents/") or p == "artifact-template.json" for p in source):
            raise ValueError(f"move Codex metadata from claude/{name} to codex-src/{name}")
        result["claude", name] = source

    combined = read_tree(SKILLS / "combined-src")
    if "SKILL.md" not in combined:
        raise ValueError("missing combined-src/SKILL.md")
    for name, workflow in zip(NAMES[:2], ("extraction", "mapping")):
        source = result["claude", name]
        body = strip_front_matter(source["SKILL.md"])
        if workflow == "mapping":
            body = body.replace(b"references/output-format.md", b"references/mapping-output-format.md")
        combined[f"references/{workflow}.md"] = body
        for relative, content in source.items():
            if relative == "SKILL.md":
                continue
            target = ("references/mapping-output-format.md"
                      if relative == "references/output-format.md" else relative)
            if target in combined and combined[target] != content:
                raise ValueError(f"combined resource collision: {target}")
            combined[target] = content
    result["claude", NAMES[2]] = combined

    for name in NAMES:
        source = result["claude", name]
        codex = dict(source)
        codex["references/workflow.md"] = strip_front_matter(source["SKILL.md"])
        overlay = read_tree(SKILLS / "codex-src" / name)
        if "SKILL.md" not in overlay or "agents/openai.yaml" not in overlay:
            raise ValueError(f"missing Codex entry point or metadata: {name}")
        for relative, content in overlay.items():
            if relative not in {"SKILL.md", "artifact-template.json"} and not relative.startswith("agents/"):
                raise ValueError(f"domain resources belong in Claude sources, not codex-src: {name}/{relative}")
            codex[relative] = content
        result["codex", name] = codex
    return result


def archive_bytes(name: str, files: dict[str, bytes]) -> bytes:
    """Stable metadata makes archives reproducible, independent of file mtimes."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative, content in sorted(files.items()):
            info = zipfile.ZipInfo(f"{name}/{relative}", date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
    return buffer.getvalue()


def sync_tree(folder: Path, expected: dict[str, bytes]) -> None:
    # Resolve before cleanup so a Windows junction cannot redirect it elsewhere.
    allowed = {(SKILLS / agent / name).absolute() for agent in ("claude", "codex") for name in NAMES}
    target = folder.resolve()
    if target not in allowed or not target.is_relative_to(SKILLS):
        raise ValueError(f"refusing to synchronize outside a named skill directory: {target}")
    actual = read_tree(target)
    for relative in sorted(actual.keys() - expected.keys()):
        path = (target / relative).resolve()
        if not path.is_relative_to(target):
            raise ValueError(f"refusing to remove a file outside {target}")
        path.unlink()
    for relative, content in expected.items():
        path = (target / relative).resolve()
        if not path.is_relative_to(target):
            raise ValueError(f"refusing to write a file outside {target}")
        if actual.get(relative) != content:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check trees and packages; write nothing")
    args = parser.parse_args()
    try:
        expected = distributions()
    except ValueError as error:
        print(f"Skills out of date: {error}")
        return 1
    differences = []
    for agent in ("claude", "codex"):
        folder = SKILLS / agent
        names = {p.name for p in folder.iterdir() if p.is_dir() and (p / "SKILL.md").exists()}
        for extra in sorted(names - set(NAMES)):
            differences.append(f"unexpected skill: {agent}/{extra}")
    for (agent, name), files in expected.items():
        folder = SKILLS / agent / name
        package = folder.with_suffix(".skill")
        packed = archive_bytes(name, files)
        if args.check:
            actual = read_tree(folder)
            for relative in sorted(actual.keys() | files.keys()):
                if actual.get(relative) != files.get(relative):
                    differences.append(f"{agent}/{name}/{relative}")
            if not package.exists() or package.read_bytes() != packed:
                differences.append(f"{agent}/{name}.skill")
        else:
            sync_tree(folder, files)
            if not package.exists() or package.read_bytes() != packed:
                package.write_bytes(packed)
            print(f"built {agent}/{name}: {len(files)} files + .skill archive")
    if differences:
        print("Skills out of date; run python skills/build_combined_skill.py")
        for difference in differences:
            print(f"  {difference}")
        return 1
    print("Claude and Codex: all 3 skills, shared resources and 6 packages match their sources.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
