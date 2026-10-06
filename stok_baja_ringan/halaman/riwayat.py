"""Halaman Riwayat Transaksi: melihat, mencari, dan membatalkan transaksi yang salah input."""
from datetime import timedelta
from operator import sub

import pandas as pd
import streamlit as st

from inti import database as db
from inti import ekspor
from inti import stok as sk
from inti import tampilan as tp

master = db.baca_master()
transaksi = db.baca_transaksi()
hari_ini = pd.Timestamp(db.hari_ini())

tp.judul("Riwayat Transaksi", "history",
         "Transaksi tidak dihapus, tetapi ditandai BATAL supaya jejaknya tetap ada.")
if not tp.butuh_data(master):
    st.stop()

if transaksi.empty:
    st.info("Belum ada transaksi.")
    st.stop()

data = transaksi.merge(master[["kode", "kategori", "supplier", "nama_barang", "varian", "tipe"]], on="kode", how="left")

f1, f2, f3, f4 = st.columns([2, 1, 2, 2])
rentang = f1.date_input("Rentang tanggal", value=(sub(hari_ini, timedelta(days=30)), hari_ini), format="DD/MM/YYYY")
kategori_list = list(dict.fromkeys(master["kategori"]))
pilih_kategori = f2.selectbox("Kategori", ["Semua"] + kategori_list)
pilih_jenis = f3.multiselect("Jenis", sk.SEMUA_JENIS, default=sk.SEMUA_JENIS)
cari = f4.text_input("Cari", placeholder="nama barang, warna, keterangan, petugas")
tampil_batal = st.toggle("Tampilkan transaksi yang dibatalkan", value=False)

if isinstance(rentang, (list, tuple)) and len(rentang) == 2:
    data = data[(data["tanggal"] >= pd.Timestamp(rentang[0])) & (data["tanggal"] <= pd.Timestamp(rentang[1]))]
if pilih_kategori != "Semua":
    data = data[data["kategori"] == pilih_kategori]
data = data[data["jenis"].isin(pilih_jenis)]
if not tampil_batal:
    data = data[data["status"] != "BATAL"]
if cari.strip():
    teks = data[["nama_barang", "varian", "keterangan", "petugas", "supplier"]].fillna("").astype(str).agg(" ".join, axis=1).str.lower()
    for kata in cari.lower().split():
        data = data[teks.loc[data.index].str.contains(kata, regex=False)]

data = data.sort_values(["tanggal", "waktu_input"], ascending=False)
kolom = ["tanggal", "jenis", "kategori", "nama_barang", "varian", "jumlah", "keterangan", "petugas", "waktu_input", "status", "id"]

r1, r2 = st.columns(2)
r1.metric("Jumlah transaksi", len(data), border=True)
r2.metric("Total kuantitas", tp.angka(data["jumlah"].sum()), border=True)

st.dataframe(
    data[kolom], hide_index=True, width="stretch", height=tp.tinggi_tabel(len(data), 520),
    column_config={
        "tanggal": st.column_config.DateColumn("Tanggal", format="DD/MM/YYYY"),
        "jenis": "Jenis", "kategori": "Kategori", "nama_barang": "Nama Barang", "varian": "Warna / Ukuran",
        "jumlah": tp.kolom_angka("Jumlah"), "keterangan": "Keterangan", "petugas": "Petugas",
        "waktu_input": "Waktu Input", "status": "Status", "id": "ID",
    },
)
if not data.empty:
    st.download_button("Unduh Excel", icon=":material/download:",
                       data=ekspor.buat_excel_tabel(data[kolom].rename(columns=lambda c: c.replace("_", " ").title()), "Riwayat"),
                       file_name=f"Riwayat_Transaksi_{hari_ini:%d%m%Y}.xlsx")

st.divider()
st.subheader(":material/cancel: Batalkan transaksi yang salah")
bisa_batal = data[data["status"] != "BATAL"]
if bisa_batal.empty:
    st.caption("Tidak ada transaksi aktif pada filter ini.")
    st.stop()

label = {
    r.id: f"{r.tanggal:%d/%m/%Y}  •  {r.jenis}  •  {r.nama_barang} {r.varian}  •  {tp.angka(r.jumlah)}  •  {r.petugas or 'tanpa nama'}"
    for r in bisa_batal.itertuples()
}
with st.form("form_batal"):
    pilih = st.selectbox("Pilih transaksi", list(label), format_func=label.get)
    alasan = st.text_input("Alasan pembatalan", placeholder="Contoh: salah input jumlah, seharusnya 15")
    yakin = st.checkbox("Saya yakin transaksi ini dibatalkan")
    kirim = st.form_submit_button("Batalkan transaksi", icon=":material/cancel:")
if kirim:
    if not yakin:
        st.warning("Centang konfirmasi dulu.")
    elif not alasan.strip():
        st.warning("Tulis alasan pembatalan.")
    elif tp.butuh_petugas():
        lama = bisa_batal.loc[bisa_batal["id"] == pilih, "keterangan"].iloc[0]
        db.batalkan_transaksi(pilih, alasan.strip(), tp.petugas(), lama)
        tp.titip_pesan("Transaksi dibatalkan")
        st.rerun()
