"""NPP command entry point; extraction does not adopt workbook values."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scientific_code/NPPExtraction"))
from npp.annual import main
if __name__=="__main__":main()
