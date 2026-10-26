# uk-new-companies-by-sic

A daily CSV of companies incorporated in the UK, filtered by SIC code, from the [Companies House API](https://developer.company-information.service.gov.uk/) advanced search endpoint.

| File | What it does |
|---|---|
| `sic_lookup.py` | Search SIC 2007 code descriptions (from Companies House's public [api-enumerations](https://github.com/companieshouse/api-enumerations) file) |
| `new_companies.py` | Every company incorporated on a given day with any of the given SIC codes, written to `data/*.csv`, plus a top-5 towns summary |

## Quick start

You need a free Companies House API key: register on the [Developer Hub](https://developer.company-information.service.gov.uk/), create an application and add a REST API key. Python 3.10 or newer.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export COMPANIES_HOUSE_API_KEY=your-key-here     # never commit it

python sic_lookup.py restaurant
python new_companies.py --sic 62012,62020                    # yesterday
python new_companies.py --sic 56101,56102 --date 2026-10-22  # a specific day
```

## Real output (run on 26 October 2026)

```
$ python new_companies.py --sic 62012,62020 --date 2026-10-23
215 companies incorporated on 2026-10-23 with SIC 62012, 62020 -> data/new-companies-2026-10-23-62012-62020.csv
  London               97
  Manchester           5
  Brighton             3
  Bury St. Edmunds     3
  Leicester            3
```

CSV columns: `company_number, company_name, incorporated, company_type, sic_codes, locality, postcode, url`.

## Run it daily

```
0 7 * * * cd /path/to/uk-new-companies-by-sic && COMPANIES_HOUSE_API_KEY=$(cat ~/.ch_key) /usr/bin/python3 new_companies.py --sic 62012,62020 >> run.log 2>&1
```

Run it for yesterday (the default); today's list is still filling up. Companies are incorporated at weekends too.

## Notes

- **Auth:** the key is the HTTP Basic username and the password is blank ([authorisation guide](https://developer-specs.company-information.service.gov.uk/guides/authorisation)). The script reads it only from `COMPANIES_HOUSE_API_KEY`.
- **Rate limit:** "up to 600 requests within a five-minute period" ([rate limiting guide](https://developer-specs.company-information.service.gov.uk/guides/rateLimiting)). One day of one industry is usually one request.
- **404 = no results** on the advanced search endpoint, and the script treats it that way.
- **SIC codes are self-declared** (up to four per company) and the filter matches any of them, so expect some noise.
- **Personal data:** the script keeps only town and postcode of the registered office and never fetches officers. A registered office can be someone's home address; if you extend this, UK GDPR applies even though the register is public.

## License

Code: MIT (see `LICENSE`).
