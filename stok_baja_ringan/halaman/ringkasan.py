"""Halaman Ringkasan: gambaran stok hari ini dan pergerakan 30 hari terakhir."""
from datetime import timedelta
from operator import sub

import altair as alt
import pandas as pd
import streamlit as st

from inti import database as db
from inti import konfigurasi as kf
from inti import laporan as lp
from inti import stok as sk
from inti import tampilan as tp
from inti.tema import WARNA_JENIS

master = db.baca_master()
transaksi = db.baca_transaksi()
hari_ini = db.hari_ini()

tp.judul("Ringkasan Stok", "dashboard", f"{kf.nama_usaha()}  •  posisi {tp.tanggal(pd.Timestamp(hari_ini))}")
if not tp.butuh_data(master):
    st.stop()

data = sk.hitung_stok(master[master["aktif"]], transaksi)
trx = sk.transaksi_aktif(transaksi)
awal_bulan = pd.Timestamp(hari_ini.year, hari_ini.month, 1)
bulan_ini = trx[trx["tanggal"] >= awal_bulan]


def total_jenis(df, jenis):
    return df.loc[df["jenis"] == jenis, "jumlah"].sum()


perhatian = data[data["status"].isin(sk.STATUS_PERHATIAN)]

k1, k2, k3, k4 = st.columns(4)
k1.metric("Stok barang jadi", tp.angka(data.loc[data["tipe"] == sk.TIPE_JADI, "stok_rt"].sum()), border=True,
          help="Jumlah seluruh stok barang jadi (semua kategori dan warna).")
k2.metric("Stok plat bahan baku", tp.angka(data.loc[data["tipe"] == sk.TIPE_BAHAN, "stok_rt"].sum()), border=True)
k3.metric("Perlu perhatian", len(perhatian), border=True,
          help="Barang yang stoknya minus atau sudah di bawah stok minimum.")
k4.metric("Transaksi hari ini", int((trx["tanggal"] == pd.Timestamp(hari_ini)).sum()), border=True)

nama_bulan = lp.label_bulan((hari_ini.year, hari_ini.month))
b1, b2, b3 = st.columns(3)
b1.metric(f"Produksi {nama_bulan}", tp.angka(total_jenis(bulan_ini, sk.PRODUKSI)), border=True)
b2.metric(f"Pengeluaran {nama_bulan}", tp.angka(total_jenis(bulan_ini, sk.PENGELUARAN)), border=True)
b3.metric(f"Barang masuk {nama_bulan}", tp.angka(total_jenis(bulan_ini, sk.BARANG_MASUK)), border=True)

if not perhatian.empty:
    with st.expander(f":material/warning: {len(perhatian)} barang perlu perhatian", expanded=True):
        tampil = perhatian[["kategori", "nama_barang", "varian", "stok_rt", "stok_minimum", "status"]]
        st.dataframe(
            tampil, hide_index=True, width="stretch",
            column_config={
                "kategori": "Kategori", "nama_barang": "Nama Barang", "varian": "Warna / Ukuran",
                "stok_rt": tp.kolom_angka("Stok RT"), "stok_minimum": tp.kolom_angka("Stok Minimum"),
                "status": "Status",
            },
        )

st.subheader("Stok per kategori")
kategori_list = list(dict.fromkeys(data["kategori"]))
for tab, kategori in zip(st.tabs(kategori_list), kategori_list):
    with tab:
        bagian = data[data["kategori"] == kategori]
        jadi = bagian[bagian["tipe"] == sk.TIPE_JADI]
        bahan = bagian[bagian["tipe"] == sk.TIPE_BAHAN]
        kiri, kanan = st.columns([3, 2])
        with kiri:
            st.markdown("**Barang jadi per warna**")
            if jadi.empty:
                st.caption("Belum ada barang jadi.")
            else:
                urutan_nama = list(dict.fromkeys(jadi["nama_barang"]))
                urutan_varian = [w for w in kf.DAFTAR_WARNA if w in set(jadi["varian"])]
                urutan_varian += [v for v in dict.fromkeys(jadi["varian"]) if v not in urutan_varian]
                matriks = jadi.pivot_table(index="nama_barang", columns="varian", values="stok_rt", aggfunc="sum")
                matriks = matriks.reindex(index=urutan_nama, columns=urutan_varian)
                matriks["Total"] = matriks.sum(axis=1)
                matriks.index.name = "Nama Barang"
                st.dataframe(matriks, width="stretch",
                             column_config={c: tp.kolom_angka(c) for c in matriks.columns})
        with kanan:
            st.markdown("**Plat bahan baku**")
            if bahan.empty:
                st.caption("Belum ada bahan baku.")
            else:
                st.dataframe(
                    bahan[["nama_barang", "varian", "stok_rt", "status"]], hide_index=True, width="stretch",
                    column_config={
                        "nama_barang": "Plat", "varian": "Jenis", "stok_rt": tp.kolom_angka("Stok RT"),
                        "status": "Status",
                    },
                )

st.subheader("Pergerakan 30 hari terakhir")
pilih = st.segmented_control("Kategori", ["Semua"] + kategori_list, default="Semua", label_visibility="collapsed")
mulai = sub(pd.Timestamp(hari_ini), timedelta(days=29))
harian = lp.ringkas_per_hari(transaksi, master, mulai, pd.Timestamp(hari_ini),
                             None if pilih in (None, "Semua") else pilih)
if harian.empty:
    st.caption("Belum ada transaksi dalam 30 hari terakhir.")
else:
    urutan_jenis = list(WARNA_JENIS)[:3]
    harian["hari"] = harian["tanggal"].dt.strftime("%d/%m")
    urutan_hari = list(dict.fromkeys(harian.sort_values("tanggal")["hari"]))
    grafik = (
        alt.Chart(harian)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X("hari:O", title=None, sort=urutan_hari, axis=alt.Axis(labelAngle=0)),
            xOffset=alt.XOffset("jenis:N", sort=urutan_jenis),
            y=alt.Y("jumlah:Q", title="Jumlah"),
            color=alt.Color("jenis:N", title=None, sort=urutan_jenis,
                            scale=alt.Scale(domain=urutan_jenis, range=[WARNA_JENIS[j] for j in urutan_jenis]),
                            legend=alt.Legend(orient="top")),
            tooltip=[alt.Tooltip("tanggal:T", title="Tanggal", format="%d/%m/%Y"),
                     alt.Tooltip("jenis:N", title="Jenis"), alt.Tooltip("jumlah:Q", title="Jumlah", format=",.0f")],
        )
        .properties(height=320)
    )
    st.altair_chart(grafik, width="stretch")
