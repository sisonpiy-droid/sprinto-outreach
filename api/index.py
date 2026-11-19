"""Offline-only web view of the pipeline. Forces OFFLINE=1: no network, no keys, no real email."""
import os
import sys
import tempfile
from html import escape as esc
from http.server import BaseHTTPRequestHandler
from pathlib import Path

os.environ["OFFLINE"] = "1"
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(tempfile.gettempdir())  # send.py writes outbox/ relative to cwd; only the temp dir is writable on Vercel

import impact  # noqa: E402
import run  # noqa: E402

LABEL = {"drafted": "email drafted", "not_qualified": "not qualified", "disqualified": "disqualified",
         "manual_review": "needs a human", "failed": "needs a human", "no_contact": "needs a human",
         "no_hook": "needs a human"}


def card(r):
    out = [f'<section class="{r["status"]}"><h2>{esc(r["domain"])} <small>{LABEL.get(r["status"], r["status"])}'
           f'{"" if r.get("score") is None else f" · fit {r["score"]}"}</small></h2><p>{esc(r["reason"])}</p>']
    if r.get("evidence"):
        out.append("<h3>Evidence</h3><ul>" + "".join(
            f'<li><b>{esc(e["question"])}</b> {"answered" if e["answered"] else "unanswered: " + esc(e["if_unanswered"])}'
            f' <small>{esc(", ".join(e["fetched"]) or "homepage was enough")}</small></li>' for e in r["evidence"]) + "</ul>")
    if r.get("contact"):
        c = r["contact"]
        out.append(f'<h3>Contact</h3><p>{esc(c["name"])}, {esc(c["title"])}<br><small>{esc(c["why"])}</small></p>')
        out.append("<h3>Pain points</h3><ul>" + "".join(
            f'<li>{esc(p["pain"])} <small>{esc(p["evidence"])}</small></li>' for p in r["pain_points"]) + "</ul>")
        out.append(f'<h3>Email</h3><p><b>Hook:</b> {esc(r["hook"])}<br><b>Subject:</b> {esc(r["subject"])}</p>'
                   f'<pre>{esc(r["body"])}</pre>')
    for f in r.get("flags", []):
        out.append(f"<p><small>flag: {esc(f)}</small></p>")
    return "".join(out) + "</section>"


def page():
    contacts = str(ROOT / "data/contacts.csv")
    rows = [run.process(d, contacts) for d in (ROOT / "data/domains.txt").read_text().split()]
    st, im = impact.run_stats(rows), impact.monthly_summary()
    return f"""<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Sprinto outreach</title><style>
body{{font:16px/1.5 system-ui;max-width:760px;margin:0 auto;padding:24px 16px;background:#fafafa;color:#111}}
section{{background:#fff;border:1px solid #ddd;border-left:4px solid #bbb;border-radius:8px;padding:4px 16px;margin:12px 0}}
section.drafted{{border-left-color:#16a34a}}section.manual_review,section.failed,section.no_contact,section.no_hook{{border-left-color:#d97706}}
small{{color:#666;font-weight:400}}h2 small{{font-size:.65em}}h3{{font-size:.85em;text-transform:uppercase;color:#555;margin:14px 0 4px}}
pre{{white-space:pre-wrap;background:#f3f3f3;padding:12px;border-radius:6px}}ul{{padding-left:20px}}</style>
<h1>Sprinto outreach pipeline</h1>
<p>Offline demo on fictional companies and canned model replies. Nothing is sent.
{st["companies"]} companies: {esc(str(st["by_status"]))}; {st["needs_human"]} for a human.
Average {st["avg_fetches_beyond_homepage"]} page fetches beyond the homepage (cap 4).
Estimated {im["hours_saved_per_month"]} hours saved a month, net ₹{im["net_value_per_month_inr"]:,}.</p>{"".join(card(r) for r in rows)}"""


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
