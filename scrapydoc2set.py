#!/usr/local/bin/python

import sqlite3
import urllib2
from bs4 import BeautifulSoup

db = sqlite3.connect('scrapy.docset/Contents/Resources/docSet.dsidx')
cur = db.cursor()

try: cur.execute('DROP TABLE searchIndex;')
except: pass

cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

url = 'http://doc.scrapy.org/en/latest/'
page = urllib2.urlopen(url)
soup = BeautifulSoup(page)

# add documentation functions to db
for tag in soup.find_all('a'):
    name = tag.string
    path = tag.get('href')

    if name or path in url:
        if path.split('#')[0] not in ('versioning.html', 'contributing.html'):
            cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, 'func', path))
            # clean up the mess
            cur.execute("delete from searchIndex where name = ' Edit on GitHub';")
            cur.execute("delete from searchIndex where name like '0.%';")
            cur.execute("delete from searchIndex where name = '#scrapy IRC channel';")
            cur.execute("delete from searchIndex where name = ' Scrapy';")

            print 'name: %s, path: %s' % (name, path)

db.commit()
db.close()
