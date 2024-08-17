from copy import deepcopy
from OutputData import *

class BaseNeighborhood:
    def __init__(self, inputData, initialSequence, evaluationLogic, solutionPool):
        self.InputData = inputData
        self.Sequence = initialSequence
        self.EvaluationLogic = evaluationLogic
        self.SolutionPool = solutionPool

        self.Moves = [] #Lösungen
        self.MoveSolutions = []#bewertete Lösungen

        self.Type = 'None'

    def DiscoverMoves(self):
        raise Exception('DiscoverMoves() is not implemented for the abstract BaseNeighborhood class.')

    def EvaluateMoves(self, evaluationStrategy):
        if evaluationStrategy == 'BestImprovement':
            self.EvaluateMovesBestImprovement()
        elif evaluationStrategy == 'FirstImprovement':
            self.EvaluateMovesFirstImprovement()
        else:
            raise Exception(f'Evaluation strategy {evaluationStrategy} not implemented.')
        
    def EvaluateMove(self, move):
        
        solutionNodes = []
        for node in self.InputData.InputNodes:
            if node.Id in move.Sequence:
                solutionNodes.append(node)
        #Erstellen einer Lösung aus dem move
        moveSolution = Solution(solutionNodes, move.Sequence)
        
        self.EvaluationLogic.DefineTotalValues(moveSolution)

        return moveSolution
    
    """ Evaluate all moves. """
    def EvaluateMovesBestImprovement(self):
        
        for move in self.Moves:
            moveSolution = self.EvaluateMove(move)
            #nur hinzufügen, wenn auch feasible!
            if moveSolution.TotalTime <= self.InputData.TimeLimit:
                self.MoveSolutions.append(moveSolution)

    """ Evaluate all moves until the first one is found that improves the best solution found so far. """
    def EvaluateMovesFirstImprovement(self):
        bestObjective = self.SolutionPool.GetHighestTotalScoreSolution().TotalScore #hier

        for move in self.Moves:
            moveSolution = self.EvaluateMove(move)
            #nur hinzufügen, wenn auch feasible!
            if moveSolution.TotalTime <= self.InputData.TimeLimit:
                self.MoveSolutions.append(moveSolution)
            if moveSolution.TotalScore > bestObjective:
                # abort neighborhood evaluation because an improvement has been found
                return
            
    def MakeBestMove(self):
        self.MoveSolutions.sort(key = lambda solution: solution.TotalTime, reverse=False) # sort solutions ascending by TotalTime
        self.MoveSolutions.sort(key = lambda solution: solution.TotalScore, reverse=True) # sort solutions descending by TotalScore

        if len(self.MoveSolutions) == 0:
            print("There was no feasible move in the Neighborhood.")
            return None
            
        else:
            bestNeighborhoodSolution = self.MoveSolutions[0]
        return bestNeighborhoodSolution
        

    def Update(self, sequence):
        self.Sequence = sequence

        self.Moves.clear()
        self.MoveSolutions.clear()

    def LocalSearch(self, neighborhoodEvaluationStrategy, solution):

        hasSolutionImproved = True

        while hasSolutionImproved:
            self.Update(solution.Sequence)
            self.DiscoverMoves()
            self.EvaluateMoves(neighborhoodEvaluationStrategy)
        
            #Lösung beibehalten, wenn kein besserer Move möglich war, sonst ersetzen
            if self.MakeBestMove() == None:
                bestNeighborhoodSolution = solution
            else:
                bestNeighborhoodSolution = self.MakeBestMove()

            #wenn die Lösung besser war, einmal alles updaten
            if bestNeighborhoodSolution.TotalScore > solution.TotalScore:
                print("New best solution has been found!")
                print(bestNeighborhoodSolution)

                self.SolutionPool.AddSolution(bestNeighborhoodSolution)

                solution.Sequence = bestNeighborhoodSolution.Sequence
                solution.TotalScore = bestNeighborhoodSolution.TotalScore
                solution.TotalTime = bestNeighborhoodSolution.TotalTime
            
            #war nur die Zeit besser, ist das auch einen nennenswerte Verbesserung
            elif (bestNeighborhoodSolution.TotalScore == solution.TotalScore) and (bestNeighborhoodSolution.TotalTime < solution.TotalTime):
                print(f"Time improvement made: {bestNeighborhoodSolution.TotalTime}")
            
                self.SolutionPool.AddSolution(bestNeighborhoodSolution)

                solution.Sequence = bestNeighborhoodSolution.Sequence
                solution.TotalScore = bestNeighborhoodSolution.TotalScore
                solution.TotalTime = bestNeighborhoodSolution.TotalTime
            
            #Abbruch, wenn keine Verbesserung möglich war
            else:
                print(f"Reached local optimum of {self.Type} neighborhood. Stop local search.")
                hasSolutionImproved = False

""" Represents the swap of the element at IndexA with the element at IndexB for a given sequence (= solution). """
class SwapMove: # nur Abwandlug aus VL
    def __init__(self, initialSequence, indexA, indexB):
        self.Sequence = list(initialSequence) # create a copy of the sequence
        self.IndexA = indexA
        self.IndexB = indexB

        self.Sequence[indexA] = initialSequence[indexB]
        self.Sequence[indexB] = initialSequence[indexA]
        
""" Contains all $n choose 2$ swap moves for a given Sequence (= solution). """
class SwapNeighborhood(BaseNeighborhood): # nur Abwandlung aus VL
    def __init__(self, inputData, initialSequence, evaluationLogic, solutionPool):
        super().__init__(inputData, initialSequence, evaluationLogic, solutionPool)

        self.Type = 'Swap'

    """ Generate all $n choose 2$ moves. """
    def DiscoverMoves(self):
        for i in range(len(self.Sequence)):
            for j in range(len(self.Sequence)):
                if i < j:
                    swapMove = SwapMove(self.Sequence, i, j)
                    self.Moves.append(swapMove)

""" Represents the insertion of the element at IndexA at the new position IndexB for a given sequence (= solution). """
class InsertionMove: # nur Abwandlung aus VL
    def __init__(self, initialSequence, indexA, indexB):
        self.Sequence = [] # create a copy of the sequence
        self.IndexA = indexA
        self.IndexB = indexB

        for k in range(len(initialSequence)):
            if k == indexA:
                continue

            self.Sequence.append(initialSequence[k])

        self.Sequence.insert(indexB, initialSequence[indexA])

""" Contains all $(n - 1)^2$ insertion moves for a given sequence (= solution). """
class InsertionNeighborhood(BaseNeighborhood): # nur Abwandlung aus VL
    def __init__(self, inputData, initialSequence, evaluationLogic, solutionPool):
        super().__init__(inputData, initialSequence, evaluationLogic, solutionPool)

        self.Type = 'Insertion'

    def DiscoverMoves(self):
        for i in range(len(self.Sequence)):
            for j in range(len(self.Sequence)):
                if i == j or i == j + 1:
                    continue

                insertionMove = InsertionMove(self.Sequence, i, j)
                self.Moves.append(insertionMove)

class AddMove: #Move der schaut, ob noch irgendwo(!) ein weiterer Node eingefügt werden kann
    def __init__(self, initialSequence, index, element ):
        self.Sequence = list(initialSequence)
        self.Sequence.insert(index, element)
        
class AddNeighborhood(BaseNeighborhood):
    def __init__(self, inputData, initialSequence, evaluationLogic, solutionPool):
        super().__init__(inputData, initialSequence, evaluationLogic, solutionPool)

        self.Type = "Add"
        self.Sequence = initialSequence
        #"Residue" sind die nicht erreichten Knoten
        self.Residue = [x for x in range(2,self.InputData.NodeCount+1) if x not in self.Sequence]

    def DiscoverMoves(self):
        for node in self.Residue:
            for position in range(len(self.Sequence)+1):
                addMove = AddMove(self.Sequence, position, node)
                self.Moves.append(addMove)

#ReMove wird aktuell nicht genutzt
class ReMove: #entfernt einfach einen Knoten, Idee dahinter war Dekonstruktion für Rekonstruktion, funktioniert aber nicht gut mit VNS
    def __init__(self, initialSequence, index):
        self.Sequence = list(initialSequence)
        self.Sequence.pop(index)

class ReNeighborhood(BaseNeighborhood):
    def __init__(self, inputData, initialSequence, evaluationLogic, solutionPool):
        super().__init__(inputData, initialSequence, evaluationLogic, solutionPool)

        self.Type = "Re"
        self.Sequence = initialSequence

    def DiscoverMoves(self):
        for index in range(len(self.Sequence)):
            reMove = ReMove(self.Sequence, index)
            self.Moves.append(reMove)

class ExchangeMove: #Tauscht erreichten knoten mit einem Knoten aus der Menge aus nicht erreichten Knoten
    def __init__(self, initialSequence, index, element):
        self.Sequence = list(initialSequence)
        self.Sequence[index] = element
class ExchangeNeighborhood(BaseNeighborhood):
    def __init__(self, inputData, initialSequence, evaluationLogic, solutionPool):
        super().__init__(inputData, initialSequence, evaluationLogic, solutionPool)

        self.Type = "Exchange"
        self.Sequence = initialSequence
        #"Residue" sind die nicht erreichten Knoten
        self.Residue = [x for x in range(2,self.InputData.NodeCount+1) if x not in self.Sequence]

    def DiscoverMoves(self):
        for node in self.Residue:
            for index in range(len(self.Sequence)):
                exchangeMove = ExchangeMove(self.Sequence, index, node)
                self.Moves.append(exchangeMove)

class BlockExchangeMove: # entfernt einen 2er Block aus der Lösung und füllt Lücke mit unerreichten Knoten
    def __init__(self, initialSequence, index, element1, element2):
        self.Sequence = list(initialSequence)
        #Substituieren der Elemente in der Sequenz
        self.Sequence[index:index+1] = [element1, element2]
        
class BlockExchangeNeighborhood(BaseNeighborhood):
    def __init__(self, inputData, initialSequence, evaluationLogic, solutionPool):
        super().__init__(inputData, initialSequence, evaluationLogic, solutionPool)

        self.Type = "BlockExchange"
        self.Sequence = initialSequence
        #"Residue" sind die nicht erreichten Knoten
        self.Residue = [x for x in range(2,self.InputData.NodeCount+1) if x not in self.Sequence]

    def DiscoverMoves(self):
        for element1 in self.Residue:
            for element2 in self.Residue:
                if element1 != element2:
                    for index in range(len(self.Sequence)):
                        blockExchangeMove = BlockExchangeMove(self.Sequence, index, element1, element2)
                        self.Moves.append(blockExchangeMove)

class ExchangeMove: #Tauscht erreichten knoten mit einem Knoten aus der Menge aus nicht erreichten Knoten
    def __init__(self, initialSequence, index, element):
        self.Sequence = list(initialSequence)
        self.Sequence[index] = element
class ExchangeNeighborhood(BaseNeighborhood):
    def __init__(self, inputData, initialSequence, evaluationLogic, solutionPool):
        super().__init__(inputData, initialSequence, evaluationLogic, solutionPool)

        self.Type = "Exchange"
        self.Sequence = initialSequence
        #"Residue" sind die nicht erreichten Knoten
        self.Residue = [x for x in range(2,self.InputData.NodeCount+1) if x not in self.Sequence]

    def DiscoverMoves(self):
        for node in self.Residue:
            for index in range(len(self.Sequence)):
                exchangeMove = ExchangeMove(self.Sequence, index, node)
                self.Moves.append(exchangeMove)