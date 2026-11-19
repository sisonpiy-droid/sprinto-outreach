# Illustrative assumptions from Case 2 (15-20 min per company by hand, 8-15 companies a week).
MANUAL_MINUTES_PER_COMPANY = 17.5
COMPANIES_PER_WEEK = 12
WEEKS_PER_MONTH = 52 / 12
HOURLY_COST_INR = 1200
TOOL_COST_PER_MONTH_INR = 6000
TARGET_SECONDS_PER_COMPANY = 120  # pre-build decision 1: under 2 minutes


def monthly_summary():
    hours_saved = MANUAL_MINUTES_PER_COMPANY * COMPANIES_PER_WEEK / 60 * WEEKS_PER_MONTH  # inputs are per week
    value = hours_saved * HOURLY_COST_INR
    return {
        "hours_saved_per_month": round(hours_saved, 1),
        "net_value_per_month_inr": round(value - TOOL_COST_PER_MONTH_INR),
    }


def run_stats(rows):
    n = len(rows) or 1
    by = {}
    for r in rows:
        by[r["status"]] = by.get(r["status"], 0) + 1
    return {
        "companies": len(rows),
        "by_status": by,
        "needs_human": sum(r["needs_human"] for r in rows),
        "avg_seconds_per_company": round(sum(r["seconds"] for r in rows) / n, 2),
        "target_seconds_per_company": TARGET_SECONDS_PER_COMPANY,
        "avg_fetches_beyond_homepage": round(sum(r.get("fetches", 0) for r in rows) / n, 1),
    }
