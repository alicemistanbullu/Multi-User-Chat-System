
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import os
import signal

class ServerControlGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Server Control Panel")
        self.root.geometry("850x600")
        self.root.configure(bg="#111827")

        self.process = None
        self.running = False

        self.create_interface()
        self.check_log()

    def create_interface(self):
        header = tk.Frame(self.root, bg="#1f2937", height=80)
        header.pack(fill="x")

        tk.Label(
            header,
            text="CHAT SERVER CONTROL",
            font=("Arial", 19, "bold"),
            fg="white",
            bg="#1f2937"
        ).pack(pady=20)

        status_frame = tk.Frame(self.root, bg="#111827")
        status_frame.pack(fill="x", padx=25, pady=20)

        tk.Label(
            status_frame,
            text="Server Status:",
            font=("Arial", 12),
            fg="white",
            bg="#111827"
        ).pack(side="left")

        self.status_label = tk.Label(
            status_frame,
            text="STOPPED",
            font=("Arial", 12, "bold"),
            fg="#ef4444",
            bg="#111827"
        )
        self.status_label.pack(side="left", padx=10)

        button_frame = tk.Frame(self.root, bg="#111827")
        button_frame.pack(pady=10)

        self.start_button = tk.Button(
            button_frame,
            text="START SERVER",
            command=self.start_server,
            bg="#16a34a",
            fg="white",
            font=("Arial", 11, "bold"),
            width=18,
            relief="flat"
        )
        self.start_button.pack(side="left", padx=10)

        self.stop_button = tk.Button(
            button_frame,
            text="STOP SERVER",
            command=self.stop_server,
            bg="#dc2626",
            fg="white",
            font=("Arial", 11, "bold"),
            width=18,
            relief="flat",
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=10)

        log_title = tk.Label(
            self.root,
            text="SERVER LOGS",
            font=("Arial", 13, "bold"),
            fg="white",
            bg="#111827"
        )
        log_title.pack(anchor="w", padx=25, pady=(25, 10))

        self.log_area = tk.Text(
            self.root,
            bg="#1f2937",
            fg="#d1d5db",
            font=("Consolas", 10),
            relief="flat",
            state="disabled"
        )
        self.log_area.pack(fill="both", expand=True, padx=25, pady=(0, 25))

        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

    def start_server(self):
        if self.process is not None and self.process.poll() is None:
            return

        self.process = subprocess.Popen(
            ["python", "-u", "chat_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        self.running = True
        self.status_label.config(text="RUNNING", fg="#22c55e")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

        threading.Thread(
            target=self.read_output,
            daemon=True
        ).start()

    def read_output(self):
        for line in self.process.stdout:
            self.root.after(0, self.add_log, line.rstrip())

        self.root.after(0, self.server_stopped)

    def add_log(self, message):
        self.log_area.config(state="normal")
        self.log_area.insert("end", message + "\n")
        self.log_area.see("end")
        self.log_area.config(state="disabled")

    def stop_server(self):
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()

    def server_stopped(self):
        self.running = False
        self.status_label.config(text="STOPPED", fg="#ef4444")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

    def check_log(self):
        if os.path.exists("logs/chat_log.txt"):
            try:
                with open("logs/chat_log.txt", "r", encoding="utf-8") as file:
                    lines = file.readlines()

                self.log_area.config(state="normal")
                self.log_area.delete("1.0", "end")
                self.log_area.insert("end", "".join(lines[-100:]))
                self.log_area.see("end")
                self.log_area.config(state="disabled")
            except:
                pass

        self.root.after(3000, self.check_log)

    def close_window(self):
        if self.process is not None and self.process.poll() is None:
            answer = messagebox.askyesno(
                "Exit",
                "Server is running. Do you want to stop it and exit?"
            )

            if not answer:
                return

            self.process.terminate()

        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerControlGUI(root)
    root.mainloop()
