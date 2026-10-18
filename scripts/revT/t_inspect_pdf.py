from pathlib import Path
import sys,json,re
from pypdf import PdfReader
import pypdfium2 as pdfium
sys.stdout.reconfigure(encoding='utf-8')
W=Path(__file__).resolve().parents[2]/'work/revT';W.mkdir(parents=True,exist_ok=True)
for name in ['Titan Ridge DD Datasheet.pdf','Alpine-Ridge DP Datasheet.pdf','Universal Serial Bus 4.pdf']:
    src=Path('C:/Users/micro/Downloads')/name;r=PdfReader(src);texts=[q.extract_text() or '' for q in r.pages]
    (W/(src.stem+'.txt')).write_text('\n'.join(f'\n=== PDF PAGE {i+1} ===\n'+t for i,t in enumerate(texts)),encoding='utf-8')
    print(name,'pages',len(texts),'embedded',list(r.attachments),flush=True)
    for i,t in enumerate(texts):
        if i<3 or any(k in t.lower() for k in ['package dimensions','ball assignment','ball map','ordering information']):print('PAGE',i+1,t[:1700],flush=True)
    if 'Titan' in name or 'Alpine' in name:
        doc=pdfium.PdfDocument(src);doc[0].render(scale=1.3).to_pil().save(W/(src.stem+'_cover.png'))
    (W/(src.stem+'_PAGES.json')).write_text(json.dumps(texts,ensure_ascii=False,indent=2),encoding='utf-8')
