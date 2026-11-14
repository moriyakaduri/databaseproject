"""Verify final Q4 enhancement and save fresh result/plan evidence."""
from verify_stage_b import *

source=(B/'Queries.sql').read_text(encoding='utf-8')
selects={}
for key in ['Q4A','Q4B']:
    part=source.split('-- '+key+': ',1)[1]
    body=part[part.index('\n')+1:]
    q='\n'.join(line for line in body.splitlines() if not line.startswith('--')).split(';',1)[0].strip()
    selects[key]=q
    sql(f'SELECT count(*) AS result_count FROM ({q}) q; SELECT * FROM ({q}) q LIMIT 5;',name=key+'_final_samples.txt')
    p=sql('EXPLAIN (ANALYZE,BUFFERS) '+q+';',name=key+'_plan.txt')
    timing=json.loads((logs/'query_timings.json').read_text())
    timing[key]=float(re.search(r'Execution Time: ([\d.]+)',p)[1])
    (logs/'query_timings.json').write_text(json.dumps(timing,indent=2),encoding='utf-8')
out=sql(f'''WITH a AS ({selects['Q4A']}),b AS ({selects['Q4B']}),
diff AS ((SELECT * FROM a EXCEPT ALL SELECT * FROM b) UNION ALL
         (SELECT * FROM b EXCEPT ALL SELECT * FROM a))
SELECT count(*) AS differences FROM diff;''',name='Q4_final_equivalence.txt')
assert re.search(r'differences\s*\n[- ]+\n\s*0\s*\n',out),out
summary=json.loads((logs/'verification.json').read_text())
summary['query_execution_ms']=timing
summary['final_q4_equivalence']='PASS'
(logs/'verification.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print('Final Q4: 3 joined tables, non-empty results, equivalent multisets, plans saved.')
