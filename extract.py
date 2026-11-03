import llm

PROMPT = """From this company page extract JSON with keys:
company, product, is_saas (bool), stage, employees (int), compliance_signals (list).
Use null when the page does not say.

PAGE:
{text}"""


def extract(domain, text):
    return llm.ask("extract", domain, PROMPT.format(text=text))
