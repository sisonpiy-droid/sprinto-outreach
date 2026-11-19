"""Step 3: qualify against Sprinto's ICP with an agent loop driven by the Evidence Map.

The model extracts facts into named fields; this code decides whether the evidence is
enough, which page to fetch next, when to stop, and when to hand over to a human.
"""
import json

import config
import extract
import llm
import scrape

PROMPT = """Sprinto sells compliance automation (SOC 2, ISO 27001, GDPR) to B2B SaaS companies at
Series A-C that are preparing for an audit or are pressed by enterprise customers to get
certified. Score this company's ICP fit from 0 to 100 and explain in one sentence that cites
the facts. Return JSON: score, reason.

FACTS: {facts}
GAPS: {flags}"""


def _stage_known(f):
    return bool(f.get("funding_stage")) or (f.get("open_roles") or 0) >= 5 or bool(f.get("enterprise_tier"))


# One row per question: where to look, the fetch limit, and code checks for "enough" (done)
# and "stop" (kill). Mirrors the Evidence Map in the L4 lecture; worst case 4 fetches.
QUESTIONS = [
    dict(ask="Already certified?", paths=["security", "trust"], limit=1,
         done=lambda f: bool(f.get("certifications")),
         kill=lambda f: bool(f.get("certifications")), kill_reason="already holds a named certification",
         if_unanswered="treat as not certified, flag"),
    dict(ask="B2B SaaS?", paths=["product", "about"], limit=1,
         done=lambda f: bool(f.get("buyer")),
         kill=lambda f: f.get("is_saas") is False, kill_reason="not a B2B SaaS company",
         if_unanswered="manual_review"),
    dict(ask="Right stage?", paths=["careers", "pricing", "customers"], limit=2,
         done=_stage_known, kill=lambda f: False, kill_reason="",
         if_unanswered="qualify at lower rank, flagged"),
]


def _merge(facts, new):
    for k, v in new.items():
        if isinstance(v, list):
            facts[k] = facts.get(k, []) + [x for x in v if x not in facts.get(k, [])]
        elif v not in (None, ""):
            facts[k] = v


def _dead(facts):
    return next((q for q in QUESTIONS if q["kill"](facts)), None)


def qualify(domain, home_text):
    facts, trail, fetches, flags = {}, [], 0, []
    _merge(facts, extract.extract(domain, "home", home_text))

    def result(status, reason, score):
        return dict(status=status, reason=reason, score=score, facts=facts, evidence=trail,
                    fetches=fetches, flags=flags, needs_human=status == "manual_review")

    for q in QUESTIONS:
        notes, tries = [], 0
        while not _dead(facts) and not q["done"](facts) and tries < q["limit"]:
            page = q["paths"][tries]
            tries += 1
            fetches += 1
            text, note = scrape.fetch(domain, page)
            if text:
                _merge(facts, extract.extract(domain, page, text))
            notes.append(f"/{page}: {'read' if text else note}")
        answered = q["done"](facts)
        trail.append(dict(question=q["ask"], answered=answered, fetched=notes,
                          if_unanswered=None if answered else q["if_unanswered"]))
        dead = _dead(facts)
        if dead:
            return result("disqualified", dead["kill_reason"], 0)
        if not answered and q["if_unanswered"] == "manual_review":
            return result("manual_review", f"{q['ask']} not answered within {q['limit']} fetch", None)
        if not answered:
            flags.append(f"{q['ask']} unanswered: {q['if_unanswered']}")

    ans = llm.ask("qualify", domain, PROMPT.format(facts=json.dumps(facts), flags="; ".join(flags) or "none"))
    score = ans["score"] - (config.STAGE_UNKNOWN_PENALTY if not _stage_known(facts) else 0)
    return result("qualified" if score >= config.QUALIFY_THRESHOLD else "not_qualified", ans["reason"], score)
