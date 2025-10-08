import tkinter as tk
from tkinter import ttk

class SplashScreen:
    def __init__(self, root, next_app):
        self.root = root
        self.next_app = next_app

        # Konfigurasi tampilan splash
        self.root.title("Loading...")
        self.root.geometry("500x300")
        self.root.configure(bg="#1e1e1e")
        self.root.overrideredirect(True)  # Hilangkan title bar

        tk.Label(
            self.root,
            text="Inventory Manager",
            font=("Segoe UI", 20, "bold"),
            bg="#1e1e1e",
            fg="white"
        ).pack(pady=80)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=20)

        self.percent_label = tk.Label(self.root, text="0%", fg="white", bg="#1e1e1e")
        self.percent_label.pack()

        self.loading_progress()

    def loading_progress(self):
        for i in range(101):
            self.root.after(i * 20, lambda i=i: self.update_progress(i))

    def update_progress(self, value):
        self.progress["value"] = value
        self.percent_label.config(text=f"{value}%")
        if value == 100:
            self.root.after(500, self.start_main_app)

    def start_main_app(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.overrideredirect(False)
        self.next_app()
