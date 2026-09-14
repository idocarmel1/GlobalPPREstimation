import pathlib,sys
sys.path.insert(0,r'C:\Users\idoca\.agents\skills\ecopath-extraction\scripts');from pdf_backend import extract_text,page_count
p=pathlib.Path(sys.argv[1]);t=extract_text(p/'file-e30dfe50.pdf');print(type(t));(p/'extracted/work/article_text.txt').write_text(str(t),encoding='utf-8')
