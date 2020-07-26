from flask import Flask, render_template, request, url_for
from settings import *
import requests
from collections import OrderedDict
from typing import *
from datetime import datetime
import math

app = Flask(__name__)

DEFAULT_RESULTS_PER_PAGE = 20
#TODO: responsive this
DEFAULT_MAX_PAGE_BUTTONS = 8


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('q', type=str)
    page = request.args.get('p', 1, type=int)
    sort = request.args.get('sort', "score desc", type=str)

    results_per_page = DEFAULT_RESULTS_PER_PAGE
    solr_query = {'q': 'content:"{}"'.format(keyword),

                  'rows': results_per_page,
                  'start': (page - 1) * results_per_page,

                  'sort': sort,

                  'hl': 'on',
                  'hl.fl': 'content',
                  'hl.method': 'unified',
                  'hl.tag.pre': '<span class="yellow">',
                  'hl.tag.post': '</span>'}
    r = requests.get(SOLR_SELECT_ENDPOINT, solr_query)
    query_response = r.json(object_pairs_hook=OrderedDict)

    total_results = query_response['response']['numFound']
    paginator = build_paginator(results_per_page, total_results, request.args)

    results = build_result(query_response)
    return render_template('result.html', results=results, paginator=paginator)


def build_result(solr_response: OrderedDict) -> List[dict]:
    results = []
    for doc in solr_response['response']['docs']:
        result = {}
        result['issue'] = doc['issue']
        result['link'] = FELIX_ARCHIVE_LINK.format(doc['issue'])
        result['page'] = doc['page']
        # Somehow python doesn't like the UTC indicator "Z" at the end of date string
        result['date'] = datetime.fromisoformat(doc['date'].replace('Z', '')).strftime('%d %B %Y')
        # TODO:handle multiple highlights in a page
        result['highlighted'] = solr_response['highlighting'][doc['id']]['content'][0].replace("\n", " ")
        results.append(result)
    return results


def build_paginator(results_per_page: int, total_results: int, args):
    q = args.get('q', type=str)
    cur_p = args.get('p', 1, type=int)
    sort = request.args.get('sort', "score desc", type=str)

    total_pages = math.ceil(total_results / results_per_page)
    left_most = math.floor((cur_p - 1) / DEFAULT_MAX_PAGE_BUTTONS) * DEFAULT_MAX_PAGE_BUTTONS + 1

    paginator = {}
    if cur_p == 1:
        paginator['left'] = '<li class="disabled"><a><i class="material-icons">chevron_left</i></a></li>'
    else:
        paginator['left'] = \
            '<li class="waves-effect"><a href="{}"><i class="material-icons">chevron_left</i></a></li>'. \
                format(url_for('search', q=q, sort=sort, p=cur_p - 1))

    paginator['page_buttons'] = []
    for i in range(left_most, min(total_pages + 1, left_most + DEFAULT_MAX_PAGE_BUTTONS)):
        page_url = url_for('search', q=q, sort=sort, p=i)
        if i == cur_p:
            paginator['page_buttons'].append('<li class="active black"><a href="{}">{}</a></li>'.format(page_url, i))
        else:
            paginator['page_buttons'].append(
                '<li class="waves-effect black"><a href="{}">{}</a></li>'.format(page_url, i))

    if cur_p == total_pages or total_pages == 0:
        paginator['right'] = '<li class="disabled"><a><i class="material-icons">chevron_right</i></a></li>'
    else:
        paginator['right'] = \
            '<li class="waves-effect"><a href="{}"><i class="material-icons">chevron_right</i></a></li>'. \
                format(url_for('search', q=q, sort=sort, p=cur_p + 1))
    return paginator
