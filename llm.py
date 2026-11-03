import json
from pathlib import Path
import config

_CANNED = Path(__file__).parent / "fixtures" / "llm_responses.json"


def ask(step, domain, prompt):
    """Return the model's JSON reply as a dict."""
    if config.OFFLINE:
        canned = json.loads(_CANNED.read_text())
        return canned[step][domain]

    from google import genai
    client = genai.Client(api_key=config.API_KEY)
    resp = client.models.generate_content(
        model=config.MODEL,
        contents=prompt,
        config={"temperature": config.TEMPERATURE},
    )
    return json.loads(resp.text)
