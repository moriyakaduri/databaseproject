-- הרצה פעם אחת לאחר שלב א׳ המעודכן/המיגרציה. שלושה אילוצים חדשים.
BEGIN;
ALTER TABLE doctor ADD CONSTRAINT chk_doctor_firstname_nonblank
 CHECK (length(btrim(firstname))>0);
ALTER TABLE labtest ADD CONSTRAINT chk_labtest_time_order
 CHECK ((startedat IS NULL OR scheduledat IS NULL OR startedat>=scheduledat)
    AND (completedat IS NULL OR (startedat IS NOT NULL AND completedat>=startedat)));
ALTER TABLE labalert ADD CONSTRAINT chk_labalert_ack_time
 CHECK (acknowledgedat IS NULL OR acknowledgedat>=createdat);
COMMIT;

-- שלוש ההכנסות הבאות נועדו להיכשל ב-23514 על שם האילוץ המתאים.
-- ב-pgAdmin: הריצו BEGIN+SAVEPOINT+INSERT עד לקבלת השגיאה,
-- ואז הריצו ROLLBACK TO SAVEPOINT ואחריו ROLLBACK בנפרד.
-- psql: לשם הרצת כל הקובץ השתמשו ב-ON_ERROR_STOP=off בחלק ההדגמות בלבד.
BEGIN;
SAVEPOINT invalid_doctor;
INSERT INTO doctor(doctorid,licensenumber,firstname,lastname,specialty)
VALUES(-900001,'DEMO-BAD-NAME','   ','Demo','Demo');
ROLLBACK TO SAVEPOINT invalid_doctor;
ROLLBACK;

BEGIN;
SAVEPOINT invalid_test;
INSERT INTO labtest(labtestid,status,scheduledat,startedat,completedat,orderid,testtypeid)
SELECT -900001,'Completed',TIMESTAMP '2026-01-02',TIMESTAMP '2026-01-01',
       TIMESTAMP '2026-01-03',o.orderid,tt.testtypeid
FROM testorder o CROSS JOIN testtype tt ORDER BY o.orderid,tt.testtypeid LIMIT 1;
ROLLBACK TO SAVEPOINT invalid_test;
ROLLBACK;

BEGIN;
SAVEPOINT invalid_alert;
INSERT INTO labalert(alertid,severity,message,createdat,status,acknowledgedat,resultid)
SELECT -900001,'Low','Invalid demonstration',TIMESTAMP '2026-02-02',
       'Acknowledged',TIMESTAMP '2026-02-01',resultid
FROM testresult ORDER BY resultid LIMIT 1;
ROLLBACK TO SAVEPOINT invalid_alert;
ROLLBACK;
