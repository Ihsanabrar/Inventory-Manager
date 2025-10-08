import tkinter as tk
from tkinter import ttk, messagebox
from utils.database import get_connection

class BarangApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📦 Manajemen Barang")
        self.root.geometry("800x500")
        self.root.config(bg="#1e1e1e")

        tk.Label(self.root, text="📦 Manajemen Barang", bg="#1e1e1e", fg="white", font=("Segoe UI", 14, "bold")).pack(pady=10)

        # Frame input data
        frame_input = tk.Frame(self.root, bg="#1e1e1e")
        frame_input.pack(pady=5)

        labels = ["Kode", "Nama", "Kategori", "Stok", "Harga Beli", "Harga Jual"]
        self.entries = {}
        for i, label in enumerate(labels):
            tk.Label(frame_input, text=label, bg="#1e1e1e", fg="white").grid(row=0, column=i, padx=5)
            entry = tk.Entry(frame_input, width=12)
            entry.grid(row=1, column=i, padx=5)
            self.entries[label.lower().replace(" ", "_")] = entry

        # Tombol CRUD
        frame_btn = tk.Frame(self.root, bg="#1e1e1e")
        frame_btn.pack(pady=5)

        tk.Button(frame_btn, text="Tambah", bg="#0078D7", fg="white", command=self.add_data).grid(row=0, column=0, padx=5)
        tk.Button(frame_btn, text="Edit", bg="#FFB000", fg="black", command=self.update_data).grid(row=0, column=1, padx=5)
        tk.Button(frame_btn, text="Hapus", bg="#D83A56", fg="white", command=self.delete_data).grid(row=0, column=2, padx=5)
        tk.Button(frame_btn, text="Refresh", bg="#555", fg="white", command=self.load_data).grid(row=0, column=3, padx=5)

        # Kolom pencarian
        frame_search = tk.Frame(self.root, bg="#1e1e1e")
        frame_search.pack(pady=10)

        tk.Label(frame_search, text="Cari:", bg="#1e1e1e", fg="white").grid(row=0, column=0, padx=5)
        self.entry_search = tk.Entry(frame_search, width=30)
        self.entry_search.grid(row=0, column=1, padx=5)
        tk.Button(frame_search, text="Cari", bg="#0078D7", fg="white", command=self.search_data).grid(row=0, column=2, padx=5)

        # Tabel data barang
        columns = ("kode", "nama", "kategori", "stok", "harga_beli", "harga_jual")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree.bind("<ButtonRelease-1>", self.on_row_select)

        self.load_data()

    # ================= CRUD FUNCTION =================
    def load_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT kode_barang, nama_barang, kategori, stok, harga_beli, harga_jual FROM barang")
        data = cursor.fetchall()
        conn.close()

        for row in data:
            self.tree.insert("", tk.END, values=row)

    def add_data(self):
        data = {key: entry.get() for key, entry in self.entries.items()}

        if not all(data.values()):
            messagebox.showwarning("Peringatan", "Semua field harus diisi!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO barang (kode_barang, nama_barang, kategori, stok, harga_beli, harga_jual) VALUES (?, ?, ?, ?, ?, ?)",
                           (data["kode"], data["nama"], data["kategori"], data["stok"], data["harga_beli"], data["harga_jual"]))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sukses", "Data berhasil ditambahkan!")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menambah data: {e}")

    def update_data(self):
        data = {key: entry.get() for key, entry in self.entries.items()}
        if not all(data.values()):
            messagebox.showwarning("Peringatan", "Pilih data dulu dari tabel untuk diubah!")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE barang SET nama_barang=?, kategori=?, stok=?, harga_beli=?, harga_jual=? WHERE kode_barang=?
        """, (data["nama"], data["kategori"], data["stok"], data["harga_beli"], data["harga_jual"], data["kode"]))
        conn.commit()
        conn.close()

        messagebox.showinfo("Sukses", "Data berhasil diperbarui!")
        self.load_data()

    def delete_data(self):
        kode = self.entries["kode"].get()
        if not kode:
            messagebox.showwarning("Peringatan", "Pilih data yang mau dihapus!")
            return

        confirm = messagebox.askyesno("Konfirmasi", f"Hapus barang dengan kode {kode}?")
        if not confirm:
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM barang WHERE kode_barang=?", (kode,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Sukses", "Data berhasil dihapus!")
        self.load_data()

    def search_data(self):
        keyword = self.entry_search.get().lower()
        if not keyword:
            messagebox.showwarning("Peringatan", "Masukkan kata kunci pencarian dulu!")
            return

        for i in self.tree.get_children():
            self.tree.delete(i)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT kode_barang, nama_barang, kategori, stok, harga_beli, harga_jual FROM barang WHERE LOWER(nama_barang) LIKE ? OR LOWER(kategori) LIKE ?", 
                       (f"%{keyword}%", f"%{keyword}%"))
        data = cursor.fetchall()
        conn.close()

        if not data:
            messagebox.showinfo("Info", f"Tidak ada data dengan kata kunci '{keyword}'")

        for row in data:
            self.tree.insert("", tk.END, values=row)

    def on_row_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        data = self.tree.item(selected)["values"]
        if data:
            for i, key in enumerate(self.entries):
                self.entries[key].delete(0, tk.END)
                self.entries[key].insert(0, data[i])
