from __future__ import unicode_literals

import logging
import logging.config
import re
from datetime import datetime, timedelta

from flask_login import current_user
from google.appengine.ext import ndb

from models.models import Issue


class Query:
    """
    Provides ready-to-use functions for querying the database
    """

    def __init__(self):
        # self.my_user = my_user
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

    def get_user_issues(self, user):
        """
        return all the issues from the user
        
        :param user: user
        :returns: list of user issues if the list is not empty
        """
        if user.series_list:
            return Issue.query(Issue.series.IN(user.series_list)).fetch()
        else:
            return None

    def get_issues(self):
        """
        Retrieves current user's issues from last week-onwards. 
        If the user's is not authenticated, returns all the issues from last week-onwards
        
        :returns: dictionary of issues lists for the mainpage template, plus the number of issues and the total price amount
        """
        ret = {}
        if current_user.is_authenticated:
            if current_user.series_list:
                self.issues = Issue.query(Issue.series.IN(current_user.series_list)).order(Issue.date)
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
            self.week_issues = self.issues.filter(ndb.AND(Issue.date >= start_week, Issue.date <= end_week))
            self.future_issues = self.issues.filter(Issue.date > end_week)
            self.past_issues = self.issues.filter(ndb.AND(Issue.date >= start_last_week, Issue.date < start_week))
            # END FILTERING QUERY

            self.week_issues_count = self.issues.count(limit=None),
            self.future_issues_count = self.future_issues.count(limit=None),
            self.past_issues_count = self.past_issues.count(limit=None),

            for issue in self.past_issues:
                # SUM WEEKLY PRICES
                try:
                    self.past_issues_sum += float(re.sub(",", ".", issue.price[2:]))
                except TypeError:
                    self.past_issues_sum += 0

            for issue in self.week_issues:
                # SUM WEEKLY PRICES
                try:
                    self.week_issues_sum += float(re.sub(",", ".", issue.price[2:]))
                except TypeError:
                    self.week_issues_sum += 0

        # END QUERY

        ret['issues'] = self.issues
        ret['week_issues'] = self.week_issues
        ret['future_issues'] = self.future_issues
        ret['past_issues'] = self.past_issues
        ret['special_issues'] = self.special_issues

        # ISSUES COUNT
        ret['week_issues_count'] = self.week_issues_count
        ret['future_issues_count'] = self.future_issues_count
        ret['past_issues_count'] = self.past_issues_count

        # ISSUES TOTAL PRICES
        ret['week_issues_sum'] = self.week_issues_sum
        ret['past_issues_sum'] = self.past_issues_sum
        ret['special_issues_sum'] = self.special_issues_sum

        ret['nullobj'] = Issue(id="null", date=datetime.today())  # empty placeholder issue

        return ret

    def get_user_specials(self, user):
        """
        Retrieves user's special issues. 
        
        :param user: user
        :returns: list of special issues
        """
        return ndb.get_multi(user.specials_list)

    def get_specials(self):
        """
        return current users's special numbers
        If the users is not autenticated, return an empty list
        
        :returns: dictionary of issues list and the summed price
        """
        ret = {}
        if current_user.is_authenticated:
            if current_user.specials_list:
                # special_keys = [ndb.Key(Issue, special_id) for special_id in current_user.specials_list]
                self.special_issues = ndb.get_multi(current_user.specials_list)
                for issue in self.special_issues:
                    self.logger.debug("SPECIALS: " + str(issue.key.id()).decode('utf-8'))

            if self.special_issues:
                for issue in self.special_issues:
                    # SUM WEEKLY PRICES
                    self.special_issues_sum += float(re.sub(",", ".", issue.price[2:]))

        ret['special_issues'] = self.special_issues
        ret['special_issues_sum'] = self.special_issues_sum
        return ret

    def check_if_empty(self):
        """
        Checks if the database is empty
        
        :returns: 0 or 1 if the database has at least one issue
        """
        q = Issue.query().fetch(limit=1)
        return q
