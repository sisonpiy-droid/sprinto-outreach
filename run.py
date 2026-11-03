import argparse
import json
import time
from pathlib import Path

import contacts
import drafts
import extract
import qualify
import scrape
import send
import impact

def run(domains, contacts_path):
    rows = []
    for d in domains:
        t0 = time.time()
        text = scrape.fetch(d)
        company = extract.extract(d, text) if text else {}
        q = qualify.qualify(d, company) if company else {"score": 0, "qualified": False, "reason": "no data"}
        row = {"domain": d, "score": q["score"], "qualified": q["qualified"], "reason": q["reason"]}
        if q["qualified"]:
            contact = contacts.find_contact(d, contacts_path)
            if contact:
                mail = drafts.draft(d, company, contact)
                row["contact"] = contact["name"]
                row["subject"] = mail["subject"]
                row["send"] = send.send(d, mail["subject"], mail["body"])
        row["seconds"] = round(time.time() - t0, 2)
        rows.append(row)
        print(f"{d:22} score={q['score']:<4} qualified={q['qualified']!s:5} {row.get('contact', '-')}")
    Path("runs").mkdir(exist_ok=True)
    with open("runs/run_log.jsonl", "a") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(impact.monthly_summary())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--domains", default="data/domains.txt")
    ap.add_argument("--contacts", default="data/contacts.csv")
    a = ap.parse_args()
    run(Path(a.domains).read_text().split(), a.contacts)
