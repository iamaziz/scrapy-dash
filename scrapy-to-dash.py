import requests, sqlite3, os, urllib
from bs4 import BeautifulSoup as bs


# download html documentation
cmdcommand = """ cd . && rm -rf Scrapy.docset && mkdir -p Scrapy.docset/Contents/Resources/Documents && cd Scrapy.docset && httrack -%v2 -T60 -R99 --sockets=7 -%c1000 -c10 -A999999999 -%N0 --disable-security-limits -F 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.19 (KHTML, like Gecko) Ubuntu/11.10 Chromium/18.0.1025.168' --mirror --keep-alive --robots=0 "http://doc.scrapy.org/en/latest/" -n -* +*.css +*css.php +*.ico +*/fonts/* +*.svg +*.ttf +fonts.googleapis.com* +*.woff +*.eot +*.png +*.jpg +*.gif +*.jpeg +*.js +http://doc.scrapy.org/en/latest/* -github.com* +raw.github.com* && rm -rf hts-* && mkdir -p Contents/Resources/Documents && mv -f *.* Contents/Resources/Documents/
 """
os.system(cmdcommand)



# CONFIGURATION
docset_name = 'Scrapy.docset'
output = docset_name + '/Contents/Resources/Documents/'

# create docset directory
if not os.path.exists(output): os.makedirs(output)

# add icon
icon = 'http://upload.wikimedia.org/wikipedia/commons/7/7f/Smile_icon.png'
urllib.urlretrieve(icon, docset_name + "/icon.png")


def update_db(name, typ, path):

	try:
	  cur.execute("SELECT rowid FROM searchIndex WHERE path = ?", (path,))
	  dbpath = cur.fetchone()
	  cur.execute("SELECT rowid FROM searchIndex WHERE name = ?", (name,))
	  dbname = cur.fetchone()

	  if dbpath is None and dbname is None:
	      cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, typ, path))
	      print('DB add >> name: {0} | type: {1} | path: {3}'.format(name, typ, path))
	  else:
	      print("record exists")
	except:
		pass


def add_urls():

  # index pages
  pages = {
    'Section'       : 'http://doc.scrapy.org/en/latest/',
    'func'          : 'http://doc.scrapy.org/en/latest/genindex.html',
    'Command'       : 'http://doc.scrapy.org/en/latest/topics/commands.html',
    'Module'        : 'http://doc.scrapy.org/en/latest/py-modindex.html',
      }

  # loop through index pages:
  for p in pages:
    base_path = 'doc.scrapy.org/en/latest/'
    typ = p
    # soup each index page
    html = requests.get(pages[p]).text
    soup = bs(html)
    
    for a in soup.findAll('a'):
      name = a.text.strip()
      name = name.replace('\n', '')

      if len(name) > 2:
        path = a.get('href')
        
        filtered = ('index.html', 'http', '//', 'irc:', 'spiders.html', 'benchmarking.html', 'shell.html')
        dirpath = ['Command']

        if '#' in path and len(path) > 2 and not path.startswith(filtered):
          if typ in dirpath:
            base_path = pages[p].replace('http://','')
          path = base_path + path
          update_db(name, typ, path)


def add_infoplist():
  name = docset_name.split('.')[0]
  info = " <?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
         "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\"> " \
         "<plist version=\"1.0\"> " \
         "<dict> " \
         "    <key>CFBundleIdentifier</key> " \
         "    <string>{0}</string> " \
         "    <key>CFBundleName</key> " \
         "    <string>{1}</string>" \
         "    <key>DocSetPlatformFamily</key>" \
         "    <string>{2}</string>" \
         "    <key>isDashDocset</key>" \
         "    <true/>" \
         "    <key>isJavaScriptEnabled</key>" \
         "    <true/>" \
         "    <key>dashIndexFilePath</key>" \
         "    <string>{3}</string>" \
         "</dict>" \
         "</plist>".format(name, name, name, 'doc.scrapy.org/en/latest/' + 'index.html')
  open(docset_name + '/Contents/info.plist', 'wb').write(info)

# create and connect to SQLite
db = sqlite3.connect(docset_name + '/Contents/Resources/docSet.dsidx')
cur = db.cursor()
try:
    cur.execute('DROP TABLE searchIndex;')
except:
    pass
    cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
    cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

# start
add_urls()
add_infoplist()

# commit and close db
db.commit()
db.close()
