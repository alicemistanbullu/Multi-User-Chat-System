
import socket
import time

HOST = "127.0.0.1"
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

client.sendall(b"FragmentTest\n")
time.sleep(1)

parts = [
    b"Fragmented ",
    b"TCP ",
    b"message ",
    b"test\n"
]

for part in parts:
    client.sendall(part)
    time.sleep(0.5)

time.sleep(1)
client.close()
