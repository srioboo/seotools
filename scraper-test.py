import sys
import cloudscraper
from bs4 import BeautifulSoup
 
# print('Number of arguments:', len(sys.argv), 'arguments.')
# print('Argument List:', str(sys.argv))

if len(sys.argv) == 2:
    url = sys.argv[1]
else:
    url = 'https://salrion.netlify.app'

# crea el scrapper
scraper = cloudscraper.create_scraper() 
 
# obtien la url y la parsea
html = scraper.get(url)
soup = BeautifulSoup(html.text, 'lxml')

# obtiene los datos e imprime en consola
metatitle = (soup.find('title')).get_text()
print(metatitle)