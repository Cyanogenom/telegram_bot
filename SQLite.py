import sqlite3


class SQLite:

    def __init__(self, dbname):
        self.connection = sqlite3.connect(dbname)
        self.cursore = self.connection.cursor()

    def run_query(self, query):
        with self.connection:
            return self.cursore.execute(query).fetchall()

    def close(self):
        self.connection.close()