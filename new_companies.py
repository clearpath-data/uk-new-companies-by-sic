"""Daily list of new UK companies by SIC code, from the Companies House API.

Usage:
    export COMPANIES_HOUSE_API_KEY=...   # free key from developer.company-information.service.gov.uk
    python new_companies.py --sic 62012,62020 [--date 2026-10-23] [--out-dir data]
"""
import argparse
import collections
import csv
import datetime as dt
import os
import pathlib
import time

import requests

API = "https://api.company-information.service.gov.uk"
PAGE_SIZE = 5000  # documented maximum for advanced search ("a range of 1 to 5000")

session = requests.Session()
# The API key is the Basic-auth username; the password is empty.
session.auth = (os.environ["COMPANIES_HOUSE_API_KEY"], "")


def get(path: str, params: dict) -> dict:
    for _ in range(3):
        r = session.get(API + path, params=params, timeout=30)
        if r.status_code == 429:  # 600 requests per 5-minute window
            reset = int(r.headers.get("X-RateLimit-Reset", time.time() + 60))
            time.sleep(max(reset - time.time(), 1))
            continue
        if r.status_code == 404:  # documented as "No companies found"
            return {"hits": 0, "items": []}
        r.raise_for_status()
        return r.json()
    raise RuntimeError("Rate-limited three times in a row")


def new_companies(day: dt.date, sic_codes: list[str]) -> list[dict]:
    """All companies incorporated on `day` with any of `sic_codes`."""
    rows, start = [], 0
    while True:
        page = get("/advanced-search/companies", {
            "incorporated_from": day.isoformat(),
            "incorporated_to": day.isoformat(),
            "sic_codes": ",".join(sic_codes),
            "size": PAGE_SIZE,
            "start_index": start,
        })
        items = page.get("items", [])
        for c in items:
            addr = c.get("registered_office_address", {})
            rows.append({
                "company_number": c["company_number"],
                "company_name": c["company_name"],
                "incorporated": c.get("date_of_creation", ""),
                "company_type": c.get("company_type", ""),
                "sic_codes": " ".join(c.get("sic_codes", [])),
                "locality": addr.get("locality", ""),
                "postcode": addr.get("postal_code", ""),
                "url": f"https://find-and-update.company-information.service.gov.uk/company/{c['company_number']}",
            })
        start += len(items)
        if not items or start >= page.get("hits", 0):
            return rows


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--sic", required=True, help="comma-separated SIC 2007 codes, e.g. 62012,62020")
    p.add_argument("--date", type=dt.date.fromisoformat, default=dt.date.today() - dt.timedelta(days=1))
    p.add_argument("--out-dir", default="data")
    args = p.parse_args()

    sic = [s.strip() for s in args.sic.split(",") if s.strip()]
    rows = new_companies(args.date, sic)

    out = pathlib.Path(args.out_dir) / f"new-companies-{args.date}-{'-'.join(sic)}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["company_number"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} companies incorporated on {args.date} with SIC {', '.join(sic)} -> {out}")
    towns = collections.Counter(r["locality"].strip().title() for r in rows if r["locality"])
    for town, n in towns.most_common(5):
        print(f"  {town:<20} {n}")


if __name__ == "__main__":
    main()
