import sqlite3


class SQLiteClient:
    def __init__(self, database_name: str):
        self.connection = sqlite3.connect(database_name)

    def execute_non_query(self, query: str, params: tuple = None):
        with self.connection:
            if params is not None:
                self.connection.execute(query, params)
            else:
                self.connection.execute(query)

    def execute_non_query_many(self, query: str, params: iter):
        with self.connection:
            self.connection.executemany(query, params)

    def execute_query(self, query: str, params: tuple = None) -> list:
        with self.connection:
            return self.connection.execute(query, params).fetchall()

    def execute_query_many(self, query: str, params: iter):
        with self.connection:
            return self.connection.executemany(query, params).fetchall()
