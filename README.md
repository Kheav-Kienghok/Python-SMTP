# Chat Application with Email Notifications

This is a multi-client chat application built using Python's `socket` module for networking, `threading` for concurrency, and `aiosmtplib` for sending asynchronous email notifications. The application supports both broadcast and direct messaging between users, and notifies users via email when they receive direct messages.

## Features

- **Multi-client support:** Multiple clients can connect to the server and chat in real-time.
- **Broadcast messages:** Messages sent by a user are broadcast to all other connected clients.
- **Direct messaging:** Users can send private messages to other users using the `/dm [recipient_name] [message]` command.
- **Email notifications:** Direct messages trigger email notifications to the recipient.
- **Input validation:** Client emails are validated before joining the chat.
- **Server commands:** The server can broadcast messages to all clients and kick clients if necessary.

## Technologies Used

- **Socket Programming:** The core client-server communication is handled using Python's `socket` library.
- **Multithreading:** Each client connection is handled on a separate thread to support multiple clients simultaneously.
- **Asynchronous Email Sending:** Email notifications are sent using `aiosmtplib`, an asynchronous SMTP library.
- **Email Validation:** Regular expressions are used to validate the format of client email addresses.
- **Environment Variables:** Sensitive information like the sender's email and password are managed via environment variables using the `dotenv` module.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
    ```

2. Install the required dependencies:
    ```
    pip install -r requirements.txt
    ```

3. Set up your environment variables:
   - Create a `.env` file in the root directory of your project.
   - Add your email credentials for sending email notifications. Replace the placeholders with your actual information:
   ```plaintext
   SENDER_EMAIL=your-email@example.com
   PASSWORD=your-email-password
   ```

4. Run the Server:
   - Start the server by executing the following command in your terminal:
   ``` 
   python server.py
   ```

5. Run the Client:
   - Open a new terminal window or tab, then navigate to the project directory and run the client:
   ```
   python client.py
   ```

6. **Connect to the Chat:**
   - When prompted, enter your name and email address to join the chat. Make sure to use a valid email format to receive notifications.

## Interaction

- **Broadcast Messages:**  
  Type your message and hit `Enter` to send it to all connected clients. Everyone in the chat will see your message in real-time.

- **Direct Messaging:**  
  To send a private message to another user, use the command:  
  `/dm [recipient_name] [message]`  
  For example:  
  `/dm John Hello, how are you?`  
  The recipient will receive an email notification for the direct message.

## Error Handling

- If an invalid email format is provided, you will be prompted to enter a valid email before joining the chat.
- If you attempt to send a direct message to a non-existent user, you will receive an error message.

## Conclusion

This chat application is designed for real-time communication with email notifications, providing a seamless experience for users. Feel free to explore and contribute to the project!
