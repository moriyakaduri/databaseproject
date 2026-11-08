-- 4selectAll.sql
-- HOSPITAL LABORATORY - PostgreSQL 16 / pgAdmin
-- Read-only checks: these queries do not change any data.
-- Full SELECT for each table, followed by a limited JOIN example.
-- The full table reads can return tens of thousands of rows.

-- 1. Count the records in every table (at least 4 have >200 rows).
SELECT 'PATIENT' AS table_name, COUNT(*) AS row_count FROM PATIENT
UNION ALL SELECT 'DOCTOR', COUNT(*) FROM DOCTOR
UNION ALL SELECT 'TESTTYPE', COUNT(*) FROM TESTTYPE
UNION ALL SELECT 'LABTECHNICIAN', COUNT(*) FROM LABTECHNICIAN
UNION ALL SELECT 'TESTORDER', COUNT(*) FROM TESTORDER
UNION ALL SELECT 'LABTEST', COUNT(*) FROM LABTEST
UNION ALL SELECT 'TESTRESULT', COUNT(*) FROM TESTRESULT
UNION ALL SELECT 'LABALERT', COUNT(*) FROM LABALERT;

-- 2. Display a sample from each of the eight approved tables.
SELECT * FROM PATIENT ORDER BY PatientID;
SELECT * FROM DOCTOR ORDER BY DoctorID;
SELECT * FROM TESTTYPE ORDER BY TestTypeID;
SELECT * FROM LABTECHNICIAN ORDER BY TechnicianID;
SELECT * FROM TESTORDER ORDER BY OrderID;
SELECT * FROM LABTEST ORDER BY LabTestID;
SELECT * FROM TESTRESULT ORDER BY ResultID;
SELECT * FROM LABALERT ORDER BY AlertID;

-- 3. Example: show the order, patient, doctor, test, result and alert.
-- These are the existing tables and foreign keys from the approved DSD.
SELECT
    o.OrderID,
    p.FirstName AS patient_first_name,
    p.LastName AS patient_last_name,
    d.FirstName AS doctor_first_name,
    d.LastName AS doctor_last_name,
    tt.TestName,
    lt.Status AS labtest_status,
    tr.NumericValue,
    tr.TextValue,
    tr.IsAbnormal,
    a.Severity AS alert_severity
FROM TESTORDER AS o
JOIN PATIENT AS p ON p.PatientID = o.PatientID
JOIN DOCTOR AS d ON d.DoctorID = o.DoctorID
JOIN LABTEST AS lt ON lt.OrderID = o.OrderID
JOIN TESTTYPE AS tt ON tt.TestTypeID = lt.TestTypeID
LEFT JOIN TESTRESULT AS tr ON tr.LabTestID = lt.LabTestID
LEFT JOIN LABALERT AS a ON a.ResultID = tr.ResultID
ORDER BY o.OrderID, lt.LabTestID
LIMIT 100;
