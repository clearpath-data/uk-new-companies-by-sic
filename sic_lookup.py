"""Look up SIC 2007 code descriptions from Companies House's public api-enumerations file."""
import sys

import requests
import yaml

URL = "https://raw.githubusercontent.com/companieshouse/api-enumerations/master/constants.yml"


def sic_descriptions() -> dict[str, str]:
    data = yaml.safe_load(requests.get(URL, timeout=30).text)
    # The file also holds older 4-digit SIC 2003 codes; current filings use 5-digit SIC 2007.
    return {str(k): v for k, v in data["sic_descriptions"].items() if len(str(k)) == 5}


if __name__ == "__main__":
    names = sic_descriptions()
    words = [w.lower() for w in sys.argv[1:]]
    for code, desc in sorted(names.items()):
        if all(w in desc.lower() for w in words):
            print(code, desc)
