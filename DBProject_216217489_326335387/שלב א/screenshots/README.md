# צילומי הוכחה

הקבצים הם צילומי מסך אמיתיים שנשמרו לאחר צפייה בהם. אין כאן הדמיה של חלון מסוף או הודעת הצלחה.

- `pgadmin-backup-details.jpg`: הודעת Successfully completed בממשק pgAdmin ותוכן תהליך pg_dump.
- `pgadmin-backup-finished.jpg`: רשומת תהליך הגיבוי בממשק pgAdmin.
- `validation-log.jpg`: תצוגת יומן פלט בדיקות PostgreSQL שנשמר, כולל הספירות ותשע בדיקות תאריכים/סטטוסים.
- `method1-sql-log.jpg`: יומן הרצת SQL שמור, עם INSERT 0 380, INSERT 0 480 ו־COMMIT.
- `method3-csv-log.jpg`: יומן ייבוא CSV שמור, עם COPY 420 ו־COMMIT.
- `method2-python-insert-log.jpg`: פלט INSERT באצוות של SQL שנוצר ב־Python.
- `method2-python-commit-log.jpg`: סוף אותו יומן, כולל סנכרון המזהים ו־COMMIT.
- `python-generation-log.jpg`: פלט הרצה חוזרת של תוכנית Python, כמויות וטביעת SHA-256 המאשרת פלט זהה לקובץ האכלוס.
- `restore-cli-log.jpg`: יומן אימות שחזור גיבוי CLI לבסיס נתונים נפרד.
- `restore-pgadmin-log.jpg`: יומן אימות שחזור קובץ הגיבוי שהופק ב־pgAdmin לבסיס נתונים נפרד.

צילומי VS Code מציגים את יומני ההרצה המקוריים שנשמרו בקבצים, ולא צילום מסוף בזמן ההכנסה המקורית. קובצי הטקסט, קוד המקור ופלט SQL מצורפים בנפרד כדי לאפשר בדיקה ושחזור. צילום גיבוי pgAdmin הוא של הממשק שבו בוצעה הפעולה עצמה.

אין צילומי AI Studio, משום שהמשתמשת הורתה לדלג על שלב זה. אין צילומי מחשב השותפה, משום שהשחזור שם טרם בוצע.

- create-drop-temporary-log.jpg: יומן בדיקת CREATE ו־DROP בבסיס זמני בלבד; בסיום נותרו אפס טבלאות public.
