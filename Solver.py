import numpy
import os
from InputData import *
from OutputData import *
from EvaluationLogic import *
from ConstructiveHeuristics import *
#from ImprovementAlgorithm import *

class Solver: # analog zur Vorlesung bis auf Write Methode
    def __init__(self, inputData, seed):
        self.InputData = inputData
        self.Seed = seed
        self.RNG = numpy.random.default_rng(seed)

        self.EvaluationLogic = EvaluationLogic(inputData)
        self.SolutionPool = SolutionPool()
        
        self.ConstructiveHeuristic = ConstructiveHeuristics(self.EvaluationLogic, self.SolutionPool)

    def ConstructionPhase(self, constructiveSolutionMethod):
        self.ConstructiveHeuristic.Run(self.InputData, constructiveSolutionMethod)

        bestInitalSolution = self.SolutionPool.GetHighestTotalScoreSolution()

        print("Constructive solution found.")
        print(bestInitalSolution)
        return bestInitalSolution
    
    def ImprovementPhase(self, startSolution, algorithm):
        algorithm.Initialize(self.EvaluationLogic, self.SolutionPool, self.RNG)
        bestSolution = algorithm.Run(startSolution)

        print("Best found Solution.")
        print(bestSolution)

    def RunLocalSearch(self, constructiveSolutionMethod, algorithm):
        startSolution = self.ConstructionPhase(constructiveSolutionMethod)

        self.ImprovementPhase(startSolution, algorithm)
    
    def WriteSolution(self): #Erstellt Solution Ordner und schreibt Lösungsdatei
        solution = self.SolutionPool.GetHighestTotalScoreSolution()
        #Erstellen des Dicts mit der Lösung
        result = {"TotalScore":solution.TotalScore,
                  "Permutation": str([1]+solution.Sequence+[1]),
                  "Duration":solution.TotalTime}
        #Erstellen des Ordners
        os.makedirs("Solutions", exist_ok=True)
        #derive path
        file_Path = os.path.abspath(self.InputData.Path)
        #Speicherpath erstellen
        file_Name = os.path.join("Solutions", "Solution-" + os.path.basename(file_Path))
        #File abspeichern
        with open(file_Name, 'w') as file:
            json.dump(result, file, indent=4)