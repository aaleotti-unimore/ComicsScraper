import Queue
import httplib
import logging
import logging.config
import threading
import urllib2
from datetime import datetime

from bs4 import BeautifulSoup

from managers.db_manager import DB_manager


class Parser():
    """
    Parses the website page and saves to the database
    """

    def __init__(self, min_pages, max_pages):
        self.dbm = DB_manager()
        self.logger = logging.getLogger(__name__)

        self.urls_to_load = []
        for i in range(min_pages, max_pages):
            self.urls_to_load.append('http://comics.panini.it/store/pub_ita_it/magazines/cmc-m.html?limit=25&p=%d' % i)

        # parallel fetch of the pages
        q = self.fetch_parallel(self.urls_to_load)
        while not q.empty():
            self.page_parser(q.get())
            q.task_done()

    def read_url(self, url, queue):
        """
        read a specific url, putting the data in the queue
        :param url: url to parse
        :param queue: thread queue
        """

        try:
            data = urllib2.urlopen(url).read()
            self.logger.debug('Fetched %s from %s' % (len(data), url))
            queue.put(data)
        except urllib2.HTTPError as e:
            self.logger.error('HTTPError = ' + str(e.code))
            # return "#"
        except urllib2.URLError as e:
            self.logger.error('URLError = ' + str(e.reason))
            # return "#"
        except httplib.HTTPException as e:
            self.logger.error('HTTPException' + str(e))
            # return "#"
        except Exception:
            import traceback
            self.logger.error('generic exception: ' + traceback.format_exc())
            # return "#"

    def fetch_parallel(self, urls_to_load):
        """
        parses url in parallel
        :param urls_to_load: urls to load
        :return: thread queue
        """
        result = Queue.Queue()
        threads = [threading.Thread(target=self.read_url, args=(url, result)) for url in urls_to_load]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return result

    def page_parser(self, url):
        """
        parses the single page to collect comics issues
        :param url: page url
        """
        parsed = []  # list of parsed elements
        desc_urls = []  # list of issue description ulrs

        soup = BeautifulSoup(url, 'lxml')
        issues = soup.find_all('div', attrs={'class': "list-group-item"})  # list of all found comics issues

        for issue in issues:
            issue_parsed_data = {}

            title = issue.find('h3', class_="product-name").find('a')  # issue title
            issue_parsed_data['title'] = " ".join(title.get_text().split())
            issue_parsed_data['url'] = str(title.get('href'))

            subtitle = issue.find('h3', class_="product-name").find('small',
                                                                    attrs={"class": "subtitle"})  # issue subtitle
            if subtitle:
                issue_parsed_data['subtitle'] = " ".join(subtitle.text.split())

            series = issue.find('h3', class_="product-name").find('small', attrs={"class": "serie"})  # issue serie
            if series:
                issue_parsed_data['series'] = " ".join(series.text.split())
            else:
                issue_parsed_data['series'] = "One Shot"

            reprint = issue.find('h5', attrs={"class": "reprint"})  # if reprint
            if reprint:
                issue_parsed_data['reprint'] = " ".join(reprint.text.split())

            date_str = issue.find('h4', class_="publication-date").text.strip()  # publication date
            if date_str:
                struct_date = datetime.strptime(date_str, "%d/%m/%Y")
                issue_parsed_data['date'] = struct_date

            price = issue.find('p', class_="old-price")  # price
            if price:
                issue_parsed_data['price'] = price.text.strip()

            thmb = issue.find('img', class_="img-thumbnail img-responsive")  # issue cover
            if thmb:
                issue_parsed_data['image'] = thmb["src"]

            parsed.append(issue_parsed_data)
            desc_urls.append(issue_parsed_data['url'])

        q = self.fetch_summary_parallel(parsed)  # parses every issue's summary for the synopsis
        while not q.empty():
            self.dbm.save_to_DB(q.get()) # saves the fetched data to the database
            q.task_done()

        self.logger.debug("Items parsed: %d", len(parsed))

    def fetch_summary_parallel(self, parsed_issues):
        """
        Parallel fetch of issues synopsis
        :param parsed_issues: parsed issues
        :return: parsing result
        """
        result = Queue.Queue()
        threads = [threading.Thread(target=self.parse_issue_summary, args=(issue, result)) for issue in parsed_issues]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return result

    def parse_issue_summary(self, issue, queue):
        """
        Parses the issue summary
        :param issue: issue
        :param queue: thread queue
        :return: 
        """
        url = issue['url']
        summary = []
        try:
            opened_url = urllib2.urlopen(url, None, 145)
            page = opened_url.read()
            soup = BeautifulSoup(page, 'lxml')
            parsed_description = soup.find('div', attrs={'id': "description"})
            stripped_descr = parsed_description.text.lstrip().rstrip().split(u'\u2022')
            summary = stripped_descr[1:]

        except urllib2.HTTPError as e:
            self.logger.error('HTTPError = ' + str(e.code))
        except urllib2.URLError as e:
            self.logger.error('URLError = ' + str(e.reason))
        except httplib.HTTPException as e:
            self.logger.error('HTTPException' + str(e))
        except Exception:
            import traceback
            self.logger.error('generic exception: ' + traceback.format_exc())

        issue['summary'] = summary
        queue.put(issue)
