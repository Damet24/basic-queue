import json
import logging
import socket


def send_message(host='127.0.0.1', port=8080, message='Hola, servidor!'):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((host, port))
            client_socket.sendall(message.encode())

            response = client_socket.recv(1024)
            logging.warning(f'Respuesta del servidor: {response.decode()}')
    except ConnectionRefusedError:
        print("No se ha podido establecer la conexion")

def config():
    add = {
        "params": ['credentials', 'add', 'daniel', 'password']
    }
    edit1 = {
        "params": ['credentials', 'edit', 'username', 'daniel', 'daniel_2']
    }
    edit2 = {
        "params": ['credentials', 'edit', 'daniel_2', 'daniel_3', 'password_2']
    }
    edit3 = {
        "params": ['credentials', 'edit', 'daniel_3', 'password_4']
    }
    send_message(message=f"[credentials=admin:admin][len=1024]\r\nconfig:{json.dumps(add)}")
    send_message(message=f"[credentials=admin:admin][len=1024]\r\nconfig:{json.dumps(edit1)}")
    send_message(message=f"[credentials=admin:admin][len=1024]\r\nconfig:{json.dumps(edit2)}")

def main():
    data = {
        "name": "Daniel",
        "last_name": "Mercado"
    }
    send_message(message=f"[credentials=daniel:password][len=1024]\r\nadd:{json.dumps(data)}")
    send_message(message=f"[credentials=user:password][len=1024]\r\nadd:{json.dumps(data)}")
    send_message(message=f"[credentials=admin:admin][len=1024]\r\nadd:{json.dumps(data)}")

    send_message(message=f"[credentials=user:password][len=1024]\r\nget_batch:1")

if __name__ == '__main__':
    config()
    # main()
