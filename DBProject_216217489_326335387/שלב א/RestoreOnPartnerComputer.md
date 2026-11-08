# שחזור במחשב השותפה — לביצוע ואימות

**מצב: טרם בוצע במחשב אחר.** ההוראות מיועדות למחשב שבו מותקן Docker עם PostgreSQL 16, או PostgreSQL 16 עם psql ו־pg_restore. אין להשתמש בבסיס נתונים קיים שמכיל מידע שרוצים לשמור.

## אפשרות א׳ — מכולת PostgreSQL 16 קיימת

1. להעביר למחשב השותפה את תיקיית `שלב א`, לרבות Backup ו־audit.
2. לפתוח PowerShell בתיקיית `שלב א`.
3. לבחור את שם המכולה המקומית (בהוראות להלן `postgres_db`). אם השם שונה, להחליף רק את שם המכולה בפקודות.
4. לבצע העתקת גיבוי והבדיקות:

```powershell
docker cp ./Backup/backup_cli_2026-11-08.dump postgres_db:/tmp/partner_restore.dump
docker cp ./audit/validate.sql postgres_db:/tmp/partner_validate.sql
docker exec postgres_db sh -c 'createdb -U "$POSTGRES_USER" stage_a_partner_restore'
docker exec postgres_db sh -c 'pg_restore -U "$POSTGRES_USER" -d stage_a_partner_restore --no-owner --no-privileges --exit-on-error /tmp/partner_restore.dump'
docker exec postgres_db sh -c 'psql -U "$POSTGRES_USER" -d stage_a_partner_restore -v ON_ERROR_STOP=1 -f /tmp/partner_validate.sql' | Tee-Object -FilePath ./audit/partner_restore_result.txt
```

אם בסיס בשם זה כבר קיים, יש לבחור שם חדש במקום `stage_a_partner_restore` בכל הפקודות. אין למחוק בסיס קיים כדי לפנות את השם. פקודות createdb ו־pg_restore צריכות להסתיים ללא שגיאה.

## אפשרות ב׳ — PostgreSQL מקומי

```powershell
createdb -U YOUR_LOCAL_USER stage_a_partner_restore
pg_restore -U YOUR_LOCAL_USER -d stage_a_partner_restore --no-owner --no-privileges --exit-on-error Backup/backup_cli_2026-11-08.dump
psql -U YOUR_LOCAL_USER -d stage_a_partner_restore -v ON_ERROR_STOP=1 -f audit/validate.sql | Tee-Object -FilePath audit/partner_restore_result.txt
```

להחליף YOUR_LOCAL_USER בשם המשתמש המקומי. אין להכניס סיסמאות לקובצי ההגשה או לצילומים.

## תוצאות צפויות

| טבלה | רשומות |
|---|---:|
| PATIENT | 3,000 |
| DOCTOR | 500 |
| TESTTYPE | 500 |
| LABTECHNICIAN | 500 |
| TESTORDER | 5,000 |
| LABTEST | 30,000 |
| TESTRESULT | 24,000 |
| LABALERT | 3,157 |

יש לראות הודעת PASS מבדיקות המבנה, תשע בדיקות תאריכים/סטטוסים עם אפס הפרות, ו־24,000 שורות בשאילתת JOIN המסכמת. יש לצלם במחשב השותפה את תהליך השחזור והספירות, לשמור בתיקיית screenshots עם שם שמציין partner, ולשמור את יומן הפלט. רק לאחר בדיקה של הקבצים האלה אפשר לעדכן את סעיף השחזור במחשב אחר כהושלם. מחשב זהה עם בסיס נתונים זמני נוסף אינו מהווה מחשב אחר.
