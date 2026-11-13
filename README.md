# Multi-User Chat System

## 1. Project Description

This project is a multi-user chat application developed using Python TCP sockets and WebSockets.

The system supports multiple clients, public and private messaging, unique nicknames, server-side logging, rate limiting, and live server monitoring.

The application provides both a terminal-based chat client and a graphical user interface (GUI). A launcher is also included to make it easier to open the application interfaces.

## 2. Project Structure

```text
NetworkProgramming-2/
│
├── launcher.py
├── chat_server.py
├── chat_client.py
├── chat_client_gui.py
├── server_control_gui.py
├── monitoring_service.py
├── monitoring.html
├── requirements.txt
├── README.md
│
└── logs/
    └── chat_log.txt
```

## 3. Requirements

- Python 3
- websockets 15.0.1
- Python virtual environment (venv)
- Tkinter (for graphical interfaces)

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required package:

```bash
pip install -r requirements.txt
```

## 4. Running the Application

### Option 1: Using the Launcher

The launcher provides access to the graphical interfaces from a single window.

Run:

```bash
python launcher.py
```

The launcher provides two options:

- **Server Control Panel:** Opens the server control interface.
- **Chat Client:** Opens the graphical chat client.

To start the chat server:

1. Open the Server Control Panel.
2. Click the `START SERVER` button.
3. The TCP chat server and monitoring services will start.

To stop the server, click the `STOP SERVER` button.

### Open the Monitoring Dashboard

After starting the server, open the following address in a web browser:

```text
http://localhost:8000/monitoring.html
```

The monitoring page displays connected users, processed messages, and live server events.

### Option 2: Using the Terminal

The application can also be started without the graphical interfaces.

Start the server:

```bash
python chat_server.py
```

The server starts the following services:

- TCP Chat Server: Port 5000
- HTTP Monitoring: Port 8000
- WebSocket Monitoring: Port 8765

Open another terminal, activate the virtual environment, and start a chat client:

```bash
source .venv/bin/activate
python chat_client.py
```

Enter a nickname when requested.

Run the same command in additional terminals to connect multiple users.

## 5. Chat Commands

| Command | Description |
|---|---|
| `/users` | Displays the online users |
| `/msg nickname message` | Sends a private message |
| `/exit` | Leaves the chat |

Normal text messages are sent publicly to all connected users.

## 6. Message Handling

The application uses TCP sockets for chat communication.

Messages are encoded using UTF-8. Newline characters (`\n`) are used to identify message boundaries.

The server handles fragmented and multiple messages received through TCP.

The maximum accepted chat message length is 2000 characters.

The server assigns a unique nickname to each connected client. If a nickname is already in use, a number is added to it.

Nicknames beginning with `*` are not accepted from direct clients.

## 7. Logging and Monitoring

Server events are stored in:

```text
logs/chat_log.txt
```

The log file includes:

- Connection events
- Disconnection events
- Public messages
- Private messages
- Error events
- Rate-limit events

The monitoring page uses WebSockets to receive live server events.

It displays:

- Current connected user count
- Processed message count
- Live server events

The monitoring service runs on separate ports from the chat server.

## 8. Rate Limiting

The server applies a per-user rate limit.

- Maximum 5 messages within 10 seconds.
- When the limit is exceeded, the user is muted for 10 seconds.
- The server sends an error message to the user.
- Rate-limit events are recorded in the log file.

Both public and private messages are subject to this limit.
