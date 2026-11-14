"""Write measured values into the report, without fabricating screenshots."""
from pathlib import Path
import json

B=Path(__file__).resolve().parent.parent
data=json.loads((B/'audit/verification.json').read_text())
idx=data['index_timings']; qt=data['query_execution_ms']
index=B/'Index.sql'
old=index.read_text(encoding='utf-8')
s=old
for name,t in idx.items():
    needle='CREATE INDEX '+name+' ON '
    comment=f"-- מדידה חוזרת בפועל, חציון 5 הרצות: לפני {t['median_before_ms']:.3f} ms; אחרי {t['median_after_ms']:.3f} ms.\n"
    if comment not in s: s=s.replace(needle,comment+needle)
index.write_text(s,encoding='utf-8')

p=B/'README.md'
doc=p.read_text(encoding='utf-8').replace(old,s)
marker='## תוצאות בדיקה בפועל — 12.11.2026'
if marker in doc: doc=doc[:doc.index(marker)].rstrip()+'\n'
text='''
## תוצאות בדיקה בפועל — 12.11.2026

נבדק ב-PostgreSQL 16.15 בבסיס נפרד `codex_stage_b_20261112`. האכלוס כולל 66,657 רשומות בשמונה טבלאות; לפחות 500 בכל טבלה, 30,000 בדיקות ו-24,000 תוצאות. הבסיס המקורי `Hospiatl_Lab_db` לא שונה. תוצאות הבדיקות והדוגמאות נמצאות ב-[audit](audit/verification.json).

כל 12 מימושי ה-SELECT החזירו נתונים. ארבעת הזוגות הושוו בשני הכיוונים ב-EXCEPT ALL כדי לבדוק גם כפילויות. בדיקת Q4 האחרונה, לאחר הוספת מספר מטופלים וצירוף ההזמנות, נמצאת ב-[Q4_final_equivalence.txt](audit/Q4_final_equivalence.txt); הדוגמאות העדכניות הן [Q4A](audit/Q4A_final_samples.txt) ו-[Q4B](audit/Q4B_final_samples.txt). לשאר השאילתות ראו [דוגמאות עד חמש שורות](audit/03_select_samples.txt).

### מדידת ארבעת הזוגות

הטבלה מציגה זמן Execution Time של הרצה אחת לכל דרך, במילישניות. הזמנים אינם SLA ואין להסיק מהפרשים קטנים יתרון קבוע. האינדקסים החדשים כבר היו קיימים בעת מדידה זו. התוכניות המלאות עם BUFFERS נשמרו ב-audit בשם Q1A_plan.txt וכן הלאה.

| זוג | דרך A, ms | דרך B, ms | פירוש באכלוס הנוכחי |
|---|---:|---:|---|
'''
notes={1:'A מהירה משמעותית; B מבצעת ספירות מתואמות חוזרות.',2:'A מהירה משמעותית; B חוזרת על צירופי הספירה לכל מטופל.',3:'A מהירה מעט במדידה זו; ההפרש קטן והמתכנן יכול לייעל NOT EXISTS.',4:'יש להכריע לפי המספרים: שתי הדרכים מבצעות צבירה דומה, וההפרש במדידה בודדת אינו הוכחה ליתרון קבוע.'}
for n in range(1,5): text+=f"| Q{n} | {qt[f'Q{n}A']:.3f} | {qt[f'Q{n}B']:.3f} | {notes[n]} |\n"
text+='''
### מדידות האינדקסים

חציון של חמש הרצות לפני וחמש אחרי כל אינדקס, עם ANALYZE ובלי לשנות enable_seqscan:

| אינדקס | לפני, ms | אחרי, ms | שינוי בתוכנית |
|---|---:|---:|---|
'''
scans={
 'idx_testorder_patient_date':'Seq Scan על testorder הוחלף ב-Bitmap Index/Heap Scan.',
 'idx_labtest_type_status':'Seq Scan על labtest הוחלף ב-Index Scan.',
 'idx_labalert_open_created':'Seq Scan על labalert הוחלף ב-Bitmap Index/Heap Scan על האינדקס החלקי.'}
for name,t in idx.items(): text+=f"| {name} | {t['median_before_ms']:.3f} | {t['median_after_ms']:.3f} | {scans[name]} |\n"
text+='''
במדידה הראשונה של אינדקס המטופל דווקא נרשמה האטה: 0.359 ms לפני לעומת 4.062 ms אחרי. זאת ראיה לכך שמדידה בודדת מושפעת ממטמון ותזמון; המדידה החוזרת הראתה חציון נמוך יותר אחרי יצירת האינדקס. גם במקרים האחרים אין לייחס כל הפרש בזמן לאינדקס לבדו; יש לקרוא את מספר הרשומות, סוגי הסריקה ונתוני BUFFERS. [מדידה ראשונה](audit/09_index_before_after.txt), [חמש החזרות המלאות](audit/10_repeated_index_plans.txt).

### שינויים, אילוצים וטרנזקציות

כל אחת משלוש המחיקות ושלושת העדכונים השפיעה על רשומות קיימות. לאחר ROLLBACK נבדקה התאמה מלאה של הטבלה למצבה הקודם בשני כיווני EXCEPT ALL. [יומן לפני/אחרי וביטול](audit/07_mutations.txt). שלוש ההכנסות השגויות נכשלו בקוד 23514 ועל שם האילוץ הנכון, ללא הפרת אילוץ אחר קודם לכן. [השגיאות הצפויות](audit/06_expected_errors.txt). בהדגמת הטרנזקציות התקבלו restored=true וגם persisted=true. [יומן הטרנזקציות](audit/08_transactions.txt).

### גיבוי ומיגרציה

[backup2.dump](backup2.dump) הוא גיבוי Custom של בסיס הבדיקה המעודכן, הכולל את האכלוס, שלושת האילוצים ושלושת האינדקסים ואת סימון COMMIT בשדה Notes. הוא שוחזר בהצלחה לבסיס `codex_stage_b_20261112_restore` באותו שרת. הושוו כל ערכי הרשומות באמצעות טביעות MD5 מסודרות, מטא־דאטה עמודות, הגדרות האינדקסים, מבנה האילוצים וההגדרות המדויקות של שלושת האילוצים החדשים. [השוואת השחזור](audit/13_restore_comparison.txt), [בדיקת נפחים וקשרים בשחזור](audit/11_backup2_restore.txt).

pg_dump/pg_restore כתבו מחדש ביטויי cast של מערכי VARCHAR באילוצי IN הישנים. לכן השוואת מחרוזת של pg_get_constraintdef לבדה הציגה הבדל תחבירי. ההבדל תועד ב-[catalog_diff.txt](audit/catalog_diff.txt); האילוצים החדשים והאינדקסים נמצאו זהים, ובדיקות הנתונים והקטלוג עברו.

StageA_Migration.sql הורץ על עותק נפרד של הבסיס המקורי. נבדק שכל העמודות הקודמות נשמרו ללא שינוי ושתאריכי ההסמכה החדשים זהים לתאריכים בהקמה מאפס. [יומן המיגרציה](audit/14_migration.txt), [שימור הרשומות המקוריות](audit/15_preserved_original_rows.txt).

SHA-256 של backup2.dump:

```text
'''+data['backup_sha256']+'''
```

צילומי pgAdmin החדשים עדיין לא בוצעו: Computer Use נעצר משום שלא הצליח לזהות בבטחה את כתובת הדפדפן. ייצוא תרשימים מעודכנים, שחזור במחשב אחר ו-TAG ההגשה עדיין פתוחים. אין להגיש את הדוח כאילו צילומי המסך כבר צורפו.
'''
doc=doc.replace('- [ ] גיבוי מעודכן בשם backup2 באמצעות pg_dump ובדיקת שחזור בעותק נפרד.', '- [x] גיבוי מעודכן בשם backup2 באמצעות pg_dump ובדיקת שחזור בעותק נפרד באותו מחשב.')
p.write_text(doc+'\n'+text,encoding='utf-8')
print('Measured timings, backup evidence, migration evidence and remaining gaps published.')
