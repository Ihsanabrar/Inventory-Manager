import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox
from utils.database import get_connection
from ui.laporan import LaporanApp
from ui.barang import BarangApp

class DashboardApp:
    def __init__(self, parent, show_manage_items=None, show_report=None, logout=None):
        self.parent = parent
        self.show_manage_items = show_manage_items
        self.show_report = show_report
        self.logout_callback = logout

        # layout main frame already provided as `parent`
        header = tb.Frame(self.parent, bootstyle="dark")
        header.pack(fill="x", pady=(6,12))
        tb.Label(header, text="🏠 Dashboard Inventori", font=("Segoe UI", 16, "bold"), bootstyle="inverse-dark").pack(pady=6)

        # Button cards row (center)
        card_row = tb.Frame(self.parent, bootstyle="dark")
        card_row.pack(pady=6)

        tb.Button(card_row, text="📦 Kelola Barang", bootstyle="primary", width=20, command=self.open_barang).grid(row=0, column=0, padx=8, pady=6)
        tb.Button(card_row, text="📊 Laporan", bootstyle="success", width=12, command=self.open_laporan).grid(row=0, column=1, padx=8, pady=6)
        tb.Button(card_row, text="🚪 Logout", bootstyle="danger", width=12, command=self.logout).grid(row=0, column=2, padx=8, pady=6)

        # Separator
        tb.Separator(self.parent).pack(fill="x", pady=8)

        # Form two-columns
        form = tb.Frame(self.parent, bootstyle="dark")
        form.pack(padx=20, pady=8, fill="x")

        labels = ["Kode", "Nama", "Kategori", "Stok", "Harga Beli", "Harga Jual"]
        self.entries = {}
        # two columns layout
        left_frame = tb.Frame(form, bootstyle="dark")
        right_frame = tb.Frame(form, bootstyle="dark")
        left_frame.grid(row=0, column=0, padx=(0,20), sticky="nw")
        right_frame.grid(row=0, column=1, padx=(20,0), sticky="ne")

        # Left column
        tb.Label(left_frame, text="Kode").grid(row=0, column=0, sticky="w", pady=4)
        self.entries["kode"] = tb.Entry(left_frame, width=25); self.entries["kode"].grid(row=1, column=0, pady=4)

        tb.Label(left_frame, text="Kategori").grid(row=2, column=0, sticky="w", pady=4)
        self.entries["kategori"] = tb.Entry(left_frame, width=25); self.entries["kategori"].grid(row=3, column=0, pady=4)

        tb.Label(left_frame, text="Harga Beli").grid(row=4, column=0, sticky="w", pady=4)
        self.entries["harga_beli"] = tb.Entry(left_frame, width=25); self.entries["harga_beli"].grid(row=5, column=0, pady=4)

        # Right column
        tb.Label(right_frame, text="Nama").grid(row=0, column=0, sticky="w", pady=4)
        self.entries["nama"] = tb.Entry(right_frame, width=25); self.entries["nama"].grid(row=1, column=0, pady=4)

        tb.Label(right_frame, text="Stok").grid(row=2, column=0, sticky="w", pady=4)
        self.entries["stok"] = tb.Entry(right_frame, width=25); self.entries["stok"].grid(row=3, column=0, pady=4)

        tb.Label(right_frame, text="Harga Jual").grid(row=4, column=0, sticky="w", pady=4)
        self.entries["harga_jual"] = tb.Entry(right_frame, width=25); self.entries["harga_jual"].grid(row=5, column=0, pady=4)

        # Action buttons
        btn_row = tb.Frame(self.parent, bootstyle="dark")
        btn_row.pack(pady=8)
        tb.Button(btn_row, text="Tambah", bootstyle="primary", command=self.add_barang).grid(row=0, column=0, padx=6)
        tb.Button(btn_row, text="Update", bootstyle="warning", command=self.update_barang).grid(row=0, column=1, padx=6)
        tb.Button(btn_row, text="Hapus", bootstyle="danger", command=self.delete_barang).grid(row=0, column=2, padx=6)
        tb.Button(btn_row, text="Clear", bootstyle="secondary", command=self.clear_input).grid(row=0, column=3, padx=6)

        # Search area
        search_frame = tb.Frame(self.parent, bootstyle="dark")
        search_frame.pack(pady=6, fill="x")
        tb.Label(search_frame, text="Cari Barang:").pack(side="left", padx=(10,6))
        self.entry_search = tb.Entry(search_frame, width=30)
        self.entry_search.pack(side="left", padx=(0,6))
        tb.Button(search_frame, text="Cari", bootstyle="primary", command=self.search_barang).pack(side="left")
        tb.Button(search_frame, text="Tampilkan Semua", bootstyle="secondary", command=self.load_data).pack(side="left", padx=(6,0))

        # Table (ttk Treeview)
        style = tb.Style()  # ttkbootstrap style
        style.configure("mystyle.Treeview", rowheight=24)
        self.tree = ttk.Treeview(self.parent, columns=("id", "kode", "nama", "kategori", "stok", "beli", "jual"),
                                 show="headings", style="mystyle.Treeview")
        self.tree.pack(padx=10, pady=8, fill="both", expand=True)

        for col, text in [("id","ID"),("kode","Kode"),("nama","Nama"),("kategori","Kategori"),("stok","Stok"),("beli","Harga Beli"),("jual","Harga Jual")]:
            self.tree.heading(col, text=text)
            self.tree.column(col, anchor="center")

        self.tree.bind("<ButtonRelease-1>", self.on_row_select)
        self.load_data()

    # ==== CRUD Function ====
    def add_barang(self):
        data = (
            self.entries["kode"].get(),
            self.entries["nama"].get(),
            self.entries["kategori"].get(),
            self.entries["stok"].get(),
            self.entries["harga_beli"].get(),
            self.entries["harga_jual"].get()
        )
        if not all(data):
            messagebox.showwarning("Peringatan", "Semua field harus diisi!")
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO barang (kode_barang, nama_barang, kategori, stok, harga_beli, harga_jual)
                VALUES (?, ?, ?, ?, ?, ?)
            """, data)
            conn.commit()
            messagebox.showinfo("Sukses", "Data berhasil ditambahkan!")
            self.load_data()
            self.clear_input()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menambah data: {e}")
        finally:
            conn.close()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM barang")
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    def on_row_select(self, event):
        sel = self.tree.focus()
        if not sel:
            return
        data = self.tree.item(sel, "values")
        self.selected_id = data[0]
        # map to entries: kode=1 nama=2 kategori=3 stok=4 harga_beli=5 harga_jual=6
        self.entries["kode"].delete(0, "end"); self.entries["kode"].insert(0, data[1])
        self.entries["nama"].delete(0, "end"); self.entries["nama"].insert(0, data[2])
        self.entries["kategori"].delete(0, "end"); self.entries["kategori"].insert(0, data[3])
        self.entries["stok"].delete(0, "end"); self.entries["stok"].insert(0, data[4])
        self.entries["harga_beli"].delete(0, "end"); self.entries["harga_beli"].insert(0, data[5])
        self.entries["harga_jual"].delete(0, "end"); self.entries["harga_jual"].insert(0, data[6])

    def update_barang(self):
        if not getattr(self, "selected_id", None):
            messagebox.showwarning("Peringatan", "Pilih data yang mau diupdate!")
            return
        conn = get_connection(); cursor = conn.cursor()
        cursor.execute("""
            UPDATE barang SET kode_barang=?, nama_barang=?, kategori=?, stok=?, harga_beli=?, harga_jual=?
            WHERE id=?
        """, (
            self.entries["kode"].get(),
            self.entries["nama"].get(),
            self.entries["kategori"].get(),
            self.entries["stok"].get(),
            self.entries["harga_beli"].get(),
            self.entries["harga_jual"].get(),
            self.selected_id
        ))
        conn.commit(); conn.close()
        messagebox.showinfo("Sukses", "Data berhasil diperbarui!")
        self.load_data()
        self.clear_input()

    def delete_barang(self):
        if not getattr(self, "selected_id", None):
            messagebox.showwarning("Peringatan", "Pilih data yang mau dihapus!")
            return
        if not messagebox.askyesno("Konfirmasi", "Yakin mau hapus data ini?"):
            return
        conn = get_connection(); cursor = conn.cursor()
        cursor.execute("DELETE FROM barang WHERE id=?", (self.selected_id,))
        conn.commit(); conn.close()
        messagebox.showinfo("Sukses", "Data berhasil dihapus!")
        self.load_data()
        self.clear_input()

    def search_barang(self):
        keyword = self.entry_search.get()
        for i in self.tree.get_children():
            self.tree.delete(i)
        conn = get_connection(); cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM barang 
            WHERE nama_barang LIKE ? OR kategori LIKE ? OR kode_barang LIKE ?
        """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        rows = cursor.fetchall(); conn.close()
        for row in rows:
            self.tree.insert("", "end", values=row)
        if not rows:
            messagebox.showinfo("Info", "Tidak ada data ditemukan.")

    def clear_input(self):
        for k in self.entries:
            self.entries[k].delete(0, "end")
        self.selected_id = None

    def open_barang(self):
        # kalau mau buka sebagai toplevel
        win = tb.Toplevel(self.parent)
        BarangApp(win)

    def open_laporan(self):
        win = tb.Toplevel(self.parent)
        LaporanApp(win)

    def logout(self):
        if messagebox.askyesno("Konfirmasi", "Yakin mau logout?"):
            if self.logout_callback:
                self.logout_callback()
            else:
                # fallback: destroy root window
                self.parent.winfo_toplevel().destroy()
