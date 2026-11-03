import csv


def find_contact(domain, path="data/contacts.csv", live=False):
    if live:
        from hunter import HunterClient
        client = HunterClient()
        return client.find_decision_maker(domain)

    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if row["domain"] == domain:
                return {"name": row["name"], "title": row["title"], "email": row["email"]}
    return None
