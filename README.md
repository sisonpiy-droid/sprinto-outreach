# sprinto-outreach

7-step cold-outreach pipeline for Sprinto (Case 2): scrape, extract, qualify
(with an agent loop), find the contact, draft, send.

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # OFFLINE=1 needs no keys
python run.py               # reads data/domains.txt, writes outbox/ and runs/run_log.jsonl
```

OFFLINE=1 reads cached pages from fixtures/pages and canned model replies from
fixtures/llm_responses.json. No network, no cost. Company names are fictional.
