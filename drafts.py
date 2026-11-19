"""Steps 5 and 6: two likely pain points for this person, then a personalised email."""
import config
import llm

PAIN_PROMPT = """{name} is {title} at {company} ({product}). Facts we know: {facts}
Name the two most likely pain points for someone in this role right now. Each must be backed by a
fact above. Return JSON: pain_points (list of exactly 2 objects with keys pain, evidence)."""

DRAFT_PROMPT = """Write a cold email from {sender} at Sprinto to {name}, {title} at {company}.
Address them by first name. Open with this specific hook, in your own words: {hook}
Speak to these pain points: {pains}
Under 90 words, one soft ask for a short call, no hype, no claims we cannot back.
Return JSON: subject, body."""


def pain_points(domain, facts, contact):
    p = PAIN_PROMPT.format(name=contact["name"], title=contact["title"], company=domain,
                           product=facts.get("product"), facts=facts)
    return llm.ask("pain_points", domain, p)["pain_points"]


def draft(domain, facts, contact, pains, hook):
    p = DRAFT_PROMPT.format(sender=config.SENDER_NAME, name=contact["name"], title=contact["title"],
                            company=domain, hook=hook, pains=[x["pain"] for x in pains])
    return llm.ask("draft", domain, p)
