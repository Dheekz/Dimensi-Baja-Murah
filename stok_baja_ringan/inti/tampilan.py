"""Komponen tampilan yang dipakai bersama oleh semua halaman."""
from operator import sub

import pandas as pd
import streamlit as st

from inti import database as db
from inti import konfigurasi as kf


def judul(teks, ikon, keterangan=None):
    st.title(f":material/{ikon}: {teks}")
    if keterangan:
        st.caption(keterangan)


def angka(n):
    """Format angka gaya Indonesia: 1.300"""
    try:
        n = float(n)
    except (TypeError, ValueError):
        return str(n)
    teks = f"{abs(n):,.0f}".replace(",", ".")
    return f"({teks})" if n < 0 else teks


def tanggal(t):
    if t is None or pd.isna(t):
        return ""
    return f"{t.day} {kf.NAMA_BULAN[sub(t.month, 1)]} {t.year}"


def tinggi_tabel(jumlah_baris, maksimum=600):
    """Tinggi tabel menyesuaikan jumlah baris supaya tidak ada ruang kosong."""
    return min(36 * (jumlah_baris + 1) + 4, maksimum)


def kolom_angka(label, bantuan=None):
    return st.column_config.NumberColumn(label, format="%d", help=bantuan)


def petugas():
    return st.session_state.get("petugas", "").strip()


def panel_samping(penyimpanan):
    with st.sidebar:
        st.markdown(f"**{kf.nama_usaha()}**")
        st.text_input("Nama petugas", key="petugas", placeholder="Tulis nama Anda",
                      help="Nama ini dicatat di setiap transaksi yang Anda simpan.")
        if penyimpanan.mode == "Google Sheet":
            st.caption(":material/cloud_done: Terhubung ke Google Sheet")
        else:
            st.caption(":material/science: Mode lokal (demo). Hubungkan Google Sheet di menu Pengaturan.")
        if st.button("Muat ulang data", icon=":material/refresh:", width="stretch"):
            db.segarkan()
            st.rerun()


def butuh_data(master):
    """Menampilkan petunjuk bila master barang masih kosong. Mengembalikan True bila data ada."""
    if master.empty:
        st.info(
            "Database masih kosong. Buka menu **Pengaturan** lalu tekan "
            "**Isi data awal dari template Excel**, atau tambahkan barang di menu **Master Barang**.",
            icon=":material/info:",
        )
        st.page_link("halaman/pengaturan.py", label="Buka Pengaturan", icon=":material/settings:")
        return False
    return True


def butuh_petugas():
    if not petugas():
        st.warning("Isi **Nama petugas** di panel kiri sebelum menyimpan.", icon=":material/badge:")
        return False
    return True


def titip_pesan(teks):
    """Menyimpan pesan untuk ditampilkan setelah halaman dimuat ulang."""
    st.session_state["pesan_tertunda"] = teks


def tampilkan_pesan():
    teks = st.session_state.pop("pesan_tertunda", None)
    if teks:
        st.toast(teks, icon=":material/check_circle:")
