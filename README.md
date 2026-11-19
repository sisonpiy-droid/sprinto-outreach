# sprinto-outreach

7-step cold-outreach pipeline for Sprinto (MESA Case 2): scrape, extract, qualify
(agent loop), find the contact, pain points, draft, send.

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # OFFLINE=1 needs no keys
python run.py               # reads data/domains.txt, writes outbox/ and runs/run_log.jsonl
python test_pipeline.py     # one check per Evidence Map path
```

OFFLINE=1 reads cached pages from fixtures/pages and canned model replies from
fixtures/llm_responses.json. No network, no cost. Company names are fictional.

## How each step works

1. **Scrape** (`scrape.py`): single fetch per page, cached, robots.txt respected, 1s delay, HTML cleaned
   to text (nav, scripts and forms dropped). A failure records its reason and the company goes to a human.
2. **Extract** (`extract.py`): the model fills named fields (buyer, certifications, funding stage,
   open roles...), never a free-form summary.
3. **Qualify** (`qualify.py`): an agent loop driven by an Evidence Map. Code, not the model, checks
   whether the fields are filled, picks the next page, enforces the fetch limit (worst case 4 beyond
   the homepage) and decides when to stop.

   | Question | Look at | Limit | Unanswered | Stop early |
   |---|---|---|---|---|
   | Already certified? | /security, /trust | 1 | treat as not certified, flag | yes: disqualify |
   | B2B SaaS? | /product, /about | 1 | manual review | yes: disqualify |
   | Right stage? | /careers, /pricing, /customers | 2 | qualify at lower rank (-10), flag | no |

   Then the model scores ICP fit 0-100 from the facts; 70 or more qualifies.
4. **Contact** (`contacts.py`): Hunter.io Domain Search if `HUNTER_API_KEY` is set, otherwise
   `data/contacts.csv`. Candidates are ranked by who owns security work (security/compliance, then
   engineering leadership, then founder at companies under 50 people), never by "manager" in the
   title. If nobody qualifies, a human is flagged.
5. **Pain points** (`drafts.py`): exactly two, each with the fact that backs it.
6. **Draft** (`drafts.py`): addressed to the contact by name, opening with a specific signal from the
   company's own pages. Any email that misses the first name is flagged.
7. **Send** (`send.py`): drafts to `outbox/` by default. A real Gmail send needs `OFFLINE=0`,
   `TO_ADDRESS` set to your own address, `GMAIL_APP_PASSWORD`, and the explicit `--send` flag.

Every row in `runs/run_log.jsonl` records the evidence, fetches, score, contact and why they were
chosen, pain points, hook and flags, so each decision can be defended.
