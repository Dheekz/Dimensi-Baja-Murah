"""Perhitungan stok real time.

Rumus sama dengan sheet "Real Time" di Excel lama:
  Barang jadi : stok awal + produksi + barang masuk, dikurangi pengeluaran
  Bahan baku  : stok awal + barang masuk, dikurangi pengeluaran dan
                pemakaian untuk produksi barang jadi yang memakai plat itu
Ditambah koreksi hasil stok opname (koreksi tambah dan koreksi kurang).
Transaksi hanya dihitung bila tanggalnya sama atau setelah tanggal stok awal.
"""
import pandas as pd

PRODUKSI = "PRODUKSI"
PENGELUARAN = "PENGELUARAN"
BARANG_MASUK = "BARANG MASUK"
KOREKSI_TAMBAH = "KOREKSI TAMBAH"
KOREKSI_KURANG = "KOREKSI KURANG"
SEMUA_JENIS = [PRODUKSI, PENGELUARAN, BARANG_MASUK, KOREKSI_TAMBAH, KOREKSI_KURANG]
JENIS_HARIAN = [PRODUKSI, PENGELUARAN, BARANG_MASUK]

TIPE_JADI = "BARANG JADI"
TIPE_BAHAN = "BAHAN BAKU"

STATUS_AMAN = "Aman"
STATUS_KOSONG = "Kosong"
STATUS_MENIPIS = "Menipis"
STATUS_MINUS = "Minus, cek data"
STATUS_PERHATIAN = [STATUS_MENIPIS, STATUS_MINUS]

_KOLOM_JENIS = {
    PRODUKSI: "produksi",
    BARANG_MASUK: "barang_masuk",
    PENGELUARAN: "pengeluaran",
    KOREKSI_TAMBAH: "koreksi_tambah",
    KOREKSI_KURANG: "koreksi_kurang",
}


def transaksi_aktif(transaksi):
    return transaksi[transaksi["status"] != "BATAL"]


def _tentukan_status(baris):
    stok = baris["stok_rt"]
    if stok < 0:
        return STATUS_MINUS
    if baris["stok_minimum"] > 0 and stok <= baris["stok_minimum"]:
        return STATUS_MENIPIS
    if stok == 0:
        return STATUS_KOSONG
    return STATUS_AMAN


def hitung_stok(master, transaksi, sampai=None):
    """Mengembalikan master barang lengkap dengan kolom pergerakan dan stok_rt."""
    hasil = master.copy()
    trx = transaksi_aktif(transaksi)
    if sampai is not None:
        trx = trx[trx["tanggal"] <= pd.Timestamp(sampai)]

    batas = master.set_index("kode")["tanggal_stok_awal"]
    trx = trx.assign(batas=trx["kode"].map(batas))
    sah = trx[trx["batas"].isna() | (trx["tanggal"] >= trx["batas"])]

    if sah.empty:
        rekap = pd.DataFrame()
    else:
        rekap = sah.pivot_table(index="kode", columns="jenis", values="jumlah", aggfunc="sum", fill_value=0)

    for jenis, kolom in _KOLOM_JENIS.items():
        if jenis in rekap.columns:
            hasil[kolom] = hasil["kode"].map(rekap[jenis]).fillna(0)
        else:
            hasil[kolom] = 0.0

    # Pemakaian plat untuk produksi
    peta = master.set_index("kode")[["bahan_baku", "rasio"]]
    prod = trx[trx["jenis"] == PRODUKSI].join(peta, on="kode")
    prod = prod[prod["bahan_baku"].fillna("").astype(str).str.strip() != ""]
    if prod.empty:
        hasil["dipakai_produksi"] = 0.0
    else:
        prod = prod.assign(
            pakai=prod["jumlah"] * prod["rasio"],
            batas_bahan=prod["bahan_baku"].map(batas),
        )
        prod = prod[prod["batas_bahan"].isna() | (prod["tanggal"] >= prod["batas_bahan"])]
        hasil["dipakai_produksi"] = hasil["kode"].map(prod.groupby("bahan_baku")["pakai"].sum()).fillna(0)

    bertambah = hasil["stok_awal"] + hasil["produksi"] + hasil["barang_masuk"] + hasil["koreksi_tambah"]
    berkurang = hasil["pengeluaran"] + hasil["dipakai_produksi"] + hasil["koreksi_kurang"]
    hasil["stok_rt"] = bertambah.sub(berkurang)
    hasil["selisih"] = hasil["stok_awal"].sub(hasil["stok_rt"])
    hasil["status"] = hasil.apply(_tentukan_status, axis=1) if not hasil.empty else []
    return hasil


def label_barang(baris):
    varian = str(baris.get("varian", "")).strip()
    return f"{baris['nama_barang']} {varian}".strip()
