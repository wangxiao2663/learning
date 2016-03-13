# -*- coding: utf-8 -*-
import random
 
# 玩家实体类
class Player(object):
    def __init__(self, entityId):
        super(Player, self).__init__()
        # 玩家标识
        self.entityId = entityId
 
    def onFubenEnd(self, mailBox):
        score = random.randint(1, 10)
        print "onFubenEnd player %d score %d"%(self.entityId, score)
 
        # 向副本管理进程发送自己的id和战斗信息
        mailBox.onEvalFubenScore(self.entityId, score)
 
# 副本管理类
class FubenStub(object):
    def __init__(self, players):
        super(FubenStub, self).__init__()
        self.players = players
 
    def evalFubenScore(self):
        self.playerRelayCnt = 0
        self.totalScore = 0
 
        # 通知每个注册的玩家，副本已经结束，索取战斗信息
        for player in self.players:
            player.onFubenEnd(self)
 
    def onEvalFubenScore(self, entityId, score):
        # 收到其中一个玩家的战斗信息
        print "onEvalFubenScore player %d score %d"%(entityId, score)
        self.playerRelayCnt += 1
        self.totalScore += score
 
        # 当收集完所有玩家的信息后，打印评分
        if len(self.players) == self.playerRelayCnt:
            print 'The fuben totalScore is %d'%self.totalScore
 
if __name__ == '__main__':
    # 模拟创建玩家实体
    players = [Player(i) for i in xrange(3)]
 
    # 副本开始时，每个玩家将自己的MailBox注册到副本管理进程
    fs = FubenStub(players)
 
    # 副本进行中
    # ....
 
    # 副本结束，开始评分
    fs.evalFubenScore()