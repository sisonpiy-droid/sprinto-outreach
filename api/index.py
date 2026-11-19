"""Offline-only web view of the pipeline. Forces OFFLINE=1: no network, no keys, no real email."""
import json, os, sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

os.environ["OFFLINE"] = "1"
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import tempfile; os.chdir(tempfile.gettempdir())  # send.py writes outbox/ relative to cwd; only /tmp is writable on Vercel

import contacts, drafts, extract, qualify, scrape, send, impact  # noqa: E402


def run_all():
    rows = []
    for d in (ROOT / "data/domains.txt").read_text().split():
        text = scrape.fetch(d)
        company = extract.extract(d, text) if text else {}
        q = qualify.qualify(d, company) if company else {"score": 0, "qualified": False, "reason": "no data"}
        row = {"domain": d, "score": q["score"], "qualified": q["qualified"], "reason": q["reason"]}
        if q["qualified"]:
            c = contacts.find_contact(d, str(ROOT / "data/contacts.csv"))
            if c:
                mail = drafts.draft(d, company, c)
                row.update(contact=f'{c["name"]} ({c["title"]})', subject=mail["subject"], body=mail["body"],
                           send=send.send(d, mail["subject"], mail["body"]))
        rows.append(row)
    return rows


def page():
    esc = lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;")
    cards = "".join(
        f'<section class="{"ok" if r["qualified"] else "no"}"><h2>{esc(r["domain"])} '
        f'<small>score {esc(r["score"])} · {"qualified" if r["qualified"] else "skipped"}</small></h2>'
        f'<p>{esc(r["reason"])}</p>'
        + (f'<p><b>To:</b> {esc(r["contact"])}<br><b>Subject:</b> {esc(r["subject"])}</p><pre>{esc(r["body"])}</pre>'
           if "body" in r else "") + "</section>"
        for r in run_all())
    s = impact.monthly_summary()
    return f"""<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Sprinto outreach</title><style>
body{{font:16px/1.5 system-ui;max-width:760px;margin:0 auto;padding:24px 16px;background:#fafafa;color:#111}}
section{{background:#fff;border:1px solid #ddd;border-left:4px solid #bbb;border-radius:8px;padding:4px 16px;margin:12px 0}}
section.ok{{border-left-color:#16a34a}}small{{color:#666;font-weight:400;font-size:.7em}}
pre{{white-space:pre-wrap;background:#f3f3f3;padding:12px;border-radius:6px}}</style>
<h1>Sprinto outreach pipeline</h1>
<p>Offline demo on fictional companies and canned model replies. Nothing is sent.
Estimated {s["hours_saved_per_month"]} hours saved a month, net ₹{s["net_value_per_month_inr"]:,}.</p>{cards}"""


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            body, code = page().encode(), 200
        except Exception as e:  # show the failure instead of a blank 500
            body, code = f"error: {e}".encode(), 500
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)
