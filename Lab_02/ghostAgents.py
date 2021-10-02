from game import Agent
import util

class GhostAgent( Agent ):
    def __init__( self, index ):
        super().__init__(index)
        self.index = index

    def getAction(self, state):
        dist = self.getDistribution(state)
        return util.chooseFromDistribution(dist)

    def getDistribution(self, state):
        
        util.raiseNotDefined()

class RandomGhost( GhostAgent ):

    def getDistribution( self, state ):
        dist = util.Counter()
        for a in state.getLegalActions( self.index ): dist[a] = 1.0
        dist.normalize()
        return dist
