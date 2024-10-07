import sqlite3


class Database:
    def __init__(self, db_name: str = 'queue.db'):
        self.connection = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        with self.connection:
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS queue (
                    id VARCHAR(100) PRIMARY KEY,
                    content TEXT,
                    processed INTEGER DEFAULT 0
                )
            ''')

    def insert(self, _id: str, content: str):
        with self.connection:
            self.connection.execute('INSERT INTO queue (id, content) VALUES (?, ?)', (_id, content))

    def insert_many(self, iterable: iter(tuple[str, str])):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.executemany('INSERT INTO queue (id, content) VALUES (?, ?)', iterable)

    def mark_processed(self, id: str):
        with self.connection:
            self.connection.execute('UPDATE queue SET processed = 1 WHERE id = ?', (id,))

    def fetch_all(self) -> list:
        with self.connection:
            return self.connection.execute('SELECT * FROM queue WHERE processed = 1').fetchall()
