
import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
processes = []


def open_server_panel():
    process = subprocess.Popen(
        [sys.executable, "server_control_gui.py"],
        cwd=BASE_DIR
    )
    processes.append(process)


def open_chat_client():
    process = subprocess.Popen(
        [sys.executable, "chat_client_gui.py"],
        cwd=BASE_DIR
    )
    processes.append(process)


def close_launcher():
    for process in processes:
        if process.poll() is None:
            process.terminate()

    root.destroy()


root = tk.Tk()
root.title("Multi User Chat System")
root.geometry("500x350")
root.minsize(500, 350)
root.configure(bg="#111827")
root.resizable(True, True)

header = tk.Frame(root, bg="#1f2937", height=110)
header.pack(fill="x")

tk.Label(
    header,
    text="MULTI USER CHAT SYSTEM",
    font=("Arial", 19, "bold"),
    fg="white",
    bg="#1f2937"
).pack(pady=(25, 5))

tk.Label(
    header,
    text="Main Control Center",
    font=("Arial", 10),
    fg="#94a3b8",
    bg="#1f2937"
).pack()

main_frame = tk.Frame(root, bg="#111827")
main_frame.pack(fill="both", expand=True, padx=40, pady=25)

tk.Label(
    main_frame,
    text="Select an interface",
    font=("Arial", 13, "bold"),
    fg="white",
    bg="#111827"
).pack(pady=(0, 18))


def create_button(text, command, color):
    tk.Button(
        main_frame,
        text=text,
        command=command,
        bg=color,
        fg="white",
        activebackground=color,
        activeforeground="white",
        font=("Arial", 11, "bold"),
        relief="flat",
        height=2,
        cursor="hand2"
    ).pack(fill="x", pady=7)


create_button("SERVER CONTROL PANEL", open_server_panel, "#16a34a")
create_button("CHAT CLIENT", open_chat_client, "#7c3aed")

status_label = tk.Label(
    root,
    text="Ready",
    font=("Arial", 9),
    fg="#94a3b8",
    bg="#111827"
)
status_label.pack(pady=(0, 15))

root.protocol("WM_DELETE_WINDOW", close_launcher)

root.mainloop()
