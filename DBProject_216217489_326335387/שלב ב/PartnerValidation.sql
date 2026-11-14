-- Read-only checks after restoring backup2 into a NEW database.
\set ON_ERROR_STOP on
BEGIN READ ONLY;
SELECT 'patient' AS table_name,count(*) FROM patient UNION ALL
SELECT 'doctor',count(*) FROM doctor UNION ALL
SELECT 'testtype',count(*) FROM testtype UNION ALL
SELECT 'labtechnician',count(*) FROM labtechnician UNION ALL
SELECT 'testorder',count(*) FROM testorder UNION ALL
SELECT 'labtest',count(*) FROM labtest UNION ALL
SELECT 'testresult',count(*) FROM testresult UNION ALL
SELECT 'labalert',count(*) FROM labalert ORDER BY table_name;
SELECT table_name,column_name,data_type,is_nullable
FROM information_schema.columns
WHERE table_schema='public' AND data_type='date'
ORDER BY table_name,column_name;
SELECT conname,pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conname IN ('chk_doctor_firstname_nonblank','chk_labtest_time_order','chk_labalert_ack_time')
ORDER BY conname;
SELECT indexname,indexdef FROM pg_indexes
WHERE schemaname='public' AND indexname IN
('idx_testorder_patient_date','idx_labtest_type_status','idx_labalert_open_created')
ORDER BY indexname;
DO $$
BEGIN
 IF (SELECT count(*) FROM patient)<>3000 OR (SELECT count(*) FROM doctor)<>500
 OR (SELECT count(*) FROM testtype)<>500 OR (SELECT count(*) FROM labtechnician)<>500
 OR (SELECT count(*) FROM testorder)<>5000 OR (SELECT count(*) FROM labtest)<>30000
 OR (SELECT count(*) FROM testresult)<>24000 OR (SELECT count(*) FROM labalert)<>3157
 THEN RAISE EXCEPTION 'Unexpected table counts'; END IF;
 IF (SELECT count(*) FROM information_schema.columns WHERE table_schema='public' AND data_type='date')<>2
 THEN RAISE EXCEPTION 'Expected two DATE columns'; END IF;
 IF EXISTS(SELECT FROM information_schema.tables WHERE table_schema='public' AND lower(table_name) IN ('dat','date'))
 THEN RAISE EXCEPTION 'Unexpected date entity'; END IF;
 IF (SELECT count(*) FROM pg_constraint WHERE connamespace='public'::regnamespace AND convalidated
 AND conname IN ('chk_doctor_firstname_nonblank','chk_labtest_time_order','chk_labalert_ack_time'))<>3
 THEN RAISE EXCEPTION 'Missing new constraints'; END IF;
 IF (SELECT count(*) FROM pg_indexes WHERE schemaname='public' AND indexname IN
 ('idx_testorder_patient_date','idx_labtest_type_status','idx_labalert_open_created'))<>3
 THEN RAISE EXCEPTION 'Missing new indexes'; END IF;
 RAISE NOTICE 'PASS: expected row counts, two DATE columns, three constraints and three indexes';
END $$;
COMMIT;
