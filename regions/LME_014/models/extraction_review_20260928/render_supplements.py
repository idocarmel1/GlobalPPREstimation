from pathlib import Path
import win32com.client
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent/'evidence'
word=win32com.client.DispatchEx('Word.Application');word.Visible=False;word.DisplayAlerts=0
try:
 for paper in ['PAT-2023','LME014-OcampoReinaldo-2016']:
  p=next((ROOT/'regions/LME_014/papers'/paper).glob('*.docx'))
  d=word.Documents.Open(str(p),ReadOnly=True,AddToRecentFiles=False,Visible=False)
  d.ExportAsFixedFormat(str(OUT/(paper+'_supplement.pdf')),17)
  d.Close(False)
finally:word.Quit()
