import urllib2
import httplib
import logging.config
import logging
from dbmanager import DbManager
from datetime import datetime
from bs4 import BeautifulSoup


class Parsatore():
    def __init__(self, min_pages, max_pages):
        self.dbm = DbManager()
        # logging.config.fileConfig('logging.conf')
        # create logger
        self.logger = logging.getLogger(__name__)
        self.urls = []
        # max_pages = 6
        # min_pages = 4
        for i in range(min_pages, max_pages):
            self.urls.append('http://comics.panini.it/store/pub_ita_it/magazines/cmc-m.html?limit=25&p=%d' % i)

    def parser(self):
        # lista elementi parsati
        for url in self.urls:
            parsed = []
            try:
                self.logger.debug("parsing URL " + url)
                result = urllib2.urlopen(url, None, 60)
                page = result.read()
                soup = BeautifulSoup(page, 'lxml')
                # lettra di tutti gli elementi div della lista delle uscite
                uscite = soup.find_all('div', attrs={'class': "list-group-item"})

                for uscita in uscite:
                    # dizionario contenente tutti i valori da salvare nell'oggetto Issue sul DB
                    diz = {}

                    # ottiene titolo e url della pagina per ritorvare la Sinossi
                    title = uscita.find('h3', class_="product-name").find('a')
                    diz['title'] = " ".join(title.get_text().split())
                    diz['url'] = str(title.get('href'))
                    # self.logger.debug("Getting description of: " + diz['title'])
                    diz['desc'] = self.parse_description(diz['url'])

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
                    parsed.append(diz)

                    thmb = uscita.find('img', class_="img-thumbnail img-responsive")
                    diz['image'] = thmb["src"]
                    # self.logger.debug("parsed issue:" + diz['title'])
            except urllib2.URLError:
                self.logger.exception('Caught exception fetching url')

            self.dbm.save_to_DB(parsed)
            self.logger.debug("Items parsed: %d", len(parsed))
            # return parsed

    def parse_description(self, url):
        result = None
        try:
            result = urllib2.urlopen(url, None, 145)
            page = result.read()
            soup = BeautifulSoup(page, 'lxml')
            descr = soup.find('div', attrs={'id': "description"})
            str = descr.text.lstrip().rstrip().split(u'\u2022')
            # self.logger.debug(str)
            return str[1:]

        except urllib2.HTTPError as e:
            self.logger.error('HTTPError = ' + str(e.code))
            return "#"
        except urllib2.URLError as e:
            self.logger.error('URLError = ' + str(e.reason))
            return "#"
        except httplib.HTTPException as e:
            self.logger.error('HTTPException')
            return "#"
        except Exception:
            import traceback
            self.logger.error('generic exception: ' + traceback.format_exc())
            return "#"
