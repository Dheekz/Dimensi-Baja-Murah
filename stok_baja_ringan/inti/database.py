"""Lapisan database.

Aplikasi memakai Google Sheet sebagai database. Bila kredensial belum
diisi di secrets, aplikasi otomatis berjalan dalam mode lokal (file CSV
di folder data_lokal) supaya tetap bisa dicoba.

Semua halaman cukup memanggil fungsi di bawah ini (baca_master,
baca_transaksi, simpan_transaksi, dan seterusnya) tanpa perlu tahu
datanya disimpan di mana.
"""
import random
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import streamlit as st

from inti import konfigurasi as kf

KOLOM = {
    kf.TAB_MASTER: [
        "kode", "kategori", "supplier", "tipe", "nama_barang", "varian", "satuan",
        "bahan_baku", "rasio", "stok_awal", "tanggal_stok_awal", "stok_minimum",
        "urutan", "aktif",
    ],
    kf.TAB_TRANSAKSI: [
        "id", "tanggal", "jenis", "kode", "jumlah", "keterangan", "petugas",
        "waktu_input", "status",
    ],
}

FOLDER_LOKAL = Path(__file__).resolve().parent.parent / "data_lokal"


def _bersihkan_nilai(nilai):
    """Mengubah tipe numpy menjadi tipe Python biasa agar bisa dikirim ke Google."""
    if nilai is None:
        return ""
    if isinstance(nilai, float) and np.isnan(nilai):
        return ""
    if isinstance(nilai, np.integer):
        return int(nilai)
    if isinstance(nilai, np.floating):
        nilai = float(nilai)
    if isinstance(nilai, float) and nilai.is_integer():
        return int(nilai)
    if isinstance(nilai, (pd.Timestamp, datetime, date)):
        return nilai.strftime(kf.FORMAT_TANGGAL)
    return nilai


def _ke_baris(df):
    return [[_bersihkan_nilai(v) for v in baris] for baris in df.itertuples(index=False)]


# Penyimpanan Google Sheet

class PenyimpananGoogleSheet:
    mode = "Google Sheet"

    def __init__(self, info_akun, alamat):
        import gspread

        klien = gspread.service_account_from_dict(info_akun)
        alamat = str(alamat).strip()
        if alamat.startswith("http"):
            self.buku = klien.open_by_url(alamat)
        else:
            self.buku = klien.open_by_key(alamat)
        self.url = self.buku.url
        self._lembar = {}
        self._pastikan_tab()

    def _pastikan_tab(self):
        ada = {ws.title: ws for ws in self.buku.worksheets()}
        for nama, kolom in KOLOM.items():
            if nama in ada:
                self._lembar[nama] = ada[nama]
                continue
            ws = self.buku.add_worksheet(title=nama, rows=1000, cols=len(kolom))
            ws.update(values=[kolom], range_name="A1")
            ws.freeze(rows=1)
            self._lembar[nama] = ws

    def baca(self, nama):
        from gspread.utils import ValueRenderOption

        nilai = self._lembar[nama].get_all_values(
            value_render_option=ValueRenderOption.unformatted
        )
        kolom = KOLOM[nama]
        if len(nilai) < 2:
            return pd.DataFrame(columns=kolom)
        df = pd.DataFrame(nilai[1:], columns=nilai[0])
        for k in kolom:
            if k not in df.columns:
                df[k] = ""
        return df[kolom]

    def tambah(self, nama, df):
        self._lembar[nama].append_rows(_ke_baris(df[KOLOM[nama]]), value_input_option="RAW")

    def tulis_ulang(self, nama, df):
        ws = self._lembar[nama]
        ws.clear()
        ws.update(values=[KOLOM[nama]] + _ke_baris(df[KOLOM[nama]]), range_name="A1")

    def ubah_nilai(self, nama, id_kolom, id_nilai, perubahan):
        kolom = KOLOM[nama]
        ws = self._lembar[nama]
        daftar_id = ws.col_values(kolom.index(id_kolom) + 1)
        if id_nilai not in daftar_id:
            raise KeyError(f"Data {id_nilai} tidak ditemukan")
        baris = daftar_id.index(id_nilai) + 1
        for k, v in perubahan.items():
            ws.update_cell(baris, kolom.index(k) + 1, _bersihkan_nilai(v))


# Penyimpanan lokal (mode demo)

class PenyimpananLokal:
    mode = "Lokal (demo)"

    def __init__(self, folder=FOLDER_LOKAL):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.url = None
        for nama, kolom in KOLOM.items():
            berkas = self._berkas(nama)
            if not berkas.exists():
                pd.DataFrame(columns=kolom).to_csv(berkas, index=False, encoding="utf8")

    def _berkas(self, nama):
        return self.folder / f"{nama}.csv"

    def baca(self, nama):
        return pd.read_csv(self._berkas(nama), dtype=str, keep_default_na=False, encoding="utf8")

    def tambah(self, nama, df):
        df[KOLOM[nama]].to_csv(self._berkas(nama), mode="a", header=False, index=False, encoding="utf8")

    def tulis_ulang(self, nama, df):
        df[KOLOM[nama]].to_csv(self._berkas(nama), index=False, encoding="utf8")

    def ubah_nilai(self, nama, id_kolom, id_nilai, perubahan):
        df = self.baca(nama)
        cocok = df[id_kolom] == id_nilai
        if not cocok.any():
            raise KeyError(f"Data {id_nilai} tidak ditemukan")
        for k, v in perubahan.items():
            df.loc[cocok, k] = v
        self.tulis_ulang(nama, df)


@st.cache_resource(show_spinner="Menghubungkan ke database...")
def ambil_penyimpanan():
    try:
        info = dict(st.secrets["gcp_service_account"])
        alamat = st.secrets["google_sheet"]["spreadsheet"]
    except Exception:
        return PenyimpananLokal()
    return PenyimpananGoogleSheet(info, alamat)


# Konversi tipe data

def sekarang():
    return datetime.now(ZoneInfo(kf.ZONA_WAKTU))


def hari_ini():
    return sekarang().date()


def ke_tanggal(seri):
    """Mengubah isi kolom tanggal (teks hari/bulan/tahun atau angka serial Sheet) jadi Timestamp."""
    def satu(v):
        if v is None or (isinstance(v, float) and np.isnan(v)) or str(v).strip() == "":
            return pd.NaT
        if isinstance(v, (int, float, np.integer, np.floating)):
            return pd.Timestamp(1899, 12, 30) + pd.Timedelta(days=float(v))
        teks = str(v).strip()
        for pola in (kf.FORMAT_TANGGAL, "%d/%m/%y", "%Y/%m/%d"):
            try:
                return pd.Timestamp(datetime.strptime(teks, pola))
            except ValueError:
                pass
        return pd.to_datetime(teks, dayfirst=True, errors="coerce")

    return pd.to_datetime(seri.map(satu)).dt.normalize()


def _ke_angka(seri):
    teks = seri.astype(str).str.replace(",", ".", regex=False).str.strip()
    return pd.to_numeric(teks, errors="coerce").fillna(0)


def siapkan_master(df):
    df = df.copy()
    for k in KOLOM[kf.TAB_MASTER]:
        if k not in df.columns:
            df[k] = ""
    for k in ("kode", "kategori", "supplier", "tipe", "nama_barang", "varian", "satuan", "bahan_baku"):
        df[k] = df[k].astype(str).str.strip()
    df["kategori"] = df["kategori"].str.upper()
    df["tipe"] = df["tipe"].str.upper()
    for k in ("rasio", "stok_awal", "stok_minimum", "urutan"):
        df[k] = _ke_angka(df[k])
    df.loc[df["rasio"] == 0, "rasio"] = 1
    df["tanggal_stok_awal"] = ke_tanggal(df["tanggal_stok_awal"])
    df["aktif"] = ~df["aktif"].astype(str).str.upper().isin(["TIDAK", "FALSE", "0", "NONAKTIF"])
    df = df[df["kode"] != ""]
    return df.sort_values(["kategori", "urutan", "nama_barang"], kind="stable").reset_index(drop=True)


def siapkan_transaksi(df):
    df = df.copy()
    for k in KOLOM[kf.TAB_TRANSAKSI]:
        if k not in df.columns:
            df[k] = ""
    for k in ("id", "jenis", "kode", "keterangan", "petugas", "waktu_input", "status"):
        df[k] = df[k].astype(str).str.strip()
    df["jenis"] = df["jenis"].str.upper()
    df["status"] = df["status"].str.upper().replace("", "AKTIF")
    df["tanggal"] = ke_tanggal(df["tanggal"])
    df["jumlah"] = _ke_angka(df["jumlah"])
    return df[df["kode"] != ""].reset_index(drop=True)


# Fungsi baca dengan cache

@st.cache_data(ttl=kf.TTL_CACHE, show_spinner="Memuat data barang...")
def baca_master():
    return siapkan_master(ambil_penyimpanan().baca(kf.TAB_MASTER))


@st.cache_data(ttl=kf.TTL_CACHE, show_spinner="Memuat transaksi...")
def baca_transaksi():
    return siapkan_transaksi(ambil_penyimpanan().baca(kf.TAB_TRANSAKSI))


def segarkan():
    baca_master.clear()
    baca_transaksi.clear()


# Fungsi tulis

def _id_baru(urut=0):
    acak = random.randint(0, 9999)
    return f"TRX{sekarang():%Y%m%d%H%M%S}{urut:03d}{acak:04d}"


def simpan_transaksi(daftar, petugas):
    """daftar berisi dict: tanggal (date atau teks), jenis, kode, jumlah, keterangan."""
    if not daftar:
        return 0
    waktu = sekarang().strftime("%d/%m/%Y %H:%M:%S")
    baris = []
    for i, d in enumerate(daftar):
        tgl = d["tanggal"]
        if not isinstance(tgl, str):
            tgl = tgl.strftime(kf.FORMAT_TANGGAL)
        baris.append(dict(
            id=_id_baru(i), tanggal=tgl, jenis=d["jenis"], kode=d["kode"],
            jumlah=_bersihkan_nilai(d["jumlah"]), keterangan=d.get("keterangan", ""),
            petugas=petugas or "", waktu_input=waktu, status="AKTIF",
        ))
    ambil_penyimpanan().tambah(kf.TAB_TRANSAKSI, pd.DataFrame(baris, columns=KOLOM[kf.TAB_TRANSAKSI]))
    baca_transaksi.clear()
    return len(baris)


def batalkan_transaksi(id_transaksi, alasan, petugas, keterangan_lama=""):
    catatan = f"DIBATALKAN oleh {petugas or 'petugas'}: {alasan}".strip()
    if keterangan_lama:
        catatan = f"{keterangan_lama} | {catatan}"
    ambil_penyimpanan().ubah_nilai(
        kf.TAB_TRANSAKSI, "id", id_transaksi, {"status": "BATAL", "keterangan": catatan}
    )
    baca_transaksi.clear()


def simpan_master(df):
    """Menulis ulang seluruh master barang (dipakai saat menambah atau mengedit barang)."""
    keluar = df.copy()
    keluar["tanggal_stok_awal"] = keluar["tanggal_stok_awal"].map(
        lambda v: v.strftime(kf.FORMAT_TANGGAL) if pd.notna(v) and hasattr(v, "strftime") else (v or "")
    )
    keluar["aktif"] = keluar["aktif"].map(lambda v: "YA" if v in (True, "YA", "TRUE") else "TIDAK")
    ambil_penyimpanan().tulis_ulang(kf.TAB_MASTER, keluar[KOLOM[kf.TAB_MASTER]])
    baca_master.clear()


def isi_data_awal(dengan_transaksi, petugas):
    from inti import data_awal

    baris_master = data_awal.susun_master()
    ambil_penyimpanan().tulis_ulang(
        kf.TAB_MASTER, pd.DataFrame(baris_master, columns=KOLOM[kf.TAB_MASTER])
    )
    jumlah_trx = 0
    if dengan_transaksi:
        jumlah_trx = simpan_transaksi(data_awal.susun_transaksi(baris_master), petugas)
    segarkan()
    return len(baris_master), jumlah_trx
