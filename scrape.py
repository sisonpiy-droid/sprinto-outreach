import re
import time
from html.parser import HTMLParser
from pathlib import Path

import requests

import config

PAGES = Path(__file__).parent / "fixtures" / "pages"
_cache = {}  # one fetch per (domain, page) per process
SKIP = {"script", "style", "noscript", "nav", "svg", "form"}
BREAKS = {"br", "p", "div", "li", "h1", "h2", "h3", "tr", "section", "footer"}
# short lines are usually nav/buttons, but these short lines are signal
KEEP = re.compile(r"soc ?2|iso ?27001|gdpr|hipaa|series [a-e]\b|seed|certified", re.I)


def fetch(domain, path="home"):
    """Return (text, note). text is "" when nothing usable came back; note says why."""
    key = (domain, path)
    if key not in _cache:
        _cache[key] = _fetch(domain, path)
    return _cache[key]


def _fetch(domain, path):
    if config.OFFLINE:
        f = PAGES / f"{domain}_{path}.txt"
        return (f.read_text(encoding="utf-8"), "") if f.exists() else ("", "page not found")
    base = f"https://{domain}"
    url = base + ("/" if path == "home" else f"/{path}")
    if not _allowed(base, url):
        return "", "blocked by robots.txt"
    time.sleep(config.FETCH_DELAY)
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": config.USER_AGENT})
    except requests.RequestException as e:
        return "", f"request failed: {type(e).__name__}"
    if r.status_code in (401, 403, 429, 503):
        return "", f"blocked or login wall (http {r.status_code})"
    if r.status_code >= 400:
        return "", f"http {r.status_code}"
    text = clean(r.text)
    note = "thin page: may be JavaScript-rendered" if len(text.split()) < config.THIN_WORDS else ""
    return text, note


def _allowed(base, url):
    from urllib.robotparser import RobotFileParser
    try:
        r = requests.get(base + "/robots.txt", timeout=5, headers={"User-Agent": config.USER_AGENT})
        if r.status_code != 200:
            return True  # no robots.txt = nothing forbidden
        rp = RobotFileParser()
        rp.parse(r.text.splitlines())
        return rp.can_fetch(config.USER_AGENT, url)
    except requests.RequestException:
        return True


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip, self.out = 0, []

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
        if tag in BREAKS:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in SKIP and self.skip:
            self.skip -= 1
        if tag in BREAKS:
            self.out.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def clean(html):
    """HTML -> short plain text: drop scripts/nav/forms, short UI lines and duplicates."""
    p = _Text()
    p.feed(html)
    seen, out = set(), []
    for line in "".join(p.out).splitlines():
        line = " ".join(line.split())
        if (len(line.split()) >= 6 or KEEP.search(line)) and line not in seen:
            seen.add(line)
            out.append(line)
    return "\n".join(out)[:4000]
