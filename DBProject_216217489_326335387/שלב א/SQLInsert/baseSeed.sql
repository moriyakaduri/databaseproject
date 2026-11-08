-- 3insertTables.sql
-- HOSPITAL LABORATORY - PostgreSQL 16 / pgAdmin
-- DATA ARE COMPLETELY SYNTHETIC, NOT REAL PATIENT RECORDS.
-- Run AFTER 2createTables.sql, ONCE, when the tables are EMPTY.
-- Data are generated in SQL with generate_series() to avoid a huge file.
-- Includes 4 tables with > 200 rows, as required by the course slides.
-- Intended counts: 3,000 patients, 120 doctors, 20 test types,
-- 80 technicians, 5,000 orders, 10,000 lab tests, 8,000 results,
-- plus alerts for abnormal results (over 20,000 total rows).
-- This SQL generation counts as ONE insertion method; use other methods
-- (such as CSV/Mockaroo/manual INSERT) separately if the lecturer requires 3.

BEGIN;

-- 1. PATIENT - 3,000 fictional patients (NO real IDs or phone numbers)
INSERT INTO PATIENT (PatientID, IDNumber, FirstName, LastName, DateOfBirth, Gender, Phone)
SELECT
    i,
    (800000000 + i)::text,
    (ARRAY['Noam','Maya','Daniel','Lia','Amit','Yael','Uri','Shira','Neta','Omer'])[((i - 1) % 10) + 1],
    (ARRAY['Cohen','Levi','Mizrahi','Barak','Shalev','Alon','Tal','Noy','Erez','Rosen'])[((i * 3 - 1) % 10) + 1],
    DATE '1950-01-01' + ((i * 41) % 25000),
    CASE WHEN i % 29 = 0 THEN 'other' WHEN i % 2 = 0 THEN 'F' ELSE 'M' END,
    '050' || LPAD(i::text, 7, '0')
FROM generate_series(1, 3000) AS g(i);

-- 2. DOCTOR - 120 fictional doctors
INSERT INTO DOCTOR (DoctorID, LicenseNumber, FirstName, LastName, Specialty, Phone)
SELECT
    i,
    'LIC' || LPAD(i::text, 6, '0'),
    (ARRAY['Dana','Roni','Adi','Eitan','Michal','Tomer','Hila','Nir','Liron','Yuval'])[((i - 1) % 10) + 1],
    (ARRAY['Katz','Golan','Levy','Harel','Shamir','BenDavid','Koren','Shani','Or','Peled'])[((i * 7 - 1) % 10) + 1],
    (ARRAY['Internal Medicine','Pediatrics','Cardiology','Emergency Medicine',
           'Endocrinology','Hematology','Nephrology','Family Medicine'])[((i - 1) % 8) + 1],
    '052' || LPAD(i::text, 7, '0')
FROM generate_series(1, 120) AS g(i);

-- 3. TESTTYPE - 20 real-world test types, but no real patient results
INSERT INTO TESTTYPE (TestTypeID, TestCode, TestName, Category, DefaultUnit) VALUES
( 1, 'GLU',   'Glucose',               'Chemistry',     'mg/dL'),
( 2, 'HGB',   'Hemoglobin',            'Hematology',   'g/dL'),
( 3, 'WBC',   'White Blood Cells',     'Hematology',   '10^3/uL'),
( 4, 'PLT',   'Platelets',             'Hematology',   '10^3/uL'),
( 5, 'CREA',  'Creatinine',            'Chemistry',    'mg/dL'),
( 6, 'NA',    'Sodium',                'Chemistry',    'mmol/L'),
( 7, 'K',     'Potassium',             'Chemistry',    'mmol/L'),
( 8, 'CA',    'Calcium',               'Chemistry',    'mg/dL'),
( 9, 'ALT',   'Alanine Transaminase',  'Liver',        'U/L'),
(10, 'AST',   'Aspartate Transaminase','Liver',        'U/L'),
(11, 'CRP',   'C-Reactive Protein',    'Inflammation', 'mg/L'),
(12, 'CHOL',  'Total Cholesterol',     'Lipids',       'mg/dL'),
(13, 'HDL',   'HDL Cholesterol',       'Lipids',       'mg/dL'),
(14, 'LDL',   'LDL Cholesterol',       'Lipids',       'mg/dL'),
(15, 'TRIG',  'Triglycerides',         'Lipids',       'mg/dL'),
(16, 'TSH',   'Thyroid Stimulating Hormone', 'Hormones', 'mIU/L'),
(17, 'VITD',  'Vitamin D',            'Vitamins',     'ng/mL'),
(18, 'HBA1C', 'Hemoglobin A1c',        'Chemistry',    '%'),
(19, 'UCULT', 'Urine Culture',         'Microbiology', NULL),
(20, 'BTYPE', 'Blood Type',            'Immunology',   NULL);

-- 4. LABTECHNICIAN - 80 fictional laboratory workers
INSERT INTO LABTECHNICIAN (TechnicianID, FirstName, LastName, CertificationNumber, Phone)
SELECT
    i,
    (ARRAY['Gal','Ruth','Niv','Lital','Sivan','Bar','Tali','Yoni'])[((i - 1) % 8) + 1],
    (ARRAY['Levin','Mori','Segal','Oren','Shahaf','Dagan','Raviv','Eyal'])[((i * 3 - 1) % 8) + 1],
    'CERT' || LPAD(i::text, 6, '0'),
    '054' || LPAD(i::text, 7, '0')
FROM generate_series(1, 80) AS g(i);

-- 5. TESTORDER - 5,000 orders; parent patient and doctor records exist
INSERT INTO TESTORDER (OrderID, OrderedAt, Priority, Notes, PatientID, DoctorID)
SELECT
    i,
    TIMESTAMP '2026-01-01 07:00:00'
        + ((i - 1) % 300) * INTERVAL '1 day'
        + (i % 15) * INTERVAL '10 minutes',
    CASE WHEN i % 25 = 0 THEN 'STAT'
         WHEN i % 7 = 0 THEN 'Urgent'
         ELSE 'Routine' END,
    CASE WHEN i % 11 = 0 THEN 'Fasting recommended (demo order)'
         ELSE 'Routine laboratory request (demo order)' END,
    ((i * 17 - 1) % 3000) + 1,
    ((i * 13 - 1) % 120) + 1
FROM generate_series(1, 5000) AS g(i);

-- 6. LABTEST - exactly 2 lab tests per order = 10,000 tests
-- 80% Completed; 10% InProgress; 10% Scheduled.
-- Technician is optional (NULL on Scheduled tests).
INSERT INTO LABTEST
    (LabTestID, Status, PerformedLocation, ScheduledAt, StartedAt,
     CompletedAt, OrderID, TestTypeID, TechnicianID)
SELECT
    g.i,
    CASE WHEN g.i % 10 = 0 THEN 'Scheduled'
         WHEN g.i % 10 = 1 THEN 'InProgress'
         ELSE 'Completed' END,
    CASE WHEN g.i % 5 = 0 THEN 'Chemistry Laboratory'
         WHEN g.i % 5 = 1 THEN 'Hematology Laboratory'
         ELSE 'Central Laboratory' END,
    o.OrderedAt + INTERVAL '1 day' + (g.i % 5) * INTERVAL '1 hour',
    CASE WHEN g.i % 10 = 0 THEN NULL
         ELSE o.OrderedAt + INTERVAL '1 day' + (g.i % 5) * INTERVAL '1 hour' + INTERVAL '30 minutes' END,
    CASE WHEN g.i % 10 IN (0, 1) THEN NULL
         ELSE o.OrderedAt + INTERVAL '1 day' + (g.i % 5) * INTERVAL '1 hour' + INTERVAL '90 minutes' END,
    o.OrderID,
    ((g.i * 7 + (g.i / 20)) % 20) + 1,
    CASE WHEN g.i % 10 = 0 THEN NULL ELSE ((g.i * 11 - 1) % 80) + 1 END
FROM generate_series(1, 10000) AS g(i)
JOIN TESTORDER AS o ON o.OrderID = ((g.i + 1) / 2);

-- 7. TESTRESULT - 8,000 results for the 8,000 completed tests
-- NumericValue OR TextValue is populated, based on test type.
INSERT INTO TESTRESULT
    (ResultID, NumericValue, TextValue, Unit, ResultedAt, IsAbnormal, LabTestID)
SELECT
    ROW_NUMBER() OVER (ORDER BY lt.LabTestID)::integer,
    CASE WHEN lt.TestTypeID >= 19 THEN NULL
         ELSE ROUND((CASE lt.TestTypeID
              WHEN  1 THEN  65 + lt.LabTestID % 100
              WHEN  2 THEN  10 + (lt.LabTestID % 80) / 10.0
              WHEN  3 THEN   3 + (lt.LabTestID % 110) / 10.0
              WHEN  4 THEN 100 + lt.LabTestID % 400
              WHEN  5 THEN 0.5 + (lt.LabTestID % 18) / 10.0
              WHEN  6 THEN 130 + lt.LabTestID % 20
              WHEN  7 THEN   3 + (lt.LabTestID % 25) / 10.0
              WHEN  8 THEN   8 + (lt.LabTestID % 30) / 10.0
              WHEN  9 THEN   8 + lt.LabTestID % 110
              WHEN 10 THEN  10 + lt.LabTestID % 100
              WHEN 11 THEN   1 + lt.LabTestID % 50
              WHEN 12 THEN 130 + lt.LabTestID % 180
              WHEN 13 THEN  25 + lt.LabTestID % 70
              WHEN 14 THEN  60 + lt.LabTestID % 160
              WHEN 15 THEN  60 + lt.LabTestID % 220
              WHEN 16 THEN 0.2 + (lt.LabTestID % 80) / 10.0
              WHEN 17 THEN   8 + lt.LabTestID % 70
              WHEN 18 THEN 4.5 + (lt.LabTestID % 45) / 10.0
              END)::numeric, 3)
    END,
    CASE WHEN lt.TestTypeID = 19 THEN
              CASE WHEN lt.LabTestID % 7 = 0 THEN 'Growth detected' ELSE 'No growth' END
         WHEN lt.TestTypeID = 20 THEN
              (ARRAY['O+','A+','B+','AB+','O-','A-','B-','AB-'])[((lt.LabTestID - 1) % 8) + 1]
         ELSE NULL END,
    tt.DefaultUnit,
    lt.CompletedAt + (lt.LabTestID % 120) * INTERVAL '1 minute',
    CASE WHEN lt.TestTypeID = 20 THEN FALSE
         WHEN lt.TestTypeID = 19 THEN lt.LabTestID % 7 = 0
         ELSE (lt.LabTestID % 7 = 0 OR lt.LabTestID % 13 = 0) END,
    lt.LabTestID
FROM LABTEST AS lt
JOIN TESTTYPE AS tt ON tt.TestTypeID = lt.TestTypeID
WHERE lt.Status = 'Completed';

-- 8. LABALERT - one alert for each flagged abnormal result
INSERT INTO LABALERT
    (AlertID, Severity, Message, CreatedAt, Status, AcknowledgedAt, ResultID)
SELECT
    ROW_NUMBER() OVER (ORDER BY tr.ResultID)::integer,
    CASE WHEN tr.ResultID % 17 = 0 THEN 'Critical'
         WHEN tr.ResultID % 5 = 0 THEN 'High'
         WHEN tr.ResultID % 2 = 0 THEN 'Medium'
         ELSE 'Low' END,
    'Demo alert: abnormal result for lab test #' || tr.LabTestID || '. Review required.',
    tr.ResultedAt + INTERVAL '10 minutes',
    CASE WHEN tr.ResultID % 4 = 0 THEN 'Resolved'
         WHEN tr.ResultID % 4 = 1 THEN 'Acknowledged'
         ELSE 'Open' END,
    CASE WHEN tr.ResultID % 4 IN (0, 1)
         THEN tr.ResultedAt + INTERVAL '2 hours' ELSE NULL END,
    tr.ResultID
FROM TESTRESULT AS tr
WHERE tr.IsAbnormal = TRUE;

-- Because explicit primary-key values were used, synchronize the
-- identity sequences so future INSERTs without an ID do not conflict.
SELECT setval(pg_get_serial_sequence('patient', 'patientid'), (SELECT MAX(patientid) FROM patient), TRUE);
SELECT setval(pg_get_serial_sequence('doctor', 'doctorid'), (SELECT MAX(doctorid) FROM doctor), TRUE);
SELECT setval(pg_get_serial_sequence('testtype', 'testtypeid'), (SELECT MAX(testtypeid) FROM testtype), TRUE);
SELECT setval(pg_get_serial_sequence('labtechnician', 'technicianid'), (SELECT MAX(technicianid) FROM labtechnician), TRUE);
SELECT setval(pg_get_serial_sequence('testorder', 'orderid'), (SELECT MAX(orderid) FROM testorder), TRUE);
SELECT setval(pg_get_serial_sequence('labtest', 'labtestid'), (SELECT MAX(labtestid) FROM labtest), TRUE);
SELECT setval(pg_get_serial_sequence('testresult', 'resultid'), (SELECT MAX(resultid) FROM testresult), TRUE);
SELECT setval(pg_get_serial_sequence('labalert', 'alertid'), (SELECT MAX(alertid) FROM labalert), TRUE);

COMMIT;
