import urllib2
from datetime import datetime
from bs4 import BeautifulSoup
import logging.config, logging





# import sys
#
# reload(sys)
# sys.setdefaultencoding('utf8')

class Parsatore():
    def __init__(self):
        logging.config.fileConfig('logging.conf')
        # create logger
        self.logger = logging.getLogger(__name__)

        self.urls = [
            'http://comics.panini.it/store/pub_ita_it/magazines/cmc-m.html?limit=25&p=1',
            'http://comics.panini.it/store/pub_ita_it/magazines/cmc-m.html?limit=25&p=2',
            'http://comics.panini.it/store/pub_ita_it/magazines/cmc-m.html?limit=25&p=3',
            'http://comics.panini.it/store/pub_ita_it/magazines/cmc-m.html?limit=25&p=4',
            'http://comics.panini.it/store/pub_ita_it/magazines/cmc-m.html?limit=25&p=5',
            'http://comics.panini.it/store/pub_ita_it/magazines/cmc-m.html?limit=25&p=6',
            'http://comics.panini.it/store/pub_ita_it/magazines/cmc-m.html?limit=25&p=7',
            'http://comics.panini.it/store/pub_ita_it/magazines/cmc-m.html?limit=25&p=8'
        ]

    def parser(self):
        parsed = []
        for url in self.urls:
            try:
                result = urllib2.urlopen(url, None, 45)
                page = result.read()
                soup = BeautifulSoup(page, 'lxml')

                uscite = soup.find_all('div', attrs={'class': "list-group-item"})

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
                    self.logger.debug("parsed issue:" + diz['title'])
            except urllib2.URLError:
                self.logger.exception('Caught exception fetching url')
        self.logger.debug("Items parsed: %d", len(parsed))
        return parsed
