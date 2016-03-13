from gevent import monkey; monkey.patch_all()
import gevent
import urllib2

class IFakeSyncCall(object):
    def __init__(self):
        super(IFakeSyncCall, self).__init__()
        self.generators = {}
 
    @staticmethod
    def FAKE_SYNCALL():
        def fwrap(method):
            def fakeSyncCall(instance, *args, **kwargs):
                instance.generators[method.__name__] = method(instance, *args, **kwargs) #list
                func, args = instance.generators[method.__name__].next()
                func(*args)
            return fakeSyncCall
        return fwrap
 
    def onFakeSyncCall(self, identify, result):
        try:
            func, args = self.generators[identify].send(result)
            func(*args)
        except StopIteration:
            self.generators.pop(identify)


import random
 

class Player(object):
    def __init__(self, entityId, url):
        super(Player, self).__init__()
        self.entityId = entityId
        self.url = url
 
    def onFubenEnd(self, mailBox):
        score = self.getPlayerData()
        print "onFubenEnd player %s:%d score %d"%(self.url, self.entityId, score)
        mailBox.onFakeSyncCall('evalFubenScore', (self.url, self.entityId, score))
    
    def getPlayerData(self):
        resp = urllib2.urlopen(self.url)
        data = resp.read()
        return len(data)

class FubenStub(IFakeSyncCall):
    def __init__(self, players):
        super(FubenStub, self).__init__()
        self.players = players
 
    @IFakeSyncCall.FAKE_SYNCALL()
    def evalFubenScore(self):
        totalScore = 0
        for player in self.players:
            url, entityId, score = yield (player.onFubenEnd, (self,))
            print "onEvalFubenScore player %s:%d score %d"%(url, entityId, score)
            totalScore += score
 
        print 'the totalScore is %d'%totalScore
 
if __name__ == '__main__':
    players_baidu = [Player(i, "https://www.baidu.com") for i in xrange(3)]
    fb1 = FubenStub(players_baidu)
    
    players_taobao = [Player(i, "https://www.taobao.com") for i in xrange(3)]
    fb2 = FubenStub(players_taobao)

    players_ths = [Player(i, "https://www.10jqka.com") for i in xrange(3)]
    fb3 = FubenStub(players_ths)

    gevent.joinall([
            gevent.spawn(fb1.evalFubenScore),
            gevent.spawn(fb2.evalFubenScore),
            #gevent.spawn(fb3.evalFubenScore),
    ])
    