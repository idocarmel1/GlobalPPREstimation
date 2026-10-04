"""Project command entry point."""
import sys,runpy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
if __name__=="__main__":runpy.run_module('tools.project_core.maps.open_map',run_name="__main__")
