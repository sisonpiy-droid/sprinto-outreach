from pathlib import Path
import requests
import config

PAGES = Path(__file__).parent / "fixtures" / "pages"


def fetch(domain, path="home"):
    """Return cleaned page text for a domain (home or about page)."""
    try:
        if config.OFFLINE:
            return (PAGES / f"{domain}_{path}.txt").read_text()
        url = f"https://{domain}/" + ("" if path == "home" else path)
        html = requests.get(url, timeout=10).text
        return clean(html)
    except:
        return ""


def clean(html):
    lines = [l.strip() for l in html.splitlines() if len(l.split()) >= 8]
    seen, out = set(), []
    for l in lines:
        if l not in seen:
            seen.add(l)
            out.append(l)
    return "\n".join(out)[:8000]
