
import socket
import threading

HOST = "0.0.0.0"
PORT = 5000

clients = {}
lock = threading.Lock()


def send_message(client, message):
    try:
        client.sendall((message + "\n").encode())
    except:
        pass


def broadcast(message):
    with lock:
        connected = list(clients.values())

    for client in connected:
        send_message(client, message)


def send_users():
    with lock:
        users = list(clients.keys())

    broadcast("USERS:" + ",".join(users))


def handle_client(conn, addr):
    nickname = None

    try:
        nickname = conn.recv(1024).decode().strip()

        if not nickname or nickname.startswith("*"):
            send_message(conn, "ERROR:Invalid nickname")
            return

        with lock:
            original = nickname
            number = 1

            while nickname in clients:
                nickname = original + str(number)
                number += 1

            clients[nickname] = conn

        send_message(conn, "WELCOME:" + nickname)
        broadcast("SYSTEM:" + nickname + " joined the chat.")
        send_users()

        print(nickname, "connected from", addr)

        buffer = ""

        while True:
            data = conn.recv(1024).decode()

            if not data:
                break

            buffer += data

            while "\n" in buffer:
                message, buffer = buffer.split("\n", 1)

                if message.startswith("/msg "):
                    parts = message.split(" ", 2)

                    if len(parts) < 3:
                        send_message(conn, "ERROR:Invalid private message")
                        continue

                    recipient = parts[1]
                    private_message = parts[2]

                    with lock:
                        target = clients.get(recipient)

                    if target:
                        send_message(
                            target,
                            "PRIVATE:" + nickname + ":" + private_message
                        )
                        send_message(conn, "SENT:" + recipient)
                    else:
                        send_message(conn, "ERROR:User not found")

                elif message == "/users":
                    send_users()

                elif message == "/quit":
                    return

                elif message:
                    broadcast("PUBLIC:" + nickname + ":" + message)

    except:
        pass

    finally:
        if nickname:
            with lock:
                if nickname in clients and clients[nickname] == conn:
                    del clients[nickname]

            broadcast("SYSTEM:" + nickname + " left the chat.")
            send_users()

        conn.close()
        print("Client disconnected:", addr)


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()

    print("Chat server started.")
    print("Listening on port", PORT)

    while True:
        conn, addr = server.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(conn, addr)
        )

        thread.start()


if __name__ == "__main__":
    start_server()
