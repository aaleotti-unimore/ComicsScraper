from __future__ import unicode_literals

"""`main` is the top level module for your Flask application."""

from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, g, request
from google.appengine.ext import ndb
from google.appengine.api import users
from db_manager import db_manager
from werkzeug import debug
from bs4 import BeautifulSoup
from db_entities import Issue, Serie, Users

app = Flask(__name__)
app.wsgi_app = debug.DebuggedApplication(app.wsgi_app, True)


# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

@app.context_processor
def inject_user():
    my_user = None
    logout_url = None
    login_url = None
    google_user = users.get_current_user()
    if google_user:
        logout_url = users.create_logout_url('/')
        my_user = Users.get_or_insert(str(google_user.user_id()))
        # my_user.serie_list = [
        #     ndb.Key(Serie, 'Avengers'),
        #     ndb.Key(Serie, 'Iron Man'),
        #     ndb.Key(Serie, 'Devil e i Cavalieri Marvel'),
        #     ndb.Key(Serie, 'Incredibili Inumani'),
        #     ndb.Key(Serie, 'Marvel Crossover'),
        #     ndb.Key(Serie, 'Marvel Miniserie')
        # ]
        my_user.put()
        print my_user
    else:
        login_url = users.create_login_url('/')
    g.user = my_user
    return dict(my_user=my_user, login_url=login_url, logout_url=logout_url)


@app.route('/')
@app.route('/index.html')
def main():
    # DATETIME RANGES SETTINGS
    today = datetime.today()
    start_week = today - timedelta(today.weekday())
    end_week = start_week + timedelta(7)
    start_last_week = today - timedelta(today.weekday()) - (timedelta(7))
    # END DATETIME RANGES SETTINGS

    # QUERY
    google_user = users.get_current_user()
    if google_user:
        my_user = Users.get_or_insert(str(google_user.user_id()))
        if my_user.serie_list:
            issues = Issue.query(Issue.serie.IN(my_user.serie_list)).order(Issue.data)
        else:
            issues = None
    else:
        issues = Issue.query()

    week_issues = None
    future_issues = None
    past_issues = None
    week_issues_count = None
    future_issues_count = None
    past_issues_count = None
    week_sum = 0
    past_sum = 0
    if issues:
        week_issues = issues.filter(ndb.AND(Issue.data >= start_week, Issue.data <= end_week))
        future_issues = issues.filter(Issue.data > end_week)
        past_issues = issues.filter(ndb.AND(Issue.data >= start_last_week, Issue.data < start_week))

        week_issues_count = issues.count(limit=None),
        future_issues_count = future_issues.count(limit=None),
        past_issues_count = past_issues.count(limit=None),

        # SUM WEEKLY PRICES

        import re
        for issue in past_issues:
            past_sum += float(re.sub(",", ".", issue.prezzo[2:]))

        for issue in week_issues:
            week_sum += float(re.sub(",", ".", issue.prezzo[2:]))

            # END SUM WEEKLY PRICES

    # END QUERY

    return render_template("mainpage_contents.html",
                           issues=week_issues,
                           issues_count=week_issues_count,
                           week_sum=week_sum,
                           future_issues=future_issues,
                           future_issues_count=future_issues_count,
                           past_issues=past_issues,
                           past_issues_count=past_issues_count,
                           past_sum=past_sum
                           )


@app.route('/user_page', methods=['GET', 'POST'])
def my_page():
    dbm = db_manager()
    list = dbm.get_series(Serie.query())
    # for serie in list:
    #     print(serie)
    return render_template("my_lists.html", series=list)


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500


@app.route('/tasks/weekly_update')
def cronjob():
    par = Parsatore()
    dbm = db_manager()
    dbm.save_to_DB(par.parser())
    return redirect('/')


@app.route('/restricted/cleardb')
def clear_db():
    ndb.delete_multi(
        Issue.query().fetch(keys_only=True)
    )
    cronjob()
    return redirect('/')


import logging
import sys
import urllib2

reload(sys)
sys.setdefaultencoding('utf8')


class Parsatore():
    def __init__(self):
        self.urls = [
            'http://comics.panini.it/store/pub_ita_it/magazines/cmc-m.html?limit=25&p=1',
            'http://comics.panini.it/store/pub_ita_it/magazines/cmc-m.html?limit=25&p=2',
            'http://comics.panini.it/store/pub_ita_it/magazines/cmc-m.html?limit=25&p=3',
            'http://comics.panini.it/store/pub_ita_it/magazines/cmc-m.html?limit=25&p=4',
            'http://comics.panini.it/store/pub_ita_it/magazines/cmc-m.html?limit=25&p=5',
            'http://comics.panini.it/store/pub_ita_it/magazines/cmc-m.html?limit=25&p=6',
            'http://comics.panini.it/store/pub_ita_it/magazines/cmc-m.html?limit=25&p=7',
        ]

    def parser(self):
        parsed = []
        for url in self.urls:
            try:
                result = urllib2.urlopen(url, None, 45)
                page = result.read()
                soup = BeautifulSoup(page, 'lxml')
                uscite = soup.find_all('div', attrs={'class': "list-group-item row item "})

                for uscita in uscite:
                    diz = {}

                    title = uscita.find('h3', class_="product-name").find('a').get_text()
                    diz['title'] = " ".join(title.split())

                    subtitle = uscita.find('h3', class_="product-name").find('small', attrs={"class": "subtitle"})
                    if subtitle:
                        diz['subtitle'] = " ".join(subtitle.text.split())

                    serie = uscita.find('h3', class_="product-name").find('small', attrs={"class": "serie"})
                    if serie:
                        diz['serie'] = " ".join(serie.text.split())

                    ristampa = uscita.find('h5', attrs={"class": "reprint"})
                    if ristampa:
                        diz['ristampa'] = " ".join(ristampa.text.split())

                    data_str = uscita.find('h4', class_="publication-date").text.strip()
                    struct_date = datetime.strptime(data_str, "%d/%m/%Y")
                    diz['data'] = struct_date
                    diz['prezzo'] = uscita.find('p', class_="old-price").text.strip()
                    parsed.append(diz)

                    thmb = uscita.find('img', class_="img-thumbnail img-responsive")
                    diz['image'] = thmb["src"]

            except urllib2.URLError:
                logging.exception('Caught exception fetching url')

        return parsed
