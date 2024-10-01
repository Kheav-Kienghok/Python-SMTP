# Chat Server and Client

This project implements a chat server and client using Python's socket programming. The server allows multiple clients to connect, send messages, and receive direct messages (DMs). It also sends email notifications for new messages and DMs.

## Features

- **Multi-client Support**: Multiple clients can connect to the server simultaneously.
- **Broadcast Messaging**: Clients can send messages to all connected clients.
- **Direct Messaging**: Clients can send direct messages to specific users.
- **Email Notifications**: Email notifications are sent for every new message and direct message (requires valid email credentials).

## Requirements

- Python 3.x
- `colorama` library for colored terminal output
- `python-dotenv` library to manage environment variables
- `smtplib` for sending emails

You can install the required libraries using pip:

```bash
pip install colorama python-dotenv
```

## Environment Variables

Before running the server, create a `.env` file in the root directory and set the following variables:

```plaintext
SENDER_EMAIL = your_email@gmail.com
PASSWORD = your_email_password
```

### Variable Descriptions

- **`SENDER_EMAIL`**: The email address from which notification emails will be sent. This should be a valid email account.
  
- **`PASSWORD`**: The password for the email account specified in `SENDER_EMAIL`. Ensure that your email settings allow for SMTP access. For Gmail, you may need to enable "Less secure app access" or use an App Password if you have two-factor authentication enabled.
