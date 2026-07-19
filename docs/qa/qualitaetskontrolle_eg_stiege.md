# Qualitätskontrolle – EG mit neuer Stiege

**Ausgabe:** `plaene/vergabeplan/Vergabeplan_Maschinenhalle_EG.pdf`
**Verfahren:** Originalseite 3 per `insert_pdf` unverändert übernommen; Stiege als neue Vektorebene ergänzt. Keine Rasterisierung.

## Kontrolle A – Maßkontrolle

| Prüfpunkt | Soll | Ergebnis |
|---|---|---|
| Seitengröße | A3 quer, 1191 × 842 pt | 1191 × 842 pt ✓ |
| Maßstab (9 Bestandsketten) | 28,3465 pt/m (1:100) | Abw. < 0,1 % ✓ |
| Lichte Stiegenraumbreite | ~1,15 m (Markup) | 32,53 pt = 1,148 m ✓ |
| Lauf Nord | 2,60 m (Markup) | 73,77 pt = 2,602 m ✓ |
| Lauf Süd | 3,82 m (Markup) | 108,40 pt = 3,824 m ✓ |
| Ostkante Stiege an Bestandswand | x = 531,8 | 531,8 (angeschnappt) ✓ |
| Südende neue Wand an Süd-Lagerwand | y = 494,2 | 494,2 (angeschnappt) ✓ |

## Kontrolle B – Overlay/Deckungskontrolle

Original-Seite 3 und Ausgabe koordinatengenau bei 300 dpi überlagert. Außerhalb des Stiegenbereichs deckungsgleich.

## Kontrolle C – PDF-Diff

- Geänderte Pixel gesamt: 21 112 (0,121 % der Seite)
- **Bounding-Box der Änderung: x 494,4–544,8 pt, y 176,2–494,2 pt** (= Stiegenbereich)
- **Änderungen außerhalb des Stiegenbereichs: 0 Pixel** ✓
- Eingebettete Bilder in der Ausgabe: **0** (nichts rasterisiert) ✓
- Blaue 1‑m-Referenzbox: nicht enthalten (Overlay liegt auf dem Original ohne Box) ✓

Ergebnis wie gefordert: Bestand keine Differenz, nur der neue Stiegenbereich zeigt Differenz.

Diff-Bild: `docs/qa/pdf_diff.png` (Magenta = Änderung).

## Dokumentierte Annahmen (mangels übermittelter Antworten – bitte bestätigen/korrigieren)

Das interaktive Rückfrage-Fenster brach dreimal mit Verbindungsfehler ab; die Antworten kamen nicht an. Folgende Punkte wurden mit der plausibelsten Lesart ausgeführt und sind leicht änderbar:

1. **Laufrichtung:** Antritt Süd (Zugang aus dem Lager), Aufwärtspfeil nach Norden, Austritt oben auf Podest P1 an der Nordwand.
2. **Stufenteilung:** 24 Steigungen 16,7/28,9 (Lauf Nord 9 Auftritte, Lauf Süd 13 Auftritte). Entspricht einer Geschosshöhe ≈ 4,00 m; **verbindliche Höhe folgt in Phase 3** und wird dann angepasst.
3. **Öffnung ~0,90 m in Nordwand** (Stiegenkopf): als neue EG-Türöffnung markiert (nur Laibungsandeutung).
4. **Weiße Box 1,6 × 2,0 m** westlich der neuen Wand: **nicht interpretiert und nicht gezeichnet** (Bedeutung unklar – Tür / Vorraum / Deckendurchbruch / Objekt?).
5. Overlay-Text in Helvetica statt BankGothicBT-Light (Originalfont nicht frei verfügbar) – reine Anmutungsabweichung.
