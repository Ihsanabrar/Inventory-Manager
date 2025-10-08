import csv
from tkinter import messagebox
from utils.database import get_connection

def export_to_csv(file_path):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT kode_barang, nama_barang, kategori, stok, harga_beli, harga_jual FROM barang")
        data = cursor.fetchall()
        conn.close()

        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Kode Barang", "Nama Barang", "Kategori", "Stok", "Harga Beli", "Harga Jual"])
            writer.writerows(data)

        messagebox.showinfo("Sukses", f"Data berhasil diekspor ke:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Gagal ekspor CSV: {e}")
