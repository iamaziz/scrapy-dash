import os
import urllib2
from bs4 import BeautifulSoup
import requests

root_url = 'http://doc.scrapy.org/en/latest/'
data = requests.get(root_url).text
soup = BeautifulSoup(data)

# get the documentation links
page_ids = []
for link in soup.find_all('a'):
    page_ids.append(link.get('href'))

docpath = 'scrapy.docset/Contents/Resources/Documents'

"""
download scrapy dodumenation from the linked urls
"""
def scrape_page(page_id):
    try:
        url = root_url + page_id
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page)

        if page_id.startswith("/"): page_id = page_id[1:]

        # figure out directories and create them
        if "/" in page_id and not "https://" in page_id and not "http://" in page_id:
            subdir = page_id
            folder = os.path.join(docpath, '')

            # split subdirs
            for i in range(len(subdir.split("/")) - 1):
                folder += subdir.split("/")[i] + "/"

            # create a directory of sub-folder(s)
            if not os.path.exists(folder):
                os.makedirs(folder)
            print folder

        html = page_id
        open(os.path.join(docpath, html), 'wb').write(soup.prettify().encode('ascii', 'ignore'))

    except:
        pass

if __name__ == '__main__':
    for page_id in page_ids:
        scrape_page(page_id)
