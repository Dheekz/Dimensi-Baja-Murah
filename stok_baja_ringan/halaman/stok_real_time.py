"""Halaman Stok Real Time: pengganti sheet "Real Time" di Excel."""
import pandas as pd
import streamlit as st

from inti import database as db
from inti import ekspor
from inti import stok as sk
from inti import tampilan as tp

master = db.baca_master()
transaksi = db.baca_transaksi()
hari_ini = db.hari_ini()

tp.judul("Stok Real Time", "inventory_2",
         "Stok RT = stok awal + produksi + barang masuk, dikurangi pengeluaran dan plat yang dipakai produksi.")
if not tp.butuh_data(master):
    st.stop()

kategori_list = list(dict.fromkeys(master["kategori"]))
f1, f2, f3, f4 = st.columns([2, 2, 2, 1])
pilih_kategori = f1.multiselect("Kategori", kategori_list, default=kategori_list)
pilih_tipe = f2.segmented_control("Tipe", [sk.TIPE_JADI, sk.TIPE_BAHAN], selection_mode="multi",
                                  default=[sk.TIPE_JADI, sk.TIPE_BAHAN])
cari = f3.text_input("Cari nama atau warna", placeholder="contoh: spandek hitam")
per_tanggal = f4.date_input("Posisi per tanggal", value=hari_ini, format="DD/MM/YYYY")

o1, o2 = st.columns(2)
tampil_nonaktif = o1.toggle("Tampilkan barang nonaktif", value=False)
hanya_perhatian = o2.toggle("Hanya yang perlu perhatian", value=False)

data = sk.hitung_stok(master, transaksi, sampai=pd.Timestamp(per_tanggal))
data = data[data["kategori"].isin(pilih_kategori) & data["tipe"].isin(pilih_tipe or [])]
if not tampil_nonaktif:
    data = data[data["aktif"]]
if hanya_perhatian:
    data = data[data["status"].isin(sk.STATUS_PERHATIAN)]
if cari.strip():
    teks = (data["nama_barang"] + " " + data["varian"] + " " + data["supplier"]).str.lower()
    for kata in cari.lower().split():
        data = data[teks.loc[data.index].str.contains(kata, regex=False)]

m1, m2, m3 = st.columns(3)
m1.metric("Jumlah item", len(data), border=True)
m2.metric("Total stok RT", tp.angka(data["stok_rt"].sum()), border=True)
m3.metric("Perlu perhatian", int(data["status"].isin(sk.STATUS_PERHATIAN).sum()), border=True)

kolom = ["kategori", "supplier", "nama_barang", "varian", "stok_awal", "produksi", "barang_masuk",
         "dipakai_produksi", "pengeluaran", "koreksi_tambah", "koreksi_kurang", "stok_rt", "selisih", "status"]
st.dataframe(
    data[kolom], hide_index=True, width="stretch", height=tp.tinggi_tabel(len(data)),
    column_config={
        "kategori": "Kategori", "supplier": "Supp", "nama_barang": "Nama Barang", "varian": "Warna / Ukuran",
        "stok_awal": tp.kolom_angka("Stok Awal"),
        "produksi": tp.kolom_angka("Produksi"),
        "barang_masuk": tp.kolom_angka("Barang Masuk"),
        "dipakai_produksi": tp.kolom_angka("Dipakai Produksi", "Plat yang terpakai untuk produksi barang jadi"),
        "pengeluaran": tp.kolom_angka("Pengeluaran"),
        "koreksi_tambah": tp.kolom_angka("Koreksi Tambah", "Hasil stok opname yang menambah stok"),
        "koreksi_kurang": tp.kolom_angka("Koreksi Kurang", "Hasil stok opname yang mengurangi stok"),
        "stok_rt": tp.kolom_angka("STOK RT"),
        "selisih": tp.kolom_angka("Selisih", "Stok awal dikurangi stok RT, sama seperti kolom selisih di Excel"),
        "status": "Status",
    },
)

if not data.empty:
    nama_berkas = f"Stok_Real_Time_{per_tanggal:%d%m%Y}.xlsx"
    st.download_button(
        "Unduh Excel", data=ekspor.buat_excel_tabel(
            data[kolom].rename(columns=lambda c: c.replace("_", " ").title()), "Real Time"),
        file_name=nama_berkas, icon=":material/download:",
    )
