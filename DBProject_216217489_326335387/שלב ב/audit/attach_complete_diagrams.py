"""Attach the complete source-rendered diagrams and record their provenance."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET
from PIL import Image

B=Path(__file__).resolve().parent.parent
ROOT=B.parent.parent
D=B/'diagrams'
render=json.loads((B/'audit/local_diagram_rendering.json').read_text(encoding='utf-8'))
assert render['erd']['rendered_node_count']==61 and render['erd']['rendered_edge_count']==60
assert render['dsd']['column_count']==53 and render['dsd']['foreign_key_count']==7
for stem in ['updated-erd','updated-dsd']:
    with Image.open(D/(stem+'.png')) as im:
        im.verify()
    ET.parse(D/(stem+'.svg'))

section='''## התרשימים המלאים המעודכנים

קובצי המקור יובאו ונבדקו ב-ERDPlus. לאחר שגם המשתמשת דיווחה שהורדה ידנית באמצעות Download image נכשלת, נוצרו התמונות הבאות מקובצי המקור המאומתים באמצעות מחולל מקומי. **אלה תמונות מלאות של המודל המעודכן, ולא צילומי מסך או הורדות PNG מקוריות מהאתר.** פריסת הרכיבים הורחבה לשיפור הקריאות; הישויות, השדות, המפתחות והקשרים נשמרו. התמונות הישנות של שלב א׳ נשמרו ללא שינוי ואינן מייצגות את העמודה החדשה.

### ERD מעודכן

התרשים כולל שמונה ישויות, 46 מאפיינים ושבעה קשרים. שני מאפייני DATE משמעותיים מודגשים בירוק. קו תוקף ההסמכה מחובר ישירות לטכנאי, ומיקומו שונה בתצוגה המקומית כדי שלא יחצה את מאפיין המפתח. ריבוי הקשרים נשמר מהמקור שנבדק באתר.

![ERD מלא מעודכן](diagrams/updated-erd.png)

[PNG ברזולוציה מלאה](diagrams/updated-erd.png) · [JPEG](diagrams/updated-erd.jpeg) · [SVG וקטורי](diagrams/updated-erd.svg) · [מקור ERDPlus](diagrams/ERD-revised.erdplus)

### DSD מעודכן

התרשים מציג את כל שמונה הטבלאות, 53 העמודות ושבעת המפתחות הזרים, לרבות טיפוסים, אורכי מחרוזות, אפשרות NULL, מפתחות ראשיים וייחודיות. TechnicianID בבדיקה הוא אופציונלי, ולכן מסומן 0..1 בצד הטכנאי; LabTestID בתוצאה ייחודי, ולכן נשמר הקשר 1 מול 0..1 בין בדיקה לתוצאה. UQ נבדק מול createTables.sql. התמונות נבדקו חזותית לאחר יצירתן.

![DSD מלא מעודכן](diagrams/updated-dsd.png)

[PNG ברזולוציה מלאה](diagrams/updated-dsd.png) · [SVG וקטורי](diagrams/updated-dsd.svg) · [מקור ERDPlus סופי](diagrams/DSD-stage-b-verified.erdplus)

יצירה חוזרת: `python audit/render_verified_diagrams.py`. רישום תכולה, ספירות ו-SHA-256 נמצא ב-[local_diagram_rendering.json](audit/local_diagram_rendering.json). אין צורך להמשיך לנסות את כפתור ההורדה לצורך צפייה בתמונות האלה. אם תידרש דווקא הורדה מקורית מהאתר, התקלה בכפתור נותרה פתוחה ויש לבדוק אותה בדפדפן אחר או מול האתר.
'''
p=B/'README.md';doc=p.read_text(encoding='utf-8')
old='**מגבלה פתוחה:** פקודת Download image דרך כלי השליטה נתקעה בכמה ניסיונות ולא נמצא PNG שהורד. הצילומים הבאים הם צילומי אימות חלקיים של הממשק, ואינם תחליף לייצוא התמונות המלאות. אין לשנות את שמם ל-approved-erd.jpeg או approved-dsd.png. ממתינים לבדיקת הורדה ידנית; לאחר קבלת קבצים יש לבדוק אותם ולהטמיע את התמונות המלאות.'
new='פקודת Download image נכשלה דרך כלי השליטה וגם בלחיצה ידנית של המשתמשת. לכן נוצרו תמונות מלאות מקומית מקובצי המקור שאומתו באתר; הן מוצגות בסעיף התרשימים המלאים להלן, עם ציון אופן הפקתן. הצילומים הבאים נשמרו כראיות לבדיקה באתר בלבד.'
doc=doc.replace(old,new)
doc=doc.replace('**[פתוח: לצרף את ייצואי התמונות המלאים לאחר שהורדתם תצליח.]**','ראו את שני התרשימים המלאים בסעיף הבא.\n\n'+section)
doc=doc.replace('- [ ] ייצוא תרשימים מעודכנים ב-ERDPlus לאחר תיקון שלב א׳.',
                '- [x] יבוא ובדיקת התרשימים ב-ERDPlus, והפקת תמונות מלאות מהמקורות המאומתים. Download image באתר נכשל גם ידנית; אופן ההפקה המקומית מתועד.')
doc=doc.replace('ייבוא ובדיקת מקורות התרשימים הושלמו; הורדת תמונות מלאות, שחזור במחשב אחר ו-TAG ההגשה עדיין פתוחים.',
                'ייבוא ובדיקת המקורות והפקת תמונות מלאות הושלמו. שחזור במחשב אחר ו-TAG ההגשה עדיין פתוחים. ההורדה המקורית מהאתר נכשלה, והתמונות הופקו מקומית כאמור לעיל.')
p.write_text(doc,encoding='utf-8')
(D/'README.md').write_text('# תרשימים מעודכנים — קבצים מלאים\n\n'+section.replace('(diagrams/','(').replace('(audit/','(../audit/')+'\n\n'+new+'\n',encoding='utf-8')
p=ROOT/'README.md';doc=p.read_text(encoding='utf-8');doc=doc.replace('הם יובאו ונבדקו ב-ERDPlus; הורדת התמונות המלאות ממתינה לפתרון תקלה בפקודת Download image.',
                'הם יובאו ונבדקו ב-ERDPlus, ותמונות מלאות הופקו מקומית מהמקורות המאומתים לאחר שההורדה באתר נכשלה גם ידנית. אופן ההפקה מתועד בדוח.');p.write_text(doc,encoding='utf-8')
p=B/'audit/verification.json';v=json.loads(p.read_text(encoding='utf-8'));v.update({'diagram_images_complete':True,'diagram_rendering_method':'local render of ERDPlus-verified sources','erd_exports_updated':True,'native_erdplus_image_download':False,'local_diagram_visual_qa':'PASS'});p.write_text(json.dumps(v,indent=2),encoding='utf-8')
p=B/'audit/erdplus_verification.json';v=json.loads(p.read_text(encoding='utf-8'));v.update({'complete_images_available':True,'image_provenance':'local rendering of verified .erdplus models','remaining_dependency':'Native website Download image still fails. Complete PNG/JPEG/SVG artifacts are now provided locally.'});p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
p=B/'audit/UI_STATUS.md';doc=p.read_text(encoding='utf-8');doc+='\n\n## תמונות מלאות לאחר כשל ההורדה הידנית\n\nהמשתמשת אישרה שגם הורדה ידנית נכשלת. נוצרו ונבדקו חזותית updated-erd.png/.jpeg/.svg ו-updated-dsd.png/.svg ישירות מקובצי המקור המאומתים. ה-ERD כולל 61 רכיבים ו-60 קווים; ה-DSD כולל 8 טבלאות, 53 עמודות ו-7 מפתחות זרים. אופציונליות הטכנאי מסומנת 0..1, ושני שדות DATE מודגשים. כל התמונות הוטמעו בדוח עם ציון ברור שזו הפקה מקומית ולא הורדה מקורית מהאתר. אין צורך בפעולת הורדה נוספת מצד המשתמשת לצורך הקבצים שסופקו. ההורדה המקורית מהאתר נותרה תקלה חיצונית; שחזור במחשב השותפה ו-TAG/פרסום עדיין לא בוצעו.\n';p.write_text(doc,encoding='utf-8')
print('Complete diagram images validated and embedded; native-download failure and local provenance are explicit.')
