'''This generates ../publications.markdown using the data in
../data/ads_scrape.json

--- teal (teal.dillon@gmail.com)
'''
import json
import datetime

from typing import Dict, List, Any


# Constants
author_of_interest = "Teal"  # Identifying name here.

header = '\n'.join([
    "---",
    "layout: page",
    "title: Publications",
    "permalink: /publications/",
    "---",
    "",
    "# Refereed Publications\n"
    ])


# Definitions
def get_ads_data(file: str="../data/ads_scrape.json") -> Dict[str, Any]:
    '''Fetches ads data from a json file.'''
    with open(file, 'r') as infile:
        data = json.load(infile)

    return data


def markdown_pub(publications: Dict[str, Any]) -> str:
    '''Turns a dict of publications into markdown-formatted string.'''
    outstr = ''

    for data in publications:
        # Authors first.
        outstr += author_string(data['authors']) + ". "

        # Title
        outstr += f"_{data['title']}_. "

        # Publication
        outstr += f"_{data['pub']}_, "

        # Date
        outstr += pub_date_str(data['pubdate']) + ". "

        # ADS link
        outstr += f"[ADS Entry]({data['url']})."

        # Double escape for spaces between the entries, though this could be
        # better separation TK
        outstr += '\n\n'

    return outstr


def author_string(authors: List[str],
                  author_of_interest: str=author_of_interest,
                  ) -> str:
    '''Generates the author string, including the relevant author assigned to
    the constant at the top of the file.
    '''
    outstr = ''
    author_of_interest = author_of_interest.lower()

    for i, author in enumerate(authors):
        if author_of_interest in author.lower():
            # Bold this author.
            outstr += f"**{author}**; "

        else:
            outstr += f"{author}; "

    # Return the outstr without the final space and comma (for consistency).
    return outstr[:-2]


def pub_date_str(date:str) -> str:
    '''Takes a date in the form YYYY-MM-DD and converts it into named month +
    year.
    '''
    year, month, day = [int(x) for x in date.split('-')]

    # The day is 0-indexed in ADS for some reason. Idk what standard it's
    # trying to conform to.
    day += 1

    date = datetime.date(year, month, day)

    return date.strftime("%B %Y")


def output_to_md_file(md_string: str,
                      write_file: str="../publications.markdown"
                      ) -> None:
    '''Takes the string produced by markdown_pub and writes it to the
    appropriate publications.markdown file.
    '''
    outstr = header

    outstr += md_string

    with open(write_file, 'w') as outfile:
        outfile.write(outstr)



def main():
    '''Main body of the program,'''
    ads_data = get_ads_data()

    md_str = markdown_pub(ads_data)

    print(md_str)

    output_to_md_file(md_str)


if __name__ == "__main__":
    main()
