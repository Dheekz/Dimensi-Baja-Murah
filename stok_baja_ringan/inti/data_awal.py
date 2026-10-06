"""Data awal yang disalin dari template Excel STOK_GMP dan STOK_SPANDEK.

Dipakai satu kali saat database masih kosong (menu Pengaturan).
Nama barang yang di Excel memakai tanda strip ditulis ulang dengan spasi,
contoh "Spandek pasir 0.30 6m".
"""
from inti.konfigurasi import DAFTAR_WARNA

TIPE_JADI = "BARANG JADI"
TIPE_BAHAN = "BAHAN BAKU"
TANGGAL_MULAI = "27/07/2026"

# Barang jadi: (kategori, supplier, nama, stok awal per warna, (nama plat, varian plat))
BARANG_JADI = [
    ("GMP", "WIJA", "2 STEP GMP SUPER", [0, 0, 0, 0, 0], ("PLAT WIJA", "SPR")),
    ("GMP", "WIJA", "2 STEP GMP KW", [0, 0, 0, 0, 0], ("PLAT WIJA", "KW")),
    ("GMP", "WIJA", "NOK C", [0, 0, 0, 0, 0], ("PLAT NOK", "C")),
    ("GMP", "WIJA", "NOK V", [0, 0, 0, 0, 0], ("PLAT NOK", "V")),
    ("GMP", "WIJA", "1 STEP", [0, 0, 0, 0, 0], ("PLAT GM", "1 STEP")),
    ("GMP", "WIJA", "2 STEP STD", [0, 0, 0, 0, 0], ("PLAT GM", "STD")),
    ("SPANDEK", "WIJA", "Spandek pasir 0.30 6m", [135, 84, 81, 0, 0], ("POLOSAN 0.30", "6m")),
    ("SPANDEK", "WIJA", "Spandek pasir 0.25 6m", [149, 137, 164, 0, 0], ("POLOSAN 0.25", "6m")),
    ("SPANDEK", "WIJA", "Spandek pasir 0.30 5m", [80, 42, 50, 0, 0], ("POLOSAN 0.30", "5m")),
    ("SPANDEK", "WIJA", "Spandek pasir 0.25 5m", [67, 60, 71, 0, 0], ("POLOSAN 0.25", "5m")),
    ("SPANDEK", "WIJA", "Spandek pasir 0.30 4m", [35, 41, 35, 0, 0], ("POLOSAN 0.30", "4m")),
    ("SPANDEK", "WIJA", "Spandek pasir 0.25 4m", [18, 45, 13, 0, 0], ("POLOSAN 0.25", "4m")),
    ("SPANDEK", "WIJA", "NOK SPANDEK", [35, 35, 41, 0, 0], ("PLAT NOK SPANDEK", "")),
    ("SPANDEK", "CVDMS", "2 STEP GLOSSY", [0, 10, 50, 0, 0], None),
    ("SPANDEK", "CVDMS", "1 STEP", [0, 40, 0, 0, 0], ("POLOSAN GENTENG", "1 STEP")),
    ("SPANDEK", "CVDMS", "NOK SAMPING", [49, 0, 0, 0, 0], ("POLOSAN GENTENG", "NOK S")),
    ("SPANDEK", "CVDMS", "MINIMALIST", [200, 0, 300, 0, 0], ("POLOSAN GENTENG", "MINIM")),
]

# Bahan baku plat: (kategori, supplier, nama, varian, stok awal)
BAHAN_BAKU = [
    ("GMP", "WIJA", "PLAT WIJA", "SPR", 0),
    ("GMP", "WIJA", "PLAT WIJA", "KW", 0),
    ("GMP", "WIJA", "PLAT BESM", "KW", 0),
    ("GMP", "WIJA", "PLAT GM", "STD", 0),
    ("GMP", "WIJA", "PLAT GM", "1 STEP", 0),
    ("GMP", "WIJA", "PLAT NOK", "C", 0),
    ("GMP", "WIJA", "PLAT NOK", "V", 0),
    ("SPANDEK", "WIJA", "POLOSAN 0.30", "6m", 0),
    ("SPANDEK", "WIJA", "POLOSAN 0.30", "5m", 13),
    ("SPANDEK", "WIJA", "POLOSAN 0.30", "4m", 0),
    ("SPANDEK", "WIJA", "POLOSAN 0.25", "6m", 219),
    ("SPANDEK", "WIJA", "POLOSAN 0.25", "5m", 0),
    ("SPANDEK", "WIJA", "POLOSAN 0.25", "4m", 0),
    ("SPANDEK", "WIJA", "PLAT NOK SPANDEK", "", 43),
    ("SPANDEK", "CVDMS", "POLOSAN GENTENG", "NOK S", 0),
    ("SPANDEK", "CVDMS", "POLOSAN GENTENG", "2X4 TIP", 0),
    ("SPANDEK", "CVDMS", "POLOSAN GENTENG", "2X4 TEB", 0),
    ("SPANDEK", "CVDMS", "POLOSAN GENTENG", "1 STEP", 0),
    ("SPANDEK", "CVDMS", "POLOSAN GENTENG", "MINIM", 1300),
]

# Transaksi yang sudah tercatat di template: (tanggal, jenis, kategori, nama, varian, jumlah)
TRANSAKSI_TEMPLATE = [
    ("28/07/2026", "PENGELUARAN", "SPANDEK", "Spandek pasir 0.30 6m", "Merah", 15),
    ("28/07/2026", "PENGELUARAN", "SPANDEK", "Spandek pasir 0.30 6m", "Hitam", 75),
    ("28/07/2026", "PENGELUARAN", "SPANDEK", "Spandek pasir 0.25 6m", "Merah", 10),
    ("28/07/2026", "PENGELUARAN", "SPANDEK", "Spandek pasir 0.30 5m", "Hitam", 50),
    ("28/07/2026", "PENGELUARAN", "SPANDEK", "Spandek pasir 0.25 4m", "Merah", 16),
    ("28/07/2026", "PENGELUARAN", "SPANDEK", "Spandek pasir 0.25 4m", "Hitam", 10),
    ("29/07/2026", "PRODUKSI", "SPANDEK", "Spandek pasir 0.30 6m", "Hitam", 30),
    ("28/07/2026", "BARANG MASUK", "SPANDEK", "POLOSAN 0.30", "6m", 500),
    ("28/07/2026", "BARANG MASUK", "SPANDEK", "POLOSAN 0.30", "5m", 100),
    ("28/07/2026", "BARANG MASUK", "SPANDEK", "POLOSAN 0.30", "4m", 150),
]


def awalan_kode(kategori):
    """Tiga huruf pertama kategori sebagai awalan kode barang."""
    huruf = "".join(ch for ch in str(kategori).upper() if ch.isalnum())
    return (huruf or "BRG")[:3]


def susun_master():
    """Menghasilkan daftar baris master barang (list of dict)."""
    baris = []
    nomor = {}
    peta_bahan = {}

    def kode_baru(kategori):
        awal = awalan_kode(kategori)
        nomor[awal] = nomor.get(awal, 0) + 1
        return f"{awal}{nomor[awal]:03d}"

    # Bahan baku dibuat lebih dulu supaya kodenya bisa dipakai barang jadi
    bahan_rows = []
    for kategori, supplier, nama, varian, stok in BAHAN_BAKU:
        kode = kode_baru(kategori)
        peta_bahan[(kategori, nama, varian)] = kode
        bahan_rows.append(dict(
            kode=kode, kategori=kategori, supplier=supplier, tipe=TIPE_BAHAN,
            nama_barang=nama, varian=varian, satuan="lembar", bahan_baku="",
            rasio=1, stok_awal=stok, tanggal_stok_awal=TANGGAL_MULAI,
            stok_minimum=0, aktif="YA",
        ))

    urutan = 0
    for kategori, supplier, nama, stok_warna, plat in BARANG_JADI:
        for warna, stok in zip(DAFTAR_WARNA, stok_warna):
            urutan += 1
            kode_plat = peta_bahan.get((kategori, plat[0], plat[1]), "") if plat else ""
            baris.append(dict(
                kode=kode_baru(kategori), kategori=kategori, supplier=supplier,
                tipe=TIPE_JADI, nama_barang=nama, varian=warna, satuan="lembar",
                bahan_baku=kode_plat, rasio=1, stok_awal=stok,
                tanggal_stok_awal=TANGGAL_MULAI, stok_minimum=0, urutan=urutan,
                aktif="YA",
            ))
    for item in bahan_rows:
        urutan += 1
        item["urutan"] = urutan
        baris.append(item)
    return baris


def susun_transaksi(master_rows):
    """Mengubah transaksi template menjadi baris transaksi dengan kode barang."""
    cari = {(m["kategori"], m["nama_barang"], m["varian"]): m["kode"] for m in master_rows}
    hasil = []
    for tanggal, jenis, kategori, nama, varian, jumlah in TRANSAKSI_TEMPLATE:
        kode = cari.get((kategori, nama, varian))
        if kode:
            hasil.append(dict(tanggal=tanggal, jenis=jenis, kode=kode, jumlah=jumlah,
                              keterangan="Data dari template Excel"))
    return hasil
