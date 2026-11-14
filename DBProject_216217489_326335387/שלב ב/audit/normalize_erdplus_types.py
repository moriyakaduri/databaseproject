"""Use ERDPlus's verified type/size format, established by UI export samples."""
from pathlib import Path
import json
import re
import shutil

B=Path(__file__).resolve().parent.parent
p=B/'diagrams/DSD-revised.erdplus'
d=json.loads(p.read_text(encoding='utf-8'))
for node in d['data']['nodes']:
    if node['type']!='Table':continue
    for col in node['data']['columns']:
        if col.get('isForeignKey'):continue
        t=col['type']
        if m:=re.fullmatch(r'VARCHAR\((\d+)\)',t):
            col['type']='VARCHAR(n)';col['size']=m[1]
        elif m:=re.fullmatch(r'NUMERIC\((\d+),(\d+)\)',t):
            col['type']='NUMERIC(p s)';col['size']=m[1]+','+m[2]
        elif t in ['TIMESTAMP','TEXT','BOOLEAN']:
            col['type']='Custom';col['size']=t
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copyfile(p,B/'diagrams/DSD-stage-b-verified.erdplus')
for name in ['DSD-metadata-sample.erdplus','DSD-metadata-final.erdplus']:
    src=Path('C:/Users/user6/Downloads')/name
    if src.exists():shutil.copyfile(src,B/'audit'/name)
print('Normalized VARCHAR(n)/size, NUMERIC(p s)/size and Custom/size in the final DSD.')
