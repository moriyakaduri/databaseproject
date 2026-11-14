"""Read-only final audit of the exact delivered SQL and existing test databases.

Requires the local PostgreSQL Docker container used for the recorded tests.
Does not recreate databases or run mutating demonstration scripts.
"""
import hashlib
import json
import re
from datetime import datetime, timezone
from verify_stage_b import B, A, DB, RESTORE, sql, verify_restored_copy

source = (B / 'Queries.sql').read_text(encoding='utf-8')
queries = {}
for key in ['Q1A','Q1B','Q2A','Q2B','Q3A','Q3B','Q4A','Q4B','Q5','Q6','Q7','Q8']:
    section = source.split('-- '+key+': ', 1)[1]
    body = section[section.index('\n')+1:]
    queries[key] = '\n'.join(line for line in body.splitlines() if not line.startswith('--')).split(';',1)[0].strip()

evidence = []
results = {}
for key, query in queries.items():
    out = sql(f"BEGIN READ ONLY; WITH q AS MATERIALIZED ({query}) SELECT json_build_object('rows',(SELECT count(*) FROM q),'sample',(SELECT row_to_json(s) FROM (SELECT * FROM q LIMIT 1) s)); COMMIT;")
    obj = json.loads(next(line.strip() for line in out.splitlines() if line.strip().startswith('{')))
    assert obj['rows'] > 0 and len(obj['sample']) > 2, (key, obj)
    results[key] = {'rows':obj['rows'], 'columns':len(obj['sample'])}
    evidence.append(key+'\n'+out)
    print(f'{key}: {obj["rows"]} rows, {len(obj["sample"])} columns PASS',flush=True)

for n in range(1,5):
    out = sql(f"""BEGIN READ ONLY;
WITH a AS ({queries[f'Q{n}A']}), b AS ({queries[f'Q{n}B']}),
diff AS ((SELECT * FROM a EXCEPT ALL SELECT * FROM b) UNION ALL
         (SELECT * FROM b EXCEPT ALL SELECT * FROM a))
SELECT json_build_object('differences',count(*)) FROM diff;
COMMIT;""")
    obj = json.loads(next(line.strip() for line in out.splitlines() if line.strip().startswith('{')))
    assert obj['differences'] == 0, (n,obj)
    evidence.append(f'Q{n} equivalence\n'+out)
    print(f'Q{n} equivalence PASS',flush=True)

partner_check = (B/'PartnerValidation.sql').read_text(encoding='utf-8')
evidence.append(sql(partner_check,db=RESTORE))
verify_restored_copy()
backup_hash = hashlib.sha256((B/'backup2.dump').read_bytes()).hexdigest()
assert backup_hash == '6fcacd9ef01f0bad38d48ff35348453af207af81723bd78855ac054150ff6a98'
manifest = json.loads((B/'audit/screenshot_manifest.json').read_text(encoding='utf-8'))
gallery = (B/'screenshots/README.md').read_text(encoding='utf-8')
for item in manifest:
    assert hashlib.sha256((B/'screenshots'/item['file']).read_bytes()).hexdigest() == item['sha256']
    assert f']({item["file"]})' in gallery
for filename in ['updated-erd.png','updated-dsd.png']:
    assert f'diagrams/{filename}' in (B/'README.md').read_text(encoding='utf-8')

files = [B/name for name in ['Queries.sql','Constraints.sql','RollbackCommit.sql','Index.sql','StageA_Migration.sql','PartnerValidation.sql','backup2.dump']]
files += [A/'createTables.sql',A/'SQLInsert/baseSeed.sql',A/'DataImportFiles/technicians.csv',A/'DataImportFiles/import.sql']
summary = {'checked_at_utc':datetime.now(timezone.utc).isoformat(), 'status':'PASS',
           'database':DB,'restored_database':RESTORE,'selects':results,
           'equivalent_pairs':4,'authentic_screenshots_in_gallery':len(manifest),
           'source_sha256':{str(p.relative_to(B.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
           'scope':'Read-only final checks; mutation/constraint/transaction/index tests are retained in numbered audit logs.',
           'limitations':['Native ERDPlus image download failed; full diagrams rendered locally from verified sources.',
                          'Some pgAdmin screenshots show leftmost columns; full SQL and text results are supplied.',
                          'backup2 was restored locally; partner-machine backup2 restore has not yet been performed.']}
(B/'audit/final_submission_check.txt').write_text('\n'.join(evidence),encoding='utf-8')
(B/'audit/final_submission_check.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: backup hash, restored database equality, all 85 screenshots and complete diagram references.',flush=True)
