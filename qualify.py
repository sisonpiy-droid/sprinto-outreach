import config
import llm
import scrape
import extract

PROMPT = """Sprinto sells compliance automation (SOC 2, ISO 27001, GDPR) to SaaS
companies at Series A-C that are preparing for an audit or pressed by enterprise
customers. Score this company's fit and say if more information is needed.
Return JSON: score (0-100), reason, needs_more (bool).

COMPANY: {company}"""


def qualify(domain, company):
    result = llm.ask("qualify", domain, PROMPT.format(company=company))
    rounds = 0
    while result["needs_more"] and rounds < config.MAX_ROUNDS:
        more = scrape.fetch(domain, "about")
        company = {**company, **extract.extract(domain, more)}
        result = llm.ask("qualify_more", domain, PROMPT.format(company=company))
        rounds += 1
    result["qualified"] = result["score"] >= config.QUALIFY_THRESHOLD
    return result
