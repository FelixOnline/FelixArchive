import os
from dataclasses import dataclass
from typing import List

import pandas as pd
from flask import render_template_string, Flask

from settings import THUMBNAIL_LINK, FELIX_ARCHIVE_LINK, GENERATED_LISTING_DIR, FELIX_DATES_CSV


@dataclass
class IssueListing:
    issue: int
    thumbnail_link: str = None
    pdf_link: str = None

    def __post_init__(self):
        self.thumbnail_link = THUMBNAIL_LINK.format(self.issue)
        self.pdf_link = FELIX_ARCHIVE_LINK.format(self.issue)


@dataclass
class YearListing:
    year: int
    first_issue_thumbnail_link: str


year_template = """
<div class="container">
  <div class="issue-cards-container">
    {% for issue in issues %}
      <div class="card">
        <a href="{{ issue.pdf_link }}">
          <div class="card-image">
            <img src="{{ issue.thumbnail_link }}">
          </div>
          <div class="card-action">
            Issue {{ issue.issue }}
          </div>
        </a>
      </div>
    {% endfor %}
  </div>
</div>
"""

all_years_template = """
<div class="container">
  <div class="issue-cards-container">
    {% for year in years %}
      <div class="card">
        <a href="/browse/{{ year.year }}">
          <div class="card-image">
            <img src="{{ year.first_issue_thumbnail_link }}">
          </div>
          <div class="card-action">
            {{ year.year }}
          </div>
        </a>
      </div>
    {% endfor %}
  </div>
</div>
"""

df = pd.read_csv(FELIX_DATES_CSV, parse_dates=["date"])


def issues_of_year(year: int) -> List[int]:
    selected = df[df["date"].dt.year == year]
    return list(selected["issue_no"])


def generate_year(year: int):
    issues = [IssueListing(issue=i) for i in issues_of_year(year)]
    rendered = render_template_string(year_template, issues=issues)
    with open(os.path.join(GENERATED_LISTING_DIR, f"{year}.html"), "w") as f:
        f.write(rendered)


def generate():
    years = []
    for year in df["date"].dt.year.unique():
        first_issue = df[df["date"].dt.year == year].iloc[0]["issue_no"]
        generate_year(year)
        years.append(YearListing(year=year, first_issue_thumbnail_link=THUMBNAIL_LINK.format(first_issue)))

    rendered = render_template_string(all_years_template, years=years)
    with open(os.path.join(GENERATED_LISTING_DIR, "years_listing.html"), "w") as f:
        f.write(rendered)


if __name__ == "__main__":
    try:
        os.mkdir(GENERATED_LISTING_DIR)
    except FileExistsError:
        pass
    with Flask(__name__).app_context():
        generate()
