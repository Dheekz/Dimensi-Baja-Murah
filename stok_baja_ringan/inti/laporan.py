"""Menyusun tabel laporan mingguan seperti sheet Produksi, Pengeluaran dan Barang masuk di Excel.

Kolom: tiap tanggal Senin sampai Sabtu (Minggu ikut muncul bila ada transaksi),
lalu TOTAL PEKAN untuk tiap pekan, dan TOTAL di paling kanan.
Baris: tiap barang per warna, ditambah baris TOTAL per nama barang.
"""
from datetime import timedelta
from operator import sub

import pandas as pd

from inti import konfigurasi as kf
from inti import stok as sk

KOLOM_INFO = ["Supplier", "Nama Barang", "Varian"]
PENANDA = "_baris"  # isi, subtotal, total


def _senin(tanggal):
    return sub(tanggal, timedelta(days=tanggal.weekday()))


def daftar_bulan(transaksi, jumlah_ke_belakang=12):
    """Pilihan bulan (tahun, bulan) mulai bulan ini mundur ke belakang plus bulan yang ada datanya."""
    from inti.database import hari_ini

    ini = hari_ini()
    pilihan = set()
    tahun, bulan = ini.year, ini.month
    for _ in range(jumlah_ke_belakang):
        pilihan.add((tahun, bulan))
        bulan = sub(bulan, 1)
        if bulan == 0:
            bulan, tahun = 12, sub(tahun, 1)
    if not transaksi.empty:
        for t in transaksi["tanggal"].dropna():
            pilihan.add((t.year, t.month))
    return sorted(pilihan, reverse=True)


def label_bulan(tahun_bulan):
    tahun, bulan = tahun_bulan
    return f"{kf.NAMA_BULAN[sub(bulan, 1)]} {tahun}"


def rentang_bulan(tahun_bulan):
    tahun, bulan = tahun_bulan
    mulai = pd.Timestamp(tahun, bulan, 1)
    return mulai, mulai + pd.offsets.MonthEnd(0)


def tabel_mingguan(master, transaksi, kategori, jenis, mulai, selesai):
    """Mengembalikan (DataFrame, daftar keterangan kolom)."""
    mulai, selesai = pd.Timestamp(mulai).normalize(), pd.Timestamp(selesai).normalize()
    m = master[master["kategori"] == kategori]
    t = sk.transaksi_aktif(transaksi)
    t = t[(t["jenis"] == jenis) & (t["tanggal"] >= mulai) & (t["tanggal"] <= selesai) & t["kode"].isin(m["kode"])]

    if jenis == sk.PRODUKSI:
        dasar = m[m["tipe"] == sk.TIPE_JADI]
    elif jenis == sk.BARANG_MASUK:
        dasar = m[m["tipe"] == sk.TIPE_BAHAN]
    else:
        dasar = m
    pakai = m[(m["kode"].isin(dasar["kode"]) & m["aktif"]) | m["kode"].isin(t["kode"])]

    nilai = t.groupby(["kode", "tanggal"])["jumlah"].sum()
    tanggal_berisi = set(t["tanggal"])

    # Susun kolom per pekan
    kolom_meta = []
    hari = pd.date_range(mulai, selesai, freq="D")
    pekan = {}
    for h in hari:
        pekan.setdefault(_senin(h), []).append(h)
    for nomor, (senin, daftar_hari) in enumerate(sorted(pekan.items()), start=1):
        dipakai = []
        for h in daftar_hari:
            if h.weekday() < 6 or h in tanggal_berisi:
                label = f"{kf.HARI_PENDEK[h.weekday()]} {h:%d/%m}"
                kolom_meta.append(dict(kunci=label, hari=kf.NAMA_HARI[h.weekday()], tanggal=h, total=False))
                dipakai.append((label, h))
        kolom_meta.append(dict(kunci=f"TOTAL PEKAN {nomor}", hari=f"TOTAL PEKAN {nomor}",
                               tanggal=None, total=True, isi=[h for h in daftar_hari]))
    kolom_meta.append(dict(kunci="TOTAL", hari="TOTAL", tanggal=None, total=True, isi=list(hari)))

    def baris_untuk(kode):
        data = {}
        for k in kolom_meta:
            if k["total"]:
                data[k["kunci"]] = float(sum(nilai.get((kode, h), 0) for h in k["isi"]))
            else:
                data[k["kunci"]] = float(nilai.get((kode, k["tanggal"]), 0))
        return data

    baris = []
    for (supplier, nama), kelompok in pakai.groupby(["supplier", "nama_barang"], sort=False):
        subtotal = {k["kunci"]: 0.0 for k in kolom_meta}
        for _, item in kelompok.iterrows():
            data = baris_untuk(item["kode"])
            for k, v in data.items():
                subtotal[k] += v
            baris.append({"Supplier": supplier, "Nama Barang": nama, "Varian": item["varian"], **data, PENANDA: "isi"})
        if len(kelompok) > 1:
            baris.append({"Supplier": supplier, "Nama Barang": nama, "Varian": "TOTAL", **subtotal, PENANDA: "subtotal"})

    df = pd.DataFrame(baris, columns=KOLOM_INFO + [k["kunci"] for k in kolom_meta] + [PENANDA])
    if not df.empty:
        isi = df[df[PENANDA] == "isi"]
        total = {k["kunci"]: isi[k["kunci"]].sum() for k in kolom_meta}
        df = pd.concat([df, pd.DataFrame([{"Supplier": "", "Nama Barang": "TOTAL SEMUA", "Varian": "", **total, PENANDA: "total"}])],
                       ignore_index=True)
    return df, kolom_meta


def ringkas_per_hari(transaksi, master, mulai, selesai, kategori=None):
    """Jumlah per tanggal per jenis, untuk grafik."""
    t = sk.transaksi_aktif(transaksi)
    t = t[(t["tanggal"] >= pd.Timestamp(mulai)) & (t["tanggal"] <= pd.Timestamp(selesai)) & t["jenis"].isin(sk.JENIS_HARIAN)]
    if kategori:
        t = t[t["kode"].isin(master.loc[master["kategori"] == kategori, "kode"])]
    return t.groupby(["tanggal", "jenis"], as_index=False)["jumlah"].sum()
