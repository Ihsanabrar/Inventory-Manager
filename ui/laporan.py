import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from utils.database import get_connection
import openpyxl
from utils.export_csv import export_to_csv

class LaporanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Laporan - Inventory Manager")
        self.root.geometry("700x450")
        self.root.config(bg="#1e1e1e")

        title = tk.Label(
            self.root,
            text="📊 Laporan Data Barang",
            bg="#1e1e1e",
            fg="white",
            font=("Segoe UI", 16, "bold")
        )
        title.pack(pady=10)

        # Frame Statistik
        stats_frame = tk.Frame(self.root, bg="#1e1e1e")
        stats_frame.pack(pady=10)

        self.label_total_barang = tk.Label(stats_frame, text="", fg="white", bg="#1e1e1e", font=("Segoe UI", 12))
        self.label_total_barang.pack(anchor="w")

        self.label_total_stok = tk.Label(stats_frame, text="", fg="white", bg="#1e1e1e", font=("Segoe UI", 12))
        self.label_total_stok.pack(anchor="w")

        self.label_total_modal = tk.Label(stats_frame, text="", fg="white", bg="#1e1e1e", font=("Segoe UI", 12))
        self.label_total_modal.pack(anchor="w")

        # Tabel barang stok rendah
        tk.Label(self.root, text="Barang dengan stok rendah (<= 5):", fg="white", bg="#1e1e1e").pack(pady=(10, 0))

        # 🔍 Frame pencarian & filter
        filter_frame = tk.Frame(self.root, bg="#1e1e1e")
        filter_frame.pack(pady=5)

        tk.Label(filter_frame, text="Cari Nama:", fg="white", bg="#1e1e1e").grid(row=0, column=0, padx=5)
        self.entry_search = tk.Entry(filter_frame)
        self.entry_search.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="Kategori:", fg="white", bg="#1e1e1e").grid(row=0, column=2, padx=5)
        self.combo_kategori = ttk.Combobox(filter_frame, values=["Semua"], state="readonly", width=15)
        self.combo_kategori.grid(row=0, column=3, padx=5)
        self.combo_kategori.set("Semua")

        btn_cari = tk.Button(filter_frame, text="🔎 Cari", bg="#22A699", fg="white",
                            font=("Segoe UI", 9, "bold"), command=self.filter_laporan)
        btn_cari.grid(row=0, column=4, padx=5)


        self.tree = ttk.Treeview(
            self.root,
            columns=("kode", "nama", "stok"),
            show="headings",
            height=8
        )
        self.tree.pack(pady=5, fill="x", padx=10)

        self.tree.heading("kode", text="Kode Barang")
        self.tree.heading("nama", text="Nama Barang")
        self.tree.heading("stok", text="Stok")

        self.tree.column("kode", width=150)
        self.tree.column("nama", width=300)
        self.tree.column("stok", width=100)

        # Tombol Export
        btn_export = tk.Button(
            self.root,
            text="💾 Export ke Excel",
            bg="#22A699",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self.export_excel
        )
        btn_export.pack(pady=10)

        self.load_laporan()

    def load_laporan(self):
        conn = get_connection()
        cursor = conn.cursor()

        # Total barang
        cursor.execute("SELECT COUNT(*) FROM barang")
        total_barang = cursor.fetchone()[0]

        # Total stok
        cursor.execute("SELECT SUM(stok) FROM barang")
        total_stok = cursor.fetchone()[0] or 0

        # Total modal
        cursor.execute("SELECT SUM(harga_beli * stok) FROM barang")
        total_modal = cursor.fetchone()[0] or 0

        # Barang stok rendah
        cursor.execute("SELECT kode_barang, nama_barang, stok FROM barang WHERE stok <= 5")
        barang_rendah = cursor.fetchall()

        conn.close()

        # Update label
        self.label_total_barang.config(text=f"Total Jenis Barang: {total_barang}")
        self.label_total_stok.config(text=f"Total Stok Barang: {total_stok}")
        self.label_total_modal.config(text=f"Total Nilai Modal: Rp {total_modal:,.0f}")

        # Isi tabel
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in barang_rendah:
            self.tree.insert("", tk.END, values=row)

        self.data_laporan = {
            "total_barang": total_barang,
            "total_stok": total_stok,
            "total_modal": total_modal,
            "barang_rendah": barang_rendah
        }

    def export_excel(self):
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx")],
                title="Simpan Laporan Sebagai"
            )
            if not filepath:
                return

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Laporan Barang"

            # Header summary
            ws.append(["LAPORAN DATA BARANG"])
            ws.append([])
            ws.append(["Total Jenis Barang", self.data_laporan["total_barang"]])
            ws.append(["Total Stok Barang", self.data_laporan["total_stok"]])
            ws.append(["Total Nilai Modal", f"Rp {self.data_laporan['total_modal']:,.0f}"])
            ws.append([])

            # Bagian: barang stok rendah
            ws.append(["Barang dengan stok rendah (<=5)"])
            ws.append(["Kode Barang", "Nama Barang", "Stok"])
            for row in self.data_laporan["barang_rendah"]:
                ws.append(row)
            ws.append([])

            # BAGIAN BARU: semua barang (full list)
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT kode_barang, nama_barang, kategori, stok, harga_beli, harga_jual FROM barang")
            all_items = cursor.fetchall()
            conn.close()

            ws.append(["Semua Barang"])
            ws.append(["Kode Barang", "Nama Barang", "Kategori", "Stok", "Harga Beli", "Harga Jual"])
            for item in all_items:
                ws.append(item)

            wb.save(filepath)
            messagebox.showinfo("Sukses", f"Laporan berhasil disimpan ke:\n{filepath}")

        except Exception as e:
            messagebox.showerror("Error", f"Gagal export laporan: {e}")


    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            export_to_csv(file_path)

    def filter_laporan(self):
        search_text = self.entry_search.get().lower()
        selected_kategori = self.combo_kategori.get()

        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT kode_barang, nama_barang, stok FROM barang WHERE 1=1"
        params = []

        if selected_kategori != "Semua":
            query += " AND kategori = ?"
            params.append(selected_kategori)

        if search_text:
            query += " AND LOWER(nama_barang) LIKE ?"
            params.append(f"%{search_text}%")

        cursor.execute(query, params)
        filtered_data = cursor.fetchall()
        conn.close()

        # 🔄 Update daftar kategori di combo box
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT kategori FROM barang")
        kategori_list = [row[0] for row in cursor.fetchall()]
        conn.close()

        self.combo_kategori["values"] = ["Semua"] + kategori_list


        # Hapus data lama di tabel
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Tampilkan hasil pencarian
        for row in filtered_data:
            self.tree.insert("", tk.END, values=row)
