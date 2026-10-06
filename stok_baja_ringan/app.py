"""Aplikasi pelaporan stok toko baja ringan.

Jalankan dengan perintah:  streamlit run app.py
"""
from pathlib import Path

import streamlit as st

from inti import akses, tampilan
from inti import database as db
from inti import konfigurasi as kf
from menu import buat_navigasi

FOLDER = Path(__file__).resolve().parent

st.set_page_config(
    page_title=f"{kf.NAMA_APLIKASI} | {kf.nama_usaha()}",
    page_icon=":material/roofing:",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.logo(str(FOLDER / "assets" / "logo.svg"), icon_image=str(FOLDER / "assets" / "ikon.svg"), size="large")

if not akses.sudah_masuk():
    akses.form_masuk()
    st.stop()

navigasi = buat_navigasi()

try:
    penyimpanan = db.ambil_penyimpanan()
except Exception as galat:
    st.error(
        "Gagal terhubung ke Google Sheet. Periksa isi secrets "
        "(gcp_service_account dan google_sheet), dan pastikan Google Sheet sudah "
        "dibagikan ke email service account sebagai Editor.",
        icon=":material/cloud_off:",
    )
    st.exception(galat)
    st.stop()

tampilan.panel_samping(penyimpanan)
tampilan.tampilkan_pesan()
akses.tombol_keluar()
navigasi.run()
