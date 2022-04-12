import sys
import requests
import time
import csv
import re
from bs4 import BeautifulSoup

def scrape_menu(soup, base_url='', language=''):
    # categories
    # categories = soup.find(id='menu_')
    categories = soup.select("a[class^='menu_']")

    # file namess
    csv_menu_file = 'data_menu' + '_' + base_url + '_' + language
    csv_url_file = 'data_url' + '_' + base_url + '_' + language

    for cat in categories:
        url = cat['href']
        catnum = cat['id']
        catid = cat['data-catid']

        write_to_csv([catid,catnum,url], csv_menu_file)
        write_to_csv([url], csv_url_file)
    log('Categories tree: ', len(categories))

# this is an example to scrape a book
def scrape(source_url, soup):  # Takes the driver and the subdomain for concats as params
    # Find the elements of the article tag
    books = soup.find_all("article", class_="product_pod")

    # Iterate over each book article tag
    for each_book in books:
        info_url = source_url+"/"+each_book.h2.find("a")["href"]
        cover_url = source_url+"/catalogue" + each_book.a.img["src"].replace("..", "")

        title = each_book.h2.find("a")["title"]
        rating = each_book.find("p", class_="star-rating")["class"][1]
        # can also be written as : each_book.h2.find("a").get("title")
        price = each_book.find("p", class_="price_color").text.strip().encode(
            "ascii", "ignore").decode("ascii")
        availability = each_book.find(
            "p", class_="instock availability").text.strip()

        # Invoke the write_to_csv function
        write_to_csv([info_url, cover_url, title, rating, price, availability])

# write data to csv
def write_to_csv(list_input, file_name='data'):
    # The scraped info will be written to a CSV here.
    try:
        with open(f'{file_name}.csv', "a", encoding='UTF8', newline='') as fopen:  # Open the csv file.
            csv_writer = csv.writer(fopen)
            csv_writer.writerow(list_input)
    except:
        return False

# Auxiliary method to print data in a formatted way
def log(data, value):
    print(data)
    print(f'\t{value}')
    print("")

# get head metadata
def get_head_metadata(soup):

    # get title
    metatitle = (soup.find('title')).get_text()
    log("metatile: ", metatitle)

    # get metadescription
    metadescription = soup.find('meta',attrs={'name':'description'})["content"]
    log("metadescription: ", metadescription)

    # get metarobots
    if soup.find('meta',attrs={'name':'robots'}) != None:
        robots_directives = soup.find('meta',attrs={'name':'robots'})["content"].split(",")
        log('Directivas robot',robots_directives)
        write_to_csv(robots_directives)
    else:
        log("Directivas robot", "not found")

    # get viewport
    viewport = soup.find('meta',attrs={'name':'viewport'})["content"]
    log('Vieport:', viewport)

    # get charset
    charset = soup.find('meta',attrs={'charset':True})["charset"]
    log('Charset: ', charset)

# get canonical and hreflang
def get_canonical(soup):
    
    # canonical
    if soup.find('link',attrs={'rel':'canonical'}) != None:
        canonical = soup.find('link',attrs={'rel':'canonical'})["href"]
        log('Canonical: ', canonical)
    else:
        log('Canonical: ', 'not found')

# get canonical and hreflang
def get_hreflang(soup):
    # hreflang
    list_hreflangs = [[a['href'], a["hreflang"]] for a in soup.find_all('link', href=True, hreflang=True)]
    # log('Hreflangs: ', list_hreflangs)
    return list_hreflangs

# get language
def get_lang(soup):
    html_language = soup.find('html')["lang"]
    log('Html language: ', html_language)

# get media
def get_media(soup):
    if soup.find('link',attrs={'media':'only screen and (max-width: 640px)'}) != None:
        mobile_alternate = soup.find('link',attrs={'media':'only screen and (max-width: 640px)'})["href"]
        log('Mobile alternate: ', mobile_alternate)
    else:    
        log('Mobile alternate: ', 'not found')

# alter cookies
def alter_cookie(session, node):
    # get de cookies
    mi_cookies = session.cookies
    cookies_dic = mi_cookies.get_dict()
    # log('cookies: ',cookies_dic)

    # get searched cookie
    jsession = mi_cookies.get('JSESSIONID')
    # log('jsession: ', jsession)

    jsession_arr = jsession.split(':')

    # for i in range(len(nodes_arr)):
    jsession_alt = jsession.replace(':' + jsession_arr[1], ':' + node)
    print('jsession_new: ', jsession_alt)

    session.cookies.set('JSESSIONID', jsession_alt, domain='www.midomain.com')

    # Example google cookies
    # a_session = requests.Session()
    # a_session.get('https://google.com/')
    # session_cookies = a_session.cookies
    # cookies_dictionary = session_cookies.get_dict()
    # print('Google cookies: ',cookies_dictionary)

# this get the data
# TODO rename it to a propper name
def browse_and_scrape(formatted_url, page_number=1):

    # nodes
    nodes_arr = ['c1pro01','c1pro02','c1pro03','c1pro04','c2pro01','c2pro02','c2pro03','c2pro04']

    try:
        # get session
        session = requests.Session()
        response = session.get(formatted_url)
        
        # get head metadata
        # get_head_metadata(soup)

        # get canonical
        # get_canonical(soup)

        
        # get language
        # get_lang(soup)

        # get media
        # get_media(soup)

        # alter cookies
        for i in range(len(nodes_arr)):
            alter_cookie(session, nodes_arr[i])

            # after alter session get data and get text
            response = session.get(formatted_url)
            # get de text
            html_text = response.text

            # Prepare the soup
            soup = BeautifulSoup(html_text, "html.parser")
            # log('Now Scraping:', formatted_url)

            # get canonical and hreflang
            list_hreflangs = get_hreflang(soup)
            # log('Hreflangs: ', list_hreflangs)

            # hreflang loop
            # for x in list_hreflangs:
            #    print(str(x))

            # Be a responsible citizen by waiting before you hit again
            time.sleep(3)

            # scrape menu data
            scrape_menu(soup)

        return True
    except Exception as e:
        print(e)
        return e

if __name__ == "__main__":
    if len(sys.argv) == 2:
        # print(sys.argv[1])
        seed_url = sys.argv[1]
    else:
        seed_url = 'https://salrion.netlify.app'

    for argument in sys.argv:
        # recorrer los argumentos
        print(argument)

    print("Web scraping has begun")
    result = browse_and_scrape(seed_url)
    if result == True:
        print("Web scraping is now complete!")
    else:
        print(f"Oops, That doesn't seem right!!! - {result}")                        