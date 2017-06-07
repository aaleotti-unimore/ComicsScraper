"""
This module contains the business logic for the single Issue view
"""

from __future__ import unicode_literals, print_function

import csv
import logging

from flask import render_template, Blueprint, redirect

from handlers.database import Database
from models.models import Issue

logger = logging.getLogger(__name__)
from amazon.api import AmazonAPI, SearchException, AmazonException

show_issue_api = Blueprint('show_issue_api', __name__)

with open('static/secrets/accessKeys.csv') as csvfile:
    accessKeys = csv.DictReader(csvfile)
    for row in accessKeys:
        amz = {
            'access_key': row['Access key ID'],
            'secret_key': row['Secret access key'],
            'associate_tag': 'amazingkirbi-21',
            'locale': 'it'
        }



@show_issue_api.route('/show_issues/<issue_id>')
def issue_page(issue_id):
    """
    Renders an issue page given its issue id. contains all the infos of the isse and manages the Amazon API
    
    :param issue_id: issue id as defined in the model
    :returns: renders the "issue_page.html" template or redirects to index with a 302 html code if the issue is not found
    """


    # issue_id = "Avengers 1"
    issue = Issue.query(
        Issue.title == issue_id
    ).fetch()
    if issue:
        dbm = Database()

        try:
            amazon = AmazonAPI(amz['access_key'], amz['secret_key'], amz['associate_tag'], region="IT")
            products = amazon.search_n(5, Keywords=issue_id, SearchIndex='Books')
            if issue[0].subtitle:
                sub_products = amazon.search_n(5, Keywords=issue[0].subtitle, SearchIndex='Books')
                products = sub_products + products

            return render_template('issue_page.html', issues=issue, products=products)
        except SearchException:
            products = None
            return render_template('issue_page.html', issues=issue, products=products)
        except AmazonException:
            pass

    return redirect('/', 302)
