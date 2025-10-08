import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from utils.database import init_db
from ui.dashboard import DashboardApp
from ui.login_page import LoginPage
from ui.barang import BarangApp
from ui.splash_screen import SplashScreen
from ui.laporan import LaporanApp
import sys, os
from utils.database import backup_database

init_db()


def resource_path(relative_path):
    """Dapatkan path absolut (baik dari .py maupun .exe)"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Manager")
        # ukuran default jendela kecil (user requested)
        self.root.geometry("900x650")
        self.root.minsize(800, 600)

        # Frame aktif
        self.current_frame = None

        # Mulai dari halaman login
        self.show_login()

    def clear_frame(self):
        """Hapus frame lama sebelum pindah halaman"""
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None

    def show_login(self):
        """Tampilkan halaman login"""
        self.clear_frame()
        self.current_frame = tb.Frame(self.root, padding=(20,20), bootstyle="dark")
        self.current_frame.pack(fill="both", expand=True)
        LoginPage(self.current_frame, self.show_dashboard)

    def show_dashboard(self):
        """Tampilkan halaman dashboard"""
        self.clear_frame()
        self.current_frame = tb.Frame(self.root, padding=(10,10), bootstyle="dark")
        self.current_frame.pack(fill="both", expand=True)
        DashboardApp(self.current_frame, self.show_manage_items, self.show_report, self.logout)

    def show_manage_items(self):
        """Tampilkan halaman kelola barang"""
        self.clear_frame()
        self.current_frame = tb.Frame(self.root, padding=(10,10), bootstyle="dark")
        self.current_frame.pack(fill="both", expand=True)
        BarangApp(self.current_frame)

    def show_report(self):
        """Tampilkan halaman laporan"""
        self.clear_frame()
        self.current_frame = tb.Frame(self.root, padding=(10,10), bootstyle="dark")
        self.current_frame.pack(fill="both", expand=True)
        LaporanApp(self.current_frame)

    def logout(self):
        """Kembali ke halaman login"""
        self.show_login()


if __name__ == "__main__":
    root = tb.Window(themename="superhero")
    try:
        icon_path = resource_path("assets/icons/app.ico")
        root.iconbitmap(icon_path)
    except Exception as e:
        print("⚠️ Icon tidak ditemukan:", e)

    def on_close():
        backup_database()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)  # PASANG SEBELUM SplashScreen

    app = SplashScreen(root, next_app=lambda: MainApp(root))
    root.mainloop()
