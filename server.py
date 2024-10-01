from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from colorama import Fore, Style, init
import socket
import threading
import smtplib
import os
import re
import sys

load_dotenv()
SENDER_EMAIL = os.getenv("SENDER_EMAIL")      # Replace it with your Email
PASSWORD = os.getenv("PASSWORD")              # Replace it with your Password

PORT = 5555
HEADER = 1024
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(ADDR)
    
clients = {}
clients_lock = threading.Lock()

# Email validation function
def is_valid_email(email):
    """Validate email format."""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None


def broadcast(message, sender_name=None, exclude_client=None):
    with clients_lock:
        for client_name, client_info in list(clients.items()):
            if client_name != sender_name and client_name != exclude_client:
                try:
                    formatted_message = f"{Fore.YELLOW}{message}{Style.RESET_ALL}"
                    client_info["socket"].send(formatted_message.encode(FORMAT))
                except Exception as e:
                    print(f"Failed to send message to {client_name}: {e}")
                    client_info["socket"].close()
                    del clients[client_name]

# Direct message logic
def direct_message(sender_name, recipient_name, message):
    if recipient_name in clients:
        try:
            direct_msg = f"[DM from {sender_name}] {message}".encode(FORMAT)
            clients[recipient_name]["socket"].send(direct_msg)
            print(f"Direct message from {sender_name} to {recipient_name}: {message}")
            notify_email(sender_name, clients[recipient_name]["email"], message, dm=True)
            return True
        except Exception as e:
            print(f"{Fore.RED}Failed to send direct message: {e}{Style.RESET_ALL}")
    return False

# Email notification logic
def notify_email(sender_name, recipient_email, message, dm=False):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 465
    smtp_user = SENDER_EMAIL
    smtp_password = PASSWORD

    # Recipients are chosen based on whether it’s a direct message
    recipients = [recipient_email] if dm else [client_info["email"] for client_info in clients.values() if client_info["email"] != recipient_email]
    if not recipients:
        return  # No recipients to send to

    subject = f"Direct message from {sender_name}" if dm else f"New message from {sender_name}"
    body = message

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, recipients, msg.as_string())
        server.quit()
        print(f"Notification email sent to {recipients}")
    except Exception as e:
        print(f"{Fore.RED}Failed to send email: {e}{Style.RESET_ALL}")

# Error handling in message receiving
def handle_client(client_socket, client_name, client_email):
    with clients_lock:
        clients[client_name] = {"socket": client_socket, "email": client_email}
    
    broadcast(f"{Fore.LIGHTGREEN_EX}{client_name} has joined the chat!{Style.RESET_ALL}", exclude_client=client_name)

    while True:
        try:
            message = client_socket.recv(HEADER).decode(FORMAT)
            if not message:
                break

            if message == DISCONNECT_MESSAGE:
                print(f"{Fore.RED}{client_name} has disconnected.{Style.RESET_ALL}")
                break

            message_decoded = message.strip()
            if message_decoded.startswith("/dm"):
                parts = message_decoded.split(" ", 2)
                if len(parts) < 3:
                    client_socket.send("Invalid direct message format. Use: /dm [recipient_name] [message]".encode(FORMAT))
                    continue
                recipient_name = parts[1]
                dm_message = parts[2]
                if not direct_message(client_name, recipient_name, dm_message):
                    client_socket.send(f"Failed to send message to {recipient_name}. They might be offline.".encode(FORMAT))
            else:
                broadcast(f"{client_name}: {message_decoded}", client_name)
                notify_email(client_name, client_email, message_decoded)
                
                print(f"{client_name}: {message_decoded}")
                sys.stdout.write("Server: ")
                sys.stdout.flush()

        except Exception as e:
            print(f"{client_name} disconnected unexpectedly: {e}")
            break

    # Cleanup
    with clients_lock:
        if client_name in clients:
            del clients[client_name]
            broadcast(f"{Fore.LIGHTRED_EX}{client_name} has left the chat.{Style.RESET_ALL}")
    client_socket.close()

def server_broadcast_input():
    """Handles server-side input to send messages to all connected clients."""
    while True:
        sys.stdout.write("Server: ")
        sys.stdout.flush()
        msg = input("")

        if msg:
            formatted_msg = f"{Fore.YELLOW}[SERVER]: {msg}{Style.RESET_ALL}".encode(FORMAT)
            broadcast(formatted_msg)
            # print(f"[SERVER]: {msg}")

# Start the server
def start_server():
    init()

    print(f"Server is listening on {SERVER}...")
    server_socket.listen()

    # Start a thread to handle server input for broadcasting
    input_thread = threading.Thread(target=server_broadcast_input, daemon=True)
    input_thread.start()

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"New connection from {client_address}")

        client_socket.send("Enter your name: ".encode(FORMAT))
        client_name = client_socket.recv(HEADER).decode(FORMAT).strip()

        client_socket.send("Enter your email: ".encode(FORMAT))
        client_email = client_socket.recv(HEADER).decode(FORMAT).strip()

        if is_valid_email(client_email):
            # Start a new thread only after valid name and email
            thread = threading.Thread(target=handle_client, args=(client_socket, client_name, client_email))
            thread.start()
            print(f"[Active Connections] {threading.active_count() - 1}")
            print(f"{client_name} connected with email {client_email}")
            
        else:
            client_socket.send("Invalid email format. Disconnecting.".encode(FORMAT))
            client_socket.close()


if __name__ == "__main__":
    print("[STARTING] Server is starting ...")
    start_server()
