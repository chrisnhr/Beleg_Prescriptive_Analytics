from Neighborhood import *
import math
from copy import deepcopy
import numpy
import time
import signal

""" Base class for several types of improvement algorithms. """ 
class ImprovementAlgorithm: #analog zur Vorlesung
    def __init__(self, inputData, neighborhoodEvaluationStrategy = 'BestImprovement', neighborhoodTypes = ['Swap']):
        self.InputData = inputData

        self.EvaluationLogic = {}
        self.SolutionPool = {}
        self.RNG = {}

        self.NeighborhoodEvaluationStrategy = neighborhoodEvaluationStrategy
        self.NeighborhoodTypes = neighborhoodTypes
        self.Neighborhoods = {}

    def Initialize(self, evaluationLogic, solutionPool, rng = None):
        self.EvaluationLogic = evaluationLogic
        self.SolutionPool = solutionPool
        self.RNG = rng

    """ Similar to the so-called factory concept in software design. """
    def CreateNeighborhood(self, neighborhoodType, bestCurrentSolution):
        if neighborhoodType == 'Swap':
            return SwapNeighborhood(self.InputData, bestCurrentSolution.Sequence, self.EvaluationLogic, self.SolutionPool)
        elif neighborhoodType == 'Insertion':
            return InsertionNeighborhood(self.InputData, bestCurrentSolution.Sequence, self.EvaluationLogic, self.SolutionPool)
        else:
            raise Exception(f"Neighborhood type {neighborhoodType} not defined.")

    def InitializeNeighborhoods(self, solution):
        for neighborhoodType in self.NeighborhoodTypes:
            neighborhood = self.CreateNeighborhood(neighborhoodType, solution)
            self.Neighborhoods[neighborhoodType] = neighborhood

""" Iterative improvement algorithm through sequential variable neighborhood descent. """
class IterativeImprovement(ImprovementAlgorithm): #analog zur Vorlesung
    def __init__(self, inputData, neighborhoodEvaluationStrategy = 'BestImprovement', neighborhoodTypes = ['Swap']):
        super().__init__(inputData, neighborhoodEvaluationStrategy, neighborhoodTypes)

    def Run(self, solution):
        self.InitializeNeighborhoods(solution)    

        # According to "Hansen et al. (2017): Variable neighorhood search", this is equivalent to the 
        # sequential variable neighborhood descent with a pipe neighborhood change step.
        for neighborhoodType in self.NeighborhoodTypes:
            neighborhood = self.Neighborhoods[neighborhoodType]

            neighborhood.LocalSearch(self.NeighborhoodEvaluationStrategy, solution)
        
        return solution

#Implementierung der Metaheuristic als Erweiterung der Basisklasse ImprovementAlgorithm
class VariableNeighborhoodSearch(ImprovementAlgorithm):
    def __init__(self, inputData, acceptanceCriterion, neighborhoodTypes = ["Add","Exchange","BlockExchange"]):
        super().__init__(inputData)
        #Für die Lokale Suche wird VND aus der VL genutzt
        self.LocalSearchAlgorithm = IterativeImprovement(self.InputData, neighborhoodTypes = ["Insertion","Swap"])
        self.AcceptanceCriterion = acceptanceCriterion
        self.NeighborhoodTypes = neighborhoodTypes
    
    def Initialize(self, evaluationLogic, solutionPool, rng = numpy.random.default_rng(161)):
        self.EvaluationLogic = evaluationLogic
        self.SolutionPool = solutionPool
        self.RNG = rng

        self.LocalSearchAlgorithm.Initialize(self.EvaluationLogic, self.SolutionPool)# weil "externe" Local Search Methdode
    
    def Run(self, currentSolution):
        runTime = time.time()
        currentSolution = deepcopy(currentSolution)

        ###Acceptance Criterion
        def handler(signum, frame):
            print("Aktuell beste Lösung:")
            print(self.SolutionPool.GetHighestTotalScoreSolution())
            raise TimeoutError("Maximum Runtime reached.")
        # Set the alarm signal handler
        signal.signal(signal.SIGALRM, handler)
        # Set the alarm to go off after the specified runtime
        signal.alarm(self.AcceptanceCriterion)

        k = 0
        while k <= (len(self.NeighborhoodTypes)-1):
            ###Shake -> erstellen einer Nachbarschaft + random Auswahl einer Lösung
            currentNeighborhoodType = self.NeighborhoodTypes[k]
            currentNeighborhood = None
            if currentNeighborhoodType == "Insertion":
                currentNeighborhood = InsertionNeighborhood(self.InputData, currentSolution.Sequence, self.EvaluationLogic, self.SolutionPool)
            elif currentNeighborhoodType == "Swap":
                currentNeighborhood = SwapNeighborhood(self.InputData, currentSolution.Sequence, self.EvaluationLogic, self.SolutionPool)
            elif currentNeighborhoodType == "Add":
                currentNeighborhood = AddNeighborhood(self.InputData, currentSolution.Sequence, self.EvaluationLogic, self.SolutionPool)
            elif currentNeighborhoodType == "Exchange":
                currentNeighborhood = ExchangeNeighborhood(self.InputData, currentSolution.Sequence, self.EvaluationLogic, self.SolutionPool)
            elif currentNeighborhoodType == "Re":
                currentNeighborhood = ReNeighborhood(self.InputData, currentSolution.Sequence, self.EvaluationLogic, self.SolutionPool)
            elif currentNeighborhoodType == "BlockExchange":
                currentNeighborhood = BlockExchangeNeighborhood(self.InputData, currentSolution.Sequence, self.EvaluationLogic, self.SolutionPool)
            else:
                raise Exception("Neighborhood type not defined.")
            currentNeighborhood.Update(currentSolution.Sequence)
            currentNeighborhood.DiscoverMoves()
            currentNeighborhood.EvaluateMoves(self.NeighborhoodEvaluationStrategy)
            #Checken, ob Nachbarschaft leer ist
            if len(currentNeighborhood.MoveSolutions) > 0:
                #Auswahl einer zufälligen Lösung
                currentSolution = self.RNG.choice(currentNeighborhood.MoveSolutions)
                print("Shake:", currentSolution)

            ###Local Search -> Verbesserung der Lösung durch Intra Tour Tausche mit VND und Swap + Insertion Nachbarschaft
                currentSolution = self.LocalSearchAlgorithm.Run(currentSolution)
            ###Shake
            else:
                print("Unable to shake due to empty Neighborhood")
            ###Change Neighborhood
            #Wenn Verbesserung erzielt werden Nachbarschaften von vorne angefangen, sonst skip auf nächste Nachbarschaft
            if currentSolution.TotalScore > self.SolutionPool.GetHighestTotalScoreSolution().TotalScore:# war vorher totaltime
                self.SolutionPool.AddSolution(currentSolution)
                k = 0
                print(f"New best Solution found, resetting k to {k}.")
            else:
                k += 1
                print(f"No better solution found, incrementing k to {k}.")
        print(f"RunTime: {time.time() - runTime} s")   
        return self.SolutionPool.GetHighestTotalScoreSolution()