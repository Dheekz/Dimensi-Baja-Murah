"""Templat halaman baru.

Cara memakai:
  1. Salin file ini, beri nama baru, misalnya halaman/penjualan.py
  2. Daftarkan di menu.py, contoh:
       Menu("halaman/penjualan.py", "Nota Penjualan", ":material/receipt_long:")
  3. Ikon bisa dipilih dari fonts.google.com/icons (tulis namanya dengan garis bawah)

File ini sengaja tidak didaftarkan di menu.
"""
import streamlit as st

from inti import database as db
from inti import stok as sk
from inti import tampilan as tp

tp.judul("Judul Halaman Baru", "extension", "Keterangan singkat halaman.")

master = db.baca_master()
transaksi = db.baca_transaksi()
data_stok = sk.hitung_stok(master, transaksi)

# Contoh pemakaian tab di dalam halaman
tab_satu, tab_dua = st.tabs(["Tab pertama", "Tab kedua"])
with tab_satu:
    st.write("Isi tab pertama")
with tab_dua:
    st.dataframe(data_stok.head(10), hide_index=True)
