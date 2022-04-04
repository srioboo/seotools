import sys
import requests
import time
import csv
import re
from bs4 import BeautifulSoup

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
        with open(f'{file_name}.csv', "a") as fopen:  # Open the csv file.
            csv_writer = csv.writer(fopen)
            csv_writer.writerow(list_input)
    except:
        return False

# Auxiliary method to print data in a formatted way
def console_print(data, value):
    print(data)
    print(f'\t{value}')
    print("")

# this get the data
# TODO rename it to a propper name
def browse_and_scrape(formatted_url, page_number=1):
    # Fetch the URL - We will be using this to append to images and info routes
    url_pat = re.compile(r"(https://*.*.*)")
    print(url_pat)
    print(formatted_url)
    source_url = url_pat.search(formatted_url)
    
    # .group(0)
    source_url = source_url.group(0)
    print(source_url)

   # Page_number from the argument gets formatted in the URL & Fetched
   # formatted_url = seed_url.format(str(page_number))

    try:
        # get session
        session = requests.Session()
        response = session.get(formatted_url)

        # get de text
        html_text = response.text

        # get de cookies
        mi_cookies = session.cookies
        cookies_dic = mi_cookies.get_dict()
        # print('cookies: ',cookies_dic)

        jsession = mi_cookies.get('JSESSIONID')
        print('')
        print('jsession: ', jsession)

        # cookies con separador
        # stdata = str.split(jsession, ':')
        # print('stdata', stdata)

        # Example google cookies
        # a_session = requests.Session()
        # a_session.get('https://google.com/')
        # session_cookies = a_session.cookies
        # cookies_dictionary = session_cookies.get_dict()
        # print('Google cookies: ',cookies_dictionary)

        # Prepare the soup
        soup = BeautifulSoup(html_text, "html.parser")
        console_print('Now Scraping:', formatted_url)

        metatitle = (soup.find('title')).get_text()
        console_print("metatile: ", metatitle)

        metadescription = soup.find('meta',attrs={'name':'description'})["content"]
        console_print("metadescription: ", metadescription)

        # robots_directives = soup.find('meta',attrs={'name':'robots'})["content"].split(",")
        # robots_directives = soup.find('meta',attrs={'name':'robots'})["content"]

        if soup.find('meta',attrs={'name':'robots'}) != None:
            robots_directives = soup.find('meta',attrs={'name':'robots'})["content"].split(",")
            console_print('Directivas robot',robots_directives)
            write_to_csv(robots_directives)
        else:
            console_print("Directivas robot", "not found")

        viewport = soup.find('meta',attrs={'name':'viewport'})["content"]
        console_print('Vieport:', viewport)

        charset = soup.find('meta',attrs={'charset':True})["charset"]
        console_print('Charset: ', charset)

        html_language = soup.find('html')["lang"]
        console_print('Html language: ', html_language)

        if soup.find('link',attrs={'rel':'canonical'}) != None:
            canonical = soup.find('link',attrs={'rel':'canonical'})["href"]
            console_print('Canonical: ', canonical)
        else:
            console_print('Canonical: ', 'not found')

        list_hreflangs = [[a['href'], a["hreflang"]] for a in soup.find_all('link', href=True, hreflang=True)]
        console_print('Hreflangs: ', list_hreflangs)

        if soup.find('link',attrs={'media':'only screen and (max-width: 640px)'}) != None:
            mobile_alternate = soup.find('link',attrs={'media':'only screen and (max-width: 640px)'})["href"]
            console_print('Mobile alternate: ', mobile_alternate)
        else:    
            console_print('Mobile alternate: ', 'not found')

        # This if clause stops the script when it hits an empty page
        if soup.find("hreflang", class_="next") != None:
            # scrape(formatted_url, soup)     # Invoke the scrape function
            # Be a responsible citizen by waiting before you hit again
            time.sleep(3)
            # page_number += 1
            # Recursively invoke the same function with the increment
            # browse_and_scrape(seed_url, page_number)
        else:
            print("Entering scrape")
            scrape(formatted_url, soup)     # The script exits here
            return True
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