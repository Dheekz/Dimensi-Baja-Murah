"""Pengaturan umum aplikasi.

Nilai yang sering diganti (nama usaha, kata sandi, alamat Google Sheet)
diambil dari file secrets supaya tidak perlu mengubah kode.
"""
import streamlit as st

NAMA_APLIKASI = "Stok Baja Ringan"
NAMA_USAHA_BAWAAN = "Toko Baja Ringan"
ZONA_WAKTU = "Asia/Jakarta"

# Nama tab di Google Sheet yang dipakai sebagai tabel database
TAB_MASTER = "master_barang"
TAB_TRANSAKSI = "transaksi"

# Format tanggal yang disimpan di Google Sheet (hari/bulan/tahun)
FORMAT_TANGGAL = "%d/%m/%Y"

# Lama data disimpan di memori sebelum dibaca ulang dari Google Sheet (detik)
TTL_CACHE = 120

# Urutan warna standar produk atap
DAFTAR_WARNA = ["Merah", "Coklat", "Hitam", "Hijau", "Biru"]

NAMA_HARI = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"]
HARI_PENDEK = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
NAMA_BULAN = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]


def ambil_rahasia(bagian, kunci, bawaan=None):
    """Membaca nilai dari secrets tanpa error bila belum diisi."""
    try:
        return st.secrets[bagian][kunci]
    except Exception:
        return bawaan


def nama_usaha():
    return ambil_rahasia("aplikasi", "nama_usaha", NAMA_USAHA_BAWAAN)
