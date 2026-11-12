
import socket
import threading
import os
import time
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5000

clients = {}
client_data = {}
lock = threading.Lock()

os.makedirs("logs", exist_ok=True)


def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def write_log(message):
    with open("logs/chat_log.txt", "a", encoding="utf-8") as file:
        file.write(f"[{get_time()}] {message}\n")


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


def check_rate_limit(nickname):
    now = time.time()

    with lock:
        data = client_data.get(nickname)

        if data is None:
            return False

        if now < data["muted_until"]:
            return False

        data["message_times"] = [
            t for t in data["message_times"]
            if now - t < 10
        ]

        if len(data["message_times"]) >= 5:
            data["muted_until"] = now + 10
            write_log(f"RATE LIMIT | {nickname}")
            print(f"{nickname} muted for 10 seconds.")
            return False

        data["message_times"].append(now)

    return True


def handle_client(conn, addr):
    nickname = None

    try:
        nickname_data = b""

        while not nickname_data.endswith(b"\n"):
            part = conn.recv(1)

            if not part:
                return

            nickname_data += part

            if len(nickname_data) > 100:
                return

        nickname = nickname_data.decode().strip()

        if not nickname or nickname.startswith("*") or len(nickname) > 20:
            send_message(conn, "ERROR:Invalid nickname")
            return

        with lock:
            original = nickname
            number = 1

            while nickname in clients:
                nickname = original + str(number)
                number += 1

            clients[nickname] = conn

            client_data[nickname] = {
                "message_times": [],
                "muted_until": 0
            }

        send_message(conn, "WELCOME:" + nickname)

        broadcast("SYSTEM:" + nickname + " joined the chat.")
        send_users()

        write_log(f"CONNECTED | {nickname} | {addr[0]}")
        print(f"{nickname} connected from {addr}")
        buffer = ""

        while True:
            data = conn.recv(1024).decode()

            if not data:
                break

            buffer += data

            while "\n" in buffer:
                message, buffer = buffer.split("\n", 1)
                message = message.strip()

                if not message:
                    continue

                if message == "/quit":
                    return

                if message == "/users":
                    send_users()
                    continue

                if message.startswith("/msg "):
                    parts = message.split(" ", 2)

                    if len(parts) < 3 or not parts[2].strip():
                        send_message(conn, "ERROR:Invalid private message")
                        continue

                    recipient = parts[1]
                    private_message = parts[2]

                    if len(private_message) > 2000:
                        send_message(conn, "ERROR:Message too long")
                        continue

                    if not check_rate_limit(nickname):
                        send_message(conn, "ERROR:Rate limit exceeded. Muted for 10 seconds.")
                        continue

                    with lock:
                        target = clients.get(recipient)

                    if target:
                        send_message(
                            target,
                            "PRIVATE:" + nickname + ":" + private_message
                        )

                        send_message(conn, "SENT:" + recipient)

                        write_log(
                            f"PRIVATE | {nickname} -> {recipient} | {private_message}"
                        )
                    else:
                        send_message(conn, "ERROR:User not found")

                        write_log(
                            f"PRIVATE FAILED | {nickname} -> {recipient}"
                        )

                else:
                    if len(message) > 2000:
                        send_message(conn, "ERROR:Message too long")
                        continue

                    if not check_rate_limit(nickname):
                        send_message(conn, "ERROR:Rate limit exceeded. Muted for 10 seconds.")
                        continue

                    broadcast("PUBLIC:" + nickname + ":" + message)

                    write_log(
                        f"PUBLIC | {nickname} | {message}"
                    )

    except:
        write_log(f"ERROR | {addr[0]}")

    finally:
        if nickname:
            with lock:
                if nickname in clients and clients[nickname] == conn:
                    del clients[nickname]
                    del client_data[nickname]

            broadcast("SYSTEM:" + nickname + " left the chat.")
            send_users()

            write_log(f"DISCONNECTED | {nickname}")
            print(f"{nickname} dissconnected.")
        conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()

    print("Chat server started.")
    print("Listening on port", PORT)

    try:
        while True:
            conn, addr = server.accept()

            thread = threading.Thread(
                target=handle_client,
                args=(conn, addr)
            )

            thread.start()

    except KeyboardInterrupt:
        print("\nServer shutting down.")

    finally:
        server.close()


if __name__ == "__main__":
    start_server()
