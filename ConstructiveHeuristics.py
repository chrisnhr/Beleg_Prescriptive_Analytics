from InputData import *
from OutputData import *
from EvaluationLogic import *

class ConstructiveHeuristics:
    def __init__(self, evaluationLogic, solutionPool):
        self.EvaluationLogic = evaluationLogic
        self.SolutionPool = solutionPool

    # def HighestScoreFirst(self, nodeList, evaluationLogic): #der Reihe nach wird höchster Score hinzugefügt
    #     #Triviallösung: alle passen in Route checken
    #     #Triviallösung: keine einzige passt in Route checken -> in EvalLogic berücksichtigt
    #     sortedNodes = sorted(nodeList, key = lambda x: x.Score, reverse = True)
    #     currentSolution = Solution([],[]) #Initialisierung der "leeren" Lösung
        
    #     for node in sortedNodes:
    #         #Hinzufügen des höchstbewertetsten Knoten
    #         currentSolution.OutputNodes[node.Id] = node
    #         currentSolution.Sequence.append(node.Id)
    #         #Bewertung der Lösung
    #         evaluationLogic.DefineTotalValues(currentSolution)
    #         #Ist generierte Lösung unzulässig, wird der letzte Schritt revidiert und die Konstruktion abgebrochen
    #         if currentSolution.TotalTime > evaluationLogic.InputData.TimeLimit:
    #             del currentSolution.OutputNodes[node.Id]
    #             currentSolution.Sequence.pop()
    #             evaluationLogic.DefineTotalValues(currentSolution)
    #             break
    #     return currentSolution

    #der Reihe nach wird höchster Score hinzugefügt
    def HighestScoreFirst(self, nodeList, evaluationLogic):

        sortedNodes = sorted(nodeList, key = lambda x: x.Score, reverse = True)
        #Knoten 0 entfernen
        sortedNodes = sortedNodes[:-1]
        #Initialisierung der "leeren" Lösung
        currentSolution = Solution([],[])

        while sortedNodes:
            nextNode = sortedNodes.pop(0)
            #Hinzufügen des höchstbewertetsten Knoten
            currentSolution.OutputNodes[nextNode.Id] = nextNode
            currentSolution.Sequence.append(nextNode.Id)    
            evaluationLogic.DefineTotalValues(currentSolution)
            #wenn der Knoten "zu viel" war, wird er wieder rausgenommen
            if currentSolution.TotalTime > evaluationLogic.InputData.TimeLimit:
                del currentSolution.OutputNodes[nextNode.Id]
                currentSolution.Sequence.pop(-1)
                
        evaluationLogic.DefineTotalValues(currentSolution)
        return currentSolution
    
    def NearestNeighborFirst(self, nodeList): #der Reihe nach wird der am nächsten liegende Knoten hinzugefügt
        currentSolution = Solution([],[]) #Initialisierung der "leeren" Lösung
        #sortieren nach Entfernung vom Depot
        sortedNodes = sorted(nodeList, key = lambda x: x.Times[0], reverse = False)
        del sortedNodes[0] #Depot entfernen
        #add nearest Node
        currentSolution.OutputNodes[sortedNodes[0].Id] = sortedNodes[0]
        currentSolution.Sequence.append(sortedNodes[0].Id)
        self.EvaluationLogic.DefineTotalValues(currentSolution)
        #nach dem Hinzufügen wird Knoten aus Menge entfernt 
        del sortedNodes[0]

        #Schrittweises hinzufügen aller Knoten bis die Restriktion erreicht ist (oder alle Knoten erreicht)
        while sortedNodes:
            sortedNodes = sorted(sortedNodes, key=lambda x: x.Times[currentSolution.Sequence[-1] - 1], reverse=False)
            currentSolution.OutputNodes[sortedNodes[0].Id] = sortedNodes[0] #add nearest Node
            currentSolution.Sequence.append(sortedNodes[0].Id)
            del sortedNodes[0]
            self.EvaluationLogic.DefineTotalValues(currentSolution)
        #Sobald TimeLimit überschritten wird abgebrochen und der letzte Knoten wieder entfernt
            if currentSolution.TotalTime > self.EvaluationLogic.InputData.TimeLimit:
                break
        del currentSolution.OutputNodes[currentSolution.Sequence[-1]]
        currentSolution.Sequence.pop()
        self.EvaluationLogic.DefineTotalValues(currentSolution)

        return currentSolution
    
    def Run(self, inputData, solutionMethod): #analog zur Vorlesung
        print('Generating an initial solution according to ' + solutionMethod + '.')

        solution = None

        if solutionMethod == 'HSF':
            solution = self.HighestScoreFirst(inputData.InputNodes, self.EvaluationLogic)
        elif solutionMethod == 'NNF':
            solution = self.NearestNeighborFirst(inputData.InputNodes)
        else:
            print('Unkown constructive solution method: ' + solutionMethod + '.')
        
        self.SolutionPool.AddSolution(solution)