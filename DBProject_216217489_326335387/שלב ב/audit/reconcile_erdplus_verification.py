"""Record verified imports accurately while native image downloads remain pending."""
from pathlib import Path
import hashlib
import json
import re

B=Path(__file__).resolve().parent.parent
A=B.parent/'שלב א'
ROOT=B.parent.parent
diagram=B/'diagrams'

schema=(A/'createTables.sql').read_text(encoding='utf-8')
expected={}
for table,body in re.findall(r'CREATE TABLE (\w+) \((.*?)\n\);',schema,re.S):
    for line in body.splitlines():
        m=re.match(r'\s*(\w+)\s+(INTEGER|VARCHAR\(\d+\)|NUMERIC\(\d+,\d+\)|DATE|TIMESTAMP|TEXT|BOOLEAN)(.*)',line)
        if m: expected[(table.lower(),m[1].lower())]=m[2].replace('INTEGER','INT')
dsd=json.loads((diagram/'DSD-stage-b-verified.erdplus').read_text(encoding='utf-8'))
actual={}
for node in dsd['data']['nodes']:
    if node['type']!='Table':continue
    for col in node['data']['columns']:
        cols=col['foreignKeyProps']['columns'] if col.get('isForeignKey') else [col]
        for c in cols:
            kind=c.get('type','INT')
            if kind=='VARCHAR(n)': kind='VARCHAR('+c['size']+')'
            elif kind=='NUMERIC(p s)':kind='NUMERIC('+c['size']+')'
            elif kind=='Custom':kind=c['size']
            actual[(node['data']['label'].lower(),c['name'].lower())]=kind
assert actual==expected,{'missing':set(expected)-set(actual),'wrong':[(k,v,expected.get(k)) for k,v in actual.items() if expected.get(k)!=v]}
assert len(actual)==53

erd_url='https://erdplus.com/diagrams/732415'
dsd_url='https://erdplus.com/diagrams/732507'
evidence={
 'erd_url':erd_url,'dsd_url':dsd_url,'upload_authorized':True,'login_required':False,
 'erd_import_verified':True,'dsd_import_verified':True,'schema_column_type_comparison':'PASS: 53 columns',
 'type_format':{'varchar':'type=VARCHAR(n), size=n','numeric':'type=NUMERIC(p s), size=p,s','custom':'type=Custom, size=PostgreSQL type'},
 'native_image_export_verified':False,
 'remaining_dependency':'Download image through browser control repeatedly timed out; no PNG found in Downloads. Manual download check requested.',
 'artifacts':[]}
for p in sorted(diagram.iterdir()):
    if p.is_file():evidence['artifacts'].append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(B/'audit/erdplus_verification.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')

intro='''התרשימים המעודכנים יובאו לחשבון ERDPlus באישור המשתמשת, כגרסאות נפרדות. [פתיחת ERD מעודכן](https://erdplus.com/diagrams/732415), [פתיחת DSD סופי](https://erdplus.com/diagrams/732507). ה-ERD מכיל שמונה ישויות ושבעה קשרים ואת המאפיין החדש CertificationExpiresOn. ב-DSD נבדקו תאריך חובה והפורמט של אורכי VARCHAR; טיפוסי כל 53 העמודות במקור הסופי הושוו ל-createTables.sql. קובצי המקור הישנים נשמרו.

הקובץ הסופי לייבוא הוא [DSD-stage-b-verified.erdplus](diagrams/DSD-stage-b-verified.erdplus). ERDPlus שומר VARCHAR(n) עם size נפרד, NUMERIC(p s) עם size כגון 12,3, וטיפוסים כמו TIMESTAMP/TEXT/BOOLEAN כ-Custom עם שם הטיפוס ב-size. הפורמט אומת באמצעות שינוי בממשק וייצוא קובצי דוגמה מהאתר. גרסת DSD-revised הראשונית בחשבון היא גרסת ביניים; השתמשו ב-DSD-stage-b-verified.

**מגבלה פתוחה:** פקודת Download image דרך כלי השליטה נתקעה בכמה ניסיונות ולא נמצא PNG שהורד. הצילומים הבאים הם צילומי אימות חלקיים של הממשק, ואינם תחליף לייצוא התמונות המלאות. אין לשנות את שמם ל-approved-erd.jpeg או approved-dsd.png. ממתינים לבדיקת הורדה ידנית; לאחר קבלת קבצים יש לבדוק אותם ולהטמיע את התמונות המלאות.

![ERD מיובא — תיעוד ממשק חלקי](diagrams/erdplus-erd-verification.jpg)

![DSD מיובא — תיעוד ממשק חלקי](diagrams/erdplus-dsd-verification.jpg)

![הגדרות DATE ו-VARCHAR ב-DSD הסופי](diagrams/erdplus-dsd-date-settings.jpg)'''
p=B/'README.md';doc=p.read_text(encoding='utf-8')
start=doc.index('הוכנו קובצי מקור מקומיים מעודכנים:')
end=doc.index('\n\n**[להוסיף צילום ERD',start)
doc=doc[:start]+intro+doc[end:]
doc=doc.replace('**[להוסיף צילום ERD מעודכן ו-DSD מעודכן, לייצא approved-erd.jpeg ו-approved-dsd.png לאחר בדיקה.]**',
                '**[פתוח: לצרף את ייצואי התמונות המלאים לאחר שהורדתם תצליח.]**')
doc=doc.replace('ייצוא תרשימים מעודכנים, שחזור במחשב אחר ו-TAG ההגשה עדיין פתוחים.',
                'ייבוא ובדיקת מקורות התרשימים הושלמו; הורדת תמונות מלאות, שחזור במחשב אחר ו-TAG ההגשה עדיין פתוחים.')
p.write_text(doc,encoding='utf-8')
(diagram/'README.md').write_text('# תרשימים מעודכנים — אימות ב-ERDPlus\n\n'+intro.replace('(diagrams/','(')+'\n',encoding='utf-8')
p=ROOT/'README.md';doc=p.read_text(encoding='utf-8');doc=doc.replace('העלאתם ל-ERDPlus אושרה; הייבוא והייצוא ממתינים להתחברות המשתמשת באתר.',
 'הם יובאו ונבדקו ב-ERDPlus; הורדת התמונות המלאות ממתינה לפתרון תקלה בפקודת Download image.');p.write_text(doc,encoding='utf-8')
p=B/'audit/verification.json';summary=json.loads(p.read_text(encoding='utf-8'));summary.update({'erdplus_login_required':False,'erdplus_files_uploaded':True,'erdplus_imports_verified':True,'erdplus_dsd_type_metadata_verified':True,'erd_exports_updated':False,'erdplus_documents':{'ERD':erd_url,'DSD':dsd_url}});p.write_text(json.dumps(summary,indent=2),encoding='utf-8')
p=B/'audit/UI_STATUS.md';doc=p.read_text(encoding='utf-8');doc+='\n\n## עדכון לאחר התחברות\n\nשני המקורות יובאו ונבדקו בחשבון המחובר. DSD-stage-b-verified היא הגרסה הסופית עם טיפוסי ERDPlus תקינים; נמצא ותוקן הבדל פורמט VARCHAR/NUMERIC/Custom. נשמרו צילומי אימות ודוגמאות .erdplus שיוצאו מהאתר. השוואת 53 טיפוסי העמודות לסכמה עברה. במהלך פתיחת מאפיינים נוספה בטעות New Column, והיא הוסרה ונבדק שנותרו השדות המתוכננים. הורדת התמונות דרך Download image נתקעת ולא הפיקה PNG בתיקיית Downloads. נשלחה למשתמשת בקשה לבדוק הורדה ידנית משני הקישורים. נדרשת קליטת התמונות, בדיקתן והטמעתן בדוח; אין לסמן ייצוא מלא כהושלם. ראו erdplus_verification.json.\n';p.write_text(doc,encoding='utf-8')
print('PASS: 53 column types match PostgreSQL; imports and screenshots documented; native image export remains explicitly pending.')
