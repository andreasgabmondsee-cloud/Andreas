# Phase 2 – Analyse & Kalibrierung Obergeschoss (Datei: Grundrisse_2026_Maschinenhalle_OG.pdf)

## Kalibrierung
- PowerPoint-Export (Acrobat PDFMaker), 1 Seite 960 × 540 pt, eingebettetes Vollbild = Originalseite 3.
- Registrierung an 4 Fixpunkten: **0 px Versatz** in x und y.
- Blaue Referenzbox: **14,16 pt = 1,00 m** (identisch zum EG).
- Affine Abbildung wie EG: `x_orig = (x_mk − 124,80)·1,98978`, `y_orig = (y_mk − 46,92)·1,98941`.

## Grundlegender Unterschied zum EG (wichtig)
Das OG ist im Original-Einreichplan **nicht** als Bestand vorhanden. Der EG-Overlay-Trick (Originalseite behalten, nur Stiege ergänzen) funktioniert hier **nicht**, weil auf der OG-Ebene der gesamte EG-Inhalt (Maschinen, PKW, Raumnamen lager/werkstatt/maschinenpark, Brandabschnitte, mobile Hebebühne …) **nicht** erscheinen darf.

⇒ Der OG-Grundriss muss als **eigenständige Vektor-Planseite** neu aufgebaut werden. Übernommen wird geometrisch exakt nur die **Gebäudehülle** (Außenwände Stahlbeton + Wärmedämmung, Stützenraster, Achsen A/B, Planrahmen, Nordpfeil, Maßketten der Außenkontur) aus der Originalseite; der EG-Innenausbau entfällt. Die Stiege wird identisch zum EG übernommen.

## Erkannter Inhalt (aus Vektor- + Rastersymbolen des Markups)
- **FBOK OG = +5,28 m** (mehrfach beschriftet „+5,28"). Das ist die verbindliche OG-Fußbodenhöhe → relevant auch für die endgültige Stufenzahl der EG-Stiege (Phase 3).
- **Raumhöhen-Zonen (Dachschräge), Legende rechts:** gold ≥ 1,5 m (an der West-/Ost-Traufe), orange ≥ 1,7 m, blau ≥ 2,0 m. Symmetrisch um den First (N–S). Die Diagonalen im Plan sind die Dachflächen-/First-Projektion.
- **Stiege:** gleiche Lage/Geometrie wie EG (Schacht x 498–532, neue Mauerwerkswand x 493–498). Am Stiegenkopf ein **Deckendurchbruch** (grau-transparentes Feld) + zwei größere weiße Felder ~5,2 × 4,0 m (Luftraum/Durchbruch – zu bestätigen).
- **„Box" 1,6 × 2,0 m** westlich der neuen Wand – erscheint erneut an identischer Stelle wie im EG (weiter ungeklärt).

### Raumbuch (Einheiten, Ost-Hälfte, 2 × 2 gespiegelt)
| Einheit | Lage | Rohmaß (green) | Inhalt (Rastersymbole) |
|---|---|---|---|
| 1 | NW | 5,07 × 7,07 m | SCHLAFEN (Bett), BAD 1,78 m² Dusche 90/80 +5,28, WC 1,92 m² +5,28, GARD. |
| 2 | NO | 4,96 × 8,35 m | SCHLAFEN, BAD, WC, GARD. (gespiegelt) |
| 3 | SW | 4,93 × 7,08 m | SCHLAFEN, BAD, WC, GARD. |
| 4 | SO | 5,05 × 8,26 m | SCHLAFEN, BAD, WC, GARD. |

- **Fenster** (blau, ~1,40 × 0,88 m): je Einheit an der Außenwand; zusätzlich 2 an der West-Traufe und mittig – insgesamt 8 erfasst.
- **Stützen** (grau, 0,79 × 0,99 m): 4 Stück an den inneren Einheitsecken (Bestand-Stahlbetonstützen der Halle).
- **Möbel** (Betten, Duschtassen, WC, Waschtische, Schränke): im Markup als **Rasterbilder** eingefügt → müssen laut Vorgabe als Vektoren neu gezeichnet werden.

## Genau zu klären, bevor gezeichnet wird (Prioritätsregel 10)
1. **Umfang OG-Ausbau:** Nur baulicher Grundriss (Wände, Fenster, Türen, Stiege, Raumhöhen-Zonen, Beschriftung, Bemaßung) – oder inkl. vektorisierter Möblierung (Betten/Sanitär)?
2. **Wandstärken der neuen OG-Trennwände** (im Markup nur als Linien, keine Bemaßung): Vorschlag Trennwände 10 cm, Bad-/WC-Wände 10 cm, tragende neue Wände 20 cm – bitte bestätigen oder Maße nennen.
3. **Voids/Deckendurchbrüche** (2 weiße Felder ~5,2 × 4,0 m + Feld am Stiegenkopf): Luftraum über EG? Genaue Kontur?
4. **„Box" 1,6 × 2,0 m** (wie EG): Bedeutung?
5. **Symmetrie:** Sind die 4 Einheiten exakt gespiegelt (dann rekonstruiere ich 1 Einheit und spiegle) oder gibt es Abweichungen?
6. **Türen/Laufrichtung Stiege** aus EG weiterhin offen (deine Antworten kamen technisch nie an).
