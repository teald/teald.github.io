"""
Note: BEFORE USING THIS PAPER add your ADS token to your path or to the proper
file. See https://ads.readthedocs.io/en/latest for more details.

This script is heavily inspired by dfm/cv/update-astro-pubs, and the original
source teal got was stolen directly from
https://github.com/arjunsavel/CV/blob/main/scripts/scrape_ads.py.

Updates teal made:
    + Removed TeX dependencies
    + "referee" flag for get_papers
    + Added command line parser

--- teal (teal.dillon@gmail.com)
"""

import ads
from datetime import date
from operator import itemgetter
import json
import importlib.util
import os
import time
import requests

# Parse arguments
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--all-pubs', action='store_true',
        help="Retrieves all ADS entries, not just refereed publications."
        )

parser.add_argument('-v', '--verbose', action='store_true',
        help="Verbose output to terminal."
        )

parser.add_argument('--year-range', nargs='+',
        help="Year range to search. If one year is provided, it will only "
             "search for papers *after* that year. Otherwise, two years will "
             "bound the search."
        )

p = parser.parse_args()
verbose = p.verbose
all_pubs = p.all_pubs

# Handle different year range cases.
if len(p.year_range) >= 1:
    min_year = int(p.year_range[0])
    max_year = None

else:
    min_year = max_year = None

if len(p.year_range) == 2:
    max_year = int(p.year_range[1])

elif len(p.year_range) > 2:
    raise ValueError(f"Expected 1 or 2 arguments for --year-range, got "
                     f"{len(p.year_range)} arguments."
                     )

# need to add ADS token
def get_papers(author, refereed=True):
    papers = list(
        ads.SearchQuery(
            author=author,
            fl=[
                "id",
                "title",
                "author",
                "doi",
                "year",
                "pubdate",
                "pub",
                "property",
                "volume",
                "page",
                "identifier",
                "doctype",
                "citation_count",
                "bibcode",
            ],
            max_pages=100,
        )
    )

    dicts = []
    for paper in papers:
        if refereed:
            # Only get refereed papers.
            if 'REFEREED' not in paper.property:
                continue

        if min_year is not None:
            # Specified year range.
            paper_year = int(paper.year)

        aid = [
            ":".join(t.split(":")[1:])
            for t in paper.identifier
            if t.startswith("arXiv:")
        ]

        for t in paper.identifier:
            if len(t.split(".")) != 2:
                continue
            try:
                list(map(int, t.split(".")))
            except ValueError:
                pass
            else:
                aid.append(t)

        try:
            page = int(paper.page[0])

        except (ValueError, TypeError):
            page = None

            if paper.page is not None and paper.page[0].startswith("arXiv:"):
                aid.append(":".join(paper.page[0].split(":")[1:]))

        dicts.append(
            dict(
                doctype=paper.doctype,
                authors=list(paper.author),
                year=paper.year,
                pubdate=paper.pubdate,
                doi=paper.doi[0] if paper.doi is not None else None,
                title=paper.title[0],
                pub=paper.pub,
                volume=paper.volume,
                page=page,
                arxiv=aid[0] if len(aid) else None,
                citations=(
                    paper.citation_count
                    if paper.citation_count is not None
                    else 0
                ),
                url="https://ui.adsabs.harvard.edu/abs/" + paper.bibcode,
            )
        )

    return sorted(dicts, key=itemgetter("pubdate"), reverse=True)

if __name__ == "__main__":
    # tries once more if there's a timeout error
    try:
        paper_dict = get_papers('Teal, Dillon')

    except requests.Timeout as err:
        print('Timeout error')
        print(err)
        time.sleep(60)
        paper_dict = get_papers('Teal, Dillon')

    if verbose:
        print(f"Found {len(paper_dict)} papers.")

    with open("../data/ads_scrape.json", "w") as f:
        json.dump(paper_dict,
                 f,
                 sort_keys=True,
                 indent=2,
                 separators=(",", ": ")
                 )
