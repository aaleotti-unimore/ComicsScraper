from __future__ import unicode_literals, print_function

import logging

from flask import render_template, Blueprint, redirect

from db_entities import Issue
from managers.db_manager import DB_manager

logger = logging.getLogger(__name__)
from datetime import datetime
from amazon.api import AmazonAPI, SearchException, AmazonException, AmazonProduct

show_issue_api = Blueprint('show_issue_api', __name__)

amz = {
    'access_key': 'AKIAIORTLS4YBKHUNKPQ',
    'secret_key': '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',
    'associate_tag': 'amazingkirbi-21',
    'locale': 'it'
}


# products = amazon.search_n(5, Keywords='Iron Man 2 Marvel Masterworks', SearchIndex='Books')
# for i, product in enumerate(products):
#     pprint("{0}. '{1}'".format(i, product.large_image_url))

@show_issue_api.route('/show_issues/<issue_id>')
def issue_page(issue_id):
    # issue_id = "Avengers 1"
    issue = Issue.query(
        Issue.title == issue_id
    ).fetch()
    if issue:
        dbm = DB_manager()
        # item = dbm.to_json(issue)
        # pprint(item)
        try:
            amazon = AmazonAPI(amz['access_key'], amz['secret_key'], amz['associate_tag'], region="IT")
            # products = []
            # prAmazonProduct('B01FMPMI20', amz['associate_tag'], amazon)
            products = amazon.search_n(5, Keywords=issue_id, SearchIndex='Books')
            return render_template('issue_page.html', issues=issue, products=products)
        except SearchException:
            products = None
            return render_template('issue_page.html', issues=issue, products=products)
        except AmazonException:
            pass

    return redirect('/', 302)
