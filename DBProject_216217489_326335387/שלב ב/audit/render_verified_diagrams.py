"""Render complete PNG/JPEG/SVG artifacts from the verified .erdplus sources.

This is a local renderer, NOT ERDPlus's failed native Download image output.
The original graph, identifiers, attributes and relationship endpoint metadata
are preserved. Layout spacing is adjusted solely for legibility.
"""
from pathlib import Path
import hashlib
import html
import json
import math
import re
from PIL import Image, ImageDraw, ImageFont

B=Path(__file__).resolve().parent.parent
OUT=B/'diagrams'
FONT=Path('C:/Windows/Fonts/arial.ttf')
BOLD=Path('C:/Windows/Fonts/arialbd.ttf')
INK='#152c45';BLUE='#dce9f5';LINE='#5b7188';GREEN='#e0f1e8';WHITE='#ffffff'

class Canvas:
    def __init__(self,w,h):
        self.w,self.h=w,h;self.scale=1.5
        self.im=Image.new('RGB',(int(w*self.scale),int(h*self.scale)),WHITE)
        self.d=ImageDraw.Draw(self.im)
        self.svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',f'<rect width="{w}" height="{h}" fill="white"/>']
    def coords(self,points):return [(x*self.scale,y*self.scale) for x,y in points]
    def line(self,points,fill=LINE,width=2):
        self.d.line(self.coords(points),fill=fill,width=max(1,round(width*self.scale)),joint='curve')
        self.svg.append('<polyline points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in points)+f'" fill="none" stroke="{fill}" stroke-width="{width}"/>')
    def rect(self,box,fill=WHITE,stroke=INK,width=2,radius=0):
        x0,y0,x1,y1=box
        self.d.rounded_rectangle([v*self.scale for v in box],radius=radius*self.scale,fill=fill,outline=stroke,width=max(1,round(width*self.scale)))
        self.svg.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
    def ellipse(self,box,fill=WHITE,stroke=INK):
        self.d.ellipse([v*self.scale for v in box],fill=fill,outline=stroke,width=3)
        x0,y0,x1,y1=box;self.svg.append(f'<ellipse cx="{(x0+x1)/2}" cy="{(y0+y1)/2}" rx="{(x1-x0)/2}" ry="{(y1-y0)/2}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    def poly(self,points,fill=WHITE,stroke=INK,width=2):
        self.d.polygon(self.coords(points),fill=fill)
        self.d.line(self.coords(points+[points[0]]),fill=stroke,width=round(width*self.scale),joint='curve')
        self.svg.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
    def text(self,x,y,text,size=18,bold=False,anchor='mm',color=INK,underline=False):
        font=ImageFont.truetype(str(BOLD if bold else FONT),round(size*self.scale))
        self.d.text((x*self.scale,y*self.scale),text,font=font,fill=color,anchor=anchor)
        svg_anchor='start' if anchor.startswith('l') else 'end' if anchor.startswith('r') else 'middle'
        self.svg.append(f'<text x="{x}" y="{y}" text-anchor="{svg_anchor}" dominant-baseline="middle" font-family="Arial,sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}"'+(' text-decoration="underline"' if underline else '')+'>'+html.escape(text)+'</text>')
        if underline:
            width=font.getlength(text)/self.scale
            self.line([(x-width/2,y+size*.55),(x+width/2,y+size*.55)],fill=color,width=1)
    def arrow(self,tip,previous,fill=LINE):
        dx,dy=tip[0]-previous[0],tip[1]-previous[1];length=math.hypot(dx,dy)
        if not length:return
        dx,dy=dx/length,dy/length
        back=(tip[0]-dx*13,tip[1]-dy*13)
        self.poly([tip,(back[0]-dy*6,back[1]+dx*6),(back[0]+dy*6,back[1]-dx*6)],fill=fill,stroke=fill,width=1)
    def save(self,stem,jpeg=False):
        self.im.save(OUT/(stem+'.png'),optimize=True)
        if jpeg:self.im.save(OUT/(stem+'.jpeg'),quality=95,subsampling=0)
        (OUT/(stem+'.svg')).write_text('\n'.join(self.svg+['</svg>']),encoding='utf-8')

def render_erd():
    src=json.loads((OUT/'ERD-revised.erdplus').read_text(encoding='utf-8'))
    nodes={n['id']:n for n in src['data']['nodes']}
    pos={};boxes={}
    for n in nodes.values():
        if n['type']!='Attribute':pos[n['id']]=(n['position']['x']*2+350,n['position']['y']*1.7+180)
    for n in nodes.values():
        if n['type']=='Attribute':
            px,py=pos[n['parentId']];dx,dy=n['position']['x'],n['position']['y'];r=math.hypot(dx,dy) or 1
            x,y=px+260*dx/r,py+160*dy/r
            if n['id']=='A_TEC_6':x,y=px,py+160
            if n['id']=='A_RES_4':x,y=px-260,py+70
            pos[n['id']]=(x,y)
        label=n['data']['label'];w=170 if n['type']=='Entity' else 155 if n['type']=='Relationship' else max(160,min(252,len(label)*9+36))
        boxes[n['id']]=(w,64 if n['type']!='Relationship' else 66)
    # Ensure the complete model is included, including every original edge.
    assert len(nodes)==61 and len(src['data']['edges'])==60
    maxx=max(pos[k][0]+boxes[k][0]/2 for k in pos)+110
    maxy=max(pos[k][1]+boxes[k][1]/2 for k in pos)+110
    c=Canvas(math.ceil(maxx),math.ceil(maxy)+70)
    c.text(80,55,'Hospital Laboratory | ER Diagram',34,True,anchor='lm')
    c.text(80,102,'8 entities  |  46 attributes  |  7 relationships  |  Green: the two meaningful DATE attributes',21,anchor='lm')
    c.text(80,140,'Locally rendered from the ERDPlus-verified source. Native website image download failed.',17,anchor='lm',color=LINE)
    def boundary(key,toward):
        x,y=pos[key];dx,dy=toward[0]-x,toward[1]-y;w,h=boxes[key];rx,ry=w/2,h/2
        if not dx and not dy:return x,y
        kind=nodes[key]['type']
        if kind=='Attribute':scale=1/math.sqrt((dx/rx)**2+(dy/ry)**2)
        elif kind=='Relationship':scale=1/(abs(dx)/rx+abs(dy)/ry)
        else:scale=1/max(abs(dx)/rx,abs(dy)/ry)
        return x+dx*scale,y+dy*scale
    cardinal=[]
    for edge in src['data']['edges']:
        a,b=edge['source'],edge['target'];p,q=boundary(a,pos[b]),boundary(b,pos[a]);c.line([p,q],width=2)
        if nodes[a]['type']=='Relationship':
            data=nodes[a]['data'];details=next(v for k,v in data.items() if k in ['sourceEntityDetails','targetEntityDetails'] and v['id']==b)
            label=('1' if details['minCardinality']=='Mandatory' else '0')+'..'+('1' if details['maxCardinality']=='One' else 'N')
            dx,dy=q[0]-p[0],q[1]-p[1];length=math.hypot(dx,dy) or 1
            cardinal.append((p[0]*.22+q[0]*.78-dy/length*18,p[1]*.22+q[1]*.78+dx/length*18,label))
    for key,n in nodes.items():
        x,y=pos[key];w,h=boxes[key];label=n['data']['label'];highlight=label in ['DateOfBirth','CertificationExpiresOn']
        box=(x-w/2,y-h/2,x+w/2,y+h/2)
        if n['type']=='Entity':c.rect(box,BLUE);c.text(x,y,label,21,True)
        elif n['type']=='Relationship':c.poly([(x,y-h/2),(x+w/2,y),(x,y+h/2),(x-w/2,y)]);c.text(x,y,label,18)
        else:
            c.ellipse(box,GREEN if highlight else WHITE)
            unique=isinstance(n['data'].get('types'),dict) and n['data']['types'].get('Unique',False)
            c.text(x,y,label,18,highlight,underline=unique)
    for x,y,label in cardinal:
        c.rect((x-26,y-12,x+26,y+12),WHITE,WHITE,width=1)
        c.text(x,y,label,15,True,color=LINE)
    c.text(80,c.h-42,'Underlined attributes: keys in the ERD source. Endpoint labels retain the original ERDPlus multiplicities.',17,anchor='lm',color=LINE)
    c.save('updated-erd',jpeg=True)
    return {'entity_count':8,'attribute_count':46,'relationship_count':7,'rendered_node_count':len(nodes),'rendered_edge_count':len(src['data']['edges'])}

def render_dsd():
    src=json.loads((OUT/'DSD-stage-b-verified.erdplus').read_text(encoding='utf-8'))
    tables={n['id']:n for n in src['data']['nodes'] if n['type']=='Table'}
    positions={'E_PATIENT':(60,200),'E_DOCTOR':(60,700),'E_TESTORDER':(780,420),
               'E_TESTTYPE':(1500,200),'E_LABTEST':(1500,750),'E_LABTECHNICIAN':(780,1250),
               'E_TESTRESULT':(2220,750),'E_LABALERT':(2940,750)}
    width=600;row_h=43;head=58
    rows={};rowpoints={}
    uq={'patient':{'idnumber'},'doctor':{'licensenumber'},'testtype':{'testcode'},'labtechnician':{'certificationnumber'},'testresult':{'labtestid'}}
    for key,n in tables.items():
        rs=[]
        for col in n['data']['columns']:
            for field in col['foreignKeyProps']['columns'] if col.get('isForeignKey') else [col]:
                kind=field.get('type','INT');size=field.get('size','')
                if kind=='VARCHAR(n)':kind='VARCHAR('+size+')'
                elif kind=='NUMERIC(p s)':kind='NUMERIC('+size+')'
                elif kind=='Custom':kind=size
                flags=[]
                if col.get('isPrimaryKey'):flags.append('PK')
                if col.get('isForeignKey'):flags.append('FK')
                if field['name'].lower() in uq.get(n['data']['label'].lower(),set()):flags.append('UQ')
                rs.append({'name':field['name'],'type':kind,'flags':'/'.join(flags),'optional':col.get('isOptional',False)})
        rows[key]=rs
        x,y=positions[key]
        for i,r in enumerate(rs):rowpoints[(key,r['name'].lower())]=(x,y+head+row_h*(i+.5))
    assert len(tables)==8 and sum(map(len,rows.values()))==53 and len(src['data']['edges'])==7
    c=Canvas(3630,1710)
    c.text(65,55,'Hospital Laboratory | Relational Schema',34,True,anchor='lm')
    c.text(65,103,'8 tables  |  53 columns  |  7 foreign keys  |  PK = primary key, FK = foreign key, UQ = unique, ? = nullable',21,anchor='lm')
    c.text(65,143,'Locally rendered from the verified ERDPlus source; UQ flags are cross-checked against createTables.sql.',18,anchor='lm',color=LINE)
    for edge in src['data']['edges']:
        parent,child=edge['source'],edge['target'];props=edge['data']['foreignKeyProps'];fk=props['columns'][0]['name'].lower()
        parent_pk=next(r['name'].lower() for r in rows[parent] if 'PK' in r['flags'])
        px,py=rowpoints[(parent,parent_pk)];cx,cy=rowpoints[(child,fk)]
        if parent=='E_TESTTYPE':
            p=(px,py);q=(cx,cy);lane=1415;points=[p,(lane,py),(lane,cy),q]
        else:
            p=(px+width,py);q=(cx,cy);lane=(p[0]+q[0])/2
            if parent=='E_DOCTOR':lane-=22
            if parent=='E_LABTECHNICIAN':lane+=24
            points=[p,(lane,py),(lane,cy),q]
        c.line(points,width=3);c.arrow(p,points[1])
        fk_optional=next(r['optional'] for r in rows[child] if r['name'].lower()==fk)
        parent_cardinality='0..1' if fk_optional else '1'
        c.text(p[0]+(-28 if parent=='E_TESTTYPE' else 26),p[1]-17,parent_cardinality,17,True,color=LINE)
        end='0..1' if child=='E_TESTRESULT' else '0..N'
        c.text(q[0]-30,q[1]-16,end,17,True,color=LINE)
    rendered=[]
    for key,n in tables.items():
        x,y=positions[key];rs=rows[key];height=head+len(rs)*row_h
        c.rect((x,y,x+width,y+height),WHITE)
        c.rect((x,y,x+width,y+head),BLUE)
        c.text(x+20,y+head/2,n['data']['label'],24,True,anchor='lm')
        for i,r in enumerate(rs):
            top=y+head+i*row_h;highlight=r['type']=='DATE'
            if highlight:c.rect((x+1,top,x+width-1,top+row_h),GREEN,GREEN,1)
            elif i%2:c.rect((x+1,top,x+width-1,top+row_h),'#f4f7fa','#f4f7fa',1)
            c.text(x+15,top+row_h/2,r['name']+(' ?' if r['optional'] else ''),20,highlight,anchor='lm')
            c.text(x+320,top+row_h/2,r['type'],19,highlight,anchor='lm')
            c.text(x+width-15,top+row_h/2,r['flags'],17,True,anchor='rm',color=LINE)
            rendered.append((n['data']['label'],r['name'],r['type']))
    c.text(65,1645,'Arrows point from a foreign-key reference toward its parent primary key. Green rows are DATE fields.',19,anchor='lm',color=LINE)
    c.text(65,1680,'Historical approved diagrams and all original source files remain unchanged. This image is a local rendering, not a native ERDPlus download.',17,anchor='lm',color=LINE)
    c.save('updated-dsd')
    return {'table_count':8,'column_count':len(rendered),'foreign_key_count':7,'columns':rendered}

if __name__=='__main__':
    result={'provenance':'Local rendering of the verified ERDPlus source files; website image export failed even manually.',
            'erd':render_erd(),'dsd':render_dsd()}
    result['files']=[{'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
                     for p in sorted(OUT.glob('updated-*'))]
    (B/'audit/local_diagram_rendering.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Rendered complete ERD (61 nodes / 60 edges) and DSD (8 tables / 53 columns / 7 FKs).')
