import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

import config


def send(domain, subject, body, approved=False):
    """Step 7. Writes to outbox/ unless running live AND approved (run.py --send)."""
    if config.OFFLINE or not approved:
        Path("outbox").mkdir(exist_ok=True)
        Path(f"outbox/{domain}.txt").write_text(
            f"To: {config.TO_ADDRESS}\nSubject: {subject}\n\n{body}\n", encoding="utf-8")
        return "drafted to outbox/ (not sent)"
    if config.TO_ADDRESS.endswith("@example.com"):
        raise SystemExit("Set TO_ADDRESS in .env to your own address before sending.")
    msg = EmailMessage()
    msg["To"], msg["From"], msg["Subject"] = config.TO_ADDRESS, config.TO_ADDRESS, subject
    msg.set_content(body)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(config.TO_ADDRESS, os.environ["GMAIL_APP_PASSWORD"])
        s.send_message(msg)
    return "sent"
