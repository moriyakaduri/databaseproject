"""Static delivery checks against source files and recorded integration evidence."""
import csv
import io
import json
from pathlib import Path
import re
import subprocess
import hashlib
from urllib.parse import unquote

B=Path(__file__).resolve().parent.parent
A=B.parent/'שלב א'
ROOT=B.parent.parent
required=['Queries.sql','Constraints.sql','RollbackCommit.sql','Index.sql','StageA_Migration.sql','StageAChanges.md','README.md','backup2.dump']
for name in required: assert (B/name).is_file() and (B/name).stat().st_size,name
q=(B/'Queries.sql').read_text(encoding='utf-8')
keys=re.findall(r'^-- (Q\d[A-B]?|[DU]\d):',q,re.M)
assert keys==['Q1A','Q1B','Q2A','Q2B','Q3A','Q3B','Q4A','Q4B','Q5','Q6','Q7','Q8','D1','D2','D3','U1','U2','U3'],keys
assert len(re.findall(r'^ALTER TABLE .* ADD CONSTRAINT', (B/'Constraints.sql').read_text(encoding='utf-8'),re.M))==3
assert len(re.findall(r'^CREATE INDEX ',(B/'Index.sql').read_text(encoding='utf-8'),re.M))==3
assert len(re.findall(r'^EXPLAIN ',(B/'Index.sql').read_text(encoding='utf-8'),re.M))==6

path='DBProject_216217489_326335387/שלב א/DataImportFiles/technicians.csv'
original=subprocess.run(['git','show','5888977:'+path],cwd=ROOT,capture_output=True,check=True).stdout.decode('utf-8-sig')
old=list(csv.DictReader(io.StringIO(original)))
with (A/'DataImportFiles/technicians.csv').open(encoding='utf-8-sig',newline='') as f: new=list(csv.DictReader(f))
assert len(old)==len(new)==420
for before,after in zip(old,new):
    assert all(after[k]==v for k,v in before.items())
    assert after['certificationexpireson']

links=0
for doc in [ROOT/'README.md',A/'README.md',A/'DataDictionary.md',B/'README.md',B/'StageAChanges.md']:
    # Markdown references in SQL/code are absent from these generated blocks.
    for target in re.findall(r'\]\(([^)]+)\)',doc.read_text(encoding='utf-8-sig')):
        if re.match(r'https?://|#',target): continue
        local=(doc.parent/unquote(target.split('#',1)[0])).resolve()
        assert local.exists(),(doc,target)
        links+=1
summary=json.loads((B/'audit/verification.json').read_text())
assert summary['sql_and_restore_checks']=='PASS'
assert summary['final_q4_equivalence']=='PASS'
assert summary['screenshots_complete']
manifest=json.loads((B/'audit/screenshot_manifest.json').read_text(encoding='utf-8'))
assert len(manifest)==85
for item in manifest:
    assert hashlib.sha256((B/'screenshots'/item['file']).read_bytes()).hexdigest()==item['sha256']
doc=(B/'README.md').read_text(encoding='utf-8')
assert '**[צילום ' not in doc
original_erd=json.loads((A/'ERD/ERD.erdplus').read_text(encoding='utf-8-sig'))
revised_erd=json.loads((B/'diagrams/ERD-revised.erdplus').read_text(encoding='utf-8'))
assert len(revised_erd['data']['nodes'])==len(original_erd['data']['nodes'])+1
assert revised_erd['data']['edges'][:-1]==original_erd['data']['edges']
revised_dsd=json.loads((B/'diagrams/DSD-revised.erdplus').read_text(encoding='utf-8'))
original_dsd=json.loads((A/'DSD/DSD.erdplus').read_text(encoding='utf-8-sig'))
assert revised_dsd['data']['edges']==original_dsd['data']['edges']
tech=next(n for n in revised_dsd['data']['nodes'] if n['id']=='E_LABTECHNICIAN')
date_col=next(c for c in tech['data']['columns'] if c['name']=='CertificationExpiresOn')
assert date_col['type']=='DATE' and not date_col['isOptional']
assert summary['diagram_images_complete']
assert summary['diagram_rendering_method']=='local render of ERDPlus-verified sources'
for filename in ['updated-erd.png','updated-erd.jpeg','updated-erd.svg','updated-dsd.png','updated-dsd.svg']:
    assert (B/'diagrams'/filename).is_file(),filename
assert 'diagrams/updated-erd.png' in doc and 'diagrams/updated-dsd.png' in doc
assert 'לא צילומי מסך או הורדות PNG מקוריות מהאתר' in doc
assert not summary['original_database_modified']
assert (B/'backup2.dump').read_bytes().startswith(b'PGDMP')
print(f'PASS: {len(required)} delivery artifacts, 12 SELECT implementations, 6 mutations, 3 constraints, 3 indexes, 6 EXPLAINs, {links} local links, and all 420 prior CSV rows preserved.')
print('PASS: 85 authentic screenshot hashes and revised local diagram structure.')
print('PASS: full diagram artifacts and explicit local-rendering provenance.')
print('NOTE: backup2 restore on partner computer remains a partner action; submission tag is verified separately against remote Git. Native website image download failed; complete local diagrams are included.')
