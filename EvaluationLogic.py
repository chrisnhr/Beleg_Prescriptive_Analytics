from InputData import *
from OutputData import *

class EvaluationLogic:
    def __init__(self, inputData):
        self.InputData = inputData

    def __init__(self, inputData):
        self.InputData = inputData
    
    def DefineTotalValues(self, currentSolution):
        total_score = 0
        total_time = 0

        # einfache Summe aller Scores in der Lösung
        for key in currentSolution.OutputNodes.keys():
            total_score += currentSolution.OutputNodes[key].Score
        
        #Entfernung Depot-"erster Knoten"
        total_time += currentSolution.OutputNodes[currentSolution.Sequence[0]].Times[0]
        #Entfernung Depot-"letzter Knoten"
        total_time += currentSolution.OutputNodes[currentSolution.Sequence[-1]].Times[0]
        # if total_time >= self.InputData.TimeLimit:
        #     raise Exception("Das Time Limit wurde bereits mit dem ersten Knoten überschritten.")
        #Berechnung der Entfernungen zwischen "erstem Knoten" und "letzen Knoten"
        for i in range(len(currentSolution.Sequence)-1):
            total_time += currentSolution.OutputNodes[currentSolution.Sequence[i]].Times[currentSolution.Sequence[i+1]-1]

        currentSolution.TotalScore = total_score
        currentSolution.TotalTime = total_time