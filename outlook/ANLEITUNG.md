# Anleitung: Claude Code steuert Outlook 2016 auf deinem PC

Danach kannst du Claude Code auf deinem Windows-PC z. B. sagen:
*„Was ist heute Neues im Posteingang?“*, *„Antworte Gerhard, dass die Teile bei Fink liegen“*,
*„Leite die Rechnung an die Buchhaltung weiter“* oder *„Lösch die Amazon-Mails von gestern“*.
Claude schreibt die Texte in deinem Stil (`docs/email-schreibstil.md`) und **sendet erst, wenn du zustimmst.**

Dauer: ca. 15 Minuten. Alle Befehle in **PowerShell** eingeben (Start → „PowerShell“).

---

## Schritt 1 – Programme installieren (einmalig)

```powershell
winget install -e --id Python.Python.3.12
```
```powershell
winget install -e --id Git.Git
```
Danach **PowerShell schließen und neu öffnen**.

Claude Code installieren:
```powershell
irm https://claude.ai/install.ps1 | iex
```
Wieder PowerShell neu öffnen und mit `claude --version` prüfen.

> Falls `winget` fehlt: Python von https://www.python.org/downloads/ (Haken bei
> „Add python.exe to PATH“!) und Git von https://git-scm.com/download/win installieren.

## Schritt 2 – Dieses Repo auf den PC holen

```powershell
cd $HOME\Documents
```
```powershell
git clone https://github.com/andreasgabmondsee-cloud/Andreas.git
```
```powershell
cd Andreas
```
```powershell
git checkout claude/sleepy-ride-bpn958
```

(Beim ersten Mal fragt Git nach deinem GitHub-Login – im Browserfenster anmelden.)

## Schritt 3 – Einrichtung + Test

Outlook 2016 darf geöffnet sein. Dann:
```powershell
powershell -ExecutionPolicy Bypass -File outlook\setup.ps1
```
Das Skript installiert `pywin32`, verbindet sich mit Outlook und zeigt deine Konten und die
3 neuesten Mails. Alles grün → fertig.

## Schritt 4 – Berechtigungen aktivieren (empfohlen)

Damit Claude lesen/suchen darf, ohne jedes Mal zu fragen, aber **vor dem Senden, Antworten,
Weiterleiten und Löschen immer nachfragt**:
```powershell
New-Item -ItemType Directory -Force .claude | Out-Null
```
```powershell
Copy-Item outlook\claude-settings.vorlage.json .claude\settings.json
```

## Schritt 5 – Loslegen

```powershell
claude
```
Beim ersten Start mit deinem Claude-Konto anmelden. Dann einfach auf Deutsch schreiben, z. B.:

- „Zeig mir die ungelesenen Mails der letzten 3 Tage und sag mir, wo ich antworten muss.“
- „Beantworte die Mail von Frau Pölzl: passt so, danke.“
- „Leite die letzte Rechnung von Elektro Fink an gab@gcdrachenwand.at weiter.“
- „Verschieb alle Newsletter von heute in den Papierkorb.“
- „Lern meinen Stil noch genauer aus den letzten 300 gesendeten Mails.“
  (nutzt `export-sent` und ergänzt `docs/email-schreibstil.md`)

Antworten landen zuerst als **Entwurf** in Outlook (Ordner „Entwürfe“). Du kannst sie dort
auch selbst noch ändern und abschicken – oder Claude sagen „passt, senden“.

---

## Probleme?

| Meldung | Lösung |
|---|---|
| `pywin32 fehlt` | `python -m pip install pywin32` |
| `Outlook konnte nicht ... verbunden werden` | Outlook einmal normal öffnen; PowerShell und Outlook **beide ohne** „Als Administrator ausführen“ starten (oder beide mit). |
| Outlook fragt „Ein Programm versucht, auf E-Mail-Adressen zuzugreifen“ | Virenschutz aktuell halten. Sonst: Outlook → Datei → Optionen → Trust Center → Einstellungen für das Trust Center → Programmgesteuerter Zugriff. Steht dort „Antivirenstatus: ungültig“, als Administrator gestartet auf „Nie warnen“ stellen (nur wenn du weißt, was du tust). |
| `Konto nicht gefunden` | `python outlook/outlook_tool.py accounts` zeigt die genauen Namen. |
| `Ordner nicht gefunden` | `python outlook/outlook_tool.py folders` zeigt den Ordnerbaum (deutsche Namen, z. B. „Posteingang/Projekte“). |
| Umlaute kaputt | Texte als Datei übergeben (`--body-file`), Claude macht das automatisch. |

## Was das Werkzeug kann

`python outlook/outlook_tool.py --help` – Übersicht. Kurz:
`accounts`, `folders`, `list`, `search`, `read`, `reply`, `forward`, `new`, `edit-draft`,
`send-draft`, `delete`, `move`, `mark`, `attachments`, `export-sent`.

Es läuft komplett lokal auf deinem PC über die Outlook-eigene Schnittstelle (COM).
Es werden keine Zugangsdaten gespeichert und nichts an fremde Server geschickt –
außer dem, was Claude zum Lesen/Formulieren an deinen Claude-Account übermittelt.
