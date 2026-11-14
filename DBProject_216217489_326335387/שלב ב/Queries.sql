-- PostgreSQL; כל SELECT עצמאי. תאריכי הסינון קבועים לשחזור התוצאות.

-- Q1A: עומס חודשי לרופא — צבירה אחת לאחר צירוף.
SELECT d.doctorid, d.firstname, d.lastname,
       EXTRACT(YEAR FROM o.orderedat)::int AS order_year,
       EXTRACT(MONTH FROM o.orderedat)::int AS order_month,
       COUNT(*) AS test_count,
       COUNT(*) FILTER (WHERE l.status='Completed') AS completed_count
FROM doctor d JOIN testorder o USING(doctorid) JOIN labtest l USING(orderid)
GROUP BY d.doctorid, EXTRACT(YEAR FROM o.orderedat), EXTRACT(MONTH FROM o.orderedat)
ORDER BY order_year, order_month, d.doctorid;

-- Q1B: אותו פלט באמצעות תתי־שאילתות מתואמות לכל רופא וחודש.
-- A צפויה להיות יעילה יותר: צבירה לאחר מעבר משותף לעומת שתי ספירות חוזרות לכל רופא וחודש ב-B. יש למדוד; אינדקסים ותוכנית המתכנן יכולים לשנות זאת.
WITH months AS (
 SELECT DISTINCT d.doctorid, d.firstname, d.lastname,
        EXTRACT(YEAR FROM o.orderedat)::int AS order_year,
        EXTRACT(MONTH FROM o.orderedat)::int AS order_month
 FROM doctor d JOIN testorder o USING(doctorid) JOIN labtest l USING(orderid)
)
SELECT m.*,
 (SELECT COUNT(*) FROM testorder o JOIN labtest l USING(orderid)
  WHERE o.doctorid=m.doctorid AND EXTRACT(YEAR FROM o.orderedat)=m.order_year
    AND EXTRACT(MONTH FROM o.orderedat)=m.order_month) AS test_count,
 (SELECT COUNT(*) FROM testorder o JOIN labtest l USING(orderid)
  WHERE o.doctorid=m.doctorid AND EXTRACT(YEAR FROM o.orderedat)=m.order_year
    AND EXTRACT(MONTH FROM o.orderedat)=m.order_month
    AND l.status='Completed') AS completed_count
FROM months m ORDER BY order_year, order_month, doctorid;

-- Q2A: התראות פתוחות למטופל — צבירה ו-HAVING.
SELECT p.patientid, p.firstname, p.lastname, COUNT(*) AS open_alerts,
       COUNT(*) FILTER (WHERE a.severity IN ('High','Critical')) AS high_alerts
FROM patient p JOIN testorder o USING(patientid) JOIN labtest l USING(orderid)
JOIN testresult r USING(labtestid) JOIN labalert a USING(resultid)
WHERE a.status='Open'
GROUP BY p.patientid HAVING COUNT(*)>=2
ORDER BY open_alerts DESC, p.patientid;

-- Q2B: אותו פלט באמצעות חישוב מתואם לכל מטופל וסינון חיצוני.
-- A צפויה להיות יעילה יותר באכלוס הנוכחי: מסננים התראות ומקבצים פעם אחת. B עשויה לבצע שתי ספירות לכל מטופל, כולל מטופלים ללא התראות. יש לאמת ב-EXPLAIN ANALYZE.
WITH totals AS (
 SELECT p.patientid, p.firstname, p.lastname,
 (SELECT COUNT(*) FROM testorder o JOIN labtest l USING(orderid)
  JOIN testresult r USING(labtestid) JOIN labalert a USING(resultid)
  WHERE o.patientid=p.patientid AND a.status='Open') AS open_alerts,
 (SELECT COUNT(*) FROM testorder o JOIN labtest l USING(orderid)
  JOIN testresult r USING(labtestid) JOIN labalert a USING(resultid)
  WHERE o.patientid=p.patientid AND a.status='Open'
    AND a.severity IN ('High','Critical')) AS high_alerts
 FROM patient p
)
SELECT * FROM totals WHERE open_alerts>=2 ORDER BY open_alerts DESC, patientid;

-- Q3A: התוצאה האחרונה לכל מטופל — פונקציית חלון ושובר שוויון ResultID.
WITH ranked AS (
 SELECT p.patientid, p.firstname, p.lastname, tt.testname,
        r.resultid, r.resultedat, r.numericvalue, r.textvalue, r.isabnormal,
        ROW_NUMBER() OVER (PARTITION BY p.patientid
                          ORDER BY r.resultedat DESC, r.resultid DESC) AS rn
 FROM patient p JOIN testorder o USING(patientid) JOIN labtest l USING(orderid)
 JOIN testtype tt USING(testtypeid) JOIN testresult r USING(labtestid)
)
SELECT patientid, firstname, lastname, testname, resultid, resultedat,
       numericvalue, textvalue, isabnormal
FROM ranked WHERE rn=1 ORDER BY patientid;

-- Q3B: אותו פלט באמצעות NOT EXISTS של תוצאה מאוחרת יותר, כולל שובר שוויון.
-- A ממיינת את קבוצות המטופלים פעם אחת. B בודקת היעדר תוצאה מאוחרת לכל מועמד; המתכנן עשוי להפוך זאת ל-Anti Join. A אינה תמיד מהירה יותר: יש להשוות בפועל ולשמור על שובר השוויון.
SELECT p.patientid, p.firstname, p.lastname, tt.testname,
       r.resultid, r.resultedat, r.numericvalue, r.textvalue, r.isabnormal
FROM patient p JOIN testorder o USING(patientid) JOIN labtest l USING(orderid)
JOIN testtype tt USING(testtypeid) JOIN testresult r USING(labtestid)
WHERE NOT EXISTS (
 SELECT 1 FROM testorder o2 JOIN labtest l2 USING(orderid)
 JOIN testresult r2 USING(labtestid)
 WHERE o2.patientid=p.patientid
   AND (r2.resultedat,r2.resultid)>(r.resultedat,r.resultid)
)
ORDER BY p.patientid;

-- Q4A: סוגי בדיקות שעומסם מעל ממוצע הקטלוג — CTE ותת־שאילתה.
WITH counts AS (
 SELECT tt.testtypeid, tt.testname, tt.category, COUNT(l.labtestid) AS test_count,
        COUNT(DISTINCT o.patientid) AS patient_count
 FROM testtype tt LEFT JOIN labtest l USING(testtypeid)
 LEFT JOIN testorder o USING(orderid)
 GROUP BY tt.testtypeid
)
SELECT * FROM counts WHERE test_count>(SELECT AVG(test_count) FROM counts)
ORDER BY test_count DESC, testtypeid;

-- Q4B: אותו פלט באמצעות AVG בחלון; הממוצע כולל גם סוגים ללא בדיקות.
-- שתי הדרכים צוברות פעם אחת. A עשויה לממש CTE ולסרוק אותו שוב לחישוב ממוצע; B מוסיפה WindowAgg ללא סריקה חוזרת מפורשת. B צפויה לחסוך מעט עבודה, אך בקטלוג קטן ההפרש עשוי להיות זניח או הפוך.
WITH counts AS (
 SELECT tt.testtypeid, tt.testname, tt.category, COUNT(l.labtestid) AS test_count,
        COUNT(DISTINCT o.patientid) AS patient_count,
        AVG(COUNT(l.labtestid)) OVER () AS mean_count
 FROM testtype tt LEFT JOIN labtest l USING(testtypeid)
 LEFT JOIN testorder o USING(orderid)
 GROUP BY tt.testtypeid
)
SELECT testtypeid,testname,category,test_count,patient_count FROM counts
WHERE test_count>mean_count ORDER BY test_count DESC,testtypeid;

-- Q5: פילוח הזמנות לפי יום, חודש, שנה ועדיפות, כולל מטופלים ורופאים ייחודיים.
SELECT EXTRACT(YEAR FROM o.orderedat)::int AS order_year,
       EXTRACT(MONTH FROM o.orderedat)::int AS order_month,
       EXTRACT(DAY FROM o.orderedat)::int AS order_day, o.priority,
       COUNT(DISTINCT o.orderid) AS order_count,
       COUNT(DISTINCT p.patientid) AS patient_count,
       COUNT(DISTINCT d.doctorid) AS doctor_count
FROM testorder o JOIN patient p USING(patientid) JOIN doctor d USING(doctorid)
GROUP BY 1,2,3,o.priority ORDER BY 1,2,3,o.priority;

-- Q6: תוקף הסמכת טכנאים ועומס — תאריך ייחוס קבוע שניתן להחליף במסך.
SELECT t.technicianid,t.firstname,t.lastname,t.certificationexpireson,
       EXTRACT(YEAR FROM t.certificationexpireson)::int AS expiry_year,
       EXTRACT(MONTH FROM t.certificationexpireson)::int AS expiry_month,
       t.certificationexpireson-DATE '2026-11-12' AS days_until_expiry,
       COUNT(l.labtestid) AS assigned_tests,
       COUNT(DISTINCT o.patientid) AS patients
FROM labtechnician t LEFT JOIN labtest l USING(technicianid)
LEFT JOIN testorder o USING(orderid)
WHERE t.certificationexpireson<=DATE '2026-11-12'+450
GROUP BY t.technicianid ORDER BY t.certificationexpireson,t.technicianid;

-- Q7: תור הזמנות עם בדיקות ממתינות; סינון הזמנות שעומסן מעל הממוצע.
WITH pending AS (
 SELECT o.orderid,p.firstname,p.lastname,d.firstname AS doctor_firstname,
        d.lastname AS doctor_lastname,o.priority,o.orderedat,
        COUNT(*) AS pending_tests
 FROM testorder o JOIN patient p USING(patientid) JOIN doctor d USING(doctorid)
 JOIN labtest l USING(orderid)
 WHERE l.status IN ('Scheduled','InProgress')
 GROUP BY o.orderid,p.patientid,d.doctorid
)
SELECT * FROM pending WHERE pending_tests>=(SELECT AVG(pending_tests) FROM pending)
ORDER BY pending_tests DESC,orderedat,orderid;

-- Q8: דוח חריגות לפי רופא וקטגוריה; EXISTS מונע הכפלת תוצאות עם כמה התראות.
SELECT d.doctorid,d.firstname,d.lastname,tt.category,
       COUNT(*) AS abnormal_results,
       COUNT(DISTINCT o.patientid) AS patients,
       MAX(r.resultedat) AS latest_abnormal
FROM doctor d JOIN testorder o USING(doctorid) JOIN labtest l USING(orderid)
JOIN testtype tt USING(testtypeid) JOIN testresult r USING(labtestid)
WHERE r.isabnormal AND EXISTS (
 SELECT 1 FROM labalert a WHERE a.resultid=r.resultid AND a.status='Open'
)
GROUP BY d.doctorid,tt.category HAVING COUNT(*)>=2
ORDER BY abnormal_results DESC,d.doctorid,tt.category;

-- הדגמות שינוי: כל יחידה עצמאית ומתבטלת ב-ROLLBACK.
-- בנתוני הדגמה בלבד אפשר להחליף ב-COMMIT לאחר בדיקת RETURNING.

-- D1: ניקוי התראות שטופלו לפני מועד הארכוב, רק אם הבדיקה הושלמה והתוצאה קיימת.
BEGIN;
DELETE FROM labalert a USING testresult r,labtest l
WHERE a.resultid=r.resultid AND r.labtestid=l.labtestid
  AND a.status IN ('Acknowledged','Resolved')
  AND a.acknowledgedat<TIMESTAMP '2026-07-01' AND l.status='Completed'
RETURNING a.alertid,a.resultid,a.status,a.acknowledgedat;
ROLLBACK;

-- D2: ניקוי בדיקות מתוכננות ישנות ללא תוצאה, רק בהזמנה המכילה בדיקה נוספת.
BEGIN;
DELETE FROM labtest l USING testorder o
WHERE l.orderid=o.orderid AND l.status='Scheduled'
  AND o.orderedat<TIMESTAMP '2026-04-01'
  AND NOT EXISTS (SELECT 1 FROM testresult r WHERE r.labtestid=l.labtestid)
  AND EXISTS (SELECT 1 FROM labtest other
              WHERE other.orderid=l.orderid AND other.labtestid<>l.labtestid
                AND other.status<>'Scheduled')
RETURNING l.labtestid,l.orderid,l.status,l.scheduledat;
ROLLBACK;

-- D3: ניקוי רופאי הדגמה ללא הזמנות, כשההתמחות עדיין מיוצגת בידי רופא אחר.
BEGIN;
DELETE FROM doctor d
WHERE d.licensenumber LIKE 'DEMO-LIC-%'
  AND NOT EXISTS (SELECT 1 FROM testorder o WHERE o.doctorid=d.doctorid)
  AND EXISTS (SELECT 1 FROM doctor active JOIN testorder o USING(doctorid)
              WHERE active.specialty=d.specialty AND active.doctorid<>d.doctorid)
RETURNING d.doctorid,d.firstname,d.lastname,d.specialty;
ROLLBACK;

-- U1: הסלמת עדיפות הזמנות עם התראות חמורות פתוחות; כלל הדגמה מנהלי.
BEGIN;
UPDATE testorder o SET priority='STAT'
WHERE o.priority<>'STAT' AND EXISTS (
 SELECT 1 FROM labtest l JOIN testresult r USING(labtestid)
 JOIN labalert a USING(resultid)
 WHERE l.orderid=o.orderid AND r.isabnormal AND a.status='Open'
   AND a.severity IN ('High','Critical')
)
RETURNING o.orderid,o.patientid,o.doctorid,o.priority;
ROLLBACK;

-- U2: סגירת התראות מאושרות ישנות של בדיקות שהושלמו; הדגמת מדיניות ארכוב בלבד.
BEGIN;
UPDATE labalert a SET status='Resolved'
FROM testresult r JOIN labtest l USING(labtestid) JOIN testorder o USING(orderid)
WHERE a.resultid=r.resultid AND a.status='Acknowledged'
  AND a.acknowledgedat<TIMESTAMP '2026-07-01'
  AND l.status='Completed' AND o.orderedat<r.resultedat
RETURNING a.alertid,a.resultid,a.status,a.acknowledgedat;
ROLLBACK;

-- U3: שיוך בדיקות מתוכננות לטכנאי בעל הסמכה בתוקף והעומס הנמוך ביותר.
BEGIN;
WITH candidate AS (
 SELECT t.technicianid FROM labtechnician t LEFT JOIN labtest l USING(technicianid)
 WHERE t.certificationexpireson>=DATE '2026-11-12'
 GROUP BY t.technicianid
 ORDER BY COUNT(l.labtestid) FILTER (WHERE l.status IN ('Scheduled','InProgress')),
          t.technicianid LIMIT 1
)
UPDATE labtest l SET technicianid=c.technicianid
FROM candidate c,testorder o
WHERE l.orderid=o.orderid AND l.status='Scheduled' AND l.technicianid IS NULL
  AND o.priority IN ('Urgent','STAT')
RETURNING l.labtestid,l.orderid,l.status,l.technicianid;
ROLLBACK;
