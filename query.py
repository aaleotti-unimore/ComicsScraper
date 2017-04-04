from __future__ import unicode_literals

import logging

"""`main` is the top level module for your Flask application."""

from datetime import datetime, timedelta
from google.appengine.ext import ndb
from db_entities import Issue
import logging.config
import re


class Query:
    def __init__(self, my_user):
        self.my_user = my_user
        self.logger = logging.getLogger(__name__)

        self.issues = None
        self.week_issues = None
        self.future_issues = None
        self.past_issues = None
        self.special_issues = None

        self.week_issues_count = 0
        self.future_issues_count = 0
        self.past_issues_count = 0

        self.week_issues_sum = 0
        self.past_issues_sum = 0
        self.special_issues_sum = 0
        # END VAR DECLARATION

    def get_issues(self):
        ret = {}
        if self.my_user:
            if self.my_user.serie_list:
                self.issues = Issue.query(Issue.serie.IN(self.my_user.serie_list)).order(Issue.data)
        else:
            self.issues = Issue.query()

        if self.issues:
            # DATETIME RANGES SETTINGS
            today = datetime.today()
            start_week = today - timedelta(today.weekday())
            end_week = start_week + timedelta(7)
            start_last_week = today - timedelta(today.weekday()) - (timedelta(7))
            # END DATETIME RANGES SETTING

            self.logger.debug("the query retrieved: " + str(self.issues.count()) + " elements")

            # FILTERING QUERY
            self.week_issues = self.issues.filter(ndb.AND(Issue.data >= start_week, Issue.data <= end_week))
            self.future_issues = self.issues.filter(Issue.data > end_week)
            self.past_issues = self.issues.filter(ndb.AND(Issue.data >= start_last_week, Issue.data < start_week))
            # END FILTERING QUERY

            self.week_issues_count = self.issues.count(limit=None),
            self.future_issues_count = self.future_issues.count(limit=None),
            self.past_issues_count = self.past_issues.count(limit=None),

            for issue in self.past_issues:
                # SUM WEEKLY PRICES
                self.past_issues_sum += float(re.sub(",", ".", issue.prezzo[2:]))

            for issue in self.week_issues:
                # SUM WEEKLY PRICES
                self.week_issues_sum += float(re.sub(",", ".", issue.prezzo[2:]))

        # END QUERY

        ret['issues'] = self.issues
        ret['week_issues'] = self.week_issues
        ret['future_issues'] = self.future_issues
        ret['past_issues'] = self.past_issues
        ret['special_issues'] = self.special_issues

        ret['week_issues_count'] = self.week_issues_count
        ret['future_issues_count'] = self.future_issues_count
        ret['past_issues_count'] = self.past_issues_count

        ret['week_issues_sum'] = self.week_issues_sum
        ret['past_issues_sum'] = self.past_issues_sum
        ret['special_issues_sum'] = self.special_issues_sum
        ret['nullobj'] = Issue(id="null", data=datetime.today())

        return ret

    def get_specials(self):
        ret = {}
        if self.my_user:
            if self.my_user.special_list:
                # special_keys = [ndb.Key(Issue, special_id) for special_id in self.my_user.special_list]
                self.special_issues = ndb.get_multi(self.my_user.special_list)
                if self.logger.getEffectiveLevel() == logging.DEBUG:
                    for issue in self.special_issues:
                        self.logger.debug("SPECIALS: " + str(issue.key.id()).decode('utf-8'))

            if self.special_issues:
                for issue in self.special_issues:
                    # SUM WEEKLY PRICES
                    self.special_issues_sum += float(re.sub(",", ".", issue.prezzo[2:]))

        ret['special_issues'] = self.special_issues
        ret['special_issues_sum'] = self.special_issues_sum
        return ret

    def check_if_empty(self):
        q = Issue.query().count()
        self.logger.debug("database has " + str(q) + " elements")
        return q
