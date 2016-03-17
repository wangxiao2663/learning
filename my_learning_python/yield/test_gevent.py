from gevent import monkey; monkey.patch_all()
import gevent
import urllib2

def f(url):
    print('GET: %s' % url)
    resp = urllib2.urlopen(url)
    data = resp.read()
    print('%d bytes received from %s.' % (len(data), url))

gevent.joinall([
        gevent.spawn(f, 'https://www.baidu.com/'),
        gevent.spawn(f, 'https://www.taobao.com/'),
        #gevent.spawn(f, 'https://www.10jqka.com/'),
])
