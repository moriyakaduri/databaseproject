"""Attach genuine pgAdmin screenshots and create revised local diagram sources."""
from pathlib import Path
import copy
import hashlib
import json
import re
from PIL import Image

B=Path(__file__).resolve().parent.parent
A=B.parent/'שלב א'
ROOT=B.parent.parent
shots=B/'screenshots'
doc=(B/'README.md').read_text(encoding='utf-8')
keys=['Q1A','Q1B','Q2A','Q2B','Q3A','Q3B','Q4A','Q4B','Q5','Q6','Q7','Q8']
def picture(name,label):
    assert (shots/name).is_file(),name
    return f'![{label}](screenshots/{name})'
for key in keys:
    doc=doc.replace(f'**[צילום הרצת {key}]**',picture(key+'-run.jpg',key+' — הרצה ב-pgAdmin'))
    doc=doc.replace(f'**[צילום תוצאת {key} — עד 5 שורות]**',picture(key+'-result.jpg',key+' — חמש שורות תוצאה'))
for key in ['D1','D2','D3','U1','U2','U3']:
    doc=doc.replace(f'**[צילום מצב לפני {key}]**',picture(key+'-before-result.jpg',key+' — מצב לפני'))
    doc=doc.replace(f'**[צילום הרצת {key}]**',picture(key+'-after-run.jpg',key+' — הרצת השינוי'))
    doc=doc.replace(f'**[צילום מצב אחרי {key}, לפני ROLLBACK]**',picture(key+'-after-result.jpg',key+' — מצב אחרי, לפני ביטול'))
for i,name in enumerate(['chk_doctor_firstname_nonblank','chk_labtest_time_order','chk_labalert_ack_time'],1):
    doc=doc.replace(f'**[צילום ALTER TABLE והכנסה שנכשלה על {name}, כולל הודעת השגיאה]**',
                    picture('constraints-alter-run.jpg','הוספת האילוצים ב-ALTER TABLE')+'\n\n'+
                    picture('constraints-alter-result.jpg','שלושת האילוצים מאומתים בקטלוג')+'\n\n'+
                    picture(f'constraint-{i}-error.jpg','23514 — '+name))
for kind in ['rollback','commit']:
    target='**[צילומי לפני, בתוך טרנזקציה ואחרי '+kind.upper()+']**'
    doc=doc.replace(target,'\n\n'.join(picture(f'tx-{kind}-{phase}-result.jpg',kind.upper()+' — '+label)
                                     for phase,label in [('before','לפני'),('inside','בתוך הטרנזקציה'),('after','אחרי')]))
for i,name in enumerate(['idx_testorder_patient_date','idx_labtest_type_status','idx_labalert_open_created'],1):
    start=doc.index('### '+name)
    end=doc.find('\n### ',start+1)
    if end<0: end=doc.index('\n## ',start+1)
    section=doc[start:end]
    section=section.replace('**[צילום EXPLAIN ANALYZE לפני ואחרי]**','\n\n'.join(
        picture(f'index-{i}-{phase}-{view}.jpg',name+' — '+label)
        for phase,label0 in [('before','לפני'),('after','אחרי')]
        for view,label in [('plan',label0+' — תוכנית'),('time',label0+' — זמן ריצה')]))
    measured=[(13.405,51.333),(82.255,6.719),(249.162,54.932)][i-1]
    section=section.replace('זמן לפני: **[למלא ms]**; זמן אחרי: **[למלא ms]**; סוג הסריקה ו-BUFFERS: **[למלא מהפלט]**. הסבר המדידה: **[לציין אם חלה האצה ומה מלמדת התוכנית; אין להמציא שיפור]**.',
        f'בצילומי pgAdmin: Execution Time לפני **{measured[0]:.3f} ms**, ואחרי **{measured[1]:.3f} ms**. '+
        ('במדידה זו זמן הריצה דווקא גדל למרות שינוי תוכנית הסריקה. האינדקס אינו מבטיח האצה; ההבדל מהמדידות החוזרות ממחיש השפעת מטמון ועומס.' if i==1 else
         'במדידה זו זמן הריצה ירד. יש לקרוא זאת לצד סוג הסריקה ו-BUFFERS בצילום ותוצאות החזרות המופיעות בהמשך, ולא להסיק מכך יחס האצה קבוע.'))
    doc=doc[:start]+section+doc[end:]
doc=doc.replace('- [ ] צילומי pgAdmin אמיתיים בכל המקומות המסומנים, כולל תוצאות של עד חמש שורות.',
                '- [x] צילומי pgAdmin אמיתיים ל-SELECT, שינויים, אילוצים, טרנזקציות ואינדקסים; תוצאות SELECT הוגבלו לחמש שורות.')
doc=doc.replace('צילומי pgAdmin החדשים עדיין לא בוצעו: Computer Use נעצר משום שלא הצליח לזהות בבטחה את כתובת הדפדפן. ייצוא תרשימים מעודכנים, שחזור במחשב אחר ו-TAG ההגשה עדיין פתוחים. אין להגיש את הדוח כאילו צילומי המסך כבר צורפו.',
'''צילומי pgAdmin נוספו לאחר חידוש החיבור דרך הדפדפן הפנימי. הם צילומי ממשק אמיתיים ולא תמונות של יומני CLI. ייצוא תרשימים מעודכנים, שחזור במחשב אחר ו-TAG ההגשה עדיין פתוחים.

בתיעוד המחיקות נשמרו חמישה מזהים בטבלה זמנית לפני הפעולה. לאחר הפעולה אותם מזהים הוצגו בצירוף חיצוני לטבלה הנוכחית: NULL ו-deleted=true מוכיחים שהרשומות נמחקו. בעדכונים אותן רשומות הוצגו עם הערכים החדשים. כל פעולה בוטלה ב-ROLLBACK. בהדגמת COMMIT נוסף הסימון UI COMMIT DEMO, נשמר ונבדק persisted=true, ואז בטרנזקציה נפרדת הוחזר Notes למצבו שלפני הדגמת הממשק. קובץ RollbackCommit.sql המקורי משאיר את סימון COMMIT DEMO בכוונה.

שלושת ALTER TABLE הודגמו בטרנזקציה נפרדת לאחר הסרה זמנית של אותם שלושה אילוצים בעותק הבדיקה; לאחר הצילום בוטלה הטרנזקציה ונשארו האילוצים המקוריים של שלב ב׳. בדיקות הכישלון הורצו לאחר הביטול ונכשלו על האילוצים הקיימים.

צילומי האינדקסים מציגים מדידות נוספות דרך הממשק, בתנאי עומס אחרים מהמדידה החוזרת. לאחר כל זוג בוטלה הטרנזקציה, ולכן נשארו שלושת האינדקסים כפי שהיו לפני התיעוד. המועדים בשאילתות קבועים. בדיקת הסיום בממשק אישרה 30,000 בדיקות, 24,000 תוצאות ושלושה אינדקסים חדשים.

![בדיקת בסיס הבדיקה](screenshots/final-database-check.jpg)

מגבלת הצילום: רוחב הדפדפן היה 614 פיקסלים, ולכן בחלק מהתמונות נראות רק העמודות השמאליות. קוד השאילתה ופלטי הבדיקה הטקסטואליים כוללים את יתר העמודות. אין לראות בתמונה החתוכה הוכחה לכל עמודה שאינה גלויה.''')
(B/'README.md').write_text(doc,encoding='utf-8')

manifest=[]
for p in sorted(shots.glob('*.jpg')):
    with Image.open(p) as im:
        im.verify()
    manifest.append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
(B/'audit/screenshot_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(shots/'README.md').write_text(f'# צילומי pgAdmin אמיתיים\n\nנשמרו {len(manifest)} תמונות מתוך הדפדפן הפנימי בזמן ההרצות על codex_stage_b_20261112. אין כאן צילומים מדומים. פירוט, סדר ופרשנות מופיעים בדוח. המניפסט ב-audit כולל SHA-256 לכל תמונה. רוחב הדפדפן מוגבל וחלק מהעמודות דורשות גלילה אופקית.\n',encoding='utf-8')

# Revisions are separate artifacts; approved historical originals stay untouched.
diagrams=B/'diagrams'
diagrams.mkdir(exist_ok=True)
erd=json.loads((A/'ERD/ERD.erdplus').read_text(encoding='utf-8-sig'))
dsd=json.loads((A/'DSD/DSD.erdplus').read_text(encoding='utf-8-sig'))
node=copy.deepcopy(next(n for n in erd['data']['nodes'] if n.get('id')=='A_TEC_5'))
node['id']='A_TEC_6';node['data']['label']='CertificationExpiresOn'
node['position']={'x':0,'y':-190}
erd['data']['nodes'].append(node)
erd['data']['edges'].append({'id':'EDG_TEC_6','type':'Attribute','source':'E_LABTECHNICIAN','target':'A_TEC_6'})
schema=(A/'createTables.sql').read_text(encoding='utf-8')
types={}
nullability={}
for name,body in re.findall(r'CREATE TABLE (\w+) \((.*?)\n\);',schema,re.S):
    for line in body.splitlines():
        m=re.match(r'\s*(\w+)\s+(INTEGER|VARCHAR\(\d+\)|NUMERIC\(\d+,\d+\)|DATE|TIMESTAMP|TEXT|BOOLEAN)(.*)',line)
        if m:
            types[(name.lower(),m[1].lower())]=m[2].replace('INTEGER','INT')
            nullability[(name.lower(),m[1].lower())]='NOT NULL' not in m[3] and 'PRIMARY KEY' not in m[3]
for table in dsd['data']['nodes']:
    if table['type']!='Table':continue
    if table['id']=='E_LABTECHNICIAN':
        table['data']['columns'].append({'id':'stage-b-certification-expires-on','name':'CertificationExpiresOn','type':'DATE','isPrimaryKey':False,'isOptional':False})
    for col in table['data']['columns']:
        if col.get('isForeignKey'):continue
        key=(table['data']['label'].lower(),col['name'].lower())
        col['type']=types[key]
        col['isOptional']=nullability[key]
assert len(types)==53,len(types)
for name,obj in [('ERD-revised.erdplus',erd),('DSD-revised.erdplus',dsd)]:
    (diagrams/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
(diagrams/'README.md').write_text('''# תרשימים מעודכנים — מקורות מקומיים

ERD-revised.erdplus מוסיף את CertificationExpiresOn כמאפיין טכנאי. DSD-revised.erdplus מוסיף את עמודת DATE NOT NULL ומתאים את טיפוסי 53 העמודות ל-createTables.sql. הקשרים והמפתחות נשמרו. הקבצים המקוריים בשלב א׳ נשמרו ללא שינוי.

אלה גרסאות מקור מקומיות. עדיין דרושים פתיחה ובדיקה חזותית ב-ERDPlus וייצוא התמונות. העלאה לאתר נעצרה בסקירה האוטומטית עד לאישור מפורש של המשתמשת. אין להציג קבצים אלה כתרשימים שיוצאו או אושרו באתר.
''',encoding='utf-8')
summary=json.loads((B/'audit/verification.json').read_text())
summary['screenshots_complete']=True
summary['screenshot_count']=len(manifest)
summary['diagram_sources_revised']=True
summary['erd_exports_updated']=False
summary['ui_index_execution_ms']={'index1':{'before':13.405,'after':51.333},'index2':{'before':82.255,'after':6.719},'index3':{'before':249.162,'after':54.932}}
(B/'audit/verification.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(f'Integrated {len(manifest)} real screenshots; local ERD/DSD sources revised; original diagrams preserved.')
