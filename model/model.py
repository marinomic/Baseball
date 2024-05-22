import copy
import itertools

import networkx as nx

from database.DAO import DAO


class Model:
    def __init__(self):
        self._grafo = nx.Graph()
        self._allTeams = []
        self._team1Salary = 0
        self._team2Salary = 0
        self._idMap = {}
        self._solBest = []
        self._totCosto = 0

    def buildGraph(self, year):
        self._grafo.clear()
        if len(self._allTeams) == 0:
            print("Lista squadre vuota")
            return
        self._grafo.add_nodes_from(self._allTeams)

        # Metodo combinations di itertools che ci restituisce tutte le combinazioni possibili degli elementi di una lista
        # di una lista che gli passiamo come argomento, e il secondo argomento è il numero di elementi che vogliamo combinare
        # in questo caso 2, perchè vogliamo combinare le squadre a coppie
        my_edges = list(itertools.combinations(self._allTeams, 2))
        # print(my_edges)  # breakpoint per il debug tstModel per capire cosa restituisce itertools.combinations,
        # infatti non è iterabile, quindi lo trasformiamo in lista
        self._grafo.add_edges_from(my_edges)
        # oppure

        # for t1 in self._allTeams:
        #     for t2 in self._allTeams:
        #         if t1 != t2:
        #             self._grafo.add_edge(t1, t2)

        salaryOfTeams = DAO.getSalaryOfTeams(year, self._idMap)

        for e in self._grafo.edges:
            team1 = e[0]
            team2 = e[1]
            weight = salaryOfTeams[team1] + salaryOfTeams[team2]
            self._grafo[team1][team2]['weight'] = weight

    def getYears(self):
        return DAO.getAllYears()

    def getTeams(self, year):
        self._allTeams = DAO.getTeams(year)
        self._idMap = {t.ID: t for t in self._allTeams}
        # for t in self._allTeams:
        #     self._idMap[t.ID] = t
        return self._allTeams

    def printGraphDetails(self):
        print(f"Grafo creato con {len(self._grafo.nodes)} nodi e {len(self._grafo.edges)} archi")

    def getTeamsVicini(self, team):
        """
        Restituisce l’elenco delle squadre adiacenti, e il peso degli archi corrispondenti, in ordine decrescente di peso.
        """
        vicini = self._grafo[team]
        vicini = sorted(vicini.items(), key=lambda x: x[1]['weight'], reverse=True)
        return vicini

    def getBestPath(self, v0):
        self._solBest = []
        self._totCosto = 0

        parziale = [v0]
        listaVicini = []
        for v in self._grafo.neighbors(v0):
            pesoV = self._grafo[v0][v]['weight']
            listaVicini.append((v, pesoV))
        listaVicini.sort(key=lambda x: x[1], reverse=True)

        parziale.append(listaVicini[0][0])
        self._ricorsioneV2(parziale)
        parziale.pop()
        return self.getWeightOfPath(self._solBest)

    # def _ricorsioneV1(self, parziale):
    #     """
    #     Si implementi una procedura ricorsiva che calcoli un percorso di peso massimo avente le seguenti caratteristiche:
    #     • Il punto di partenza è v0.
    #     • Ogni vertice può comparire una sola volta
    #     • Il peso degli archi nel percorso deve essere strettamente decrescente.
    #     """
    #     # caso terminale
    #     if self._calcolaPeso(parziale) > self._totCosto:
    #         self._solBest = copy.deepcopy(parziale)
    #         self._totCosto = self._calcolaPeso(parziale)
    #     # Verifico se posso aggiungere un altro elemento (nodo) alla lista parziale
    #     for v in self._grafo.neighbors(parziale[-1]):
    #         if v not in parziale:
    #             # Verifico se il peso dell'arco tra il nodo corrente e il nodo che sto per aggiungere è minore del peso
    #             # dell'arco tra il nodo corrente e il nodo precedente
    #             if self._grafo[parziale[-1]][v]['weight'] < self._grafo[parziale[-2]][parziale[-1]]['weight']:
    #                 parziale.append(v)
    #                 self._ricorsioneV1(parziale)
    #                 parziale.pop()
    #                 return

# Per ottenere la lista di nodi con i suoi pesi, possiamo usare il metodo getWeightOfPath
    def getWeightOfPath(self, path):
        listTuples = [(path[0], 0)]
        for i in range(len(path) - 1):
            listTuples.append((path[i + 1], self._grafo[path[i]][path[i + 1]]['weight']))
        return listTuples

    def _ricorsioneV2(self, parziale):
        # caso terminale
        if self._calcolaPeso(parziale) > self._totCosto:
            self._solBest = copy.deepcopy(parziale)
            self._totCosto = self._calcolaPeso(parziale)

        # per ottimizzare la ricorsione siccome non abbiamo un caso terminale specifico,
        # possiamo usare la lista dei vicini del nodo corrente e ordinarla per peso decrescente
        # e poi iterare su di essa
        listaVicini = []
        for v in self._grafo.neighbors(parziale[-1]):

            pesoV = self._grafo[parziale[-1]][v]['weight']
            listaVicini.append((v, pesoV))

        listaVicini.sort(key=lambda x: x[1], reverse=True)

        for v1 in listaVicini:
            if (v1[0] not in parziale and
                    v1[1] < self._grafo[parziale[-2]][parziale[-1]]['weight']):
                parziale.append(v1[0])
                self._ricorsioneV2(parziale)
                parziale.pop()
                return  # se non mettiamo il return, la ricorsione continua a scendere e non si ferma

    def _calcolaPeso(self, listOfNodes):
        if len(listOfNodes) == 1:
            return 0
        peso = 0
        for i in range(len(listOfNodes) - 1):
            peso += self._grafo[listOfNodes[i]][listOfNodes[i + 1]]['weight']
        return peso
