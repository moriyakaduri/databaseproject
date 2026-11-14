"""Reconcile report with measured evidence; preserve historical Stage A files."""
from pathlib import Path
import json
import re

B=Path(__file__).resolve().parent.parent
A=B.parent/'שלב א'
ROOT=B.parent.parent

# Q4 presents patient reach in addition to test volume, joining three tables.
for path in [B/'Queries.sql',B/'README.md']:
    s=path.read_text(encoding='utf-8')
    s=s.replace('tt.category, COUNT(l.labtestid) AS test_count\n FROM testtype tt LEFT JOIN labtest l USING(testtypeid)',
                'tt.category, COUNT(l.labtestid) AS test_count,\n        COUNT(DISTINCT o.patientid) AS patient_count\n FROM testtype tt LEFT JOIN labtest l USING(testtypeid)\n LEFT JOIN testorder o USING(orderid)')
    s=s.replace('tt.category, COUNT(l.labtestid) AS test_count,\n        AVG',
                'tt.category, COUNT(l.labtestid) AS test_count,\n        COUNT(DISTINCT o.patientid) AS patient_count,\n        AVG')
    s=s.replace('AVG(COUNT(l.labtestid)) OVER () AS mean_count\n FROM testtype tt LEFT JOIN labtest l USING(testtypeid)',
                'AVG(COUNT(l.labtestid)) OVER () AS mean_count\n FROM testtype tt LEFT JOIN labtest l USING(testtypeid)\n LEFT JOIN testorder o USING(orderid)')
    s=s.replace('SELECT testtypeid,testname,category,test_count FROM counts',
                'SELECT testtypeid,testname,category,test_count,patient_count FROM counts')
    s=s.replace('מוריה כדורי והשותפה — **[להשלים שמות ופרטי הגשה מאומתים]**', 'נועה מנוסה ומוריה כדורי (לפי דוח שלב א׳)')
    path.write_text(s,encoding='utf-8')

corrections='''# תיקוני שלב א׳ — 12.11.2026

אין טבלת DAT/Date בסכמה. נשמרו שמונה הטבלאות וכל המפתחות והקשרים. `patient.dateofbirth` נשאר DATE. נוספה עמודה שנייה משמעותית מסוג DATE:

```sql
-- בתוך CREATE TABLE LABTECHNICIAN, אחרי CertificationNumber:
CertificationExpiresOn DATE NOT NULL,
```

בבסיס קיים משתמשים פעם אחת ב-[StageA_Migration.sql](StageA_Migration.sql), אחרי גיבוי. הקובץ נבדק על עותק של הבסיס המקורי. בבסיס ריק משתמשים ב-createTables.sql המעודכן; אין להריץ את המיגרציה לאחריו, כי העמודה כבר קיימת. אין ערך DEFAULT קבוע לתוקף רישיון; האכלוס מספק תאריכים מפורשים.

## התאמת האכלוס

1. `SQLInsert/baseSeed.sql`: נוספה CertificationExpiresOn לרשימת עמודות הכנסת הטכנאים, ונוסף הביטוי `DATE '2026-01-01' + (365 + i % 730)` ל-SELECT.
2. `DataImportFiles/technicians.csv`: נוספה עמודת certificationexpireson עם אותו חישוב לפי מזהה הטכנאי; 420 הרשומות והערכים הישנים נשמרו.
3. `DataImportFiles/import.sql`: נוספה certificationexpireson לרשימת עמודות COPY.
4. `Programing/generate_data.py` ו-generated.sql אינם מכניסים טכנאים, ולכן אין צורך לשנותם. ספירות הפלט נשמרו.

לא שונו TIMESTAMP ל-DATE, כדי לא לאבד שעות הזמנה, התחלה, סיום ותוצאות. TEXT ו-BOOLEAN הם טיפוסי PostgreSQL מתאימים להערות ארוכות ולדגלים; מספרי טלפון ומספרי זיהוי נשארים VARCHAR לשמירת אפסים מובילים. הערך המספרי של התוצאה נשאר NUMERIC(12,3).

## ERD / DSD

בישות LabTechnician יש להוסיף מאפיין רגיל CertificationExpiresOn. בטבלת LABTECHNICIAN בתרשים DSD יש להוסיף עמודה באותו שם, טיפוס DATE, חובה, ללא PK/FK/UNIQUE. אין שינוי בקשרים או בריבוי. בקובצי DSD המקוריים יש טיפוסי INT כמצייני מקום גם לשדות אחרים; לפני ייצוא התרשים המעודכן יש להתאים את הטיפוסים ל-createTables.sql, לרבות DATE לתאריך לידה, VARCHAR למחרוזות ו-NUMERIC לערך תוצאה.

קובצי התרשימים והתמונות המקוריים נשמרו. עדיין נדרש עדכון וייצוא ב-ERDPlus, ובדיקה חזותית של approved-erd.jpeg ושל approved-dsd.png. אין לייחס לתמונות הישנות אישור לתוספת החדשה.

## בדיקה שנערכה

הקמה מאפס ב-PostgreSQL 16.15: patient=3,000; doctor=500; testtype=500; labtechnician=500; testorder=5,000; labtest=30,000; testresult=24,000; labalert=3,157. סך הכול 66,657. נבדקו מפתחות, NULL, אילוצים, מועדים וקשרים. המיגרציה נבדקה על עותק נפרד ונמצאה משמרת כל ערך קודם. בסיס הנתונים המקורי לא שונה.

ניתוח 3NF וההנחות העסקיות מפורטים ב-[דוח שלב ב׳](README.md). הגיבויים והראיות הישנים נשמרו כגרסה היסטורית; backup2 הוא גיבוי מעודכן של בסיס הבדיקה החדש.
'''
(B/'StageAChanges.md').write_text(corrections,encoding='utf-8')

p=A/'DataDictionary.md'
s=p.read_text(encoding='utf-8-sig')
row='| certificationexpireson | היום האחרון לתוקף הסמכת הטכנאי; נוסף בתיקון שלב א׳ 12.11.2026 | DATE | לא | — | — | — | — | — |'
if row not in s:
    section=s.index('## LABTECHNICIAN')
    end=s.index('\n## ',section+1)
    s=s[:end].rstrip()+'\n'+row+'\n'+s[end:]
    s=s.replace('הופק מהקטלוג החי', 'עדכון 12.11.2026: נוספה certificationexpireson מסוג DATE NOT NULL ונבדקה בבסיס בדיקה נפרד. הקטלוג ההיסטורי והתרשימים הישנים טרם שונו.\n\nהופק מהקטלוג החי',1)
    p.write_text(s,encoding='utf-8')

for p,notice in [
 (ROOT/'README.md','**עדכון 12.11.2026:** [דוח שלב ב׳ וקובצי SQL](DBProject_216217489_326335387/שלב%20ב/README.md), [תיקוני שלב א׳](DBProject_216217489_326335387/שלב%20ב/StageAChanges.md). הדוח שלהלן מתעד את הגשת שלב א׳ המקורית. הקוד המעודכן מוסיף תוקף הסמכה מסוג DATE; התמונות והגיבויים הישנים נשמרו כראיות היסטוריות. צילומי pgAdmin החדשים וייצוא התרשימים עדיין חסרים.'),
 (A/'README.md','**עדכון 12.11.2026:** [תיקוני שלב א׳](../שלב%20ב/StageAChanges.md) ו-[דוח שלב ב׳](../שלב%20ב/README.md). נוספה עמודת תוקף הסמכה מסוג DATE והאכלוס עודכן. הדוח והתמונות שלהלן מתעדים את הגרסה המקורית; עדיין דרוש ייצוא תרשימים מעודכנים.')]:
    s=p.read_text(encoding='utf-8-sig')
    if notice not in s: p.write_text(notice+'\n\n'+s,encoding='utf-8')
print('Report structure, Stage A dictionary and navigation updated.')
