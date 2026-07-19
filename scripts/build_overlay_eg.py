#!/usr/bin/env python3
"""EG Vergabeplan: Stiegen-Vektor-Overlay auf unveraenderte Originalseite 3."""
import fitz

SRC = "original_einreichplan.pdf"
OUT = "Vergabeplan_Maschinenhalle_EG.pdf"
PT_PER_M = 28.3465

# Geometrie in Original-pt (PyMuPDF top-left, y nach unten)
xWo, xW, xE = 494.74, 499.27, 531.80
yN, yS = 193.70, 494.20
yP1_0, yP1_1 = 193.70, 227.03
yLN_0, yLN_1 = 227.03, 300.80
yP2_0, yP2_1 = 300.80, 334.70
yLS_0, yLS_1 = 334.70, 443.10
yAntr_1 = 494.20
N_TREADS_N, N_TREADS_S = 9, 13
xStep0, xStep1 = xW, xE

W_WALL, W_STEP, W_RUNLINE, W_DIM = 0.36, 0.20, 0.30, 0.15
BLACK = (0, 0, 0)
MAUER = (0.85, 0.42, 0.10)

doc = fitz.open(SRC)
out = fitz.open()
out.insert_pdf(doc, from_page=2, to_page=2)
page = out[0]
shape = page.new_shape()

def line(p1, p2, color=BLACK, width=W_STEP, dashes=None):
    shape.draw_line(fitz.Point(*p1), fitz.Point(*p2))
    shape.finish(color=color, width=width, dashes=dashes)

def rect(x0, y0, x1, y1, color=BLACK, width=W_WALL, fill=None):
    shape.draw_rect(fitz.Rect(x0, y0, x1, y1))
    shape.finish(color=color, width=width, fill=fill)

# 1) Neue Wand (Mauerwerk) + Schraffur
rect(xWo, yN, xW, yS, color=MAUER, width=W_WALL)
x = xWo - (yS - yN); stp = 3.0
while x < xW:
    x0 = max(xWo, x); y0 = yN + (x0 - x)
    x1v = min(xW, x + (yS - yN)); y1v = yN + (x1v - x)
    if x1v > x0:
        line((x0, y0), (x1v, y1v), color=MAUER, width=0.12)
    x += stp

# 2) Podeste
rect(xStep0, yP1_0, xStep1, yP1_1, color=BLACK, width=W_STEP)
rect(xStep0, yP2_0, xStep1, yP2_1, color=BLACK, width=W_STEP)

# 3+4) Stufen
for (y0, y1, n) in [(yLN_0, yLN_1, N_TREADS_N), (yLS_0, yLS_1, N_TREADS_S)]:
    d = (y1 - y0) / n
    for k in range(1, n):
        yy = y0 + k * d
        line((xStep0, yy), (xStep1, yy), width=W_STEP)
    line((xStep0, y0), (xStep0, y1), width=W_STEP)
    line((xStep1, y0), (xStep1, y1), width=W_STEP)

# 5) Bruchlinie ueber Lauf Nord
dN = (yLN_1 - yLN_0) / N_TREADS_N
xm = (xStep0 + xStep1) / 2; yb = yLN_0 + 3 * dN; amp = 3.5
line((xStep0, yb - amp), (xm, yb + amp), width=W_STEP)
line((xm, yb + amp), (xStep1, yb - amp), width=W_STEP)

# 6) Lauflinie + Antrittskreis (Sued) + Aufwaertspfeil (Nord)
xL = (xStep0 + xStep1) / 2
yStart, yEnd = yAntr_1 - 6, yP1_0 + 8
shape.draw_circle(fitz.Point(xL, yStart), 2.2); shape.finish(color=BLACK, width=W_RUNLINE)
line((xL, yStart), (xL, yEnd), width=W_RUNLINE)
line((xL, yEnd), (xL - 2.6, yEnd + 4.5), width=W_RUNLINE)
line((xL, yEnd), (xL + 2.6, yEnd + 4.5), width=W_RUNLINE)

# 7) Oeffnung ~0,90 m Nordwand (Annahme neue Tuer EG)
line((503.09, yN - 6.5), (503.09, yN), color=BLACK, width=W_STEP)
line((528.40, yN - 6.5), (528.40, yN), color=BLACK, width=W_STEP)

# 8) Bemassung
def dimv(y0, y1, x):
    line((x, y0), (x, y1), width=W_DIM)
    line((x - 2.2, y0), (x + 2.2, y0), width=W_DIM)
    line((x - 2.2, y1), (x + 2.2, y1), width=W_DIM)
def dimh(x0, x1, y):
    line((x0, y), (x1, y), width=W_DIM)
    line((x0, y - 2.2), (x0, y + 2.2), width=W_DIM)
    line((x1, y - 2.2), (x1, y + 2.2), width=W_DIM)
yb1 = yN - 12; xd = xE + 10
dimh(xStep0, xStep1, yb1)
dimv(yLS_0, yLS_1, xd)
dimv(yLN_0, yLN_1, xd)
shape.commit()

def text(x, y, s, size=5.2, rot=0):
    page.insert_text(fitz.Point(x, y), s, fontsize=size, color=BLACK, fontname="helv", rotate=rot)

text(xL - 9, (yLS_0 + yLS_1) / 2 + 4, "STIEGE", size=6.0, rot=90)
text(xL + 4, (yLS_0 + yLS_1) / 2 + 20, "24 STG 16,7/28,9", size=4.4, rot=90)
text(xStep0 + 1.5, yP1_0 + 21, "P1", size=4.4)
text(xStep0 + 1.5, yP2_0 + 21, "P2", size=4.4)
text((xStep0 + xStep1) / 2 - 5, yb1 - 2.5, "115", size=4.2)
text(xd + 3, (yLS_0 + yLS_1) / 2 + 8, "382", size=4.2, rot=90)
text(xd + 3, (yLN_0 + yLN_1) / 2 + 8, "260", size=4.2, rot=90)

out.save(OUT, garbage=4, deflate=True)
print("gespeichert:", OUT, "Seiten:", out.page_count)
