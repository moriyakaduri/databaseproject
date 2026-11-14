-- על עותק בדיקה בלבד: DROP מסיר רק את שלושת האינדקסים בשמות של שלב ב׳.
-- אין לשנות enable_seqscan: המתכנן רשאי לבחור סריקה סדרתית.
-- יש להריץ מספר פעמים, להשוות חציון ו-BUFFERS, ולהביא בחשבון מטמון ועלות כתיבה.
ANALYZE;

-- idx_testorder_patient_date: חיפוש היסטוריית מטופל: מפתח מורכב לפי שוויון במטופל ואז טווח תאריכים ומיון.
DROP INDEX IF EXISTS idx_testorder_patient_date;
-- לפני
EXPLAIN (ANALYZE, BUFFERS)
SELECT o.orderid,o.orderedat,p.firstname,p.lastname,d.firstname AS doctor_firstname
FROM testorder o JOIN patient p USING(patientid) JOIN doctor d USING(doctorid)
WHERE o.patientid=17 AND o.orderedat>=TIMESTAMP '2026-01-01'
ORDER BY o.orderedat;
-- מדידה חוזרת בפועל, חציון 5 הרצות: לפני 0.637 ms; אחרי 0.189 ms.
CREATE INDEX idx_testorder_patient_date ON testorder(patientid,orderedat);
ANALYZE;
-- אחרי
EXPLAIN (ANALYZE, BUFFERS)
SELECT o.orderid,o.orderedat,p.firstname,p.lastname,d.firstname AS doctor_firstname
FROM testorder o JOIN patient p USING(patientid) JOIN doctor d USING(doctorid)
WHERE o.patientid=17 AND o.orderedat>=TIMESTAMP '2026-01-01'
ORDER BY o.orderedat;
-- אין הבטחה לשיפור: התוצאה נקבעת רק לפי המדידה בפועל.

-- idx_labtest_type_status: סינון לפי סוג בדיקה וסטטוס. הצירוף סלקטיבי יותר מכל סטטוס בפני עצמו.
DROP INDEX IF EXISTS idx_labtest_type_status;
-- לפני
EXPLAIN (ANALYZE, BUFFERS)
SELECT l.labtestid,tt.testname,l.status,o.orderid,o.orderedat
FROM labtest l JOIN testtype tt USING(testtypeid) JOIN testorder o USING(orderid)
WHERE l.testtypeid=25 AND l.status='Completed' ORDER BY l.labtestid;
-- מדידה חוזרת בפועל, חציון 5 הרצות: לפני 3.051 ms; אחרי 0.983 ms.
CREATE INDEX idx_labtest_type_status ON labtest(testtypeid,status);
ANALYZE;
-- אחרי
EXPLAIN (ANALYZE, BUFFERS)
SELECT l.labtestid,tt.testname,l.status,o.orderid,o.orderedat
FROM labtest l JOIN testtype tt USING(testtypeid) JOIN testorder o USING(orderid)
WHERE l.testtypeid=25 AND l.status='Completed' ORDER BY l.labtestid;
-- אין הבטחה לשיפור: התוצאה נקבעת רק לפי המדידה בפועל.

-- idx_labalert_open_created: אינדקס חלקי לתור התראות פתוחות בטווח תאריכים; קטן מאינדקס כל ההתראות.
DROP INDEX IF EXISTS idx_labalert_open_created;
-- לפני
EXPLAIN (ANALYZE, BUFFERS)
SELECT a.alertid,a.severity,a.createdat,r.isabnormal,l.labtestid
FROM labalert a JOIN testresult r USING(resultid) JOIN labtest l USING(labtestid)
WHERE a.status='Open' AND a.createdat>=TIMESTAMP '2026-06-01'
 AND a.createdat<TIMESTAMP '2026-06-08' ORDER BY a.createdat;
-- מדידה חוזרת בפועל, חציון 5 הרצות: לפני 0.841 ms; אחרי 0.522 ms.
CREATE INDEX idx_labalert_open_created ON labalert(createdat) WHERE status='Open';
ANALYZE;
-- אחרי
EXPLAIN (ANALYZE, BUFFERS)
SELECT a.alertid,a.severity,a.createdat,r.isabnormal,l.labtestid
FROM labalert a JOIN testresult r USING(resultid) JOIN labtest l USING(labtestid)
WHERE a.status='Open' AND a.createdat>=TIMESTAMP '2026-06-01'
 AND a.createdat<TIMESTAMP '2026-06-08' ORDER BY a.createdat;
-- אין הבטחה לשיפור: התוצאה נקבעת רק לפי המדידה בפועל.
