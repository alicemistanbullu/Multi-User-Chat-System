import socket
import threading
import json
import os
import time
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5000

clients = {}
lock = threading.Lock()
log_lock = threading.Lock()
message_count = 0

os.makedirs("logs", exist_ok=True)

def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_log(message):
    with log_lock:
        with open("logs/chat_log.txt", "a", encoding="utf-8") as file:
            file.write(f"[{get_time()}] {message}\n")

def send_message(client, data):
    try:
        message = json.dumps(data) + "\n"
        with client["send_lock"]:
            client["socket"].sendall(message.encode("utf-8"))
        return True
    except:
        return False

def send_users():
    with lock:
        users = list(clients.keys())
        connected = list(clients.values())

    for client in connected:
        send_message(client,{
            "type": "users",
            "users": users})

def broadcast(data):
    with lock:
        connected = list(clients.values())

    for client in connected:
        send_message(client, data)

def assign_nickname(name):
    original = name
    number = 1

    while name in clients:
        name = original + str(number)
        number += 1
    return name

def remove_client(nickname, conn):
    if nickname is None:
        return

    with lock:
        if nickname in clients and clients[nickname]["socket"] == conn:
            del clients[nickname]
        else:
            return

    broadcast({
        "type": "system",
        "message": nickname + " left the chat.",
        "time": get_time()})

    send_users()
    write_log(f"DISCONNECTED | {nickname}")

def handle_client(conn, addr):
    global message_count

    nickname = None
    client = {
        "socket": conn,
        "send_lock": threading.Lock(),
        "message_times": [],
        "muted_until": 0}

    try:
        file = conn.makefile("r", encoding="utf-8")
        line = file.readline(8193)

        if not line or len(line) > 8192 or not line.endswith("\n"):
            return
        data = json.loads(line)

        if data.get("type") != "register":
            return
        requested_name = data.get("nickname", "").strip()

        if not isinstance(requested_name, str):
            return

        if not requested_name or len(requested_name) > 20:
            send_message(client, {
                "type": "error",
                "message": "Invalid nickname."})
            return

        if requested_name.startswith("*"):
            send_message(client, {
                "type": "error",
                "message": "Nickname cannot start with *."})
            return

        with lock:
            nickname = assign_nickname(requested_name)
            client["nickname"] = nickname
            clients[nickname] = client

        send_message(client, {
            "type": "welcome",
            "nickname": nickname})

        write_log(f"CONNECTED | {nickname} | {addr[0]}")
        broadcast({
            "type": "system",
            "message": nickname + " joined the chat.",
            "time": get_time()})

        send_users()

        for line in file:
            if len(line) > 8192 or not line.endswith("\n"):
                send_message(client, {
                    "type": "error",
                    "message": "Message too large or incomplete."})
                break

            try:
                data = json.loads(line)
            except:
                send_message(client, {
                    "type": "error",
                    "message": "Invalid message format."})
                continue
            msg_type = data.get("type")
            message = data.get("message")

            if msg_type not in ["public", "private"]:
                send_message(client, {
                    "type": "error",
                    "message": "Invalid message type."})
                continue

            if not isinstance(message, str) or not message.strip() or len(message) > 2000:
                send_message(client, {
                    "type": "error",
                    "message": "Invalid message."})
                continue
            now = time.time()

            if now < client["muted_until"]:
                send_message(client, {
                    "type": "error",
                    "message": "You are muted for 10 seconds."})
                continue
            client["message_times"] = [
                t for t in client["message_times"]
                if now - t < 10]

            if len(client["message_times"]) >= 5:
                client["muted_until"] = now + 10

                send_message(client, {
                    "type": "error",
                    "message": "Rate limit exceeded. Muted for 10 seconds."})

                write_log(f"RATE LIMIT | {nickname}")
                continue
            client["message_times"].append(now)

            if msg_type == "public":
                with lock:
                    message_count += 1

                public_data = {
                    "type": "public",
                    "sender": nickname,
                    "message": message,
                    "time": get_time()}

                broadcast(public_data)

                write_log(
                    f"PUBLIC | {nickname} | {message}")

            elif msg_type == "private":
                recipient = data.get("recipient")

                if not isinstance(recipient, str):
                    continue

                with lock:
                    target = clients.get(recipient)

                if target is None:
                    send_message(client, {
                        "type": "error",
                        "message": "User not found."})

                    write_log(f"PRIVATE FAILED | {nickname} -> {recipient}")
                    continue
                private_data = {
                    "type": "private",
                    "sender": nickname,
                    "message": message,
                    "time": get_time()}

                if not send_message(target, private_data):
                    send_message(client, {
                        "type": "error",
                        "message": "User is not available."})
                    continue
                send_message(client, {
                    "type": "private_sent",
                    "recipient": recipient,
                    "message": message,
                    "time": get_time()})

                with lock:
                    message_count += 1

                write_log(f"PRIVATE | {nickname} -> {recipient} | {message}")

    except:
        write_log(f"ERROR | {addr[0]}")

    finally:
        remove_client(nickname, conn)
        conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()

    print("Chat server started.")
    print(f"Listening on {HOST}:{PORT}")

    try:
        while True:
            conn, addr = server.accept()

            thread = threading.Thread(
                target=handle_client,
                args=(conn, addr))

            thread.start()

    except KeyboardInterrupt:
        print("\nServer shutting down.")

    finally:
        server.close()


if __name__ == "__main__":
    start_server()
