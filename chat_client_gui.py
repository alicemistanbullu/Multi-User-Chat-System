
import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog
import queue

HOST = "127.0.0.1"
PORT = 5000

messages = queue.Queue()


class ChatGUI:
    def __init__(self, root, nickname):
        self.root = root
        self.nickname = nickname
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.private_user = None
        self.users = []

        self.root.title("Multi-User Chat")
        self.root.geometry("950x650")
        self.root.minsize(750, 500)
        self.root.configure(bg="#111b21")

        try:
            self.client.connect((HOST, PORT))
            self.client.sendall((nickname + "\n").encode())
            self.connected = True
        except:
            messagebox.showerror("Connection Error", "Server is not available.")
            self.root.destroy()
            return

        self.create_interface()

        self.receive_thread = threading.Thread(
            target=self.receive_messages,
            daemon=True
        )
        self.receive_thread.start()

        self.root.after(100, self.process_messages)
        self.root.protocol("WM_DELETE_WINDOW", self.exit_chat)

    def create_interface(self):
        header = tk.Frame(self.root, bg="#202c33", height=65)
        header.pack(fill="x")

        tk.Label(
            header,
            text="Multi-User Chat",
            bg="#202c33",
            fg="white",
            font=("Arial", 18, "bold")
        ).pack(side="left", padx=25, pady=15)

        self.status = tk.Label(
            header,
            text="● Connected",
            bg="#202c33",
            fg="#25d366",
            font=("Arial", 11)
        )
        self.status.pack(side="right", padx=25)

        main = tk.Frame(self.root, bg="#111b21")
        main.pack(fill="both", expand=True, padx=15, pady=15)

        sidebar = tk.Frame(main, bg="#202c33", width=220)
        sidebar.pack(side="left", fill="y", padx=(0, 12))
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="ONLINE USERS",
            bg="#202c33",
            fg="#25d366",
            font=("Arial", 11, "bold")
        ).pack(anchor="w", padx=15, pady=15)

        self.user_list = tk.Listbox(
            sidebar,
            bg="#202c33",
            fg="white",
            selectbackground="#005c4b",
            selectforeground="white",
            font=("Arial", 11),
            borderwidth=0,
            highlightthickness=0
        )
        self.user_list.pack(fill="both", expand=True, padx=10, pady=5)

        self.user_list.bind("<Double-Button-1>", self.select_private_user)

        tk.Button(
            sidebar,
            text="Private Chat",
            command=self.select_private_user,
            bg="#075e54",
            fg="white",
            activebackground="#128c7e",
            relief="flat"
        ).pack(fill="x", padx=10, pady=10)

        tk.Button(
            sidebar,
            text="Public Chat",
            command=self.select_public_chat,
            bg="#34434d",
            fg="white",
            relief="flat"
        ).pack(fill="x", padx=10, pady=(0, 10))

        chat = tk.Frame(main, bg="#0b141a")
        chat.pack(side="right", fill="both", expand=True)

        self.chat_title = tk.Label(
            chat,
            text="Public Chat",
            bg="#202c33",
            fg="white",
            font=("Arial", 12, "bold"),
            anchor="w",
            padx=15,
            pady=15
        )
        self.chat_title.pack(side="top", fill="x")

        bottom = tk.Frame(chat, bg="#202c33")
        bottom.pack(side="bottom", fill="x", padx=10, pady=10)

        self.message_entry = tk.Entry(
            bottom,
            bg="#2a3942",
            fg="white",
            insertbackground="white",
            font=("Arial", 12),
            relief="flat"
        )
        self.message_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=5,
            ipady=10
        )

        self.message_entry.bind("<Return>", self.send_message)

        tk.Button(
            bottom,
            text="Send",
            command=self.send_message,
            bg="#075e54",
            fg="white",
            activebackground="#128c7e",
            relief="flat",
            padx=20,
            pady=8
        ).pack(side="right", padx=5)

        self.chat_area = tk.Text(
            chat,
            bg="#0b141a",
            fg="#e9edef",
            font=("Arial", 11),
            wrap="word",
            state="disabled",
            borderwidth=0,
            padx=15,
            pady=15
        )
        self.chat_area.pack(fill="both", expand=True)

        self.chat_area.tag_config("public", foreground="#53d6b0")
        self.chat_area.tag_config("private", foreground="#8ab4f8")
        self.chat_area.tag_config("system", foreground="#aebac1")
        self.chat_area.tag_config("error", foreground="#ff8585")

    def add_message(self, message, tag="public"):
        self.chat_area.config(state="normal")
        self.chat_area.insert("end", message + "\n\n", tag)
        self.chat_area.see("end")
        self.chat_area.config(state="disabled")

    def receive_messages(self):
        buffer = ""

        try:
            while self.connected:
                data = self.client.recv(1024).decode()

                if not data:
                    break

                buffer += data

                while "\n" in buffer:
                    message, buffer = buffer.split("\n", 1)
                    messages.put(message)

        except:
            pass

        self.connected = False
        messages.put("DISCONNECTED")

    def process_messages(self):
        while not messages.empty():
            message = messages.get()

            if message == "DISCONNECTED":
                self.status.config(
                    text="● Disconnected",
                    fg="#ff6b6b"
                )
                self.add_message("Server connection closed.", "error")
                continue

            if message.startswith("WELCOME:"):
                self.add_message(
                    "Connected as " + message[8:],
                    "system"
                )

            elif message.startswith("PUBLIC:"):
                content = message[7:]
                parts = content.split("  ", 1)

                if len(parts) == 2:
                    self.add_message(
                        "[" + parts[0] + "] " + parts[1],
                        "public"
                    )
                else:
                    self.add_message(content, "public")

            elif message.startswith("PRIVATE:"):
                content = message[8:]
                parts = content.split("  ", 1)

                if len(parts) == 2:
                    self.add_message(
                        "[PRIVATE] [" + parts[0] + "] " + parts[1],
                        "private"
                    )
                else:
                    self.add_message(
                        "[PRIVATE] " + content,
                        "private"
                    )

            elif message.startswith("SYSTEM:"):
                self.add_message(message[7:], "system")

            elif message.startswith("USERS:"):
                self.users = message[6:].split(",") if message[6:] else []
                self.update_users()

            elif message.startswith("ERROR:"):
                self.add_message(message[6:], "error")

            elif message.startswith("SENT:"):
                self.add_message(
                    "Private message sent to " + message[5:],
                    "system"
                )

        self.root.after(100, self.process_messages)

    def update_users(self):
        selected = self.private_user

        self.user_list.delete(0, "end")

        for user in self.users:
            if user != self.nickname:
                self.user_list.insert("end", user)

        if selected not in self.users:
            self.private_user = None
            self.chat_title.config(text="Public Chat")

    def select_private_user(self, event=None):
        selection = self.user_list.curselection()

        if not selection:
            return

        self.private_user = self.user_list.get(selection[0])
        self.chat_title.config(
            text="Private Chat - " + self.private_user
        )

    def select_public_chat(self):
        self.private_user = None
        self.chat_title.config(text="Public Chat")

    def send_message(self, event=None):
        text = self.message_entry.get().strip()

        if not text or not self.connected:
            return

        if text == "/exit":
            self.exit_chat()
            return

        if text == "/users":
            self.client.sendall(b"/users\n")

        elif self.private_user:
            command = "/msg " + self.private_user + " " + text
            self.client.sendall((command + "\n").encode())

        else:
            self.client.sendall((text + "\n").encode())

        self.message_entry.delete(0, "end")

    def exit_chat(self):
        if self.connected:
            try:
                self.client.sendall(b"/exit\n")
            except:
                pass

        self.connected = False

        try:
            self.client.close()
        except:
            pass

        self.root.destroy()


def start_gui():
    root = tk.Tk()
    root.withdraw()

    nickname = simpledialog.askstring(
        "Login",
        "Enter your nickname:",
        parent=root
    )

    if not nickname:
        root.destroy()
        return

    root.deiconify()
    ChatGUI(root, nickname)
    root.mainloop()


if __name__ == "__main__":
    start_gui()
