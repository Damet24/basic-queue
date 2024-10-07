import socket
from logging import Logger

from queue import Queue
from request import decode


class Server:
    def __init__(self, queue: Queue, logger: Logger, host: str = '127.0.0.1', port: int = 8080):
        self.__q = queue
        self.__logger = logger
        self.__host = host
        self.__port = port

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.__host, self.__port))
            server_socket.listen()

            self.__logger.info(f'Server running in {self.__host}:{self.__port}')
            while True:
                client_socket, addr = server_socket.accept()
                with client_socket:
                    while True:
                        data = client_socket.recv(1024)
                        if not data:
                            break
                        message = data.decode()
                        self.__logger.info(f'Receive: {message}')
                        result = self.process_request(message)
                        response = f'Eco: {result}'
                        client_socket.sendall(response.encode())

    def process_request(self, message: str):
        decoded_message = decode(message)
        if decoded_message["command"] == "add":
            print(decoded_message["content"])
            self.__q.enqueue(decoded_message["id"], decoded_message["content"])
        if decoded_message["command"] == "get":
            return self.__q.dequeue()
        return None
