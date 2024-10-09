import json
import logging
import socket
from uuid import uuid4


def send_message(host='127.0.0.1', port=8080, message='Hola, servidor!'):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        client_socket.sendall(message.encode())

        response = client_socket.recv(1024)
        logging.warning(f'Respuesta del servidor: {response.decode()}')

if __name__ == '__main__':
    data = {
        "name": "Daniel",
        "last_name": "Mercado"
    }
    send_message(message= f"[credentials=user:password][len=1024]\r\nadd:{json.dumps(data)}")
    send_message(message= f"[credentials=user:password][len=1024]\r\nadd:{json.dumps(data)}")
    send_message(message= f"[credentials=user:password][len=1024]\r\nadd:{json.dumps(data)}")

    send_message(message= f"[credentials=user:password][len=1024]\r\nfetch:")