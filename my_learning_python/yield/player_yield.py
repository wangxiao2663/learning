
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
    def __init__(self, entityId):
        super(Player, self).__init__()
        self.entityId = entityId
 
    def onFubenEnd(self, mailBox):
        score = random.randint(1, 10)
        print "onFubenEnd player %d score %d"%(self.entityId, score)
        mailBox.onFakeSyncCall('evalFubenScore', (self.entityId, score))
 
class FubenStub(IFakeSyncCall):
    def __init__(self, players):
        super(FubenStub, self).__init__()
        self.players = players
 
    @IFakeSyncCall.FAKE_SYNCALL()
    def evalFubenScore(self):
        totalScore = 0
        for player in self.players:
            entityId, score = yield (player.onFubenEnd, (self,))
            print "onEvalFubenScore player %d score %d"%(entityId, score)
            totalScore += score
 
        print 'the totalScore is %d'%totalScore
 
if __name__ == '__main__':
    players = [Player(i) for i in xrange(3)]
 
    fs = FubenStub(players)
    fs.evalFubenScore()

    