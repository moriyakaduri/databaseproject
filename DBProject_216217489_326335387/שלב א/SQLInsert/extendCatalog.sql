-- Method 1: SQL INSERT. Run once on audited initial DB.
BEGIN;
INSERT INTO doctor (doctorid,licensenumber,firstname,lastname,specialty,phone)
SELECT i,'DEMO-LIC-'||i,'DemoDoctor'||i,'Synthetic',
(ARRAY['Hematology','Chemistry','Microbiology','Immunology','Pathology'])[(i%5)+1],NULL
FROM generate_series(121,500) g(i);
INSERT INTO testtype(testtypeid,testcode,testname,category,defaultunit)
SELECT i,'DEMO-T-'||i,'Synthetic assay variant '||i,
(ARRAY['Chemistry','Hematology','Microbiology','Immunology'])[(i%4)+1],
CASE WHEN i%4=2 THEN NULL ELSE 'demo-unit' END
FROM generate_series(21,500) g(i);
SELECT setval(pg_get_serial_sequence('doctor','doctorid'),(SELECT max(doctorid) FROM doctor));
SELECT setval(pg_get_serial_sequence('testtype','testtypeid'),(SELECT max(testtypeid) FROM testtype));
COMMIT;
