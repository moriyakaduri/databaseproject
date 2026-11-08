-- 1dropTables.sql
-- HOSPITAL LABORATORY - PostgreSQL 16 / pgAdmin
-- WARNING: Running this script PERMANENTLY DELETES the 8 project tables
-- and all of their contents in the CURRENT DATABASE.
-- Run ONLY in hospital_lab_db, and ONLY if you intend to start over.
-- Foreign-key child tables are removed before their parent tables.
-- We deliberately do not use CASCADE to avoid deleting unrelated objects.

BEGIN;

DROP TABLE IF EXISTS LABALERT;
DROP TABLE IF EXISTS TESTRESULT;
DROP TABLE IF EXISTS LABTEST;
DROP TABLE IF EXISTS TESTORDER;
DROP TABLE IF EXISTS LABTECHNICIAN;
DROP TABLE IF EXISTS TESTTYPE;
DROP TABLE IF EXISTS DOCTOR;
DROP TABLE IF EXISTS PATIENT;

COMMIT;
