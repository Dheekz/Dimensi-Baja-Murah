"""Halaman Pengaturan: status koneksi database dan pengisian data awal."""
import streamlit as st

from inti import database as db
from inti import konfigurasi as kf
from inti import tampilan as tp

tp.judul("Pengaturan", "settings")
penyimpanan = db.ambil_penyimpanan()
master = db.baca_master()
transaksi = db.baca_transaksi()

st.subheader("Database")
s1, s2, s3 = st.columns(3)
s1.metric("Mode", penyimpanan.mode, border=True)
s2.metric("Jumlah barang", len(master), border=True)
s3.metric("Jumlah transaksi", len(transaksi), border=True)
if penyimpanan.url:
    st.link_button("Buka Google Sheet", penyimpanan.url, icon=":material/open_in_new:")
else:
    st.info(
        "Aplikasi sedang memakai penyimpanan lokal untuk percobaan. Data di mode ini bisa hilang saat aplikasi "
        "dipasang ulang di server. Ikuti langkah di file PANDUAN.md untuk menghubungkan Google Sheet, "
        "lalu isi bagian secrets.",
        icon=":material/science:",
    )

st.subheader("Isi data awal dari template Excel")
st.caption(
    "Membuat daftar barang GMP dan SPANDEK (termasuk genteng CVDMS dan plat bahan baku) beserta stok awal "
    "dari file STOK_GMP dan STOK_SPANDEK. Tanggal stok awal diset 27/07/2026."
)
if not master.empty:
    st.warning(
        "Master barang sudah berisi data. Mengisi ulang akan MENIMPA seluruh master barang "
        "(transaksi yang sudah ada tidak dihapus).",
        icon=":material/warning:",
    )
with st.form("form_data_awal"):
    ikut_trx = st.checkbox("Ikut masukkan transaksi yang sudah tercatat di template (28 dan 29 Juli 2026)", value=master.empty)
    konfirmasi = st.checkbox("Saya mengerti", value=master.empty)
    isi = st.form_submit_button("Isi data awal dari template Excel", type="primary", icon=":material/upload:")
if isi:
    if not konfirmasi:
        st.warning("Centang konfirmasi dulu.")
    else:
        with st.spinner("Mengisi data awal..."):
            jumlah_barang, jumlah_trx = db.isi_data_awal(ikut_trx, tp.petugas() or "Sistem")
        tp.titip_pesan(f"{jumlah_barang} barang dan {jumlah_trx} transaksi dimasukkan")
        st.rerun()

st.subheader("Cache")
st.caption(f"Data dari Google Sheet disimpan sementara selama {kf.TTL_CACHE} detik supaya aplikasi cepat. "
           "Bila Anda mengubah isi Google Sheet secara langsung, tekan tombol di bawah.")
if st.button("Muat ulang semua data", icon=":material/refresh:"):
    db.segarkan()
    st.cache_resource.clear()
    tp.titip_pesan("Data dimuat ulang")
    st.rerun()

with st.expander("Struktur database di Google Sheet"):
    st.markdown(
        f"**Tab `{kf.TAB_MASTER}`** berisi satu baris per barang per warna: "
        + ", ".join(f"`{k}`" for k in db.KOLOM[kf.TAB_MASTER])
    )
    st.markdown(
        f"**Tab `{kf.TAB_TRANSAKSI}`** berisi satu baris per transaksi: "
        + ", ".join(f"`{k}`" for k in db.KOLOM[kf.TAB_TRANSAKSI])
    )
    st.caption("Tanggal ditulis dengan format hari/bulan/tahun. Jenis transaksi: "
               "PRODUKSI, PENGELUARAN, BARANG MASUK, KOREKSI TAMBAH, KOREKSI KURANG.")
