"""Finish backup verification and verify migration from the untouched original."""
from verify_stage_b import *
import difflib

catalog="SELECT tablename,indexname,indexdef FROM pg_indexes WHERE schemaname='public' ORDER BY indexname; SELECT conname,pg_get_constraintdef(oid) FROM pg_constraint WHERE connamespace='public'::regnamespace ORDER BY conname;"
src=sql(catalog)
dst=sql(catalog,db=RESTORE)
(logs/'12_final_catalog.txt').write_text(src,encoding='utf-8')
(logs/'12_restored_catalog.txt').write_text(dst,encoding='utf-8')
diff='\n'.join(difflib.unified_diff(src.splitlines(),dst.splitlines()))
(logs/'catalog_diff.txt').write_text(diff,encoding='utf-8')
verify_restored_copy()
print('Backup2: all row fingerprints, columns, indexes and new constraints match.',flush=True)

MIGRATION=DB+'_migration'
original='Hospiatl_Lab_db'
tables=['patient','doctor','testtype','labtechnician','testorder','labtest','testresult','labalert']
def fingerprints(db,legacy=False):
    parts=[]
    for t in tables:
        value="(to_jsonb(t)-'certificationexpireson')::text" if legacy and t=='labtechnician' else 'to_jsonb(t)::text'
        parts.append(f"SELECT '{t}' AS tab,count(*),md5(string_agg({value},E'\\n' ORDER BY {value})) AS hash FROM {t} t;")
    return sql('\n'.join(parts),db=db)

before=fingerprints(original)
new_database(MIGRATION)
dump=call(['exec','postgres_db','sh','-c','exec pg_dump -U "$POSTGRES_USER" -d "$1" -Fc','runner',original]).stdout
call(['exec','-i','postgres_db','sh','-c','exec pg_restore -U "$POSTGRES_USER" -d "$1" --no-owner --no-privileges --exit-on-error','runner',MIGRATION],dump)
assert fingerprints(MIGRATION)==before
sql((B/'StageA_Migration.sql').read_text(encoding='utf-8'),db=MIGRATION,name='14_migration.txt')
assert fingerprints(MIGRATION,legacy=True)==before
assert fingerprints(original)==before
certificate="SELECT technicianid,certificationexpireson FROM labtechnician ORDER BY technicianid;"
assert sql(certificate,db=MIGRATION)==sql(certificate)
(logs/'15_preserved_original_rows.txt').write_text('PASS: original DB unchanged; migrated copy preserves every original column value.\n'+before,encoding='utf-8')

summary={'database':DB,'restored_database':RESTORE,'migration_database':MIGRATION,
 'backup_sha256':hashlib.sha256((B/'backup2.dump').read_bytes()).hexdigest(),
 'sql_and_restore_checks':'PASS','original_database_modified':False,
 'screenshots_complete':False,'erd_exports_updated':False,
 'index_timings':json.loads((logs/'index_timings.json').read_text()),
 'query_execution_ms':json.loads((logs/'query_timings.json').read_text())}
(logs/'verification.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2),flush=True)
