"""Regenerate the four as-implemented UML PNGs and PlantUML sources (requires Pillow)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
ROOT = Path(__file__).resolve().parents[1]
FONT = "C:/Windows/Fonts/arial.ttf"
def font(n): return ImageFont.truetype(FONT, n)
def arrow(d, a, b, dashed=False):
    if dashed:
        length=math.dist(a,b)
        for t in range(0,int(length),14):
            end=min(t+7,length)
            d.line((a[0]+(b[0]-a[0])*t/length,a[1]+(b[1]-a[1])*t/length,a[0]+(b[0]-a[0])*end/length,a[1]+(b[1]-a[1])*end/length),fill="#334155",width=2)
    else: d.line((a,b),fill="#334155",width=2)
    theta=math.atan2(b[1]-a[1],b[0]-a[0])
    d.polygon([b,(b[0]-12*math.cos(theta-.45),b[1]-12*math.sin(theta-.45)),(b[0]-12*math.cos(theta+.45),b[1]-12*math.sin(theta+.45))],fill="#334155")
def centered(d,xy,s,n=20): d.multiline_text(xy,s,font=font(n),fill="#0f172a",anchor="mm",align="center",spacing=6)
sequences = [
("sequence-login","Session login",["User / browser","core.views.user_login","Django auth / session","SQLite"],[
(0,1,"POST /login/ (username, password)",False),
(1,3,"Read known user and LoginAttempt",False),
(3,1,"Account / lockout state",True),
(1,2,"If unlocked: validate credentials",False),
(2,3,"Read password hash; verify with configured hasher",False),
(1,3,"Valid: reset attempts; audit success",False),
(1,2,"Valid: login(request, user); create session",False),
(1,0,"Valid: 302 redirect / + session cookie",True),
(1,3,"Invalid: record failure; lock for 15 min at 5 attempts",False),
(1,0,"Invalid / locked: render login form with errors",True)]),
("sequence-room-allocation","Room allocation",["Admin / browser","hostel.views / form","allocate_bed service","SQLite"],[
(0,1,"POST /hostel/allocate/",False),
(1,1,"Enforce Admin role; validate form",False),
(1,2,"allocate_bed(student, bed_id, admin_user)",False),
(2,3,"Atomic: read bed / active allocations",False),
(3,2,"Current availability",True),
(2,3,"Available: create allocation; mark occupied; audit",False),
(2,1,"Success: allocation returned after transaction",True),
(1,0,"302 allocation confirmation redirect",True),
(2,1,"Occupied / conflict / DB busy: AllocationError",True),
(1,0,"Error: render form with validation message",True)]),
("sequence-fee-payment","Manual fee payment recording",["Admin / browser","fees.views / form","record_payment service","SQLite"],[
(0,1,"POST /fees/payments/new/",False),
(1,1,"Enforce Admin role; validate form",False),
(1,2,"record_payment(account, amount, mode, reference)",False),
(2,3,"Atomic: read fee account",False),
(2,2,"Validate amount / due; ONLINE requires reference",False),
(2,3,"Create payment and unique receipt; update paid; audit",False),
(2,1,"Success: payment returned after transaction",True),
(1,0,"302 /fees/receipts/{id}/",True),
(2,1,"Invalid: PaymentError (transaction rolled back)",True),
(1,0,"Error: render payment form",True)])]
for name,title,parts,steps in sequences:
    w=1600; h=1030
    im=Image.new("RGB",(w,h),"white"); d=ImageDraw.Draw(im)
    centered(d,(w/2,35),title+" - implemented Django workflow",28)
    xs=[180,590,1000,1410]
    lines=["@startuml "+name,"title "+title]
    for i,p in enumerate(parts):
        lines.append(('database' if i==3 else 'participant')+' "'+p+'" as P'+str(i))
        d.rounded_rectangle((xs[i]-170,75,xs[i]+170,145),radius=8,fill="#e2e8f0",outline="#475569",width=2)
        centered(d,(xs[i],110),p,20)
        for y in range(150,h-45,15): d.line((xs[i],y,xs[i],y+7),fill="#94a3b8",width=2)
    for j,(a,b,label,ret) in enumerate(steps):
        y=200+j*76
        lines.append('P'+str(a)+(' --> ' if ret else ' -> ')+'P'+str(b)+' : '+label)
        if a==b:
            d.line((xs[a],y,xs[a]+100,y,xs[a]+100,y+25),fill="#334155",width=2)
            arrow(d,(xs[a]+100,y+25),(xs[a],y+25))
            d.text((xs[a]+12,y-29),label,font=font(17),fill="#0f172a")
        else:
            arrow(d,(xs[a],y),(xs[b],y),ret)
            centered(d,((xs[a]+xs[b])/2,y-21),label,17)
    centered(d,(w/2,h-24),"Success and error rows are alternative outcomes. No API gateway or external payment call.",17)
    lines.append("@enduml")
    (ROOT/"src"/(name+".puml")).write_text("\n".join(lines)+"\n",encoding="utf-8")
    im.save(ROOT/(name+".png"))
im=Image.new("RGB",(1500,940),"white"); d=ImageDraw.Draw(im)
centered(d,(750,35),"HMS - implemented component architecture",30)
boxes=[(520,80,980,165,"Browser: Django HTML templates / CSS"),(440,235,1060,335,"Django routing + middleware\nSession auth, role checks, security headers"),(80,420,425,545,"core / hostel / fees\nViews, forms, services, audit"),(575,420,925,545,"complaints / leaves\nvisitors / notices"),(1075,420,1420,545,"api/v1 and api/v2\nSupplementary JSON views"),(440,630,1060,720,"Django ORM + shared models"),(440,800,1060,890,"SQLite database\nDomain records, sessions, notifications, audit")]
for x1,y1,x2,y2,label in boxes:
    d.rounded_rectangle((x1,y1,x2,y2),radius=10,fill="#eff6ff",outline="#475569",width=2)
    centered(d,((x1+x2)/2,(y1+y2)/2),label,22)
arrow(d,(750,165),(750,235)); centered(d,(990,200),"HTTP local / HTTPS when deployed",17)
for x in [252,750,1247]:
    arrow(d,(750,335),(x,420)); arrow(d,(x,545),(750,630))
arrow(d,(750,720),(750,800))
im.save(ROOT/"component-diagram.png")
(ROOT/"src"/"component-diagram.puml").write_text("""@startuml component-diagram
title Implemented Django modular monolith
skinparam componentStyle rectangle
[Browser: HTML templates / CSS] as Browser
package "Single Django application" {
 [Routing + middleware\\nSessions / RBAC / security headers] as Routing
 [core / hostel / fees] as Domains1
 [complaints / leaves / visitors / notices] as Domains2
 [api/v1 + api/v2 JSON views] as API
 [Django ORM + shared models] as ORM
}
database "SQLite: domain records, sessions, notifications, audit" as DB
Browser --> Routing : HTTP local / HTTPS deployment
Routing --> Domains1
Routing --> Domains2
Routing --> API
Domains1 --> ORM
Domains2 --> ORM
API --> ORM
ORM --> DB
@enduml
""",encoding="utf-8")
