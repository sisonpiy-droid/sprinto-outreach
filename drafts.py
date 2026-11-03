import llm

PROMPT = """Write a short cold email from Sprinto to {name} ({title}) at {company}.
Name two likely pain points and use one specific hook from: {signals}.
Return JSON: pain_points (list of 2), subject, body."""


def draft(domain, company, contact):
    p = PROMPT.format(
        name=contact["name"], title=contact["title"],
        company=company["company"], signals=company["compliance_signals"],
    )
    return llm.ask("draft", domain, p)
