# Einrichtung Outlook-Steuerung fuer Claude Code (Windows, Outlook 2016)
# Ausfuehren im Repo-Ordner:
#   powershell -ExecutionPolicy Bypass -File outlook\setup.ps1

$ErrorActionPreference = "Stop"
function Ok($m)   { Write-Host "[OK]   $m" -ForegroundColor Green }
function Warn($m) { Write-Host "[!]    $m" -ForegroundColor Yellow }
function Fail($m) { Write-Host "[FEHLER] $m" -ForegroundColor Red }

Write-Host "`n=== Outlook-Steuerung fuer Claude Code einrichten ===`n"

# 1) Python
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py -or ($py.Source -like "*WindowsApps*")) {
    Fail "Python nicht gefunden."
    Write-Host "  -> Installieren:  winget install -e --id Python.Python.3.12"
    Write-Host "     (oder https://www.python.org/downloads/ - Haken bei 'Add python.exe to PATH' setzen)"
    Write-Host "  -> Danach PowerShell neu oeffnen und dieses Skript erneut starten."
    exit 1
}
Ok ("Python: " + (& python --version))

# 2) pywin32
Write-Host "Installiere/aktualisiere pywin32 ..."
& python -m pip install --upgrade --quiet pywin32
if ($LASTEXITCODE -ne 0) { Fail "pywin32 konnte nicht installiert werden."; exit 1 }
Ok "pywin32 installiert"

# 3) Outlook vorhanden?
$olPath = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\OUTLOOK.EXE" -ErrorAction SilentlyContinue
if ($olPath) { Ok "Outlook gefunden: $($olPath.'(default)')" } else { Warn "Outlook-Pfad nicht in der Registry gefunden - Test unten zeigt, ob es trotzdem klappt." }

# 4) Verbindungstest
Write-Host "`nTeste Verbindung zu Outlook (Outlook darf offen sein) ..."
$tool = Join-Path $PSScriptRoot "outlook_tool.py"
& python $tool accounts
if ($LASTEXITCODE -ne 0) {
    Fail "Verbindung zu Outlook fehlgeschlagen. Siehe Abschnitt 'Probleme' in outlook\ANLEITUNG.md"
    exit 1
}
Ok "Outlook-Verbindung funktioniert"

& python $tool list --limit 3 | Out-Host

# 5) Claude Code
$claude = Get-Command claude -ErrorAction SilentlyContinue
if ($claude) {
    Ok "Claude Code gefunden"
} else {
    Warn "Claude Code ist noch nicht installiert."
    Write-Host "  -> Git fuer Windows:  winget install -e --id Git.Git"
    Write-Host "  -> Claude Code:       irm https://claude.ai/install.ps1 | iex"
}

Write-Host "`nFertig. Starte Claude Code in diesem Ordner mit:  claude`n"
