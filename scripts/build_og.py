#!/usr/bin/env python3
"""OG Vergabeplan: eigenstaendige Vektorseite. Basis=EG-Blatt (Rahmen/Massketten/Legende/
Nordpfeil), Innenraum maskiert, OG frisch als Vektoren. Gebaeudehuelle bleibt exakt."""
import fitz, math

SRC="original_einreichplan.pdf"; OUT="Vergabeplan_Maschinenhalle_OG.pdf"
PTM=28.3465
BLACK=(0,0,0); WHITE=(1,1,1)
GOLD=(1,0.80,0.0); ORANGE=(1,0.55,0.05); SKY=(0.30,0.62,0.85)
WALLGREY=(0.72,0.72,0.72)
W_WALL=0.5; W_THIN=0.4; W_FIX=0.5; W_DIM=0.35; W_HATCH=0.2
def M(m): return m*PTM
YM=425.0
def mir(y): return 2*YM-y

doc=fitz.open(SRC); out=fitz.open(); out.insert_pdf(doc,from_page=2,to_page=2); page=out[0]

# ===== 1) EG-Innenraum maskieren =====
sh=page.new_shape()
def wbox(x0,y0,x1,y1): sh.draw_rect(fitz.Rect(x0,y0,x1,y1)); sh.finish(color=None,fill=WHITE)
wbox(214,192.5,549,657.5); wbox(549,192.5,961,657.5)      # West- + Ost-Block innen
wbox(897,724,1136,764)                                     # EG-Titel "ERDGESCHOSS"+Hoehenzeile ueberdecken
for x0,x1 in [(594,671),(841,917)]:
    wbox(x0,186,x1,193.6); wbox(x0,657,x1,664)             # Sektionaltor-Blaetter
sh.commit()

# ===== 2) Zeichen-Helfer =====
sh=page.new_shape()
def line(p1,p2,color=BLACK,width=W_THIN,dashes=None):
    sh.draw_line(fitz.Point(*p1),fitz.Point(*p2)); sh.finish(color=color,width=width,dashes=dashes)
def rect(x0,y0,x1,y1,color=BLACK,width=W_THIN,fill=None,fo=1):
    sh.draw_rect(fitz.Rect(x0,y0,x1,y1)); sh.finish(color=color,width=width,fill=fill,fill_opacity=fo)
def circ(cx,cy,r,color=BLACK,width=W_FIX,fill=None):
    sh.draw_circle(fitz.Point(cx,cy),r); sh.finish(color=color,width=width,fill=fill)
def wallseg(x0,y0,x1,y1):   # gefuellte 20cm-Wandbox
    sh.draw_rect(fitz.Rect(x0,y0,x1,y1)); sh.finish(color=BLACK,width=0.4,fill=WALLGREY)
def hatch(x0,y0,x1,y1,color,gap=5.0):
    rect(x0,y0,x1,y1,color=color,width=W_HATCH)
    x=x0-(y1-y0)
    while x<x1:
        a=max(x0,x); ya=y0+(a-x); b=min(x1,x+(y1-y0)); yb=y0+(b-x)
        if b>a: line((a,ya),(b,yb),color=color,width=W_HATCH)
        x+=gap
T=5.669  # 20 cm

# ===== 3) Raumhoehen-Zonen (Dachschraege, First N-S, sym. zu beiden Traufen) =====
# Konturlinien der lichten Raumhoehe (dünn, farbig, gestrichelt) + Fuellandeutung im leeren Westteil
def zone_line(x,color,lab):
    line((x,193),(x,657),color=color,width=0.6,dashes="[3 2] 0")
# West-Traufe (x~215) -> First; Ost-Traufe (x~961) -> First. First ca. Gebaeudemitte-Ost.
for x,c,l in [(300,GOLD,"1,5m"),(331,ORANGE,"1,7m"),(372,SKY,"2,0m")]:
    zone_line(x,c,l)
for x,c,l in [(930,GOLD,"1,5m"),(899,ORANGE,"1,7m")]:
    zone_line(x,c,l)
# leichte Fuellandeutung nur im leeren West-Attic (keine Moebel dort)
hatch(215,196,300,656,GOLD,gap=8)
hatch(300,196,331,656,ORANGE,gap=8)

# ===== 4) Stiege (wie EG) + Durchbrueche =====
xWo,xW,xE=493.5,499.27,531.8
yN,ySs=336.4,488.4     # im OG nur Suedlauf-Bereich + Antritt sichtbar (wie Markup)
# neue Mauerwerkswand
wallseg(xWo,192.5,xW,657.5)
# Stiegendurchbruch in OG-Bodenplatte: Oeffnung ueber Stiegenlauf
op_x0,op_y0,op_x1,op_y1=498.1,300,532.0,442.1
rect(op_x0,op_y0,op_x1,op_y1,color=BLACK,width=0.8)
line((op_x0,op_y0),(op_x1,op_y1),color=BLACK,width=0.5)   # Durchbruch-Diagonale
line((op_x0,op_y1),(op_x1,op_y0),color=BLACK,width=0.5)
# 2,0 x 1,8 m Oeffnung daneben (westlich), Wand dazwischen
o2_x1=498.1-T; o2_x0=o2_x1-M(2.0); o2_cy=(op_y0+op_y1)/2; o2_y0=o2_cy-M(0.9); o2_y1=o2_cy+M(0.9)
wallseg(498.1-T,op_y0,498.1,op_y1)     # Wand zwischen Stiege und Oeffnung
rect(o2_x0,o2_y0,o2_x1,o2_y1,color=BLACK,width=0.8)
line((o2_x0,o2_y0),(o2_x1,o2_y1),color=BLACK,width=0.5); line((o2_x0,o2_y1),(o2_x1,o2_y0),color=BLACK,width=0.5)

# ===== 5) Fixture-Symbole =====
def bed(x0,y0,w,h,head='N'):
    rect(x0,y0,x0+w,y0+h,color=BLACK,width=W_FIX)
    # Decke + Kopfkissen
    if head in 'NS':
        py=y0+4 if head=='N' else y0+h-4-M(0.5)
        line((x0,y0+ (M(0.55) if head=='N' else h-M(0.55))),(x0+w,y0+(M(0.55) if head=='N' else h-M(0.55))),width=0.35)
        for k in (0.28,0.72):
            rect(x0+w*k-M(0.28),py,x0+w*k+M(0.28),py+M(0.42),color=BLACK,width=0.3)
    else:
        px=x0+4 if head=='W' else x0+w-4-M(0.5)
        line((x0+(M(0.55) if head=='W' else w-M(0.55)),y0),(x0+(M(0.55) if head=='W' else w-M(0.55)),y0+h),width=0.35)
        for k in (0.28,0.72):
            rect(px,y0+h*k-M(0.28),px+M(0.42),y0+h*k+M(0.28),color=BLACK,width=0.3)
def shower(x0,y0,w,h):
    rect(x0,y0,x0+w,y0+h,color=BLACK,width=W_FIX)
    line((x0,y0),(x0+w,y0+h),width=0.3); line((x0+w,y0),(x0,y0+h),width=0.3)
    circ(x0+w/2,y0+h/2,1.2,width=0.3)
def wc(cx,cy):   # WC von oben, Tank oben (Nord)
    rect(cx-M(0.18),cy-M(0.30),cx+M(0.18),cy-M(0.18),color=BLACK,width=0.35)  # Spuelkasten
    sh.draw_oval(fitz.Rect(cx-M(0.19),cy-M(0.19),cx+M(0.19),cy+M(0.28))); sh.finish(color=BLACK,width=0.4)
def sink(x0,y0,w,h):
    rect(x0,y0,x0+w,y0+h,color=BLACK,width=0.4)
    sh.draw_oval(fitz.Rect(x0+w*0.15,y0+h*0.2,x0+w*0.85,y0+h*0.8)); sh.finish(color=BLACK,width=0.3)
def wardrobe(x0,y0,w,h):
    rect(x0,y0,x0+w,y0+h,color=BLACK,width=0.4)
    if w>h: line((x0,y0+h*0.5),(x0+w,y0+h*0.5),width=0.3)
    else: line((x0+w*0.5,y0),(x0+w*0.5,y0+h),width=0.3)
def sofa(x0,y0,w,h):
    rect(x0,y0,x0+w,y0+h,color=BLACK,width=0.45)
    rect(x0+2,y0+2,x0+w-2,y0+h*0.6,color=BLACK,width=0.3)
def table(cx,cy,w,h):
    rect(cx-w/2,cy-h/2,cx+w/2,cy+h/2,color=BLACK,width=0.4)
def kitchen(x0,y0,w,h):
    rect(x0,y0,x0+w,y0+h,color=BLACK,width=0.45)
    circ(x0+w*0.25,y0+h/2,M(0.18),width=0.3); circ(x0+w*0.5,y0+h/2,M(0.18),width=0.3)  # Kochfeld
    sh.draw_oval(fitz.Rect(x0+w*0.72,y0+h*0.25,x0+w*0.92,y0+h*0.75)); sh.finish(color=BLACK,width=0.3)  # Spuele
def door(hinge,x,y,wdir,leng):   # Tueroeffnung mit Schwenk; hinge=(x,y), swing quarter
    r=leng
    # Blattlinie
    ang0,ang1={'NE':(270,360),'NW':(180,270),'SE':(0,90),'SW':(90,180)}[wdir]
    sh.draw_sector(fitz.Point(x,y),fitz.Point(x+r*math.cos(math.radians(ang0)),y+r*math.sin(math.radians(ang0))),(ang1-ang0))
    sh.finish(color=BLACK,width=0.3)

# ===== 6) Eine Einheit zeichnen =====
def unit(x0,y0,x1,y1,typ,flip=False):
    """typ 'A'(schmal) oder 'B'(tief). flip=True spiegelt Nord/Sued (Inhalt vertikal)."""
    def yy(v): return (y0+y1-v) if flip else v
    def R(ax0,ay0,ax1,ay1,**k):
        a,b=sorted([yy(ay0),yy(ay1)]); rect(ax0,a,ax1,b,**k)
    def WS(ax0,ay0,ax1,ay1):
        a,b=sorted([yy(ay0),yy(ay1)]); wallseg(ax0,a,ax1,b)
    w=x1-x0; h=y1-y0
    # Perimeter-Innenwaende (20cm) zum Korridor (Westseite) + zwischen Einheiten wird global gezogen
    # Nasszellen unten (BAD links, WC rechts), Schlafen oben
    ybw=y0+h-M(3.0)   # Trennlinie Schlafen / Nasszellen
    # Wand Schlafen|Nass
    WS(x0,ybw-T/2,x1,ybw+T/2)
    if typ=='A':
        # SCHLAFEN oben: Doppelbett Kopf West
        bed(x0+M(0.15),y0+M(0.5),M(1.6),M(2.0),head='W') if False else bed(x0+M(0.4),y0+M(0.4),M(2.0),M(1.6),head='N')
        wardrobe(x1-M(0.6),y0+M(0.4),M(0.55),M(2.0))
        # Nass: BAD links, WC rechts
        xmid=x0+w*0.52
        WS(xmid-T/2,ybw,xmid+T/2,y1)
        # BAD
        shower(x0+M(0.3),y1-M(1.1),M(0.9),M(0.8)); sink(x0+M(0.3),ybw+M(0.2),M(0.6),M(0.4))
        # WC
        wc(xmid+ (x1-xmid)/2, y1-M(0.7)); sink(xmid+M(0.25),ybw+M(0.2),M(0.6),M(0.4))
    else:
        # Typ B: Wohnen/Kueche oben, Schlafen mitte, Nass unten
        ykit=y0+M(3.2)
        # Kueche + Couch am Fenster (Ostwand rechts)
        kitchen(x1-M(2.6),y0+M(0.35),M(2.4),M(0.6))
        sofa(x1-M(2.2),y0+M(1.4),M(2.0),M(0.85))
        table(x0+M(1.4),y0+M(1.6),M(1.2),M(0.8))
        WS(x0,ykit-T/2,x1,ykit+T/2)
        # SCHLAFEN mitte
        bed(x1-M(2.2),ykit+M(0.4),M(2.0),M(1.6),head='N')
        wardrobe(x0+M(0.3),ykit+M(0.3),M(0.55),M(2.0))
        # Nass unten
        xmid=x0+w*0.5
        WS(xmid-T/2,ybw,xmid+T/2,y1)
        shower(x0+M(0.3),y1-M(1.1),M(0.9),M(0.8)); sink(x0+M(0.3),ybw+M(0.2),M(0.6),M(0.4))
        wc(xmid+(x1-xmid)/2,y1-M(0.7)); sink(xmid+M(0.25),ybw+M(0.2),M(0.6),M(0.4))

# Einheiten-Boxen (Innenmasse) + Korridorwand
AX=(618.5,192.5,756.6,388)     # Typ A NW
BX=(756.6,192.5,895,422)       # Typ B NE
# Korridorwand West der Einheiten (x ~ 612), zwischen Korridor und Einheiten
wallseg(612.8-T,192.5,612.8,657.5)
# Wand zwischen A und B (x=756.6)
wallseg(756.6-T/2,192.5,756.6+T/2,657.5)
# Aussen-Umriss Einheiten (Nordwand schon Envelope). Zeichne Einheiten:
unit(*AX,'A',flip=False); unit(AX[0],mir(AX[3]),AX[2],mir(AX[1]),'A',flip=True)
unit(*BX,'B',flip=False); unit(BX[0],mir(BX[3]),BX[2],mir(BX[1]),'B',flip=True)
# Wand Nord/Sued-Trennung (Mittelachse) zwischen den Einheitenreihen
wallseg(612.8,YM-T/2,895,YM+T/2)

# ===== 7) Fenster (blau, an Aussenwaenden) =====
def window(x0,y0,x1,y1):
    rect(x0,y0,x1,y1,color=(0,0.2,0.7),width=0.5,fill=SKY,fo=0.5)
for (x0,y0,x1,y1) in [(633,188,674,193.6),(852,188,892,193.6)]:   # Nordwand Fenster
    window(x0,y0,x1,y1); window(x0,mir(y1),x1,mir(y0))
for (y0,y1) in [(235,300),(330,395)]:   # Ostwand Fenster (senkrecht)
    window(957,y0,962.5,y1); # nur Andeutung

sh.commit()

# ===== 8) Beschriftung =====
sh=page.new_shape()
def txt(x,y,s,sz=5.0,rot=0,col=BLACK):
    page.insert_text(fitz.Point(x,y),s,fontsize=sz,color=col,fontname="helv",rotate=rot)
def unit_labels(x0,y0,x1,y1,flip=False):
    def yy(v): return (y0+y1-v) if flip else v
    txt(x0+M(0.6),yy(y0+M(1.4)),"SCHLAFEN",4.6)
    txt(x0+M(0.3),yy(y1-M(0.4)),"BAD 1,78m²",3.6); txt(x0+M(0.3),yy(y1-M(0.05)),"+5,28",3.2)
    txt((x0+x1)/2+M(0.2),yy(y1-M(0.4)),"WC 1,92m²",3.6)
unit_labels(*AX); unit_labels(AX[0],mir(AX[3]),AX[2],mir(AX[1]),flip=True)
unit_labels(*BX); unit_labels(BX[0],mir(BX[3]),BX[2],mir(BX[1]),flip=True)
txt(505,300,"STIEGE",5.0,rot=90); txt(op_x0+3,op_y0+M(1.2),"Durchbruch",3.4,rot=90)
# Titel OG (an Stelle des ueberdeckten EG-Titels)
txt(900,750,"OBERGESCHOSS",13.5,col=BLACK)
txt(902,761,"± 5,28 = FBOK OG = 560,49 müA",5.0)
# Raumhoehen-Legende (kompakt, oben links im leeren Bereich)
lx,ly=228,235
for i,(c,l) in enumerate([(GOLD,"lichte Raumhöhe ≥ 1,5 m"),(ORANGE,"≥ 1,7 m"),(SKY,"≥ 2,0 m")]):
    yy=ly+i*8
    sh_leg=None
    rect(lx,yy,lx+8,yy+5,color=c,width=0.5,fill=c,fo=0.6)
    txt(lx+11,yy+4.3,l,4.0)
sh.commit()

out.save(OUT,garbage=4,deflate=True)
print("OG gespeichert:",OUT,"Bilder(Ausgabe):",len(out[0].get_images()))
