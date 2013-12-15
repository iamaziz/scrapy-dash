import sqlite3
import os
import urllib2
from bs4 import BeautifulSoup as bs
import requests


root_url = 'http://doc.scrapy.org/en/latest/'
output = 'scrapy.docset/Contents/Resources/Documents'
docpath = output + '/'
if not os.path.exists(docpath): os.makedirs(docpath)

data = requests.get(root_url).text
soup = bs(data)
open(os.path.join(output, 'index.html'), 'wb').write(data.encode('ascii', 'ignore'))


def update_db(name, path):
    if path.startswith('#'):
        path = 'index.html' + path
        name = path.split('#')[-1]

    # define types following based on the structure of Scrapy's documentation
    typ = 'func'
    if path.startswith('intro'):
        typ = 'Guide'
    if path.startswith('topics'):
        typ = 'Library'
    if path.split('#')[0] in ('news.html', 'contributing.html', 'versioning.html', 'faq.html'):
        typ = 'Resource'
    if path.startswith('irc:'):
        return
    if path in ('genindex.html', 'py-modindex.html', 'index.html', 'experimental.html'):
        typ = 'Package'

    # insert into db
    cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, typ, path))
    print 'DB add >> name: %s, type: %s, path: %s' % (name, typ, path)


"""
Scan all links in a given root url then download the page of each link and update database.
"""
def add_docs():
    for i, link in enumerate(soup.findAll('a')):
        name = link.text.strip()
        path = link.attrs['href'].strip()

        print "%s: " % i,

        if path.startswith("/"): path = path[1:]

        # figure out directories and create them
        if "/" in path and not "https://" in path and not "http://" in path:
            subdir = path
            folder = os.path.join(docpath)

            # split subdirs
            for i in range(len(subdir.split("/")) - 1):
                folder += subdir.split("/")[i] + "/"

            # add a directory for sub-folder(s)
            if not os.path.exists(folder): os.makedirs(folder)

        print path,

        # download docs and update db
        try:
            print " V"
            # update db with appropriate link form (code can be updated with RegExp)
            if name and not path.endswith('/') and not path.startswith('http') and not path.startswith('/'):
                update_db(name, path)

            # download html files
            urlpath = path.split('#')[0]
            url = root_url + urlpath
            res = urllib2.urlopen(url)
            doc = open(docpath + urlpath, 'wb')
            doc.write(res.read())
            doc.close()
            print "doc: ", urlpath
        except:
            print " X"
            pass


if __name__ == '__main__':

    db = sqlite3.connect('scrapy.docset/Contents/Resources/docSet.dsidx')
    cur = db.cursor()
    try:
        cur.execute('DROP TABLE searchIndex;')
    except:
        pass
    cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
    cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

    # start
    add_docs()

    # commit and close db
    db.commit()
    db.close()