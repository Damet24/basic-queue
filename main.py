import platform
import re
import os
from pathlib import Path
import sqlite3
from collections import deque
import socket
import logging
from daemons.prefab import run


def join_paths(*paths):
    result = ""
    for path in paths:
        result = os.path.join(result, path)
    return result


def verify_files(path):
    file = Path(path)
    return file.exists()


def get_data_path():
    if re.search("Windows", platform.system()):
        return os.getenv('LOCALAPPDATA')


def execute_none_query(db, query, param=None):
    with sqlite3.connect(db) as connection:
        cursor = connection.cursor()
        if param is not None:
            print(type(param) is not list)
            if type(param) is not list:
                cursor.execute(query, param)
            else:
                cursor.executemany(query, param)
        else:
            cursor.execute(query)


def execute_query(db, query):
    with sqlite3.connect(db) as connection:
        cursor = connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()


class Database:
    def __init__(self, db_name='queue.db'):
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

    def insert(self, id, content):
        with self.connection:
            self.connection.execute('INSERT INTO queue (id, content) VALUES (?, ?)', (id, content))

    def insert_many(self, iterable):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.executemany('INSERT INTO queue (id, content) VALUES (?, ?)', iterable)

    def mark_processed(self, id):
        with self.connection:
            self.connection.execute('UPDATE queue SET processed = 1 WHERE id = ?', (id,))

    def fetch_all(self):
        with self.connection:
            return self.connection.execute('SELECT * FROM queue WHERE processed = 1').fetchall()


class Queue:
    def __init__(self, database):
        self.queue = deque()
        self.db = Database(database)

    def enqueue(self, id, content):
        self.queue.append({'id': id, 'content': content})
        self.db.insert(id, content)

    def enqueue_batch(self, iterable):
        self.queue.extend([{'id': _item[0], 'content': _item[1]} for _item in iterable])
        self.db.insert_many(iterable)

    def dequeue(self):
        if self.queue:
            item = self.queue.popleft()
            self.db.mark_processed(item['id'])
            return item
        return None

    def dequeue_batch(self, quantity=1):
        items = []
        if self.queue:
            for i in range(quantity):
                items.append(self.dequeue())
        return items

    def get_all(self):
        return list(self.queue)

    def get_processed(self):
        return self.db.fetch_all()

def encode_cui_message(object):
    return ""


def decode_cui_message(message):
    data = message.split(":", 2)
    return {
        "command": data[0],
        "id": data[1],
        "content": data[2]
    }


def proccess_request(q, message):
    decoded_message = decode_cui_message(message)
    if decoded_message["command"] == "add":
        print(decoded_message["content"])
        q.enqueue(decoded_message["id"], decoded_message["content"])

    if decoded_message["command"] == "get":
        return q.dequeue()

    return None

def start_server(host='127.0.0.1', port=8080):
    q = Queue('queue.db')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()

        logging.warning(f'Servidor escuchando en {host}:{port}')
        while True:
            client_socket, addr = server_socket.accept()
            with client_socket:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    message = data.decode()
                    logging.warning(f'Recibido: {message}')
                    result = proccess_request(q, message)
                    # Procesar el mensaje aquí y enviar una respuesta
                    response = f'Eco: {result}'
                    client_socket.sendall(response.encode())


class SleepyDaemon(run.RunDaemon):
    def run(self):
        while True:
            logging.warning("daemon running!")
            start_server()


if __name__ == "__main__":
    # MAIN_DB = "main.db"
    # data_path = get_data_path()
    # app_name = "queue"
    #
    # main_db_path = join_paths(data_path, app_name, MAIN_DB)
    # exists = verify_files(main_db_path)
    # if not exists:
    #     Path(main_db_path).touch()
    #
    # q = Queue(main_db_path)
    # q.enqueue_batch(
    #     [(1, json.dumps({"name": "Daniel Mercado"})),
    #       (2, json.dumps({"name": "Daniel Mercado"})),
    #       (3, json.dumps({"name": "Daniel Mercado"})),
    #       (4, json.dumps({"name": "Daniel Mercado"}))])
    #
    # items = q.dequeue_batch(3)
    # print(items)
    # print(q.get_processed())
    # print(q.get_all())
    logging.basicConfig(level=logging.ERROR)
    logging.debug("DEBUG")
    logging.info("INFO")
    logging.warning("WARNING")
    logging.error("ERROR")
    # logfile = os.path.join(os.getcwd(), "sleepy.log")
    # pidfile = os.path.join(os.getcwd(), "sleepy.pid")

    # logging.warning(f"working directory: {pidfile}")
    # logging.warning(Path(pidfile).read_text())

    # logging.basicConfig(filename=logfile, level=logging.DEBUG)
    # d = SleepyDaemon(pidfile=pidfile)
    # d.start()
    # start_server()