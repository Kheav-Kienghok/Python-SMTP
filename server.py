from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import socket
import threading
import smtplib
import os


load_dotenv()
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
PASSWORD = os.getenv("PASSWORD")


PORT = 5555
HEADER = 1024
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"


# Store client information: key is the name, value is dict of (socket, email)
clients = {}

# Broadcast messages to all clients
def broadcast(message, sender_name):
    for client_name, client_info in clients.items():
        if client_name != sender_name:
            try:
                client_info["socket"].send(message)
            except Exception:
                client_info["socket"].close()


# Send a direct message to a specific client
def direct_message(sender_name, recipient_name, message):
    if recipient_name in clients:
        try:
            direct_msg = f"[DM from {sender_name}] {message}".encode()
            clients[recipient_name]["socket"].send(direct_msg)
            print(f"Direct message from {sender_name} to {recipient_name}: {message}")
            
            # Send an email notification to the recipient
            notify_email(sender_name, clients[recipient_name]["email"], message, dm=True)
            return True  # Message successfully sent
        
        except Exception as e:
            print(f"Failed to send direct message: {e}")
            return False
            
    print(f"Client {recipient_name} not found.")
    return False  # Recipient not found


# Notify clients via email when a message is sent
def notify_email(sender_name, recipient_email, message, dm = False):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 465   # Using the SSL port for SMTP
    smtp_user = SENDER_EMAIL
    smtp_password = PASSWORD

    # Send notification to all other clients except the sender
    recipients = [client_info["email"] for client_name, client_info in clients.items() if client_info["email"] != recipient_email]


    # If it's a direct message, we only notify the recipient
    if dm:
        recipients = [recipient_email]
        
    if not recipients:
        return  # No one to notify

    subject = f"Direct message from {sender_name}" if dm else f"New message from {sender_name}"
    body = f"{sender_name} sent you the following direct message:\n\n{message}" if dm else f"{sender_name} sent the following message:\n\n{message}"

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Use SMTP_SSL for a secure connection
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, recipients, msg.as_string())
        server.quit()
        print(f"Notification email sent to {recipients}")

    except Exception as e:
        print(f"Failed to send email: {e}")

    
def handle_client(client_socket, client_name, client_email):
    while True:
        try:
            message = client_socket.recv(HEADER)
            if not message:
                break
            message_decoded = message.decode()
            
            # Check if the message is a direct message
            if message_decoded.startswith("/dm"):
                # Expected format: /dm recipient_name message_content
                parts = message_decoded.split(" ", 2)
                if len(parts) < 3:
                    client_socket.send("Invalid direct message format. Use: /dm [recipient_name] [message]\n".encode())
                    continue
                recipient_name = parts[1]
                dm_message = parts[2]
                
                # Send direct message
                if not direct_message(client_name, recipient_name, dm_message):
                    client_socket.send(f"Failed to send message to {recipient_name}. They might be offline.\n".encode())
            else:
                # Broadcast the message to all other clients
                broadcast(message, client_name)
                print(f"{client_name} says: {message_decoded}")
                notify_email(client_name, client_email, message_decoded)
        except Exception as e:
            print(f"Error with client {client_name}: {e}")
            break

    client_socket.close()

# Start the server and accept new clients
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER, PORT))
    server_socket.listen(5)
    print("Server is listening...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"New connection from {client_address}")

        # Ask for client name and email
        client_socket.send("Enter your name: ".encode())
        client_name = client_socket.recv(1024).decode()
        client_socket.send("Enter your email: ".encode())
        client_email = client_socket.recv(1024).decode()

        # Add the new client to the dictionary
        clients[client_name] = {"socket": client_socket, "email": client_email}
        print(f"Client {client_name} connected with email {client_email}")

        # Start a new thread to handle the client
        thread = threading.Thread(target = handle_client, args = (client_socket, client_name, client_email))
        thread.start()

start_server()
