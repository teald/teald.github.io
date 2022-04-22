"""
Heavily inspired by dfm/cv/update-astro-pubs, stolen directly from
https://github.com/arjunsavel/CV/blob/main/scripts/scrape_ads.py.
"""

import ads
from datetime import date
from operator import itemgetter
import json
import importlib.util
import os
import time
import requests

here = os.path.abspath('')
spec = importlib.util.spec_from_file_location(
    "utf8totex", os.path.join(here, "utf8totex.py")
)
utf8totex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utf8totex)

# need to add ADS token

def get_papers(author):
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
                authors=list(map(utf8totex.utf8totex, paper.author)),
                year=paper.year,
                pubdate=paper.pubdate,
                doi=paper.doi[0] if paper.doi is not None else None,
                title=utf8totex.utf8totex(paper.title[0]),
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
        paper_dict = get_papers('Savel, Arjun Baliga')
    except requests.Timeout as err:
        print('Timeout error')
        print(err)
        time.sleep(60)
        paper_dict = get_papers('Savel, Arjun Baliga')

    print(paper_dict)
    with open("../data/ads_scrape.json", "w") as f:
        json.dump(paper_dict,
                 f,
                 sort_keys=True,
                 indent=2,
                 separators=(",", ": ")
                 )
