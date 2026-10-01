"""Compatibility entry point for the maintained generic template builder."""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[1] / "build_validation_template.py"), run_name="__main__")
