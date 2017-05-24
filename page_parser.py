import Queue
import httplib
import logging
import logging.config
import threading
import urllib2
from datetime import datetime

from bs4 import BeautifulSoup

from managers.db_manager import DB_manager


class Parsatore():
    def __init__(self, min_pages, max_pages):
        self.dbm = DB_manager()
        # logging.config.fileConfig('logging.conf')
        # create logger
        self.logger = logging.getLogger(__name__)
        self.urls_to_load = []
        for i in range(min_pages, max_pages):
            self.urls_to_load.append('http://comics.panini.it/store/pub_ita_it/magazines/cmc-m.html?limit=25&p=%d' % i)

        q = self.fetch_parallel(self.urls_to_load)
        while not q.empty():  # check that the queue isn't empty
            self.page_parser(q.get())
            q.task_done()  # specify that you are done with the item

    def read_url(self, url, queue):
        try:
            data = urllib2.urlopen(url).read()
            print('Fetched %s from %s' % (len(data), url))
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
        result = Queue.Queue()
        threads = [threading.Thread(target=self.read_url, args=(url, result)) for url in urls_to_load]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return result

    def page_parser(self, page):
        # lista elementi parsati
        parsed = []
        desc_urls = []
        soup = BeautifulSoup(page, 'lxml')
        # lettura di tutti gli elementi div della lista delle uscite
        issues = soup.find_all('div', attrs={'class': "list-group-item"})

        for issue in issues:
            # dizionario contenente tutti i valori da salvare nell'oggetto Issue sul DB
            dic = {}

            # ottiene titolo e url della pagina per ritorvare la Sinossi
            title = issue.find('h3', class_="product-name").find('a')
            dic['title'] = " ".join(title.get_text().split())
            dic['url'] = str(title.get('href'))

            subtitle = issue.find('h3', class_="product-name").find('small', attrs={"class": "subtitle"})
            if subtitle:
                dic['subtitle'] = " ".join(subtitle.text.split())

            series = issue.find('h3', class_="product-name").find('small', attrs={"class": "serie"})
            if series:
                dic['series'] = " ".join(series.text.split())
            else:
                dic['series'] = "One Shot"

            reprint = issue.find('h5', attrs={"class": "reprint"})
            if reprint:
                dic['reprint'] = " ".join(reprint.text.split())

            date_str = issue.find('h4', class_="publication-date").text.strip()
            if date_str:
                struct_date = datetime.strptime(date_str, "%d/%m/%Y")
                dic['date'] = struct_date

            price = issue.find('p', class_="old-price")
            if price:
                dic['price'] = price.text.strip()

            thmb = issue.find('img', class_="img-thumbnail img-responsive")
            if thmb:
                dic['image'] = thmb["src"]

            parsed.append(dic)
            desc_urls.append(dic['url'])

        q = self.fetch_summary_parallel(parsed)
        while not q.empty():  # check that the queue isn't empty
            self.dbm.save_to_DB(q.get())
            q.task_done()  # specify that you are done with the item

        self.logger.debug("Items parsed: %d", len(parsed))

    def parse_issue_summary(self, item, queue):
        url = item['url']
        summary = []
        try:
            result = urllib2.urlopen(url, None, 145)
            page = result.read()
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

        item['summary'] = summary
        queue.put(item)

    def fetch_summary_parallel(self, parsed_items):
        result = Queue.Queue()
        threads = [threading.Thread(target=self.parse_issue_summary, args=(item, result)) for item in parsed_items]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return result
