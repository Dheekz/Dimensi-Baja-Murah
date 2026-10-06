"""Daftar menu aplikasi.

RUANG UNTUK FITUR BARU
Semua halaman didaftarkan di sini. Untuk menambah fitur:
  1. Salin halaman/templat_halaman_baru.py menjadi file baru di folder halaman
  2. Tambahkan satu baris Menu(...) di kelompok yang sesuai di bawah
  3. Simpan, aplikasi langsung menampilkan menu baru

POSISI_MENU menentukan gaya navigasi:
  "sidebar" : menu di panel kiri (bawaan)
  "top"     : menu berbentuk tab di bagian atas layar
"""
from dataclasses import dataclass

import streamlit as st

POSISI_MENU = "sidebar"


@dataclass
class Menu:
    berkas: str
    judul: str
    ikon: str
    aktif: bool = True
    utama: bool = False


DAFTAR_MENU = {
    "Harian": [
        Menu("halaman/ringkasan.py", "Ringkasan", ":material/dashboard:", utama=True),
        Menu("halaman/input_transaksi.py", "Input Transaksi", ":material/edit_note:"),
        Menu("halaman/stok_real_time.py", "Stok Real Time", ":material/inventory_2:"),
    ],
    "Laporan": [
        Menu("halaman/laporan.py", "Laporan Mingguan", ":material/table_view:"),
        Menu("halaman/riwayat.py", "Riwayat Transaksi", ":material/history:"),
    ],
    "Data": [
        Menu("halaman/stok_opname.py", "Stok Opname", ":material/fact_check:"),
        Menu("halaman/master_barang.py", "Master Barang", ":material/category:"),
        Menu("halaman/pengaturan.py", "Pengaturan", ":material/settings:"),
    ],
    # Contoh kelompok fitur berikutnya (ubah aktif menjadi True setelah halamannya dibuat):
    # "Penjualan": [
    #     Menu("halaman/penjualan.py", "Nota Penjualan", ":material/receipt_long:", aktif=False),
    # ],
}


def buat_navigasi():
    halaman = {}
    for kelompok, daftar in DAFTAR_MENU.items():
        isi = [
            st.Page(m.berkas, title=m.judul, icon=m.ikon, default=m.utama)
            for m in daftar if m.aktif
        ]
        if isi:
            halaman[kelompok] = isi
    return st.navigation(halaman, position=POSISI_MENU)
