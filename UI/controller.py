import warnings

import flet as ft


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model
        self._selectedTeam = None

    def fillDDYear(self):
        years = self._model.getYears()
        yearsDD = map(lambda x: ft.dropdown.Option(x), years)
        self._view._ddAnno.options = yearsDD
        self._view.update_page()

        # yearsDD = []
        # for y in years:
        #     yearsDD.append(ft.dropdown.Option(y))

    def handleDDAnnoSelected(self, e):
        anno_scelto = self._view._ddAnno.value
        if anno_scelto is not None:
            teams = self._model.getTeams(anno_scelto)
            self._view._txtOutSquadre.controls.append(
                    ft.Text(f"Numero di squadre nell'anno {anno_scelto}: {len(teams)}"))
            for t in teams:
                self._view._txtOutSquadre.controls.append(ft.Text(t.teamCode))
                self._view._ddSquadra.options.append(
                        ft.dropdown.Option(data=t,
                                           text=t.teamCode,
                                           on_click=self.readDDTeam))
            self._view._ddSquadra.disabled = False
            self._view.update_page()

    def readDDTeam(self, e):
        if e.control.data is None:
            self._selectedTeam = None
        else:
            self._selectedTeam = e.control.data
        print(f"readDDTeams called -- {self._selectedTeam}")

    def handleCreaGrafo(self, e):
        if self._view._ddAnno.value is None:
            self._view._txt_result.controls.append(ft.Text("Selezionare un anno"))
            self._view.update_page()
            return
        self._model.buildGraph(self._view._ddAnno.value)
        self._view._txt_result.controls.append(ft.Text("Grafo creato con successo."))
        self._view._txt_result.controls.append(ft.Text(f"Numero di nodi: {len(self._model._grafo.nodes)}"))
        self._view._txt_result.controls.append(ft.Text(f"Numero di archi: {len(self._model._grafo.edges)}"))
        self._view.update_page()

    def handleDettagli(self, e):
        vicini = self._model.getTeamsVicini(self._selectedTeam)
        self._view._txt_result.controls.clear()
        self._view._txt_result.controls.append(ft.Text(f"Dettagli squadra {self._selectedTeam.teamCode}"))
        for v in vicini:
            self._view._txt_result.controls.append(ft.Text(f"{v[1]['weight']} - {v[0]}"))
        self._view.update_page()

    def handlePercorso(self, e):
        if self._selectedTeam is None:
            warnings.warn("Selezionare una squadra")
            return
        path = self._model.getBestPath(self._selectedTeam)
        self._view._txt_result.controls.clear()
        self._view._txt_result.controls.append(ft.Text(f"Percorso migliore per {self._selectedTeam} trovato"))
        for p in path:
            self._view._txt_result.controls.append(ft.Text(f"{p[0]} -- {p[1]}"))
        self._view.update_page()
