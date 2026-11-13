import socket
import threading

HOST = "127.0.0.1"
PORT = 5000

def receive_messages(client):
    buffer = ""

    try:
        while True:
            data = client.recv(1024).decode()

            if not data:
                break

            buffer += data

            while "\n" in buffer:
                message, buffer = buffer.split("\n", 1)

                if message.startswith("WELCOME:"):
                    print("Connected as:", message[8:])

                elif message.startswith("PUBLIC:"):
                    parts = message.split(":", 3)
                    print("\n" + parts[1] + ":" + parts[2] + ":" + parts[3])

                elif message.startswith("PRIVATE:"):
                    parts = message.split(":", 3)
                    print("\n[PRIVATE] " + parts[1] + ":" + parts[2] + ":" + parts[3])

                elif message.startswith("SYSTEM:"):
                    print("\n" + message[7:])

                elif message.startswith("USERS:"):
                    print("\nOnline users:", message[6:])

                elif message.startswith("ERROR:"):
                    print("\nError:", message[6:])

                elif message.startswith("SENT:"):
                    print("\nPrivate message sent to", message[5:])

    except:
        pass

    print("\nDisconnected from server.")

def start_client():
    nickname = input("Enter nickname: ")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((HOST, PORT))
        client.sendall((nickname + "\n").encode())

        thread = threading.Thread(target=receive_messages, args=(client), daemon=True)
        thread.start()

        while thread.is_alive():
            message = input()

            if message.lower() == "/exit":
                client.sendall(b"/exit\n")
                break

            client.sendall((message + "\n").encode())

    except ConnectionRefusedError:
        print("Server is not available.")

    except:
        print("Connection error.")

    finally:
        client.close()

if __name__ == "__main__":
    start_client()
