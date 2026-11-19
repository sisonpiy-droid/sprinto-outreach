import llm

FIELDS = ("product", "buyer", "is_saas", "certifications", "funding_stage",
          "headcount", "open_roles", "enterprise_tier", "compliance_signals")

PROMPT = """Extract facts from this company web page as JSON with exactly these keys:
product (one line), buyer (who buys it, e.g. "logistics teams"), is_saas (bool: a software
product sold on subscription to businesses), certifications (security certifications the
company says it HOLDS, e.g. "SOC 2 Type II"; not ones it is working toward), funding_stage,
headcount (int), open_roles (int, number of open jobs listed), enterprise_tier (bool: pricing
page has an enterprise plan), compliance_signals (list of short quotes showing audit
preparation or customers demanding certification).
Use null (or [] for lists) when the page does not say. Do not infer.

PAGE:
{text}"""


def extract(domain, page, text):
    raw = llm.ask("extract", domain, PROMPT.format(text=text), key=page)
    return {k: raw.get(k) for k in FIELDS}
