"""Kunci akses sederhana dengan kata sandi.

Bila [aplikasi] kata_sandi diisi di secrets, pengguna harus memasukkan
kata sandi dulu. Bila kosong, aplikasi langsung terbuka.
"""
import hmac

import streamlit as st

from inti import konfigurasi as kf


def _kata_sandi():
    return kf.ambil_rahasia("aplikasi", "kata_sandi", "")


def sudah_masuk():
    if not _kata_sandi():
        return True
    return st.session_state.get("sudah_masuk", False)


def form_masuk():
    kiri, tengah, kanan = st.columns([1, 2, 1])
    with tengah:
        st.title(":material/roofing: Masuk")
        st.caption(f"Aplikasi stok {kf.nama_usaha()}")
        with st.form("form_masuk"):
            nama = st.text_input("Nama petugas")
            sandi = st.text_input("Kata sandi", type="password")
            masuk = st.form_submit_button("Masuk", type="primary", width="stretch")
        if masuk:
            if hmac.compare_digest(sandi, str(_kata_sandi())):
                st.session_state["sudah_masuk"] = True
                st.session_state["petugas"] = nama.strip()
                st.rerun()
            else:
                st.error("Kata sandi salah.")


def tombol_keluar():
    if _kata_sandi() and st.sidebar.button("Keluar", icon=":material/logout:", width="stretch"):
        st.session_state["sudah_masuk"] = False
        st.rerun()
