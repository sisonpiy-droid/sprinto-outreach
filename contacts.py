"""Step 4: find the right point of contact.

Option A: Hunter.io Domain Search (live, needs HUNTER_API_KEY). Option B: data/contacts.csv
(look people up in Apollo by hand). Either way the pick is ranked by who owns security work,
not by "the nearest person with manager in their title".
"""
import csv
import re

import requests

import config

TIERS = [
    (re.compile(r"ciso|security|compliance|trust|grc", re.I), 100, "owns security and compliance"),
    (re.compile(r"\b(cto|chief technology)\b|(vp|vice president|head|director)\b.*\beng", re.I), 80,
     "engineering leader who signs off security work"),
    (re.compile(r"founder|\bceo\b|chief executive", re.I), 60, "founder-led company, decides directly"),
]


def _rank(title, headcount):
    for pat, score, why in TIERS:
        if pat.search(title):
            if score == 60 and headcount and headcount < 50:
                return 90, why + " (company under 50 people)"
            return score, why
    return 0, "no ownership of security or engineering"


def _csv(domain, path):
    with open(path, newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r["domain"] == domain]


def _hunter(domain):
    try:
        r = requests.get("https://api.hunter.io/v2/domain-search", timeout=10,
                         params={"domain": domain, "limit": 10, "api_key": config.HUNTER_API_KEY})
        r.raise_for_status()
    except requests.RequestException:
        return []
    return [{"name": f"{e['first_name']} {e.get('last_name') or ''}".strip(), "title": e.get("position") or "",
             "email": e["value"]}
            for e in r.json()["data"]["emails"] if e.get("first_name") and (e.get("confidence") or 0) >= 50]


def find_contact(domain, headcount=None, path="data/contacts.csv"):
    """Return (contact, why). contact is None when nobody on the list owns the problem."""
    people = _hunter(domain) if (config.HUNTER_API_KEY and not config.OFFLINE) else _csv(domain, path)
    ranked = sorted(((*_rank(p["title"], headcount), p) for p in people), key=lambda x: -x[0])
    if not ranked or ranked[0][0] == 0:
        return None, f"{len(people)} candidates, none owns security or engineering"
    score, why, best = ranked[0]
    others = ", ".join(f"{p['name']} ({p['title']})" for s, _, p in ranked[1:])
    return best, f"{best['title']}: {why}" + (f". Passed over: {others}" if others else "")
