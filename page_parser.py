import httplib
import logging
import logging.config
import urllib2
import Queue
import threading
from datetime import datetime

from bs4 import BeautifulSoup

from db_manager import DbManager


class Parsatore():
    def __init__(self, min_pages, max_pages):
        self.dbm = DbManager()
        # logging.config.fileConfig('logging.conf')
        # create logger
        self.logger = logging.getLogger(__name__)
        self.urls_to_load = []
        # max_pages = 6
        # min_pages = 4
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
            self.logger.error('HTTPException')
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
        uscite = soup.find_all('div', attrs={'class': "list-group-item"})

        for uscita in uscite:
            # dizionario contenente tutti i valori da salvare nell'oggetto Issue sul DB
            diz = {}

            # ottiene titolo e url della pagina per ritorvare la Sinossi
            title = uscita.find('h3', class_="product-name").find('a')
            diz['title'] = " ".join(title.get_text().split())
            diz['url'] = str(title.get('href'))
            # self.logger.debug("Getting description of: " + diz['title'])
            # diz['desc'] = self.parse_description(diz['url'])

            subtitle = uscita.find('h3', class_="product-name").find('small', attrs={"class": "subtitle"})
            if subtitle:
                diz['subtitle'] = " ".join(subtitle.text.split())

            serie = uscita.find('h3', class_="product-name").find('small', attrs={"class": "serie"})
            if serie:
                diz['serie'] = " ".join(serie.text.split())
            else:
                diz['serie'] = "One Shot"

            ristampa = uscita.find('h5', attrs={"class": "reprint"})
            if ristampa:
                diz['ristampa'] = " ".join(ristampa.text.split())

            data_str = uscita.find('h4', class_="publication-date").text.strip()
            struct_date = datetime.strptime(data_str, "%d/%m/%Y")
            diz['data'] = struct_date
            diz['prezzo'] = uscita.find('p', class_="old-price").text.strip()
            thmb = uscita.find('img', class_="img-thumbnail img-responsive")
            diz['image'] = thmb["src"]
            parsed.append(diz)
            desc_urls.append(diz['url'])

        q = self.fetch_desc_parallel(parsed)
        while not q.empty():  # check that the queue isn't empty
            self.dbm.save_to_DB(q.get())
            q.task_done()  # specify that you are done with the item

        self.logger.debug("Items parsed: %d", len(parsed))

    def parse_description(self, item, queue):
        url = item['url']
        desc = []
        try:
            result = urllib2.urlopen(url, None, 145)
            page = result.read()
            soup = BeautifulSoup(page, 'lxml')
            parsed_description = soup.find('div', attrs={'id': "description"})
            stripped_descr = parsed_description.text.lstrip().rstrip().split(u'\u2022')
            desc = stripped_descr[1:]

        except urllib2.HTTPError as e:
            self.logger.error('HTTPError = ' + str(e.code))
        except urllib2.URLError as e:
            self.logger.error('URLError = ' + str(e.reason))
        except httplib.HTTPException as e:
            self.logger.error('HTTPException' + str(e.reason))
        except Exception:
            import traceback
            self.logger.error('generic exception: ' + traceback.format_exc())

        item['desc'] = desc
        queue.put(item)

    def fetch_desc_parallel(self, parsed_items):
        result = Queue.Queue()
        threads = [threading.Thread(target=self.parse_description, args=(item, result)) for item in parsed_items]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return result
