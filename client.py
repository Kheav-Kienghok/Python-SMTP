import socket
import threading

# Receive messages from the server
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            print(message)
        except Exception:
            print("Connection lost.")
            break

# Connect to the server
def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 5555))

    # Receive and send client name and email
    name_prompt = client_socket.recv(1024).decode()
    name = input(name_prompt)
    client_socket.send(name.encode())

    email_prompt = client_socket.recv(1024).decode()
    email = input(email_prompt)
    client_socket.send(email.encode())

    # Start a thread to receive messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    # Send messages to the server
    while True:
        message = input()
        client_socket.send(message.encode())

start_client()
