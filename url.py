import urllib2
from BeautifulSoup import BeautifulSoup

import re


reps = {'&#039;' :'\''}
exp = re.compile('(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?')


def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text

def get_url(str):
        m = exp.search(str)
        if m is not None:
            return str[m.start():m.end()]
        else:
            return None

def get_title(str):
    req = urllib2.Request(str, headers={'User-Agent' : "Pybot URL Title Grabber"})   
    try:
        source = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        print e.code
        return None
    else:
        headers = source.info().headers
        if not any('image' in s for s in headers):
            bs = BeautifulSoup(source)
            title = ' '.join(bs.title.string.split())
            title = replace_all(title, reps)
            return title
