from InputData import *

class OutputNode(DataNode):
    def __init__(self, dataNode):
        super().__init__(dataNode.Id, dataNode.X, dataNode.Y, dataNode.Score)
        self.Position = -1
        self.Times = dataNode.Times
        
class Solution:
    def __init__(self, solutionNodes, sequence):
        self.OutputNodes = {}
        # Sobald eine Node sich in einer Tour befindet, wird diese zur Output Node
        for node in solutionNodes:
            self.OutputNodes[node.Id] = OutputNode(node)
        self.Sequence = sequence
        self.TotalScore = -1
        self.TotalTime = -1

    def __str__(self):
        #da Startknoten nicht in Lösungen hinzugefügt wird, muss er Extra erwähnt werden
        return f"Sequence {[1]+ self.Sequence +[1]} collects {self.TotalScore} score points in {self.TotalTime} time units"

class SolutionPool:
    def __init__(self):
        self.Solutions = []

    def AddSolution(self, newSolution):
        self.Solutions.append(newSolution)

    def GetHighestTotalScoreSolution(self):
        #complex sort: sorts are stable -> multiple records have the same key, their original order is preserved
        # sort solutions ascending by TotalTime
        self.Solutions.sort(key = lambda solution: solution.TotalTime, reverse=False)
        # sort solutions descending TotalScore
        self.Solutions.sort(key = lambda solution: solution.TotalScore, reverse=True)

        return self.Solutions[0]