# filmfile.py

import urllib2
import json
import urllib
from google.appengine.api import urlfetch

CACHE = {}
# tquery = "http://rottentomatoes.com/m/"
imdbapi = "http://www.myapifilms.com/imdb?title="
# tdata = 'twitter:data1" content="'
# tdata2 = 'twitter:data2" content="'
# tlen = len(tdata)+3
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11' +
       '(KHTML) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;' +
       'q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}


def mycapitalizer(m):
    return m.group(1) + m.group(2).upper()


def white_to_underscore(q):
    newq = q.replace(" ", "_")
    # newerq = re.sub("(^|\s)(\S)", mycapitalizer, q)
    return newq


def dash_to_underscore(query):
    newq = query.replace("-", "_")
    return newq


def remove_apostr(astring):
    newstring = astring.replace("'", "")
    return newstring


def remove_colon(astring):
    newstring = astring.replace(":", "")
    return newstring


def remove_comma(astring):
    newstring = astring.replace(",", "")
    return newstring


def remove_the(astring):
    if astring[:4] == 'The ' or astring[:4] == 'the ':
        return astring[4:]
    else:
        return astring


def make_req(query, headers):
    req = urllib2.Request(query, headers=headers)
    try:
        page = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        pass
    return page


def set_fetch_timeout(ms):
    urlfetch.set_default_fetch_deadline(ms)
    return


def tomatoify_query(query, nothe=True):
    if nothe:
        query = remove_the(query)
    q = remove_apostr(query)
    newq = remove_colon(q)
    newquery = white_to_underscore(newq)
    q = dash_to_underscore(newquery)
    newq = remove_comma(q)
    return newq
#
# def get_tomatoes(query, nothe=True):
#     tomatoed = tomatoify_query(query, nothe)
#     tq = tquery + tomatoed
#     try:
#         page = make_req(tq, hdr).read()
#         tindex = page.find(tdata)
#         tindex2 = page.find(tdata2)
#         tcont = page[tindex:tindex+tlen]
#         tcontent2 = page[tindex2:tindex2+tlen]
#         tomatoes = [tcont[(len(tcont) - 3):], tcontent2[(len(tcont) - 3):]]
#         return tomatoes
#     except UnboundLocalError:
#         pass


def extract_plot_from_json(filmjson):
    info = json.loads(filmjson)
    if type(info) == list:
        # print type(info)
        return info[0]['plot']
    else:
        return 'not found'


def query_film_api(query):
    url = imdbapi + urllib.quote(query)
    page = make_req(url, hdr).read()
    return page


def get_film_json(query):
    plot = query_film_api(query)
    if not plot:
        pass
    else:
        return plot


def get_film_info(query):
    a = get_film_json(query)
    return extract_plot_from_json(a)


def tomato_proxy():
    return "99"


def check_cache(query):
    if query not in CACHE:
        CACHE[query] = (tomato_proxy(), get_film_info(query))
        # CACHE[query] = (get_tomatoes(query, nothe), get_film_info(query))
        return CACHE[query]
    else:
        return CACHE[query]
