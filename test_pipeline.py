"""Offline smoke check: each Evidence Map path ends where it should. Run: python test_pipeline.py"""
import os
os.environ["OFFLINE"] = "1"
import run

EXPECT = {  # domain: (status, fetches beyond homepage)
    "finlytic.example": ("drafted", 1), "cartwheel.example": ("drafted", 2), "zenstack.example": ("drafted", 1),
    "orbitdocs.example": ("not_qualified", 1), "brickbox.example": ("disqualified", 0),
    "vaultly.example": ("disqualified", 0), "mistline.example": ("manual_review", 2), "ghostco.example": ("failed", 0),
}
for d, (status, fetches) in EXPECT.items():
    r = run.process(d)
    assert (r["status"], r["fetches"]) == (status, fetches), (d, r["status"], r["fetches"], r["reason"])
    assert r["fetches"] <= 4
assert run.process("finlytic.example")["contact"]["name"] == "Rhea Menon"
assert run.process("cartwheel.example")["contact"]["name"] == "Arjun Iyer"  # not the Office Manager
print("ok")
