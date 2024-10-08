from colorama import Fore, Style, init 
from mark_function import masked_input 
import socket
import threading
import sys
import os


PORT = 5555
HEADER = 1024
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER, PORT))


# Receive messages from the server
def receive_messages(client_socket):
    """Receives messages from the server in a loop."""
    while True:
        try:
            message = client_socket.recv(HEADER).decode(FORMAT)
            if message:
                sys.stdout.write("\033[K")  # Clear the line
                sys.stdout.write(f"\r{Fore.YELLOW}{message}{Style.RESET_ALL}\n")  # Print received message

                # Check for the disconnect messages
                if "Invalid email format. Disconnecting." in message or "have been kicked." in message:
                    shutdown()
                
                # Reprint the input prompt without causing duplicate "You:"
                sys.stdout.write("\rYou: ")
                sys.stdout.flush()
            else:
                break
            
        except Exception:
            break


# Function to handle graceful shutdown
def shutdown():
    client_socket.send(DISCONNECT_MESSAGE.encode())
    client_socket.close()
    print(f"{Fore.RED}Disconnected from server!{Style.RESET_ALL}")
    os._exit(0)


# Connect to the server
def start_client():
    answer = input('Would you like to connect (yes/no)? ')
    if answer.lower() != 'yes':
        print("Exiting program.")
        return
    

    # Receive and send client name and email
    name_prompt = client_socket.recv(HEADER).decode()
    name = input(f"{Fore.YELLOW}{name_prompt}{Style.RESET_ALL}")
    client_socket.send(name.encode())

    email_prompt = client_socket.recv(HEADER).decode()
    email = masked_input(f"{Fore.CYAN}{email_prompt}{Style.RESET_ALL}")  # Use custom masked input for email
    client_socket.send(email.encode())

    # Start a thread to receive messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    # Send messages to the server
    while True:
        try:
            message = input("You: ")
            
            if message.lower() == "q":
                shutdown()  # Use shutdown function for graceful exit
            
            # yellow_message = f"{Fore.YELLOW}{message}{Style.RESET_ALL}"
            client_socket.send(message.encode())
            
        except KeyboardInterrupt:
            print(f"\n{name} have been disconnected.")
            shutdown()  # Use shutdown function for graceful exit


if __name__ == "__main__":
    init()
    start_client()
