from database.DB_connect import DBConnect
from model.team import Team


class DAO():
    @staticmethod
    def getAllYears():
        conn = DBConnect.get_connection()

        result = []

        cursor = conn.cursor(dictionary=True)
        query = """SELECT DISTINCT(YEAR)
                    FROM teams
                    WHERE year >= 1980
                    ORDER BY year DESC"""

        cursor.execute(query)

        for row in cursor:
            result.append(row['YEAR'])

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def getTeams(year):
        """
        Selezionare il numero di squadre (teams) che ha giocato in tale anno, e l’elenco delle rispettive sigle (teamCode).
        """
        conn = DBConnect.get_connection()

        result = []

        cursor = conn.cursor(dictionary=True)
        query = """
                    SELECT *
                    FROM teams
                    WHERE year = %s
                """

        cursor.execute(query, (year,))

        for row in cursor:
            result.append(Team(**row))

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def getSalaryOfTeams(year, idMap):
        """
        Il peso di ciascun arco del grafo deve corrispondere alla somma dei salari dei giocatori delle due
        squadre nell’anno considerato. Selezionare i salari di tutte le squadre che hanno giocato in tale anno.
        """
        conn = DBConnect.get_connection()

        cursor = conn.cursor(dictionary=True)
        query = """
                    SELECT t.teamCode, t.ID, SUM(salary) as totalSalary
                    FROM salaries s, teams t, appearances a
                    WHERE s.year = t.year
                    AND a.teamID = t.ID 
                    AND s.playerID = a.playerID
                    AND s.year = a.year
                    AND t.year = %s
                    GROUP BY t.teamCode
                """

        cursor.execute(query, (year,))

        result = {}
        for row in cursor:
            result[idMap[row['ID']]] = row['totalSalary']

        cursor.close()
        conn.close()
        return result
