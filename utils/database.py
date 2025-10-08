import sqlite3
import os
import sys
import shutil
from datetime import datetime

# 📁 Tentukan folder utama tergantung script atau .exe
BASE_DIR = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR))  # folder utama tempat main.exe
DB_DIR = os.path.join(PROJECT_DIR, "db")
BACKUP_DIR = os.path.join(PROJECT_DIR, "backup")

# ✅ Pastikan folder db dan backup selalu ada
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# 📂 Path database utama
DB_PATH = os.path.join(DB_DIR, "database.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def restore_if_needed():
    """♻️ Coba restore dari backup terbaru kalau database utama hilang"""
    if os.path.exists(DB_PATH):
        return

    backups = [f for f in os.listdir(BACKUP_DIR) if f.startswith("database_backup_")]
    if backups:
        backups.sort(reverse=True)
        latest_backup = os.path.join(BACKUP_DIR, backups[0])
        shutil.copy(latest_backup, DB_PATH)
        print(f"[♻️] Database dipulihkan dari backup: {latest_backup}")
    else:
        print("[⚠️] Tidak ada backup. Database baru akan dibuat.")

def init_db():
    """📦 Buat database & tabel kalau belum ada"""
    restore_if_needed()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS barang (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kode_barang TEXT UNIQUE NOT NULL,
            nama_barang TEXT NOT NULL,
            kategori TEXT,
            stok INTEGER DEFAULT 0,
            harga_beli REAL DEFAULT 0,
            harga_jual REAL DEFAULT 0
        )
    """)

    # 👤 Tambahkan admin default
    cursor.execute("SELECT * FROM admin WHERE username='admin'")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ("admin", "admin"))

    conn.commit()
    conn.close()

def backup_database():
    """💾 Backup database saat aplikasi ditutup"""
    if not os.path.exists(DB_PATH):
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"database_backup_{timestamp}.db")
    shutil.copy(DB_PATH, backup_path)
    print(f"[✅] Backup tersimpan di: {backup_path}")
