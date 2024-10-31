import socket
from logging import Logger

from contexts.application.base_service import BaseService
from contexts.application.custom_queue import Queue
from apps.server.request import RequestProcessor
from contexts.application.auth_service import AuthService
from contexts.application.configuration_service import ConfigurationService


class Server(BaseService):
    def __init__(self, configuration: ConfigurationService, queue: Queue, auth_service: AuthService,
                 processor: RequestProcessor,
                 host: str = '127.0.0.1', port: int = 8080):
        super().__init__()
        self.__q = queue
        self.__auth_service = auth_service
        self.__configuration_service = configuration
        self.__processor = processor
        self.__host = host
        self.__port = port

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.__host, self.__port))
            server_socket.listen()

            self.logger.info(f'Server running in {self.__host}:{self.__port}')
            while True:
                client_socket, addr = server_socket.accept()
                with client_socket:
                    while True:
                        data = client_socket.recv(1024)
                        if not data:
                            break
                        message = data.decode()
                        self.logger.info(f'Receive: {message}')
                        result = self.process_request(message)
                        response = result.__str__()
                        client_socket.sendall(response.encode())

    def process_request(self, message: str):
        decoded_message = RequestProcessor.decode(message)
        if not self.__auth_service.validate(decoded_message["headers"]["credentials"]):
            return "Error"
        if decoded_message["command"] == "queue":
            return self.__processor.process_queue_command(queue=self.__q, command_type=decoded_message["command"],
                                                          param=decoded_message["content"])
        return self.__processor.process_command(queue=self.__q, command_type=decoded_message["command"],
                                                param=decoded_message["content"])
