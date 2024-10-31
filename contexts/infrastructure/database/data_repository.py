from contexts.infrastructure.database.sqlite_client import SQLiteClient

class DataRepository:
    def __init__(self, sql_client: SQLiteClient):
        self.__sqlite_client = sql_client

    def create_table(self):
        self.__sqlite_client.execute_non_query('''
            CREATE TABLE IF NOT EXISTS customn_queue (
                id TEXT PRIMARY KEY,
                content TEXT,
                processed INTEGER DEFAULT 0
            )
        ''')

    def insert(self, _id: str, content: str):
        self.__sqlite_client.execute_non_query('INSERT INTO customn_queue (id, content) VALUES (?, ?)', (_id, content))

    def insert_many(self, iterable):
        self.__sqlite_client.execute_non_query_many('INSERT INTO customn_queue (id, content) VALUES (?, ?)', iterable)

    def mark_processed(self, _id: str):
        self.__sqlite_client.execute_non_query('UPDATE customn_queue SET processed = 1 WHERE id = ?', (_id,))

    def fetch_all(self) -> list:
        return self.__sqlite_client.execute_query('SELECT * FROM customn_queue WHERE processed = 1')
