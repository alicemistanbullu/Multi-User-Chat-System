import os
import asyncio
import threading
import http.server
import socketserver
import websockets
import json
from datetime import datetime

HTTP_PORT = 8000
WS_PORT = 8765

connected = set()
loop = None

user_count = 0
message_count = 0


def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


async def broadcast(data):
    if connected:
        message = json.dumps(data)

        await asyncio.gather(
            *(ws.send(message) for ws in list(connected)),
            return_exceptions=True
        )


def send_event(event_type, message, users=None, messages=None):
    global user_count, message_count

    if users is not None:
        user_count = users

    if messages is not None:
        message_count = messages

    data = {
        "type": event_type,
        "message": message,
        "time": get_time(),
        "users": user_count,
        "messages": message_count
    }

    if loop is not None:
        asyncio.run_coroutine_threadsafe(
            broadcast(data),
            loop
        )


async def ws_handler(websocket):
    connected.add(websocket)

    await websocket.send(json.dumps({
        "type": "stats",
        "users": user_count,
        "messages": message_count
    }))

    try:
        await websocket.wait_closed()
    finally:
        connected.remove(websocket)


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)

    def do_GET(self):
        if self.path == "/":
            self.path == "/monitoring.html"

        return super().do_GET()


def start_http_server():
    with socketserver.ThreadingTCPServer(
        ("0.0.0.0", HTTP_PORT),
        CustomHandler
    ) as server:
        print(f"HTTP server running on port {HTTP_PORT}")
        server.serve_forever()


async def start_ws_server():
    global loop

    loop = asyncio.get_running_loop()

    async with websockets.serve(
        ws_handler,
        "0.0.0.0",
        WS_PORT
    ):
        print(f"WebSocket server running on port {WS_PORT}")
        await asyncio.Future()


def start_monitoring():
    threading.Thread(
        target=start_http_server,
        daemon=True
    ).start()

    asyncio.run(start_ws_server())


if __name__ == "__main__":
    start_monitoring()
