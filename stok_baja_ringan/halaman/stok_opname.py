"""Halaman Stok Opname: mencocokkan stok di aplikasi dengan hitungan fisik di gudang.

Selisihnya dicatat sebagai transaksi KOREKSI TAMBAH atau KOREKSI KURANG,
jadi angka stok awal tidak perlu diubah dan riwayatnya tetap tercatat.
"""
import pandas as pd
import streamlit as st

from inti import database as db
from inti import stok as sk
from inti import tampilan as tp

master = db.baca_master()
transaksi = db.baca_transaksi()
hari_ini = db.hari_ini()

tp.judul("Stok Opname", "fact_check",
         "Isi kolom Stok Fisik sesuai hitungan di gudang. Hanya baris yang berbeda yang akan dikoreksi.")
if not tp.butuh_data(master):
    st.stop()

st.session_state.setdefault("putaran_opname", 0)
kategori_list = list(dict.fromkeys(master["kategori"]))
o1, o2, o3 = st.columns([1, 1, 2])
tanggal = o1.date_input("Tanggal opname", value=hari_ini, max_value=hari_ini, format="DD/MM/YYYY")
kategori = o2.selectbox("Kategori", kategori_list)
tipe = o3.segmented_control("Tipe", [sk.TIPE_JADI, sk.TIPE_BAHAN], default=sk.TIPE_JADI, required=True)

data = sk.hitung_stok(master, transaksi, sampai=pd.Timestamp(tanggal))
data = data[(data["kategori"] == kategori) & (data["tipe"] == tipe) & data["aktif"]]
if data.empty:
    st.info("Tidak ada barang untuk pilihan ini.")
    st.stop()

isian = data[["kode", "nama_barang", "varian", "stok_rt"]].reset_index(drop=True)
isian["stok_fisik"] = isian["stok_rt"]
hasil = st.data_editor(
    isian, hide_index=True, width="stretch", height=min(38 * (len(isian) + 1) + 4, 600),
    key=f"opname_{kategori}_{tipe}_{st.session_state['putaran_opname']}",
    column_order=["nama_barang", "varian", "stok_rt", "stok_fisik"],
    disabled=["kode", "nama_barang", "varian", "stok_rt"],
    column_config={
        "nama_barang": "Nama Barang", "varian": "Warna / Ukuran",
        "stok_rt": tp.kolom_angka("Stok di Aplikasi"),
        "stok_fisik": st.column_config.NumberColumn("Stok Fisik", min_value=0, step=1, format="%d"),
    },
)
hasil["stok_fisik"] = pd.to_numeric(hasil["stok_fisik"], errors="coerce").fillna(hasil["stok_rt"])
hasil["beda"] = hasil["stok_fisik"].sub(hasil["stok_rt"])
beda = hasil[hasil["beda"] != 0]

if beda.empty:
    st.success("Semua stok sudah cocok dengan aplikasi.", icon=":material/check_circle:")
    st.stop()

beda = beda.assign(
    jenis=beda["beda"].map(lambda x: sk.KOREKSI_TAMBAH if x > 0 else sk.KOREKSI_KURANG),
    jumlah=beda["beda"].abs(),
)
st.markdown(f"**{len(beda)} barang berbeda dan akan dikoreksi:**")
st.dataframe(
    beda[["nama_barang", "varian", "stok_rt", "stok_fisik", "jenis", "jumlah"]], hide_index=True, width="stretch",
    column_config={
        "nama_barang": "Nama Barang", "varian": "Warna / Ukuran", "stok_rt": tp.kolom_angka("Di Aplikasi"),
        "stok_fisik": tp.kolom_angka("Fisik"), "jenis": "Koreksi", "jumlah": tp.kolom_angka("Jumlah"),
    },
)
catatan = st.text_input("Catatan opname (opsional)", placeholder="Contoh: dihitung bersama kepala gudang")
if st.button("Simpan koreksi stok", type="primary", icon=":material/save:"):
    if tp.butuh_petugas():
        dasar = f"Stok opname {tanggal:%d/%m/%Y}"
        daftar = [
            dict(tanggal=tanggal, jenis=r.jenis, kode=r.kode, jumlah=r.jumlah,
                 keterangan=f"{dasar} | {catatan.strip()}" if catatan.strip() else dasar)
            for r in beda.itertuples()
        ]
        jumlah = db.simpan_transaksi(daftar, tp.petugas())
        st.session_state["putaran_opname"] += 1
        tp.titip_pesan(f"{jumlah} koreksi stok tersimpan")
        st.rerun()
