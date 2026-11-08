\set ON_ERROR_STOP on
SELECT current_database(),version();
SELECT 'patient' table_name,count(*) row_count FROM patient UNION ALL SELECT 'doctor',count(*) FROM doctor UNION ALL SELECT 'testtype',count(*) FROM testtype UNION ALL SELECT 'labtechnician',count(*) FROM labtechnician UNION ALL SELECT 'testorder',count(*) FROM testorder UNION ALL SELECT 'labtest',count(*) FROM labtest UNION ALL SELECT 'testresult',count(*) FROM testresult UNION ALL SELECT 'labalert',count(*) FROM labalert;
DO $$ DECLARE t record; c record; n bigint; big_tables int:=0; BEGIN
IF (SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE')<>8 THEN RAISE EXCEPTION 'Expected exactly 8 tables'; END IF;
FOR t IN SELECT tablename FROM pg_tables WHERE schemaname='public' LOOP
EXECUTE format('SELECT count(*) FROM %I',t.tablename) INTO n;
IF n<500 THEN RAISE EXCEPTION 'Too few rows in %',t.tablename; END IF;
IF n>=20000 THEN big_tables:=big_tables+1; END IF;
END LOOP;
IF big_tables<2 THEN RAISE EXCEPTION 'Need two tables >=20,000'; END IF;
FOR c IN SELECT conrelid::regclass tab, conname,pg_get_expr(conbin,conrelid) expr FROM pg_constraint WHERE connamespace='public'::regnamespace AND contype='c' LOOP
EXECUTE format('SELECT count(*) FROM %s WHERE NOT (%s)',c.tab,c.expr) INTO n;
IF n<>0 THEN RAISE EXCEPTION 'CHECK violation %',c.conname; END IF;
END LOOP;
FOR c IN SELECT table_name,column_name FROM information_schema.columns WHERE table_schema='public' AND is_nullable='NO' LOOP
EXECUTE format('SELECT count(*) FROM %I WHERE %I IS NULL',c.table_name,c.column_name) INTO n;
IF n<>0 THEN RAISE EXCEPTION 'NULL violation'; END IF;
END LOOP;
FOR c IN SELECT p.conrelid::regclass tab,p.confrelid::regclass parent,a.attname col,b.attname parentcol FROM pg_constraint p JOIN pg_attribute a ON a.attrelid=p.conrelid AND a.attnum=p.conkey[1] JOIN pg_attribute b ON b.attrelid=p.confrelid AND b.attnum=p.confkey[1] WHERE p.contype='f' AND p.connamespace='public'::regnamespace LOOP
EXECUTE format('SELECT count(*) FROM %s c LEFT JOIN %s p ON c.%I=p.%I WHERE c.%I IS NOT NULL AND p.%I IS NULL',c.tab,c.parent,c.col,c.parentcol,c.col,c.parentcol) INTO n;
IF n<>0 THEN RAISE EXCEPTION 'Orphan rows in %',c.tab; END IF;
END LOOP;
FOR c IN SELECT p.conrelid::regclass tab,a.attname col FROM pg_constraint p JOIN pg_attribute a ON a.attrelid=p.conrelid AND a.attnum=p.conkey[1] WHERE p.contype IN ('p','u') AND p.connamespace='public'::regnamespace LOOP
EXECUTE format('SELECT count(*) FROM (SELECT %I FROM %s WHERE %I IS NOT NULL GROUP BY %I HAVING count(*)>1) q',c.col,c.tab,c.col,c.col) INTO n;
IF n<>0 THEN RAISE EXCEPTION 'Duplicate key in %',c.tab; END IF;
END LOOP;
RAISE NOTICE 'PASS: 8 tables, volume targets, PK/UNIQUE, FK, NOT NULL and CHECK scans';
END $$;
SELECT 'test_before_order' issue,count(*) violations FROM labtest l JOIN testorder o USING(orderid) WHERE l.scheduledat<o.orderedat
UNION ALL SELECT 'start_before_schedule',count(*) FROM labtest WHERE startedat<scheduledat
UNION ALL SELECT 'end_before_start',count(*) FROM labtest WHERE completedat<startedat
UNION ALL SELECT 'result_before_completion_or_not_completed',count(*) FROM testresult r JOIN labtest l USING(labtestid) WHERE l.status<>'Completed' OR l.completedat IS NULL OR r.resultedat<l.completedat
UNION ALL SELECT 'completed_without_result',count(*) FROM labtest l LEFT JOIN testresult r USING(labtestid) WHERE l.status='Completed' AND r.resultid IS NULL
UNION ALL SELECT 'alert_before_result_or_normal',count(*) FROM labalert a JOIN testresult r USING(resultid) WHERE a.createdat<r.resultedat OR NOT r.isabnormal
UNION ALL SELECT 'ack_before_alert',count(*) FROM labalert WHERE acknowledgedat<createdat
UNION ALL SELECT 'alert_status_timestamp_mismatch',count(*) FROM labalert WHERE (status='Open' AND acknowledgedat IS NOT NULL) OR (status IN ('Acknowledged','Resolved') AND acknowledgedat IS NULL)
UNION ALL SELECT 'lab_status_timestamp_mismatch',count(*) FROM labtest WHERE (status='Scheduled' AND (startedat IS NOT NULL OR completedat IS NOT NULL)) OR (status='InProgress' AND (startedat IS NULL OR completedat IS NOT NULL)) OR (status='Completed' AND (startedat IS NULL OR completedat IS NULL));
SELECT count(*) joined_results FROM testresult r JOIN labtest l USING(labtestid) JOIN testorder o USING(orderid) JOIN patient p USING(patientid) JOIN doctor d USING(doctorid) JOIN testtype tt USING(testtypeid) LEFT JOIN labtechnician tech USING(technicianid);
SELECT conrelid::regclass,conname,pg_get_constraintdef(oid),convalidated FROM pg_constraint WHERE connamespace='public'::regnamespace ORDER BY conrelid::regclass::text,conname;
