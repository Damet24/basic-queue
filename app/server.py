import socket

from contexts.application.base_service import BaseService
from contexts.application.custom_queue import Queue
from app.request import RequestProcessor
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
        self.__running = False
        self.__server_socket = None

    def start_server(self):
        self.__running = True
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.bind((self.__host, self.__port))
        self.__server_socket.listen()
        self.logger.info(f'Server running in {self.__host}:{self.__port}')

        try:
            while self.__running:
                client_socket, addr = self.__server_socket.accept()
                self.logger.info(f'Connection from {addr}')
                self.handle_client(client_socket)
        except Exception as e:
            self.logger.error(f'Server error: {e}')
        finally:
            self.stop_server()

    def stop_server(self):
        self.__running = False
        if self.__server_socket:
            self.__server_socket.close()
        self.logger.info('Server stopped.')

    def handle_client(self, client_socket):
        with client_socket:
            while self.__running:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    message = data.decode('utf-8')
                    self.logger.info(f'Receive: {message}')
                    result = self.process_request(message)
                    response = str(result)
                    client_socket.sendall(response.encode('utf-8'))
                except Exception as e:
                    self.logger.error(f'Error handling client: {e}')
                    break

    def process_request(self, message: str):
        decoded_message = RequestProcessor.decode(message)
        if not self.__auth_service.validate(decoded_message["headers"]["credentials"]):
            return "Error"
        if decoded_message["command"] == "queue":
            return self.__processor.process_queue_command(queue=self.__q, command_type=decoded_message["command"],
                                                          param=decoded_message["content"])
        return self.__processor.process_command(queue=self.__q, command_type=decoded_message["command"],
                                                param=decoded_message["content"])
