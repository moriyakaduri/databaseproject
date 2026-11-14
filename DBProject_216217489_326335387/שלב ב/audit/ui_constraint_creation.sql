BEGIN;
ALTER TABLE doctor DROP CONSTRAINT chk_doctor_firstname_nonblank;
ALTER TABLE labtest DROP CONSTRAINT chk_labtest_time_order;
ALTER TABLE labalert DROP CONSTRAINT chk_labalert_ack_time;
ALTER TABLE doctor ADD CONSTRAINT chk_doctor_firstname_nonblank
 CHECK (length(btrim(firstname))>0);
ALTER TABLE labtest ADD CONSTRAINT chk_labtest_time_order
 CHECK ((startedat IS NULL OR scheduledat IS NULL OR startedat>=scheduledat)
    AND (completedat IS NULL OR (startedat IS NOT NULL AND completedat>=startedat)));
ALTER TABLE labalert ADD CONSTRAINT chk_labalert_ack_time
 CHECK (acknowledgedat IS NULL OR acknowledgedat>=createdat);

SELECT conname,conrelid::regclass AS table_name,convalidated
FROM pg_constraint WHERE conname IN ('chk_doctor_firstname_nonblank','chk_labtest_time_order','chk_labalert_ack_time') ORDER BY conname;
ROLLBACK;
