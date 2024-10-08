import os.path

from flask import Flask, render_template, request, url_for, redirect
from werkzeug.security import safe_join

from settings import *
import requests
from collections import OrderedDict
from typing import *
from datetime import datetime
from dateutil import parser
import math

app = Flask(__name__)


@app.route('/issue/<int:issue_no>', methods=['GET'])
def issue(issue_no: int):
    return redirect(FELIX_ARCHIVE_LINK.format(issue_no))


@app.route('/')
def index():
    return render_template('index.html', current_year=datetime.now().year, max_issue=MAX_ISSUE)


DEFAULT_RESULTS_PER_PAGE = 20
# TODO: responsive this
DEFAULT_MAX_PAGE_BUTTONS = 8
FIRST_ISSUE_DATE = "1949-12-09T00:00:00Z"


@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('q', type=str)
    page = request.args.get('p', 1, type=int)
    sort = request.args.get('sort', "score desc", type=str)
    from_date = request.args.get('from', FIRST_ISSUE_DATE, type=str)
    to_date = request.args.get('to', datetime.today().isoformat(timespec='seconds'), type=str)

    from_date = parser.parse(from_date, ignoretz=True).isoformat(timespec='seconds') + "Z"
    to_date = parser.parse(to_date, ignoretz=True).isoformat(timespec='seconds') + "Z"

    results_per_page = DEFAULT_RESULTS_PER_PAGE
    solr_query = {'defType': 'dismax',

                  'q': keyword,
                  'qf': 'content',

                  'fq': f'date:[{from_date} TO {to_date}]',

                  'rows': results_per_page,
                  'start': (page - 1) * results_per_page,

                  'sort': sort,

                  'hl': 'on',
                  'hl.fl': 'content',
                  'hl.method': 'unified',
                  'hl.tag.pre': '<span class="yellow">',
                  'hl.tag.post': '</span>',

                  'echoParams': 'none'
                  }
    r = requests.get(SOLR_SELECT_ENDPOINT, solr_query)
    query_response = r.json(object_pairs_hook=OrderedDict)

    if 'response' not in query_response:
        raise Exception("Solr query failed, response: " + str(query_response))

    total_results = query_response['response']['numFound']
    paginator = build_paginator(results_per_page, total_results, request.args)

    results = build_result(query_response)
    return render_template('result.html', results=results, paginator=paginator, current_year=datetime.now().year)


def build_result(solr_response: OrderedDict) -> List[dict]:
    results = []
    for doc in solr_response['response']['docs']:
        result = {'issue': doc['issue'],
                  'link': FELIX_ARCHIVE_LINK.format(doc['issue']),
                  'page': doc['page'],
                  # Somehow python doesn't like the UTC indicator "Z" at the end of date string
                  'date': datetime.fromisoformat(doc['date'].replace('Z', '')).strftime('%d %B %Y'),
                  # TODO:handle multiple highlights in a page
                  'highlightings': map(lambda s: s.replace("\n", " "),
                                       solr_response['highlighting'][doc['id']]['content'])
                  }
        results.append(result)
    return results


def build_paginator(results_per_page: int, total_results: int, args):
    q = args.get('q', type=str)
    cur_p = args.get('p', 1, type=int)
    sort = request.args.get('sort', type=str)
    from_date = request.args.get('from', type=str)
    to_date = request.args.get('to', type=str)

    total_pages = math.ceil(total_results / results_per_page)
    left_most = math.floor((cur_p - 1) / DEFAULT_MAX_PAGE_BUTTONS) * DEFAULT_MAX_PAGE_BUTTONS + 1

    base_query = {"q": q, "from": from_date, "to": to_date, "sort": sort}

    paginator = {}
    if cur_p == 1:
        paginator['left'] = \
            '<li class="disabled"><a><i class="material-icons grey-text text-lighten-2">chevron_left</i></a></li>'
    else:
        paginator['left'] = \
            '<li class="waves-effect"><a href="{}"><i class="material-icons">chevron_left</i></a></li>'. \
                format(url_for('search', **base_query, p=cur_p - 1))

    paginator['page_buttons'] = []
    for i in range(left_most, min(total_pages + 1, left_most + DEFAULT_MAX_PAGE_BUTTONS)):
        page_url = url_for('search', **base_query, p=i)
        if i == cur_p:
            paginator['page_buttons'].append(f'<li class="active black"><a href="{page_url}">{i}</a></li>')
        else:
            paginator['page_buttons'].append(
                f'<li class="waves-effect black"><a href="{page_url}">{i}</a></li>')

    if cur_p == total_pages or total_pages == 0:
        paginator['right'] = \
            '<li class="disabled"><a><i class="material-icons grey-text text-lighten-2">chevron_right</i></a></li>'
    else:
        paginator['right'] = \
            '<li class="waves-effect"><a href="{}"><i class="material-icons">chevron_right</i></a></li>'. \
                format(url_for('search', **base_query, p=cur_p + 1))
    return paginator


def normalise_relative_path(path: str):
    if os.path.isabs(path):
        return path
    else:
        return os.path.join(os.path.dirname(__file__), path)


@app.route('/browse/<int:year>')
def browse_year(year):
    generated_path = safe_join(normalise_relative_path(GENERATED_LISTING_DIR), f"{year}.html")
    content = open(generated_path).read()
    return render_template('issue_browser.html', current_year=datetime.now().year, content=content)


@app.route('/browse')
def browse():
    generated_path = safe_join(normalise_relative_path(GENERATED_LISTING_DIR), 'years_listing.html')
    content = open(generated_path).read()
    return render_template('issue_browser.html', current_year=datetime.now().year, content=content)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
