# Phase 1 – Technische Analyse Original-Einreichplan Maschinenhalle

**Datei:** `plaene/original/Bewilligt_EINREICHPLAN_MASCHINENHALLE_2_A3_100.pdf`
**SHA-256:** `52eb2905411a422b0d99ded44920a2c95433079d7ebc651ab887fc33e602a0a8`
**Status:** Nur Analyse – keinerlei Änderung am Original. Diese Datei ist die unveränderliche Master-Grundlage.

## Dokument

| Eigenschaft | Wert |
|---|---|
| PDF-Version | 1.7 |
| Producer | GPL Ghostscript 10.06.0 (via PDF24 Creator) |
| Seiten | 9 |
| Verschlüsselung | keine |
| OCG-Ebenen | keine |
| Annotationen | keine |

## Seitenübersicht

Alle Seiten identisch: **MediaBox = CropBox = 0 0 1191 842 pt = 420,2 × 297,0 mm (A3 quer)**, Rotation 0.

| Seite | Inhalt | Vektorpfade | Bilder |
|---|---|---|---|
| 1 | Deckblatt / Plankopf Einreichplan 1/100 | 71 | 0 |
| 2 | Lageplan 1:500 | 74 788 | 0 |
| 3 | **Erdgeschoss-Grundriss** (lager, werkstatt, lager-werkstatt, kleinteile, maschinenpark; Schnittlinien a‑a / b‑b; Brandabschnitte) | 6 226 | 0 |
| 4 | Schnitt aa | 1 670 | 0 |
| 5 | Schnitt bb | 1 277 | 0 |
| 6 | Ansicht Nord | 1 058 | 0 |
| 7 | Ansicht Ost | 816 | 0 |
| 8 | Ansicht Süd | 1 157 | 0 |
| 9 | Ansicht West | 2 636 | 0 |

**Ergebnis:** Reines Vektor-PDF (0 eingebettete Bilder auf allen Seiten, echter Text mit Font `BankGothicBT-Light`). Die Originalseite 3 kann unverändert als Vektorbasis übernommen werden (Overlay-Verfahren mit PyMuPDF/pikepdf, keine Rasterisierung).

## Koordinatensystem (verbindlich für alle Overlays)

- Arbeitsbasis: **PDF-Userspace der Seite 3**, Einheit Punkt (1 pt = 1/72 in), MediaBox `0 0 1191 842`.
- PyMuPDF-Konvention: Ursprung **links oben**, y nach unten (natives PDF: links unten, y nach oben — bei der Overlay-Erzeugung wird konsistent in einer Konvention gearbeitet und dokumentiert).
- Keine Seitenrotation, CropBox = MediaBox → keine Offset-Korrekturen nötig.

## Maßstabskontrolle Seite 3 (EG)

Nominal 1:100 auf A3 ⇒ **1 m real = 10 mm Papier = 28,3465 pt**.

Messung von 8 unabhängigen Maßketten (Maßlinienlängen, korrigiert um beidseitigen Linien-Überstand δ ≈ 0,76 pt, bestimmt aus dem Kettenpaar 1160/1710):

| Kette (cm) | Richtung | gemessen (pt) | f korrigiert (pt/m) |
|---|---|---|---|
| 2700 | horizontal | 766,62 | 28,337 |
| 1160 | horizontal | 330,09 | 28,326 |
| 1710 | horizontal | 485,88 | 28,326 |
| 1100 | horizontal | 313,08 | 28,324 |
| 1239 | horizontal | 352,35 | 28,316 |
| 625  | horizontal | 178,50 | 28,318 |
| 1720 | vertikal | 488,82 | 28,332 |
| 1980 | vertikal | 562,53 | 28,334 |
| 1675 | vertikal | 476,07 | 28,332 |

**Mittelwert f ≈ 28,33 pt/m**, Abweichung zum Nominalwert < 0,1 % (innerhalb Linienbreiten-/Messtoleranz).

⇒ Der Plan liegt maßhaltig im Maßstab **1:100** vor. Für die spätere Stiegen-Konstruktion wird mit dem nominalen Faktor **28,3465 pt/m** gearbeitet und jede Position zusätzlich gegen real gemessene Bestandskanten (Wandachsen, Gebäudeecken) registriert.

## Festgelegte Arbeitsweise für Phase „EG + Stiege“

1. Originalseite 3 wird per pikepdf/PyMuPDF **unverändert** übernommen (keine Rasterung, keine Re-Kompression der Inhalte).
2. Neue Stiege entsteht als **separate Vektor-Overlay-Ebene** exakt im Koordinatensystem der Originalseite.
3. Kalibrierung des Markups: blaue 1×1‑m-Referenzbox (Priorität 1) + Gegenkontrolle über Bestandsmaßketten (Priorität 2) + Registrierung an mehreren weit auseinanderliegenden Bestandsfixpunkten (Priorität 3).
4. Qualitätskontrolle: Maßkontrolle, Overlay-Deckungskontrolle, visueller PDF-Diff (außerhalb des Stiegenbereichs: 0 Differenz).

## Offene Punkte

- Warten auf **Datei B**: bearbeiteter EG-Plan mit eingezeichneter Stiege (inkl. blauer 1‑m-Referenzbox links oben).
- Ggf. schriftliche Stiegenmaße des Bauherrn (haben Vorrang vor der Grafik).
