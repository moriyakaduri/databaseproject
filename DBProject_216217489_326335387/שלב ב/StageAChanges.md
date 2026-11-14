# תיקוני שלב א׳ — 12.11.2026

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
