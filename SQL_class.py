import sqlite3
import psycopg2


class SQLite:

    def __init__(self, dbname):
        self.connection = sqlite3.connect(dbname)
        self.cursore = self.connection.cursor()

    def run_query(self, query):
        with self.connection:
            return self.cursore.execute(query).fetchall()

    def close(self):
        self.connection.close()

class Postrges:

    def __init__(self, init_str: str):

        self.db = psycopg2.connect(init_str)

    def run_query(self, query: str) -> list:
        cur = self.db.cursor()
        cur.execute(query)
        self.db.commit()
        try:
            result = cur.fetchall()
        except:
            result = None
        cur.close()

        return result