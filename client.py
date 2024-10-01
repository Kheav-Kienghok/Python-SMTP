from colorama import Fore, Style, init  
import socket
import threading
import sys


PORT = 5555
HEADER = 1024
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"


# Receive messages from the server
def receive_messages(client_socket):
    """Receives messages from the server in a loop."""
    while True:
        try:
            message = client_socket.recv(HEADER).decode()
            if message:
                sys.stdout.write("\033[K")  # Clear the line
                sys.stdout.write(f"\r{Fore.LIGHTWHITE_EX}{message}{Style.RESET_ALL}\n")  # Print received message

                # Reprint the input prompt without causing duplicate "You:"
                sys.stdout.write("You: ")
                sys.stdout.flush()
            else:
                break

        except Exception:
            print("Connection lost.")
            break



# Connect to the server
def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER, PORT))

    # Receive and send client name and email
    name_prompt = client_socket.recv(HEADER).decode()
    name = input(name_prompt)
    client_socket.send(name.encode())

    email_prompt = client_socket.recv(HEADER).decode()
    email = input(email_prompt)
    client_socket.send(email.encode())

    # Start a thread to receive messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    # Send messages to the server
    while True:
        try:
            message = input("You: ")
            if message.lower() == "q":
                client_socket.close()
                print("Disconnected from server.")
                break

            client_socket.send(message.encode())

        except Exception as e:
            print(f"Error sending message: {e}")
            client_socket.close()
            break


if __name__ == "__main__":
    init()
    start_client()
