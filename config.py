import os
from dotenv import load_dotenv

load_dotenv()

OFFLINE = os.getenv("OFFLINE", "1") == "1"
API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL = "gemini-2.0-flash"
TEMPERATURE = 0.7

QUALIFY_THRESHOLD = 70    # minimum ICP fit (0-100, same scale as the score) to email
MAX_ROUNDS = 2            # extra page fetches the qualifier may ask for
TO_ADDRESS = "growth.lead@example.com"  # case rule: all mail goes to the student's own inbox
