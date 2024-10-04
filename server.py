from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from colorama import Fore, Style, init
import aiosmtplib
import socket
import threading
import os
import re
import sys
import asyncio
from concurrent.futures import ThreadPoolExecutor

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

# Create a thread pool for managing client connections
executor = ThreadPoolExecutor(max_workers = 5)  # Adjust the max_workers as needed

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
                except Exception:
                    print(f"Failed to send message to {client_name}")
                    client_info["socket"].close()
                    del clients[client_name]

# Direct message logic
def direct_message(sender_name, recipient_name, message):
    if recipient_name in clients:
        try:
            direct_msg = f"{Fore.CYAN}[Private message from {sender_name}]: {message}{Style.RESET_ALL}".encode(FORMAT)
            clients[recipient_name]["socket"].send(direct_msg)
            print(f"\rDirect message from {sender_name} to {recipient_name}: {message}")
            
            # Start email notification in a new thread
            threading.Thread(
                target=start_email_notifier_loop,
                args=(notify_email(sender_name, clients[recipient_name]["email"], message, dm = True),)
            ).start()
            
            print_server()
            return True
        except Exception as e:
            print(f"{Fore.RED}Failed to send direct message: {e}{Style.RESET_ALL}")
    return False

# Async email notification logic
async def notify_email(sender_name, recipient_email, message, dm=False):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 465                 # Using the SSL port for SMTP
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
        # Create an SSL connection and send the email asynchronously
        await aiosmtplib.send(
            msg,
            hostname = smtp_server,
            port = smtp_port,
            username = smtp_user,
            password = smtp_password,
            use_tls = True,
        )
        
        for recipient in recipients: 
            print(f"{Fore.LIGHTGREEN_EX}Notification email sent to {recipient}{Style.RESET_ALL}")
            # print_server()
    
    except Exception as e:
        print(f"{Fore.RED}Failed to send email: {e}{Style.RESET_ALL}")
        # Notify the sender that the email failed
        with clients_lock:
            if sender_name in clients:
                failure_msg = f"{Fore.RED}Failed to send email notification. Error: {e}{Style.RESET_ALL}"
                clients[sender_name]["socket"].send(failure_msg.encode(FORMAT))

# Start the email notifier event loop in a separate thread
def start_email_notifier_loop(funtions):
    """Runs an event loop in a separate thread for email notifications."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(funtions)


# Error handling in message receiving
def handle_client(client_socket, client_name, client_email):
    with clients_lock:
        clients[client_name] = {"socket": client_socket, "email": client_email}
    
    broadcast(f"{Fore.LIGHTGREEN_EX}{client_name} has joined the chat!{Style.RESET_ALL}", exclude_client = client_name)

    while True:
        try:
            message = client_socket.recv(HEADER).decode(FORMAT)
            if not message:
                break

            if message == DISCONNECT_MESSAGE:
                print(f"{Fore.RED}{client_name} has disconnected.{Style.RESET_ALL}")
                break

            message_decoded = message.strip()
            if "/dm" in message:
                
                parts = message_decoded.split(" ", 2)
                if len(parts) < 3:
                    client_socket.send("Invalid direct message format. Use: /dm [recipient_name] [message]".encode(FORMAT))
                    continue
                recipient_name = parts[1]
                dm_message = parts[2]
                if not direct_message(client_name, recipient_name, dm_message):
                    client_socket.send(f"Failed to send message to {recipient_name}. They might be offline.".encode(FORMAT))
            else:
                broadcast(f"{Fore.YELLOW}{client_name}: {message_decoded}{Style.RESET_ALL}", client_name)
                
                # Start email notification in a new thread
                threading.Thread(
                    target = start_email_notifier_loop,
                    args = (notify_email(client_name, client_email, message_decoded),)
                ).start()
                
                print(f"\r{Fore.WHITE}{client_name}: {Fore.WHITE}{message_decoded}{Style.RESET_ALL}")
                print_server()

        except Exception:
            print(f"\r{Fore.LIGHTRED_EX}{client_name} has left the chat.{Style.RESET_ALL}")
            broadcast(f"{Fore.LIGHTRED_EX}{client_name} has left the chat.{Style.RESET_ALL}")
            break

    # Cleanup
    with clients_lock:
        if client_name in clients:
            del clients[client_name]
            broadcast(f"{Fore.LIGHTRED_EX}{client_name} has left the chat.{Style.RESET_ALL}")
    client_socket.close()


# Kick the client by closing their connection
def kick_client(client_socket, client_name, reason = ""):
    try:
        client_socket.send(f"{Fore.RED}{client_name} have been kicked. (Reason: {reason}){Style.RESET_ALL}".encode(FORMAT))
        client_socket.close()
        
        print(f"\r{Fore.RED}{client_name} have been kicked. (Reason: {reason}){Style.RESET_ALL}")
        print_server()
    except Exception as e:
        print(f"Failed to kick client: {e}")
        

def server_broadcast_input():
    """Handles server-side input to send messages to all connected clients."""
    while True:
        print_server()
        msg = input("")

        if msg:
            formatted_msg = f"[SERVER]: {msg}"
            broadcast(formatted_msg)
            print(f"{Fore.YELLOW}[SERVER]: {msg}{Style.RESET_ALL}")


def print_server():
    sys.stdout.write(f"{Fore.YELLOW}Server: {Style.RESET_ALL}")
    sys.stdout.flush()

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
        print(f"\rNew connection from {client_address}")
        
        print_server()

        # Send a friendly greeting first
        # Asking for name
        client_socket.send("Welcome to the chat server!\nPlease provide your name to join the chat:\n>>> ".encode(FORMAT))
        client_name = client_socket.recv(HEADER).decode(FORMAT).strip()

        # Asking for Email
        client_socket.send(f"{Fore.CYAN}Thank you, {client_name}!{Style.RESET_ALL}{Fore.YELLOW} Next, enter your email address for notifications:\n>>> {Style.RESET_ALL}".encode(FORMAT))
        client_email = client_socket.recv(HEADER).decode(FORMAT).strip()

        if is_valid_email(client_email):
            # Start a new thread only after valid name and email
            thread = threading.Thread(target = handle_client, args = (client_socket, client_name, client_email))
            thread.start()
            print(f"\r[Active Connections] {threading.active_count() - 1}")
            print(f"\r{client_name} connected with email {client_email}")
            
            print_server()
            
        else:
            client_socket.send("Invalid email format. Disconnecting....\n".encode(FORMAT))
            kick_client(client_socket, client_name, reason = "Invalid email format.")


if __name__ == "__main__":
    print("[STARTING] Server is starting ...")
    start_server()
