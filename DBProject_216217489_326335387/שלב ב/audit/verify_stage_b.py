"""Integration checks against an isolated PostgreSQL Docker database.
Never changes the original database. Requires local Docker and the project container.
Run with the bundled/system Python. Logs contain synthetic sample records only.
"""
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import sys

B=Path(__file__).resolve().parent.parent
A=B.parent/'שלב א'
ROOT=B.parent.parent
DOCKER=Path(os.environ.get('LOCALAPPDATA',''))/'Programs/DockerDesktop/resources/bin/docker.exe'
DB='codex_stage_b_20261112'
RESTORE=DB+'_restore'
logs=B/'audit'

def call(args, data=None, check=True):
    p=subprocess.run([str(DOCKER),*args],input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if check and p.returncode:
        raise RuntimeError(p.stderr.decode('utf-8',errors='replace')+p.stdout.decode('utf-8',errors='replace'))
    return p

def sql(text, db=DB, stop=True, name=None):
    p=call(['exec','-i','postgres_db','sh','-c',
            'exec psql -X -U "$POSTGRES_USER" -d "$1" -v ON_ERROR_STOP="$2" -P pager=off',
            'runner',db,'on' if stop else 'off'],text.encode('utf-8'))
    result=p.stdout.decode('utf-8')+p.stderr.decode('utf-8')
    if name: (logs/name).write_text(result,encoding='utf-8')
    return result

def new_database(name):
    # Fixed isolated names; existing test DB is evidence, not permission to delete.
    out=sql(f"SELECT datname FROM pg_database WHERE datname='{name}';",db='postgres')
    if re.search(r'\(0 rows\)',out) is None:
        raise RuntimeError(f'{name} already exists. Inspect it rather than resetting it.')
    sql(f'CREATE DATABASE {name};',db='postgres')

def schema_counts(db):
    return sql("""SELECT 'patient' AS name,count(*) FROM patient UNION ALL
SELECT 'doctor',count(*) FROM doctor UNION ALL SELECT 'testtype',count(*) FROM testtype
UNION ALL SELECT 'labtechnician',count(*) FROM labtechnician UNION ALL
SELECT 'testorder',count(*) FROM testorder UNION ALL SELECT 'labtest',count(*) FROM labtest
UNION ALL SELECT 'testresult',count(*) FROM testresult UNION ALL SELECT 'labalert',count(*) FROM labalert
ORDER BY name;""",db=db)

def verify_restored_copy():
    # pg_dump/restore can deparse equivalent array casts differently. Compare
    # column metadata, index definitions, constraint identities/structure, and
    # all row values, plus exact definitions of the three newly added CHECKs.
    probes=[
        "SELECT row_to_json(c) FROM (SELECT table_name,column_name,ordinal_position,data_type,udt_name,is_nullable,character_maximum_length,numeric_precision,numeric_scale,column_default,is_identity,identity_generation FROM information_schema.columns WHERE table_schema='public' ORDER BY table_name,ordinal_position) c;",
        "SELECT row_to_json(c) FROM (SELECT tablename,indexname,indexdef FROM pg_indexes WHERE schemaname='public' ORDER BY indexname) c;",
        "SELECT row_to_json(c) FROM (SELECT conrelid::regclass::text AS tab,conname,contype,convalidated,conkey,confkey,CASE WHEN confrelid=0 THEN NULL ELSE confrelid::regclass::text END AS parent,confupdtype,confdeltype FROM pg_constraint WHERE connamespace='public'::regnamespace ORDER BY conname) c;",
        "SELECT row_to_json(c) FROM (SELECT conname,pg_get_constraintdef(oid) FROM pg_constraint WHERE conname IN ('chk_doctor_firstname_nonblank','chk_labtest_time_order','chk_labalert_ack_time') ORDER BY conname) c;",
    ]
    tables=['patient','doctor','testtype','labtechnician','testorder','labtest','testresult','labalert']
    for t in tables:
        probes.append(f"SELECT '{t}' AS tab,count(*),md5(string_agg(row_to_json(t)::text,E'\\n' ORDER BY row_to_json(t)::text)) AS fingerprint FROM {t} t;")
    results=[]
    for i,probe in enumerate(probes):
        left,right=sql(probe),sql(probe,db=RESTORE)
        assert left==right,f'Restored copy mismatch in probe {i}: {left} {right}'
        results.append(f'Probe {i} PASS\n'+left)
    (logs/'13_restore_comparison.txt').write_text('\n'.join(results),encoding='utf-8')

def main():
    resume_errors='--resume-from-errors' in sys.argv
    if '--resume-after-seed' not in sys.argv and not resume_errors:
        new_database(DB)
        sql((A/'createTables.sql').read_text(encoding='utf-8-sig'),name='01_create.txt')
        for filename in ['SQLInsert/baseSeed.sql','SQLInsert/extendCatalog.sql']:
            sql((A/filename).read_text(encoding='utf-8-sig'))
        # Reproduce CSV method using COPY stdin. The delivered import.sql uses psql \copy.
        data=(A/'DataImportFiles/technicians.csv').read_text(encoding='utf-8-sig')
        sql("COPY labtechnician(technicianid,firstname,lastname,certificationnumber,phone,certificationexpireson) FROM STDIN WITH (FORMAT csv,HEADER true);\n"+data+"\\.\nSELECT setval(pg_get_serial_sequence('labtechnician','technicianid'),(SELECT max(technicianid) FROM labtechnician));")
        sql((A/'Programing/generated.sql').read_text(encoding='utf-8-sig'))
    validation=(A/'audit/validate.sql').read_text(encoding='utf-8-sig')
    sql(validation,name='02_stage_a_validation.txt')
    sql("""DO $$ BEGIN
 IF (SELECT count(*) FROM information_schema.columns WHERE table_schema='public' AND data_type='date')<2 THEN RAISE EXCEPTION 'Need two DATEs'; END IF;
 IF EXISTS(SELECT FROM information_schema.tables WHERE table_schema='public' AND lower(table_name) IN ('date','dat')) THEN RAISE EXCEPTION 'Unexpected DATE entity'; END IF;
END $$;""")
    print('Stage A replay and volumes PASS',flush=True)
    source=(B/'Queries.sql').read_text(encoding='utf-8')
    selects={}
    for key in ['Q1A','Q1B','Q2A','Q2B','Q3A','Q3B','Q4A','Q4B','Q5','Q6','Q7','Q8']:
        part=source.split('-- '+key+': ',1)[1]
        body=part[part.index('\n')+1:]
        body='\n'.join(line for line in body.splitlines() if not line.startswith('--'))
        selects[key]=body.split(';',1)[0].strip()
    # Remove explanatory comments, retaining the exact SQL semantics.
    sample=[]
    for key,q in ([] if resume_errors else selects.items()):
        out=sql(f'SELECT count(*) AS result_count FROM ({q}) q;\nSELECT * FROM ({q}) q LIMIT 5;')
        if '(0 rows)' in out: raise AssertionError(f'{key} has no demonstration results')
        sample.append(key+'\n'+out)
        print(key+' has results',flush=True)
    if sample: (logs/'03_select_samples.txt').write_text('\n'.join(sample),encoding='utf-8')
    pair_logs=[]
    for n in ([] if resume_errors else range(1,5)):
        qa,qb=selects[f'Q{n}A'],selects[f'Q{n}B']
        query=f'''WITH a AS ({qa}),b AS ({qb}),
diff AS ((SELECT * FROM a EXCEPT ALL SELECT * FROM b)
UNION ALL (SELECT * FROM b EXCEPT ALL SELECT * FROM a))
SELECT count(*) AS differences FROM diff;'''
        out=sql(query)
        assert re.search(r'differences\s*\n[- ]+\n\s*0\s*\n',out),out
        pair_logs.append(f'Q{n} A/B multiset equivalence\n'+out)
        print(f'Q{n} equivalence PASS',flush=True)
    if pair_logs: (logs/'04_equivalence.txt').write_text('\n'.join(pair_logs),encoding='utf-8')
    constraints=(B/'Constraints.sql').read_text(encoding='utf-8')
    cut=constraints.index('COMMIT;')+len('COMMIT;')
    if not resume_errors: sql(constraints[:cut],name='05_constraints_added.txt')
    else:
        assert '3' in sql("SELECT count(*) FROM pg_constraint WHERE conname IN ('chk_doctor_firstname_nonblank','chk_labtest_time_order','chk_labalert_ack_time');")
    out=sql('\\set VERBOSITY verbose\n'+constraints[cut:],stop=False,name='06_expected_errors.txt')
    assert out.count('ERROR:  23514:')==3,out
    for name in ['chk_doctor_firstname_nonblank','chk_labtest_time_order','chk_labalert_ack_time']:
        assert f'violates check constraint "{name}"' in out,out
    print('3 intended constraint errors PASS',flush=True)
    # Verify full table state before, during, and after each mutation, with EXCEPT ALL.
    mutation_logs=[]
    tables=['labalert','labtest','doctor','testorder','labalert','labtest']
    for key,table in zip(['D1','D2','D3','U1','U2','U3'],tables):
        q=source.split('-- '+key+': ',1)[1].split('BEGIN;',1)[1].split('ROLLBACK;',1)[0]
        out=sql(f'''CREATE TEMP TABLE before_{key} AS TABLE {table};
SELECT '{key} before' AS phase,count(*) FROM {table};
BEGIN;
{q}
SELECT '{key} after' AS phase,count(*) FROM {table};
SELECT count(*) AS changed_rows FROM
 ((SELECT * FROM {table} EXCEPT ALL SELECT * FROM before_{key})
 UNION ALL (SELECT * FROM before_{key} EXCEPT ALL SELECT * FROM {table})) diff;
ROLLBACK;
DO $$ BEGIN IF EXISTS ((SELECT * FROM {table} EXCEPT ALL SELECT * FROM before_{key})
 UNION ALL (SELECT * FROM before_{key} EXCEPT ALL SELECT * FROM {table}))
 THEN RAISE EXCEPTION 'Rollback did not restore {key}'; END IF; END $$;
DROP TABLE before_{key};''')
        assert not re.search(r'(DELETE 0|UPDATE 0)',out),key+' changed nothing'
        mutation_logs.append(key+'\n'+out)
        print(key+' mutation and rollback PASS',flush=True)
    (logs/'07_mutations.txt').write_text('\n'.join(mutation_logs),encoding='utf-8')
    out=sql((B/'RollbackCommit.sql').read_text(encoding='utf-8'),name='08_transactions.txt')
    assert 'after rollback' in out and 'after commit' in out
    assert len(re.findall(r'\| t\s*\n',out))==2,out
    print('Rollback/Commit proof PASS',flush=True)
    sql((B/'Index.sql').read_text(encoding='utf-8'),name='09_index_before_after.txt')
    print('Index script PASS',flush=True)
    # Repeat exact index probes to record warm-cache medians.
    indexes=['idx_testorder_patient_date','idx_labtest_type_status','idx_labalert_open_created']
    source_index=(B/'Index.sql').read_text(encoding='utf-8')
    timing={}
    import statistics
    plans=[]
    for index in indexes:
        section=source_index.split('DROP INDEX IF EXISTS '+index+';',1)[1]
        q=section.split('EXPLAIN (ANALYZE, BUFFERS)\n',1)[1].split(';',1)[0]+';'
        create='CREATE INDEX '+section.split('CREATE INDEX ',1)[1].split(';',1)[0]+';'
        sql('DROP INDEX '+index+'; ANALYZE;')
        times=[]
        for _ in range(5):
            p=sql('EXPLAIN (ANALYZE,BUFFERS) '+q)
            plans.append(index+' BEFORE\n'+p)
            times.append(float(re.search(r'Execution Time: ([\d.]+)',p)[1]))
        before=statistics.median(times)
        sql(create+' ANALYZE;')
        times=[]
        for _ in range(5):
            p=sql('EXPLAIN (ANALYZE,BUFFERS) '+q)
            plans.append(index+' AFTER\n'+p)
            times.append(float(re.search(r'Execution Time: ([\d.]+)',p)[1]))
        timing[index]={'median_before_ms':before,'median_after_ms':statistics.median(times)}
    (logs/'10_repeated_index_plans.txt').write_text('\n'.join(plans),encoding='utf-8')
    (logs/'index_timings.json').write_text(json.dumps(timing,indent=2),encoding='utf-8')
    # Actual timings for four equivalent query pairs; capture plans too.
    qt={}
    for key in ['Q1A','Q1B','Q2A','Q2B','Q3A','Q3B','Q4A','Q4B']:
        p=sql('EXPLAIN (ANALYZE,BUFFERS) '+selects[key]+';')
        qt[key]=float(re.search(r'Execution Time: ([\d.]+)',p)[1])
        (logs/(key+'_plan.txt')).write_text(p,encoding='utf-8')
    (logs/'query_timings.json').write_text(json.dumps(qt,indent=2),encoding='utf-8')
    print('Measured index and query plans',flush=True)
    # Backup2 is of the populated, updated validation copy; never claim a live DB backup.
    dump=call(['exec','postgres_db','sh','-c','exec pg_dump -U "$POSTGRES_USER" -d "$1" -Fc','runner',DB]).stdout
    assert dump.startswith(b'PGDMP')
    (B/'backup2.dump').write_bytes(dump)
    new_database(RESTORE)
    call(['exec','-i','postgres_db','sh','-c','exec pg_restore -U "$POSTGRES_USER" -d "$1" --no-owner --no-privileges --exit-on-error','runner',RESTORE],dump)
    assert schema_counts(DB)==schema_counts(RESTORE)
    sql(validation,db=RESTORE,name='11_backup2_restore.txt')
    catalog="SELECT tablename,indexname,indexdef FROM pg_indexes WHERE schemaname='public' ORDER BY indexname; SELECT conname,pg_get_constraintdef(oid) FROM pg_constraint WHERE connamespace='public'::regnamespace ORDER BY conname;"
    verify_restored_copy()
    sql(catalog,name='12_final_catalog.txt')
    summary={'database':DB,'restored_database':RESTORE,'backup_sha256':hashlib.sha256(dump).hexdigest(),
             'all_checks':'PASS','original_database_modified':False,'index_timings':timing,'query_execution_ms':qt}
    (logs/'verification.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__': main()
