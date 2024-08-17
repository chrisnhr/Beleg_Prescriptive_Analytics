import json

class DataNode:
    def __init__(self, Id, X, Y, Score):
        self.__nodeId = Id
        self.__X = X
        self.__Y = Y
        self.Times = []
        self.__score = Score
        
    def __str__(self):
        return f"Node {self.__nodeId} with Score {self.__score} at ({self.__X}, {self.__Y})"
    
    @property
    def Id(self):
        return self.__nodeId
    @property
    def X(self):
        return self.__X
    @property
    def Y(self):
        return self.__Y
    @property
    def Score(self):
        return self.__score

class InputData:
    def __init__(self, path):

        self.__Path = path
        self.__NodeCount = -1
        self.__TimeLimit = -1
        self.DataLoad()
        
    def DataLoad(self):

        with open(self.__Path, "r") as inputFile:
            inputData = json.load(inputFile)
        
        self.__NodeCount = inputData["NodeCount"]
        self.__TimeLimit = inputData["TimeLimit"]
        self.InputNodes = list()
        #Einlesen und Abspeichern der Nodes aus dem Input File
        for node in inputData["Nodes"]:
            self.InputNodes.append(DataNode(node["Id"], node["X"], node["Y"], node["Score"]))
        #Berechnung der Entfernung für den jeweiligen Knoten
        for i in range(len(inputData["Nodes"])):
            for j in range(len(inputData["Nodes"])):
                x1, y1 = (inputData["Nodes"][i]["X"], inputData["Nodes"][i]["Y"])
                x2, y2 = (inputData["Nodes"][j]["X"], inputData["Nodes"][j]["Y"])
                time = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
                self.InputNodes[i].Times.append(time)
    @property
    def NodeCount(self):
        return self.__NodeCount
    @property
    def TimeLimit(self):
        return self.__TimeLimit
    @property
    def Path(self):
        return self.__Path