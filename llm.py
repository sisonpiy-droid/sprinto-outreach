import json
from pathlib import Path

import config

_CANNED = Path(__file__).parent / "fixtures" / "llm_responses.json"


def ask(step, domain, prompt, key=None):
    """Return the model's JSON reply as a dict. key picks the sub-reply (e.g. which page was read)."""
    if config.OFFLINE:
        reply = json.loads(_CANNED.read_text(encoding="utf-8"))[step][domain]
        return reply[key] if key else reply

    from google import genai
    client = genai.Client(api_key=config.API_KEY)
    resp = client.models.generate_content(
        model=config.MODEL,
        contents=prompt,
        config={"temperature": config.TEMPERATURE, "response_mime_type": "application/json"},
    )
    return json.loads(resp.text)
