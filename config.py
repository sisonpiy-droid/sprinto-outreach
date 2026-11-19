import os
from dotenv import load_dotenv

load_dotenv()

OFFLINE = os.getenv("OFFLINE", "1") == "1"
API_KEY = os.getenv("GEMINI_API_KEY", "")
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY", "")  # Option A for step 4; empty = use data/contacts.csv (Option B)
MODEL = "gemini-2.0-flash"
TEMPERATURE = 0.3

QUALIFY_THRESHOLD = 70      # minimum ICP fit (0-100, same scale as the score) to email
STAGE_UNKNOWN_PENALTY = 10  # Evidence Map: unanswered stage = "qualify at lower rank, flagged"
TO_ADDRESS = os.getenv("TO_ADDRESS", "growth.lead@example.com")  # case rule: all mail goes to your own inbox
SENDER_NAME = os.getenv("SENDER_NAME", "Piyush")

USER_AGENT = "sprinto-outreach-research-bot/1.0"
FETCH_DELAY = 1.0  # seconds between live requests
THIN_WORDS = 200   # a live page with fewer words may be JavaScript-rendered
