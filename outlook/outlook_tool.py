#!/usr/bin/env python3
"""
outlook_tool.py – Outlook 2016 (Windows) per Kommandozeile steuern.

Gedacht fuer Claude Code auf dem Windows-PC: Mails lesen, suchen, beantworten,
weiterleiten, verschieben, loeschen und neue Mails anlegen. Alle Ausgaben sind
JSON (UTF-8), damit Claude sie zuverlaessig auswerten kann.

Sicherheitsprinzip: Antworten, Weiterleitungen und neue Mails werden standard-
maessig nur als ENTWURF gespeichert. Gesendet wird nur mit --send bzw. mit dem
Befehl send-draft.

Voraussetzungen: Windows, Outlook 2016 (installiert und eingerichtet),
Python 3.9+ und pywin32 (pip install pywin32).

Beispiele:
  python outlook/outlook_tool.py accounts
  python outlook/outlook_tool.py list --folder inbox --limit 20 --unread
  python outlook/outlook_tool.py search "Rechnung" --folder inbox --folder sent
  python outlook/outlook_tool.py read <ID>
  python outlook/outlook_tool.py reply <ID> --body-file antwort.txt          (Entwurf)
  python outlook/outlook_tool.py reply <ID> --all --body-file antwort.txt --send
  python outlook/outlook_tool.py forward <ID> --to a@b.at --body "Servus ..." (Entwurf)
  python outlook/outlook_tool.py new --to a@b.at --subject "..." --body-file t.txt
  python outlook/outlook_tool.py send-draft <ID>
  python outlook/outlook_tool.py delete <ID>
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# Outlook-Konstanten
# ---------------------------------------------------------------------------
OL_FOLDER = {
    "deleted": 3,
    "outbox": 4,
    "sent": 5,
    "inbox": 6,
    "drafts": 16,
    "junk": 23,
}
OL_MAIL_CLASS = 43          # olMail
OL_MAIL_ITEM = 0            # olMailItem (CreateItem)
OL_MARK_TODAY = 0           # olMarkToday
OL_CC = 2                   # olCC (Recipient.Type)
OL_BCC = 3                  # olBCC
PR_SMTP_ADDRESS = "http://schemas.microsoft.com/mapi/proptag/0x39FE001E"

ID_SEP = "."                # ID = EntryID + "." + StoreID (beides Hex)


class ToolError(Exception):
    pass


# ---------------------------------------------------------------------------
# Hilfsfunktionen (ohne COM, testbar)
# ---------------------------------------------------------------------------
def make_id(item) -> str:
    try:
        store_id = item.Parent.StoreID
    except Exception:
        store_id = ""
    return f"{item.EntryID}{ID_SEP}{store_id}" if store_id else item.EntryID


def split_id(composite: str) -> tuple[str, str | None]:
    composite = composite.strip()
    if ID_SEP in composite:
        entry, store = composite.split(ID_SEP, 1)
        return entry, (store or None)
    return composite, None


def text_to_html(text: str) -> str:
    """Klartext in schlichtes Outlook-HTML (Calibri 11pt) umwandeln."""
    paragraphs = re.split(r"\n\s*\n", text.strip("\n"))
    parts = []
    for p in paragraphs:
        lines = [html.escape(line) for line in p.split("\n")]
        parts.append("<p style=\"margin:0 0 11pt 0\">" + "<br>".join(lines) + "</p>")
    return (
        "<div style=\"font-family:Calibri,Arial,sans-serif;font-size:11pt\">"
        + "".join(parts)
        + "</div>"
    )


def insert_into_html(existing_html: str, snippet: str) -> str:
    """Snippet direkt nach dem <body>-Tag einfuegen (vor dem zitierten Verlauf)."""
    m = re.search(r"<body[^>]*>", existing_html or "", flags=re.IGNORECASE)
    if not m:
        return snippet + (existing_html or "")
    return existing_html[: m.end()] + snippet + existing_html[m.end():]


_QUOTE_MARKERS = [
    re.compile(r"^\s*-{2,}\s*(Original Message|Ursprüngliche Nachricht|Forwarded message|Weitergeleitete Nachricht)", re.I),
    re.compile(r"^\s*(Von|From)\s*:\s", re.I),
    re.compile(r"^\s*Am .{5,120}schrieb", re.I),
    re.compile(r"^\s*On .{5,120}wrote", re.I),
    re.compile(r"^\s*>"),
]


def strip_quoted(text: str) -> str:
    """Zitierten Verlauf (Von:/Am ... schrieb/> ...) abschneiden."""
    out = []
    for line in (text or "").replace("\r\n", "\n").split("\n"):
        if any(p.search(line) for p in _QUOTE_MARKERS):
            break
        out.append(line)
    return "\n".join(out).strip()


def fmt_time(value) -> str | None:
    if value is None:
        return None
    try:
        return value.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(value)


def to_naive(value):
    try:
        return dt.datetime(value.year, value.month, value.day, value.hour, value.minute, value.second)
    except Exception:
        return None


def read_body(args) -> str | None:
    if getattr(args, "body_file", None):
        if args.body_file == "-":
            return sys.stdin.read()
        with open(args.body_file, "r", encoding="utf-8-sig") as fh:
            return fh.read()
    return getattr(args, "body", None)


def split_addresses(value: str | None) -> list[str]:
    if not value:
        return []
    return [a.strip() for a in re.split(r"[;,]", value) if a.strip()]


def emit(data) -> None:
    sys.stdout.write(json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n")


# ---------------------------------------------------------------------------
# COM-Zugriff
# ---------------------------------------------------------------------------
class Outlook:
    def __init__(self):
        try:
            import win32com.client  # type: ignore
        except ImportError as exc:  # pragma: no cover - nur Windows
            raise ToolError(
                "pywin32 fehlt. Bitte installieren: python -m pip install pywin32"
            ) from exc
        try:
            self.app = win32com.client.Dispatch("Outlook.Application")
            self.ns = self.app.GetNamespace("MAPI")
        except Exception as exc:  # pragma: no cover
            raise ToolError(f"Outlook konnte nicht gestartet/verbunden werden: {exc}") from exc

    # --- Konten & Ordner -------------------------------------------------
    def accounts(self):
        result = []
        for acc in self.ns.Accounts:
            entry = {"name": acc.DisplayName, "smtp": getattr(acc, "SmtpAddress", "")}
            try:
                entry["store"] = acc.DeliveryStore.DisplayName
            except Exception:
                pass
            result.append(entry)
        return result

    def _find_account(self, name: str):
        name_l = name.lower()
        for acc in self.ns.Accounts:
            if name_l in (acc.DisplayName or "").lower() or name_l == (getattr(acc, "SmtpAddress", "") or "").lower():
                return acc
        raise ToolError(f"Konto nicht gefunden: {name}")

    def _store(self, account: str | None):
        if not account:
            return self.ns.DefaultStore
        acc = self._find_account(account)
        return acc.DeliveryStore

    def folder(self, spec: str = "inbox", account: str | None = None):
        store = self._store(account)
        key = spec.lower()
        if key in OL_FOLDER:
            return store.GetDefaultFolder(OL_FOLDER[key])
        # Pfad relativ zum Postfach-Stamm, z.B. "Posteingang/Projekte"
        node = store.GetRootFolder()
        for idx, part in enumerate([p for p in re.split(r"[\\/]", spec) if p]):
            alias = part.lower()
            if idx == 0 and alias in OL_FOLDER:
                node = store.GetDefaultFolder(OL_FOLDER[alias])
                continue
            match = None
            for f in node.Folders:
                if f.Name.lower() == alias:
                    match = f
                    break
            if match is None:
                raise ToolError(f"Ordner nicht gefunden: {spec} (Teil '{part}')")
            node = match
        return node

    def folder_tree(self, account: str | None, depth: int):
        def walk(f, level):
            entry = {"name": f.Name, "path": f.FolderPath, "count": f.Items.Count}
            try:
                entry["unread"] = f.UnReadItemCount
            except Exception:
                pass
            if level < depth:
                subs = [walk(s, level + 1) for s in f.Folders]
                if subs:
                    entry["folders"] = subs
            return entry

        stores = [self._store(account)] if account else list(self.ns.Stores)
        return [walk(s.GetRootFolder(), 0) for s in stores]

    # --- Elemente --------------------------------------------------------
    def item(self, composite_id: str):
        entry, store = split_id(composite_id)
        try:
            return self.ns.GetItemFromID(entry, store) if store else self.ns.GetItemFromID(entry)
        except Exception as exc:
            raise ToolError(f"Element nicht gefunden (ID ungueltig oder verschoben): {exc}") from exc

    @staticmethod
    def sender_address(item) -> str:
        try:
            if getattr(item, "SenderEmailType", "") == "EX":
                exu = item.Sender.GetExchangeUser()
                if exu is not None:
                    return exu.PrimarySmtpAddress
        except Exception:
            pass
        return getattr(item, "SenderEmailAddress", "") or ""

    @staticmethod
    def recipients(item):
        to, cc = [], []
        try:
            for r in item.Recipients:
                addr = r.Address
                try:
                    addr = r.PropertyAccessor.GetProperty(PR_SMTP_ADDRESS) or addr
                except Exception:
                    pass
                entry = f"{r.Name} <{addr}>" if addr and addr != r.Name else r.Name
                (cc if r.Type == OL_CC else to if r.Type != OL_BCC else []).append(entry)
        except Exception:
            pass
        return to, cc

    def summary(self, item, snippet_len: int = 160):
        is_mail = getattr(item, "Class", None) == OL_MAIL_CLASS
        data = {
            "id": make_id(item),
            "subject": getattr(item, "Subject", ""),
            "type": "mail" if is_mail else getattr(item, "MessageClass", "other"),
        }
        if is_mail:
            data.update(
                {
                    "from": f"{item.SenderName} <{self.sender_address(item)}>",
                    "received": fmt_time(getattr(item, "ReceivedTime", None)),
                    "unread": bool(item.UnRead),
                    "attachments": item.Attachments.Count,
                    "flagged": getattr(item, "IsMarkedAsTask", False),
                }
            )
            if snippet_len:
                body = (item.Body or "").replace("\r", " ").replace("\n", " ")
                data["snippet"] = re.sub(r"\s+", " ", body)[:snippet_len]
        return data

    def iter_items(self, folder, limit: int, unread: bool, since: dt.datetime | None, sort_field: str):
        items = folder.Items
        items.Sort(f"[{sort_field}]", True)
        if unread:
            items = items.Restrict("[UnRead] = True")
            items.Sort(f"[{sort_field}]", True)
        count = 0
        item = items.GetFirst()
        while item is not None and count < limit:
            if since is not None:
                stamp = to_naive(getattr(item, sort_field, None))
                if stamp is not None and stamp < since:
                    break
            yield item
            count += 1
            item = items.GetNext()


# ---------------------------------------------------------------------------
# Befehle
# ---------------------------------------------------------------------------
def parse_since(value: str | None):
    if not value:
        return None
    m = re.fullmatch(r"(\d+)d", value)
    if m:
        return dt.datetime.now() - dt.timedelta(days=int(m.group(1)))
    for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return dt.datetime.strptime(value, fmt)
        except ValueError:
            pass
    raise ToolError("--since erwartet z.B. 7d, 2026-11-01 oder 01.11.2026")


def sort_field_for(folder_spec: str) -> str:
    return "SentOn" if folder_spec.lower() in ("sent", "drafts", "outbox") else "ReceivedTime"


def cmd_accounts(ol, args):
    emit(ol.accounts())


def cmd_folders(ol, args):
    emit(ol.folder_tree(args.account, args.depth))


def cmd_list(ol, args):
    folder = ol.folder(args.folder, args.account)
    since = parse_since(args.since)
    field = sort_field_for(args.folder)
    emit(
        {
            "folder": folder.FolderPath,
            "items": [ol.summary(i) for i in ol.iter_items(folder, args.limit, args.unread, since, field)],
        }
    )


def _dasl_escape(term: str) -> str:
    return term.replace("'", "''").replace("%", "[%]")


def cmd_search(ol, args):
    term = _dasl_escape(args.query)
    fields = [
        "urn:schemas:httpmail:subject",
        "urn:schemas:httpmail:fromname",
        "urn:schemas:httpmail:fromemail",
        "urn:schemas:httpmail:displayto",
    ]
    if not args.subject_only:
        fields.append("urn:schemas:httpmail:textdescription")
    flt = "@SQL=" + " OR ".join(f"\"{f}\" LIKE '%{term}%'" for f in fields)
    since = parse_since(args.since)
    results = []
    for spec in args.folder or ["inbox"]:
        folder = ol.folder(spec, args.account)
        items = folder.Items.Restrict(flt)
        field = sort_field_for(spec)
        items.Sort(f"[{field}]", True)
        item = items.GetFirst()
        n = 0
        while item is not None and n < args.limit:
            if since is not None:
                stamp = to_naive(getattr(item, field, None))
                if stamp is not None and stamp < since:
                    break
            entry = ol.summary(item)
            entry["folder"] = folder.Name
            results.append(entry)
            n += 1
            item = items.GetNext()
    emit({"query": args.query, "items": results})


def cmd_read(ol, args):
    item = ol.item(args.id)
    data = ol.summary(item, snippet_len=0)
    to, cc = ol.recipients(item)
    body = item.Body or ""
    if args.no_quotes:
        body = strip_quoted(body)
    truncated = len(body) > args.max_chars
    data.update(
        {
            "to": to,
            "cc": cc,
            "folder": item.Parent.Name,
            "body": body[: args.max_chars],
            "body_truncated": truncated,
            "attachment_names": [a.FileName for a in item.Attachments],
        }
    )
    if args.mark_read and getattr(item, "UnRead", False):
        item.UnRead = False
        item.Save()
    emit(data)


def _finish(mail, send: bool, action: str):
    if send:
        subject = mail.Subject
        mail.Send()
        emit({"status": "gesendet", "action": action, "subject": subject})
    else:
        mail.Save()
        emit({"status": "entwurf_gespeichert", "action": action, "id": make_id(mail), "subject": mail.Subject,
              "hinweis": "Liegt im Ordner Entwuerfe. Senden mit: send-draft <id>"})


def _add_recipients(mail, to=None, cc=None, bcc=None):
    for addr in split_addresses(to):
        mail.Recipients.Add(addr)
    for addr in split_addresses(cc):
        mail.Recipients.Add(addr).Type = OL_CC
    for addr in split_addresses(bcc):
        mail.Recipients.Add(addr).Type = OL_BCC
    if to or cc or bcc:
        if not mail.Recipients.ResolveAll():
            bad = [r.Name for r in mail.Recipients if not r.Resolved]
            raise ToolError(f"Empfaenger nicht aufloesbar: {bad}")


def _attach(mail, paths):
    for p in paths or []:
        full = os.path.abspath(p)
        if not os.path.isfile(full):
            raise ToolError(f"Anhang nicht gefunden: {full}")
        mail.Attachments.Add(full)


def cmd_reply(ol, args):
    body = read_body(args)
    if not body:
        raise ToolError("Antworttext fehlt (--body oder --body-file)")
    item = ol.item(args.id)
    mail = item.ReplyAll() if args.all else item.Reply()
    mail.HTMLBody = insert_into_html(mail.HTMLBody, text_to_html(body))
    _add_recipients(mail, cc=args.cc)
    _attach(mail, args.attach)
    _finish(mail, args.send, "reply_all" if args.all else "reply")


def cmd_forward(ol, args):
    item = ol.item(args.id)
    mail = item.Forward()
    body = read_body(args)
    if body:
        mail.HTMLBody = insert_into_html(mail.HTMLBody, text_to_html(body))
    _add_recipients(mail, to=args.to, cc=args.cc, bcc=args.bcc)
    _attach(mail, args.attach)
    _finish(mail, args.send, "forward")


def _set_account(ol, mail, account_name):
    acc = ol._find_account(account_name)
    try:
        mail.SendUsingAccount = acc
    except Exception:
        # Bekannter pywin32-Workaround (DISPID 64209 = SendUsingAccount)
        mail._oleobj_.Invoke(*(64209, 0, 8, 0, acc))


def cmd_new(ol, args):
    body = read_body(args) or ""
    mail = ol.app.CreateItem(OL_MAIL_ITEM)
    if args.account:
        _set_account(ol, mail, args.account)
    mail.Subject = args.subject
    mail.HTMLBody = text_to_html(body)
    _add_recipients(mail, to=args.to, cc=args.cc, bcc=args.bcc)
    _attach(mail, args.attach)
    _finish(mail, args.send, "new")


def cmd_send_draft(ol, args):
    item = ol.item(args.id)
    if getattr(item, "Sent", False):
        raise ToolError("Dieses Element wurde bereits gesendet.")
    subject = item.Subject
    item.Send()
    emit({"status": "gesendet", "subject": subject})


def cmd_edit_draft(ol, args):
    item = ol.item(args.id)
    if getattr(item, "Sent", False):
        raise ToolError("Gesendete Mails koennen nicht bearbeitet werden.")
    if args.subject:
        item.Subject = args.subject
    body = read_body(args)
    if body:
        if args.replace_body:
            item.HTMLBody = text_to_html(body)
        else:
            # vorherigen eigenen Text ersetzen ist fehleranfaellig – neuen Text vorne einfuegen
            item.HTMLBody = insert_into_html(item.HTMLBody, text_to_html(body))
    _add_recipients(item, to=args.to, cc=args.cc, bcc=args.bcc)
    _attach(item, args.attach)
    item.Save()
    emit({"status": "entwurf_aktualisiert", "id": make_id(item), "subject": item.Subject})


def cmd_delete(ol, args):
    item = ol.item(args.id)
    subject = item.Subject
    item.Delete()  # verschiebt in "Geloeschte Elemente" (endgueltig nur, wenn schon dort)
    emit({"status": "geloescht", "subject": subject, "hinweis": "In 'Geloeschte Elemente' verschoben"})


def cmd_move(ol, args):
    item = ol.item(args.id)
    target = ol.folder(args.folder, args.account)
    moved = item.Move(target)
    emit({"status": "verschoben", "subject": moved.Subject, "folder": target.FolderPath, "id": make_id(moved)})


def cmd_mark(ol, args):
    item = ol.item(args.id)
    if args.read:
        item.UnRead = False
    if args.unread:
        item.UnRead = True
    if args.flag:
        item.MarkAsTask(OL_MARK_TODAY)
    if args.unflag:
        item.ClearTaskFlag()
    item.Save()
    emit({"status": "ok", "subject": item.Subject, "unread": bool(item.UnRead)})


def cmd_attachments(ol, args):
    item = ol.item(args.id)
    os.makedirs(args.dir, exist_ok=True)
    saved = []
    for att in item.Attachments:
        name = re.sub(r'[<>:"/\\|?*]', "_", att.FileName)
        path = os.path.join(os.path.abspath(args.dir), name)
        att.SaveAsFile(path)
        saved.append(path)
    emit({"saved": saved})


def cmd_export_sent(ol, args):
    """Gesendete Mails (ohne zitierten Verlauf) exportieren – fuer die Stil-Analyse."""
    folder = ol.folder("sent", args.account)
    rows = []
    for item in ol.iter_items(folder, args.limit, False, parse_since(args.since), "SentOn"):
        if getattr(item, "Class", None) != OL_MAIL_CLASS:
            continue
        to, cc = ol.recipients(item)
        rows.append(
            {
                "date": fmt_time(item.SentOn),
                "to": to,
                "subject": item.Subject,
                "body": strip_quoted(item.Body or "")[:4000],
            }
        )
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=2)
    emit({"exported": len(rows), "file": os.path.abspath(args.out)})


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_parser():
    p = argparse.ArgumentParser(description="Outlook 2016 per Kommandozeile steuern (JSON-Ausgabe).")
    sub = p.add_subparsers(dest="cmd", required=True)

    def body_opts(sp):
        sp.add_argument("--body", help="Text (Klartext, Absaetze mit Leerzeile)")
        sp.add_argument("--body-file", help="Text aus UTF-8-Datei lesen ('-' = stdin)")

    def account_opt(sp):
        sp.add_argument("--account", help="Konto (Anzeigename oder E-Mail-Adresse); Standard: Hauptpostfach")

    sp = sub.add_parser("accounts", help="Eingerichtete Konten anzeigen")
    sp.set_defaults(func=cmd_accounts)

    sp = sub.add_parser("folders", help="Ordnerbaum anzeigen")
    account_opt(sp)
    sp.add_argument("--depth", type=int, default=2)
    sp.set_defaults(func=cmd_folders)

    sp = sub.add_parser("list", help="Mails eines Ordners auflisten (neueste zuerst)")
    sp.add_argument("--folder", default="inbox", help="inbox|sent|drafts|deleted|junk|outbox oder Pfad 'Posteingang/Projekt'")
    account_opt(sp)
    sp.add_argument("--limit", type=int, default=20)
    sp.add_argument("--unread", action="store_true")
    sp.add_argument("--since", help="z.B. 7d, 2026-11-01, 01.11.2026")
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("search", help="Suche in Betreff/Absender/Empfaenger/Text")
    sp.add_argument("query")
    sp.add_argument("--folder", action="append", help="mehrfach moeglich; Standard inbox")
    account_opt(sp)
    sp.add_argument("--limit", type=int, default=25)
    sp.add_argument("--since")
    sp.add_argument("--subject-only", action="store_true", help="Nur Betreff/Absender/Empfaenger (schneller)")
    sp.set_defaults(func=cmd_search)

    sp = sub.add_parser("read", help="Mail vollstaendig lesen")
    sp.add_argument("id")
    sp.add_argument("--max-chars", type=int, default=20000)
    sp.add_argument("--no-quotes", action="store_true", help="Zitierten Verlauf abschneiden")
    sp.add_argument("--mark-read", action="store_true")
    sp.set_defaults(func=cmd_read)

    sp = sub.add_parser("reply", help="Antworten (Standard: Entwurf)")
    sp.add_argument("id")
    sp.add_argument("--all", action="store_true", help="Allen antworten")
    body_opts(sp)
    sp.add_argument("--cc")
    sp.add_argument("--attach", action="append")
    sp.add_argument("--send", action="store_true", help="Sofort senden statt Entwurf")
    sp.set_defaults(func=cmd_reply)

    sp = sub.add_parser("forward", help="Weiterleiten (Standard: Entwurf)")
    sp.add_argument("id")
    sp.add_argument("--to", required=True, help="Empfaenger, mehrere mit ; trennen")
    sp.add_argument("--cc")
    sp.add_argument("--bcc")
    body_opts(sp)
    sp.add_argument("--attach", action="append")
    sp.add_argument("--send", action="store_true")
    sp.set_defaults(func=cmd_forward)

    sp = sub.add_parser("new", help="Neue Mail (Standard: Entwurf)")
    sp.add_argument("--to", required=True)
    sp.add_argument("--cc")
    sp.add_argument("--bcc")
    sp.add_argument("--subject", required=True)
    body_opts(sp)
    account_opt(sp)
    sp.add_argument("--attach", action="append")
    sp.add_argument("--send", action="store_true")
    sp.set_defaults(func=cmd_new)

    sp = sub.add_parser("edit-draft", help="Entwurf ergaenzen/aendern")
    sp.add_argument("id")
    sp.add_argument("--subject")
    body_opts(sp)
    sp.add_argument("--replace-body", action="store_true", help="Gesamten Text ersetzen (Verlauf geht verloren)")
    sp.add_argument("--to")
    sp.add_argument("--cc")
    sp.add_argument("--bcc")
    sp.add_argument("--attach", action="append")
    sp.set_defaults(func=cmd_edit_draft)

    sp = sub.add_parser("send-draft", help="Gespeicherten Entwurf senden")
    sp.add_argument("id")
    sp.set_defaults(func=cmd_send_draft)

    sp = sub.add_parser("delete", help="In 'Geloeschte Elemente' verschieben")
    sp.add_argument("id")
    sp.set_defaults(func=cmd_delete)

    sp = sub.add_parser("move", help="In anderen Ordner verschieben")
    sp.add_argument("id")
    sp.add_argument("--folder", required=True)
    account_opt(sp)
    sp.set_defaults(func=cmd_move)

    sp = sub.add_parser("mark", help="Gelesen/ungelesen/Kennzeichnung setzen")
    sp.add_argument("id")
    g = sp.add_mutually_exclusive_group()
    g.add_argument("--read", action="store_true")
    g.add_argument("--unread", action="store_true")
    g2 = sp.add_mutually_exclusive_group()
    g2.add_argument("--flag", action="store_true")
    g2.add_argument("--unflag", action="store_true")
    sp.set_defaults(func=cmd_mark)

    sp = sub.add_parser("attachments", help="Anhaenge speichern")
    sp.add_argument("id")
    sp.add_argument("--dir", default="anhaenge")
    sp.set_defaults(func=cmd_attachments)

    sp = sub.add_parser("export-sent", help="Gesendete Mails fuer Stil-Analyse exportieren")
    account_opt(sp)
    sp.add_argument("--limit", type=int, default=200)
    sp.add_argument("--since")
    sp.add_argument("--out", default="gesendet_export.json")
    sp.set_defaults(func=cmd_export_sent)

    return p


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass
    args = build_parser().parse_args(argv)
    try:
        ol = Outlook()
        args.func(ol, args)
        return 0
    except ToolError as exc:
        emit({"error": str(exc)})
        return 1
    except Exception as exc:  # COM-Fehler usw.
        emit({"error": f"{type(exc).__name__}: {exc}"})
        return 2


if __name__ == "__main__":
    sys.exit(main())
