# Qualitätskontrolle – Obergeschoss (erste Vollversion)

**Ausgabe:** `plaene/vergabeplan/Vergabeplan_Maschinenhalle_OG.pdf` (A3, 1191 × 842 pt, 0 Bilder → reine Vektoren)
**Build:** `scripts/build_og.py`

## Verfahren
Eigenständige OG-Vektorseite auf Basis des EG-Blatts. Gebäudeinneres per weißer Maske entfernt (EG-Maschinen/Räume/Brandabschnitte), Sektionaltor-Blätter überdeckt, EG-Titel → „OBERGESCHOSS" ersetzt. **Gebäudehülle, Rahmen, Außenmaßketten, Achsen, Nordpfeil, Legende bleiben aus dem Original unverändert.**

## Kontrollen
- **Hüllen-/Blattkontrolle (Diff EG↔OG):** Änderungen liegen ausschließlich im maskierten Innenraum, im Titelfeld und an den überdeckten Sektionaltoren. Außerhalb (Rahmen, Maßketten 2700/1720/500-250, Achsen A/B, Legende): keine Abweichung.
- **Maßstab/Hülle:** identisch zum EG (gleiche Seite, 28,3465 pt/m). Stiege/neue Wand deckungsgleich mit EG-Position.
- **Reine Vektoren:** 0 eingebettete Bilder in der Ausgabe (Möblierung als Vektorsymbole).

## Umgesetzt (gemäß Freigabe)
- Alle Wände 20 cm; 4 Einheiten (2 Typen) exakt N/S gespiegelt.
- Vektor-Möblierung: Doppelbett, Dusche, WC, Waschtisch, Kücheneck (Kochfeld+Spüle), Sofa, Tisch, Schrank/Kasten.
- Als Deckenöffnung **nur** Stiegendurchbruch + 2,0 × 1,8 m-Öffnung daneben, mit Wand dazwischen.
- Raumhöhen-Zonen (gold ≥1,5 / orange ≥1,7 / blau ≥2,0 m) als Konturlinien + Legende + Füllandeutung im West-Attic.
- Raumbeschriftung SCHLAFEN / BAD 1,78 m² / WC 1,92 m² / +5,28; Titel „OBERGESCHOSS", FBOK OG +5,28.

## Bewusst noch als „Entwurf" markiert – Feinabstimmung erwünscht
1. **Möbel-Feinposition/-orientierung**: schematisch platziert nach Raumprogramm; exakte Lage je Einheit noch an das Markup anzugleichen (Bettausrichtung, Bad-/WC-Anordnung, Kücheneck/Couch-Seite).
2. **Türen/Durchgänge** der Einheiten noch nicht gesetzt (Eingang vom Mittelkorridor, Zimmertüren).
3. **Innenbemaßung** der Einheiten (Zimmergrößen) folgt nach Layout-Freigabe.
4. Kleiner Rest-Text „bestand/rasen" an der Ost-Außenwand (Stellplatz-Beschriftung des Bestands) bewusst belassen.
