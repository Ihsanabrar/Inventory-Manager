import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from utils.database import get_connection

class LoginPage:
    def __init__(self, parent, on_login_success=None):
        self.parent = parent
        self.on_login_success = on_login_success

        # Container center
        container = tb.Frame(self.parent, padding=(30,30), bootstyle="dark")
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        tb.Label(container, text="🔐 Login Admin", font=("Segoe UI", 18, "bold"), bootstyle="inverse-dark").pack(pady=(0,15))

        # Username
        tb.Label(container, text="Username", bootstyle="light").pack(anchor="w", pady=(4,2))
        self.entry_user = tb.Entry(container, width=30)
        self.entry_user.pack(pady=4)

        # Password
        tb.Label(container, text="Password", bootstyle="light").pack(anchor="w", pady=(8,2))
        self.entry_pass = tb.Entry(container, width=30, show="*")
        self.entry_pass.pack(pady=4)

        # Login button (primary accent)
        tb.Button(container, text="Login", bootstyle="primary", width=12, command=self.check_login).pack(pady=(12,0))

    def check_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        # Cek ke database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            messagebox.showinfo("Sukses", f"Selamat datang, {username}!")
            if self.on_login_success:
                self.on_login_success()
            return

        # Fallback default
        if username == "admin" and password == "12345":
            messagebox.showinfo("Sukses", "Login berhasil dengan akun default!")
            if self.on_login_success:
                self.on_login_success()
            return

        messagebox.showerror("Gagal", "Username atau password salah!")
