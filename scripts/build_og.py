#!/usr/bin/env python3
"""OG Vergabeplan - 1:1 nach Markup. Basis=EG-Blatt (Huelle/Rahmen/Massketten exakt),
Innenraum maskiert, OG als reine Vektoren an den gemessenen Positionen."""
import fitz, math
SRC="original_einreichplan.pdf"; OUT="Vergabeplan_Maschinenhalle_OG.pdf"
PTM=28.3465
BLACK=(0,0,0); WHITE=(1,1,1)
GOLD=(1,0.80,0.0); ORANGE=(1,0.55,0.05); SKY=(0.20,0.55,0.85)
WALLGREY=(0.62,0.62,0.62); FURN=(0.70,0.70,0.70); FURND=(0.45,0.45,0.45)
def M(m): return m*PTM
T20=M(0.20)

doc=fitz.open(SRC); out=fitz.open(); out.insert_pdf(doc,from_page=2,to_page=2); page=out[0]

# ===== 1) EG-Innenraum maskieren =====
s=page.new_shape()
def wbox(x0,y0,x1,y1): s.draw_rect(fitz.Rect(x0,y0,x1,y1)); s.finish(color=None,fill=WHITE)
wbox(214,192.5,549,657.5); wbox(549,192.5,961,657.5)
wbox(897,724,1136,764)
for x0,x1 in [(594,671),(841,917)]:
    wbox(x0,186,x1,193.6); wbox(x0,657,x1,664)
s.commit()

# ===== 2) Zonen-Fuellungen (unter allem, halbtransparent) =====
s=page.new_shape()
def zfill(x0,y0,x1,y1,c,op=0.22):
    s.draw_rect(fitz.Rect(x0,y0,x1,y1)); s.finish(color=None,fill=c,fill_opacity=op)
zfill(291.3,196,461.1,655.8,GOLD)      # West >=1,5
zfill(308.7,196,449.8,655.8,ORANGE)    # West >=1,7
zfill(460.6,307.5,623.9,541.7,ORANGE)  # Zentral >=1,7
zfill(615.3,200,897.3,660,ORANGE)      # Ost-Einheiten >=1,7
s.commit()

# ===== 3) Zeichen-Helfer =====
s=page.new_shape()
def line(p1,p2,color=BLACK,width=0.4,dashes=None):
    s.draw_line(fitz.Point(*p1),fitz.Point(*p2)); s.finish(color=color,width=width,dashes=dashes)
def rect(x0,y0,x1,y1,color=BLACK,width=0.4,fill=None,fo=1):
    s.draw_rect(fitz.Rect(x0,y0,x1,y1)); s.finish(color=color,width=width,fill=fill,fill_opacity=fo)
def oval(x0,y0,x1,y1,color=BLACK,width=0.35,fill=None):
    s.draw_oval(fitz.Rect(x0,y0,x1,y1)); s.finish(color=color,width=width,fill=fill)
def wallseg(x0,y0,x1,y1): rect(x0,y0,x1,y1,color=BLACK,width=0.4,fill=WALLGREY)

# ===== 4) Dachschnitt-Linien (First/Dachflaechen), thin =====
for tri in [[(647,428),(513,704),(380,428),(647,428)],
            [(380,422),(514,147),(647,422),(380,422)]]:
    for a,b in zip(tri,tri[1:]): line(a,b,width=0.3)
line((376,152),(376,694),width=0.5); line((755,145),(755,688),width=0.5)

# ===== 5) Stiege (wie EG) + Durchbrueche =====
xWo,xW,xE=493.5,499.27,531.8
wallseg(xWo,192.5,xW,657.5)
op=(498.1,300,532.0,442.1)
rect(*op,color=BLACK,width=0.8)
line((op[0],op[1]),(op[2],op[3]),width=0.5); line((op[0],op[3]),(op[2],op[1]),width=0.5)
o2x1=498.1-T20; o2x0=o2x1-M(2.0); cy=(op[1]+op[3])/2
wallseg(498.1-T20,op[1],498.1,op[3])
rect(o2x0,cy-M(0.9),o2x1,cy+M(0.9),color=BLACK,width=0.8)
line((o2x0,cy-M(0.9)),(o2x1,cy+M(0.9)),width=0.5); line((o2x0,cy+M(0.9)),(o2x1,cy-M(0.9)),width=0.5)

# ===== 6) Fixture-Symbole =====
def bed(bx,head):  # bx=(x0,y0,x1,y1) Bettflaeche; head='N/S/E/W'
    x0,y0,x1,y1=bx; rect(x0,y0,x1,y1,color=BLACK,width=0.5)
    w=x1-x0; h=y1-y0
    if head in 'NS':
        yk=y0+M(0.5) if head=='N' else y1-M(0.5)
        line((x0,yk),(x1,yk),width=0.35)
        yp=y0+M(0.08) if head=='N' else y1-M(0.42)
        for k in (0.27,0.73): rect(x0+w*k-M(0.28),yp,x0+w*k+M(0.28),yp+M(0.34),color=BLACK,width=0.3)
    else:
        xk=x0+M(0.5) if head=='W' else x1-M(0.5)
        line((xk,y0),(xk,y1),width=0.35)
        xp=x0+M(0.08) if head=='W' else x1-M(0.42)
        for k in (0.27,0.73): rect(xp,y0+h*k-M(0.28),xp+M(0.34),y0+h*k+M(0.28),color=BLACK,width=0.3)
def door(hx,hy,r,a0,a1):
    line((hx,hy),(hx+r*math.cos(math.radians(a0)),hy+r*math.sin(math.radians(a0))),width=0.35)
    s.draw_sector(fitz.Point(hx,hy),fitz.Point(hx+r*math.cos(math.radians(a0)),hy+r*math.sin(math.radians(a0))),a1-a0)
    s.finish(color=BLACK,width=0.3)
def shower(x0,y0,ss=M(0.9),tt=M(0.8)):
    rect(x0,y0,x0+ss,y0+tt,color=BLACK,width=0.5)
    line((x0,y0),(x0+ss,y0+tt),width=0.3); line((x0+ss,y0),(x0,y0+tt),width=0.3)
    circ=oval(x0+ss/2-1.2,y0+tt/2-1.2,x0+ss/2+1.2,y0+tt/2+1.2,width=0.3)
def wc(cx,cyt):  # Tank oben
    rect(cx-M(0.18),cyt,cx+M(0.18),cyt+M(0.12),color=BLACK,width=0.35)
    oval(cx-M(0.19),cyt+M(0.12),cx+M(0.19),cyt+M(0.55),color=BLACK,width=0.4)
def sink(x0,y0,w=M(0.55),h=M(0.4)):
    rect(x0,y0,x0+w,y0+h,color=BLACK,width=0.35); oval(x0+w*0.15,y0+h*0.2,x0+w*0.85,y0+h*0.8,width=0.3)
def grey(x0,y0,x1,y1,dark=False):
    rect(x0,y0,x1,y1,color=(0.3,0.3,0.3),width=0.35,fill=FURND if dark else FURN,fo=0.9)

# ===== 7) Waende der Einheiten (20cm) + 90cm-Tueren =====
UNITS={  # green-Umriss je Einheit
 'NW':(612.8,190.6,756.6,391.2),'NE':(756.6,187.8,897.2,424.3),
 'SW':(616.6,459.7,756.3,660.4),'SE':(756.3,425.1,899.3,659.3)}
def urect_walls(x0,y0,x1,y1,doorside,doorpos):
    # vier 20cm-Waende, Luecke 90cm an doorside
    dg=M(0.90)
    def seg_h(yy):
        if doorside in ('N','S') and ((doorside=='N' and abs(yy-y0)<1) or (doorside=='S' and abs(yy-y1)<1)):
            wallseg(x0,yy-T20/2,doorpos-dg/2,yy+T20/2); wallseg(doorpos+dg/2,yy-T20/2,x1,yy+T20/2)
        else: wallseg(x0,yy-T20/2,x1,yy+T20/2)
    def seg_v(xx):
        if doorside in ('W','E') and ((doorside=='W' and abs(xx-x0)<1) or (doorside=='E' and abs(xx-x1)<1)):
            wallseg(xx-T20/2,y0,xx+T20/2,doorpos-dg/2); wallseg(xx-T20/2,doorpos+dg/2,xx+T20/2,y1)
        else: wallseg(xx-T20/2,y0,xx+T20/2,y1)
    seg_h(y0); seg_h(y1); seg_v(x0); seg_v(x1)
# Tueren: NW/SW von West-Korridor; NE/SE von der Wand zu NW/SW (x=756.6)
urect_walls(*UNITS['NW'],'W',300);  urect_walls(*UNITS['SW'],'W',550)
urect_walls(*UNITS['NE'],'W',300);  urect_walls(*UNITS['SE'],'W',550)

# ===== 8) Moebel je Einheit (exakte Boxen) =====
BEDS={'NW':(615.3,217.2,675.7,299.8,'N'),'NE':(836.2,214.9,896.6,297.5,'N'),
      'SW':(617.0,553.1,677.4,635.7,'S'),'SE':(836.9,553.6,897.5,636.5,'S')}
BAD={'NW':(629.4,298.4,689.8,391.3),'NE':(835.2,330.2,895.9,423.0),
     'SW':(629.9,460.5,690.3,547.9),'SE':(835.9,428.5,896.4,521.4)}
WCB={'NW':(695.1,352.1,755.5,397.5),'NE':(759.1,352.1,809.0,393.7),
     'SW':(703.2,454.5,754.0,499.9),'SE':(757.4,456.2,808.2,499.7)}
for k,(x0,y0,x1,y1,hd) in BEDS.items():
    m=M(0.15); bed((x0+m,y0+m,x1-m,y1-m),hd)
# BAD: Wandkasten + Dusche + Waschtisch + Tuer
for k,(x0,y0,x1,y1) in BAD.items():
    rect(x0,y0,x1,y1,color=BLACK,width=0.5)              # Nasszellwand
    south = k in ('NW','NE')  # Dusche an aussenliegender Schmalseite
    if k in ('NW','SW'): shower(x1-M(1.0),(y0+M(0.1)) if k=='NW' else (y1-M(0.9)))
    else: shower(x0+M(0.1),(y0+M(0.1)) if k=='NE' else (y1-M(0.9)))
    sink(x0+M(0.1),y1-M(0.5) if k in('NW','NE') else y0+M(0.1))
    door(x0+M(0.1),y1-M(0.1) if k in('NW','NE') else y0+M(0.1), M(0.85), 270 if k in('NW','NE') else 90, 360 if k in('NW','NE') else 180)
# WC
for k,(x0,y0,x1,y1) in WCB.items():
    rect(x0,y0,x1,y1,color=BLACK,width=0.5)
    wc((x0+x1)/2, y0+M(0.12) if k in('NW','NE') else y1-M(0.67))
    sink(x0+M(0.08),y1-M(0.45) if k in('NW','NE') else y0+M(0.05),w=M(0.4),h=M(0.35))
# Graue Moebel (Kuecheneck-L + Couch), exakt
GREYS=[(616.3,192.9,633.0,232.3,0),(616.8,190.7,674.1,207.7,0),(615.8,301.8,677.9,318.9,1),
       (738.8,512.8,753.8,554.6,0),(705.1,499.2,753.8,513.3,0),
       (618.4,643.1,675.7,659.8,0),(617.7,619.5,634.4,659.1,0),
       (838.6,643.9,895.9,660.8,0),(879.4,620.2,896.1,659.8,0),
       (879.2,192.7,896.1,232.0,0),(838.6,189.8,895.9,206.7,0),(845.5,334.0,895.2,350.9,1),
       (758.8,338.5,807.3,352.6,0),(759.3,293.2,773.1,338.5,0),
       (759.3,513.0,774.1,555.0,0),(758.8,499.2,807.3,513.3,0),(846.7,499.9,896.4,516.8,1)]
for x0,y0,x1,y1,dk in GREYS: grey(x0,y0,x1,y1,dark=bool(dk))

# ===== 9) Korridor-/Trennwaende =====
wallseg(612.8-T20,192.5,612.8,657.5)      # Korridorwand West
wallseg(756.6-T20/2,192.5,756.6+T20/2,657.5)  # Wand A|B (mit Tuer schon oben)
wallseg(612.8,425-T20/2,899,425+T20/2)    # N/S-Trennwand
s.commit()

# ===== 10) Beschriftung + Zonenlinien + Titel =====
s=page.new_shape()
def txt(x,y,t,sz=4.6,rot=0,col=BLACK): page.insert_text(fitz.Point(x,y),t,fontsize=sz,color=col,fontname="helv",rotate=rot)
for k,(x0,y0,x1,y1) in UNITS.items():
    yy=y0+M(1.6) if k in('NW','NE') else y1-M(1.4)
    txt(x0+M(0.4),yy,"SCHLAFEN",4.4)
for k,(x0,y0,x1,y1) in BAD.items():
    txt(x0+M(0.15),(y0+M(0.5)) if k in('NW','NE') else (y1-M(0.15)),"BAD 1,78m²",3.0)
for k,(x0,y0,x1,y1) in WCB.items():
    txt(x0+M(0.1),(y0+M(0.9)) if k in('NW','NE') else (y1-M(0.15)),"WC 1,92m²",2.8)
txt(505,300,"STIEGE",4.8,rot=90); txt(op[0]+3,op[1]+M(1.2),"Durchbruch",3.2,rot=90)
# Raumhoehen-Legende
lx,ly=228,232
for i,(c,l) in enumerate([(GOLD,"lichte Raumhöhe ≥ 1,5 m"),(ORANGE,"≥ 1,7 m"),(SKY,"≥ 2,0 m")]):
    rect(lx,ly+i*8,lx+8,ly+i*8+5,color=c,width=0.5,fill=c,fo=0.6); txt(lx+11,ly+i*8+4.3,l,4.0)
txt(900,750,"OBERGESCHOSS",13.5); txt(902,761,"± 5,28 = FBOK OG = 560,49 müA",5.0)
s.commit()
out.save(OUT,garbage=4,deflate=True)
print("OG gespeichert. Bilder:",len(out[0].get_images()))
