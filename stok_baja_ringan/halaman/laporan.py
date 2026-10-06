"""Halaman Laporan Mingguan: susunan sama seperti sheet Produksi, Pengeluaran, Barang masuk di Excel."""
import pandas as pd
import streamlit as st

from inti import database as db
from inti import ekspor
from inti import laporan as lp
from inti import stok as sk
from inti import tampilan as tp

master = db.baca_master()
transaksi = db.baca_transaksi()

tp.judul("Laporan Mingguan", "table_view",
         "Rekap harian per pekan untuk tiap barang dan warna. Bisa diunduh sebagai Excel dengan susunan sheet seperti file lama.")
if not tp.butuh_data(master):
    st.stop()

kategori_list = list(dict.fromkeys(master["kategori"]))
p1, p2, p3 = st.columns([1, 1, 2])
kategori = p1.selectbox("Kategori", kategori_list)
cara = p2.segmented_control("Periode", ["Per bulan", "Rentang tanggal"], default="Per bulan", required=True)
if cara == "Per bulan":
    bulan = p3.selectbox("Bulan", lp.daftar_bulan(transaksi), format_func=lp.label_bulan)
    mulai, selesai = lp.rentang_bulan(bulan)
    nama_periode = lp.label_bulan(bulan).replace(" ", "_")
else:
    hari_ini = pd.Timestamp(db.hari_ini())
    rentang = p3.date_input("Dari dan sampai tanggal", value=(hari_ini.replace(day=1), hari_ini), format="DD/MM/YYYY")
    if not isinstance(rentang, (list, tuple)) or len(rentang) < 2:
        st.info("Pilih tanggal awal dan tanggal akhir.")
        st.stop()
    mulai, selesai = pd.Timestamp(rentang[0]), pd.Timestamp(rentang[1])
    nama_periode = f"{mulai:%d%m%Y}_sd_{selesai:%d%m%Y}"

st.caption(f"Periode {tp.tanggal(mulai)} sampai {tp.tanggal(selesai)}")

JENIS_TAB = [("Produksi", sk.PRODUKSI, ":material/precision_manufacturing:"),
             ("Pengeluaran", sk.PENGELUARAN, ":material/local_shipping:"),
             ("Barang Masuk", sk.BARANG_MASUK, ":material/move_to_inbox:")]

for tab, (judul, jenis, ikon) in zip(st.tabs([f"{i} {j}" for j, _, i in JENIS_TAB]), JENIS_TAB):
    with tab:
        tabel, meta = lp.tabel_mingguan(master, transaksi, kategori, jenis, mulai, selesai)
        if tabel.empty:
            st.caption("Tidak ada barang untuk laporan ini.")
            continue
        total = tabel.loc[tabel[lp.PENANDA] == "total", "TOTAL"].sum()
        pekan = [m for m in meta if m["total"] and m["kunci"] != "TOTAL"]
        kolom_pekan = st.columns(len(pekan) + 1)
        kolom_pekan[0].metric(f"Total {judul.lower()}", tp.angka(total), border=True)
        for kolom, m in zip(kolom_pekan[1:], pekan):
            nilai = tabel.loc[tabel[lp.PENANDA] == "total", m["kunci"]].sum()
            kolom.metric(m["kunci"].title(), tp.angka(nilai), border=True)

        hanya_isi = st.toggle("Sembunyikan barang tanpa transaksi", value=True, key=f"sembunyi_{jenis}")
        tampil = tabel
        if hanya_isi:
            tampil = tabel[(tabel["TOTAL"] != 0) | (tabel[lp.PENANDA] == "total")]
        tampil = tampil.drop(columns=[lp.PENANDA])
        kunci_angka = [m["kunci"] for m in meta]
        st.dataframe(
            tampil, hide_index=True, width="stretch", height=min(36 * (len(tampil) + 1) + 4, 620),
            column_config={
                "Supplier": st.column_config.TextColumn("Supp", pinned=True),
                "Nama Barang": st.column_config.TextColumn(pinned=True),
                "Varian": st.column_config.TextColumn("Warna / Ukuran", pinned=True),
                **{k: tp.kolom_angka(k) for k in kunci_angka},
            },
        )

st.divider()
st.markdown("**Unduh laporan Excel**")
st.caption("Berisi sheet Real Time, Produksi, Pengeluaran dan Barang masuk, sama seperti file STOK yang biasa dipakai.")
u1, u2 = st.columns(2)
with u1:
    st.download_button(
        f"Unduh laporan {kategori}", icon=":material/download:", type="primary",
        data=ekspor.buat_excel(master, transaksi, [kategori], mulai, selesai),
        file_name=f"STOK_{kategori.replace(' ', '_')}_{nama_periode}.xlsx",
    )
with u2:
    if len(kategori_list) > 1:
        st.download_button(
            "Unduh semua kategori dalam satu file", icon=":material/download:",
            data=ekspor.buat_excel(master, transaksi, kategori_list, mulai, selesai),
            file_name=f"STOK_SEMUA_{nama_periode}.xlsx",
        )
