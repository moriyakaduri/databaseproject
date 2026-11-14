# משיכה ושחזור אצל השותפה

המאגר המשותף: [databaseproject](https://github.com/moriyakaduri/databaseproject). גרסת ההגשה: `stage-b-2026-11-14`.

## משיכת הקבצים

מתוך עותק המאגר הקיים במחשב השותפה, לאחר שמירת שינויים מקומיים:

```powershell
git switch main
git pull --ff-only origin main
git fetch origin --tags
git show --no-patch stage-b-2026-11-14
```

אם Git מדווח על שינויים מקומיים או פיצול ענפים, יש לשמור ולשלב אותם לפני המשך. אין להשתמש ב-reset או force כדי לעקוף זאת. למחשב שאין בו עותק:

```powershell
git clone https://github.com/moriyakaduri/databaseproject.git
cd databaseproject
git fetch origin --tags
```

הדוח נמצא ב־`DBProject_216217489_326335387/שלב ב/README.md`, ונספח כל הצילומים ב־`screenshots/README.md`. משיכת Git מורידה את הקבצים; טעינת הגיבוי לבסיס הנתונים היא הפעולה הבאה.

## שחזור backup2 ב־pgAdmin

1. יש להתחבר לשרת PostgreSQL 16 או חדש יותר. הגיבוי הוא Custom format של PostgreSQL 16; אין לפתוח אותו כקובץ SQL.
2. צרי בסיס **חדש וריק** בשם `stage_b_partner_restore_20261114`. אין למחוק או לדרוס את בסיס הפרויקט הקיים.
3. לחצי עליו עם הכפתור הימני → Restore. בחרי `שלב ב/backup2.dump`, פורמט Custom. ב־Options סמני No owner ו־No privileges אם שמות המשתמשים שונים. השאירי Clean before restore כבוי.
4. הריצי Restore ובדקי שקוד הסיום הוא 0. פתחי Query Tool על הבסיס החדש והריצי את `PartnerValidation.sql` באמצעות psql, או ב־Query Tool לאחר הסרת שורת `\set ON_ERROR_STOP on` (זו פקודת psql).
5. שמרי צילום של סיום השחזור, הספירות ושלוש רשימות האילוצים/האינדקסים. תיעוד שחזור במחשב השותפה שנוסף לשלב א׳ מתייחס לגיבוי הקודם; הוא אינו ראיה לשחזור backup2.

אפשר גם להשתמש ב־PostgreSQL CLI מתוך תיקיית שלב ב׳ (החליפי `YOUR_POSTGRES_USER` בשם ההתחברות המקומי; הסיסמה מוזנת בבקשת הכלי):

```powershell
createdb -h localhost -U YOUR_POSTGRES_USER stage_b_partner_restore_20261114
pg_restore -h localhost -U YOUR_POSTGRES_USER --no-owner --no-privileges --exit-on-error -d stage_b_partner_restore_20261114 backup2.dump
psql -X -h localhost -U YOUR_POSTGRES_USER -d stage_b_partner_restore_20261114 -v ON_ERROR_STOP=on -f PartnerValidation.sql -L partner_backup2_validation.txt
```

## תוצאות צפויות

| טבלה | רשומות |
|---|---:|
| patient | 3000 |
| doctor | 500 |
| testtype | 500 |
| labtechnician | 500 |
| testorder | 5000 |
| labtest | 30000 |
| testresult | 24000 |
| labalert | 3157 |

נדרשים שני שדות DATE, שלושה אילוצים חדשים ושלושה אינדקסים חדשים. בסוף תופיע הודעת `PASS`. שמותיהם והגדרותיהם מוצגים על ידי קובץ הבדיקה. אין להריץ שוב את חלק הוספת האילוצים על backup2: הוא כבר מכיל אותם. SELECT נבחרים מתוך Queries.sql אפשר להריץ כרגיל.

SHA-256 של הגיבוי:

```text
6fcacd9ef01f0bad38d48ff35348453af207af81723bd78855ac054150ff6a98
```

לבדיקה ב־PowerShell:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath backup2.dump
```
