"""The two agent distributions must ship the same working domain resources."""
from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

import pytest

SKILLS = Path(__file__).resolve().parents[1] / "skills"
NAMES = {"ecopath-extraction", "ecopath-paper-to-ppr", "ewe-species-to-group-mapper"}


def payload(folder):
    return {p.relative_to(folder).as_posix(): p.read_bytes()
            for p in folder.rglob("*") if p.is_file()
            and "__pycache__" not in p.parts and ".pytest_cache" not in p.parts}


def test_both_agents_have_the_complete_skill_set_and_identical_helpers():
    for agent in ("claude", "codex"):
        assert {p.name for p in (SKILLS / agent).iterdir()
                if p.is_dir() and (p / "SKILL.md").exists()} == NAMES
    for name in NAMES:
        a, b = SKILLS / "claude" / name, SKILLS / "codex" / name
        assert payload(a / "scripts") == payload(b / "scripts")
        assert payload(a / "assets") == payload(b / "assets")
        for rel, content in payload(a / "references").items():
            assert (b / "references" / rel).read_bytes() == content
        assert (b / "agents" / "openai.yaml").is_file()
        assert not (a / "agents").exists()


@pytest.mark.parametrize("agent", ["claude", "codex"])
def test_packages_contain_exactly_the_distributed_files(agent):
    for name in NAMES:
        with zipfile.ZipFile(SKILLS / agent / f"{name}.skill") as archive:
            expected = {f"{name}/{r}": b for r, b in payload(SKILLS / agent / name).items()}
            assert set(archive.namelist()) == set(expected)
            assert all(archive.read(r) == b for r, b in expected.items())


@pytest.mark.parametrize("drift", ["script", "package", "extra_skill"])
def test_check_detects_drift_without_repairing_it(tmp_path, drift):
    target = tmp_path / "skills"
    shutil.copytree(SKILLS, target, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    if drift == "script":
        p = target / "codex/ecopath-paper-to-ppr/scripts/mapping_io.py"
        p.write_bytes(p.read_bytes() + b"\n# drift\n")
    elif drift == "package":
        p = target / "claude/ecopath-extraction.skill"
        with zipfile.ZipFile(p, "a") as archive:
            archive.writestr("ecopath-extraction/orphan.txt", "drift")
    else:
        p = target / "codex/extra/SKILL.md"
        p.parent.mkdir()
        p.write_text("unexpected skill", encoding="utf-8")
    before = {r: hashlib.sha256(b).hexdigest() for r, b in payload(target).items()}
    result = subprocess.run([sys.executable, "-B", str(target / "build_combined_skill.py"),
                             "--check"], capture_output=True, text=True)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "out of date" in result.stdout.lower()
    assert {r: hashlib.sha256(b).hexdigest() for r, b in payload(target).items()} == before
