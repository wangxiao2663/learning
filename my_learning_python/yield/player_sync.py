import random
 
class Player(object):
    def __init__(self, entityId):
        super(Player, self).__init__()
        self.entityId = entityId
 
    def onFubenEnd(self, mailBox):
        score = random.randint(1, 10)
        print "onFubenEnd player %d score %d"%(self.entityId, score)
        return self.entityId, score
 
class FubenStub(object):
    def __init__(self, players):
        super(FubenStub, self).__init__()
        self.players = players
 
    def evalFubenScore(self):
        totalScore = 0
        for player in self.players:
            entityId, score = player.onFubenEnd(self)
            print "onEvalFubenScore player %d score %d"%(entityId, score)
            totalScore += score
 
        print 'The fuben totalScore is %d'%totalScore
 
if __name__ == '__main__':
    players = [Player(i) for i in xrange(3)]
 
    fs = FubenStub(players)
    fs.evalFubenScore()