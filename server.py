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

# Store client information: (socket, name, email)
clients = []

# Broadcast messages to all clients
def broadcast(message, sender_socket):
    for client_socket, _, _ in clients:
        if client_socket != sender_socket:
            try:
                client_socket.send(message)
            except Exception:
                client_socket.close()

# Notify clients via email when a message is sent
def notify_email(sender_name, sender_email, message):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 465   # Using the SSL port for SMTP
    smtp_user = SENDER_EMAIL
    smtp_password = PASSWORD

    # Send notification to all other clients except the sender
    recipients = [email for _, _, email in clients if email != sender_email]

    if not recipients:
        return  # No one to notify

    subject = f"New message from {sender_name}"
    body = f"{sender_name} sent the following message:\n\n{message}"

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

# Handle individual client connection
def handle_client(client_socket, client_name, client_email):
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break
            broadcast(message, client_socket)
            print(f"{client_name} says: {message.decode()}")
            notify_email(client_name, client_email, message.decode())
        except Exception as e:
            print(f"Error with client {client_name}: {e}")
            break

    client_socket.close()

# Start the server and accept new clients
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 5555))
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

        # Add the new client to the list
        clients.append((client_socket, client_name, client_email))
        print(f"Client {client_name} connected with email {client_email}")

        # Start a new thread to handle the client
        thread = threading.Thread(target = handle_client, args = (client_socket, client_name, client_email))
        thread.start()

start_server()
