SELECT 'patient' table_name,count(*),md5(string_agg(row_to_json(q)::text,'' ORDER BY patientid)) original_rows_digest FROM (SELECT * FROM patient WHERE patientid<=3000) q;
SELECT 'doctor' table_name,count(*),md5(string_agg(row_to_json(q)::text,'' ORDER BY doctorid)) original_rows_digest FROM (SELECT * FROM doctor WHERE doctorid<=120) q;
SELECT 'testtype' table_name,count(*),md5(string_agg(row_to_json(q)::text,'' ORDER BY testtypeid)) original_rows_digest FROM (SELECT * FROM testtype WHERE testtypeid<=20) q;
SELECT 'labtechnician' table_name,count(*),md5(string_agg(row_to_json(q)::text,'' ORDER BY technicianid)) original_rows_digest FROM (SELECT * FROM labtechnician WHERE technicianid<=80) q;
SELECT 'testorder' table_name,count(*),md5(string_agg(row_to_json(q)::text,'' ORDER BY orderid)) original_rows_digest FROM (SELECT * FROM testorder WHERE orderid<=5000) q;
SELECT 'labtest' table_name,count(*),md5(string_agg(row_to_json(q)::text,'' ORDER BY labtestid)) original_rows_digest FROM (SELECT * FROM labtest WHERE labtestid<=10000) q;
SELECT 'testresult' table_name,count(*),md5(string_agg(row_to_json(q)::text,'' ORDER BY resultid)) original_rows_digest FROM (SELECT * FROM testresult WHERE resultid<=8000) q;
SELECT 'labalert' table_name,count(*),md5(string_agg(row_to_json(q)::text,'' ORDER BY alertid)) original_rows_digest FROM (SELECT * FROM labalert WHERE alertid<=1557) q;
