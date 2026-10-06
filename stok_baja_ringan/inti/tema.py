"""Palet warna aplikasi.

Terinspirasi dari bahan di toko baja ringan: abu baja galvalum untuk
latar dan teks, oranye atap sebagai warna aksen (sama dengan warna
aksen di file Excel lama). Warna antarmuka utama diatur di
.streamlit/config.toml, file ini dipakai untuk grafik dan file Excel.
"""

OREN = "#E0601B"
OREN_MUDA = "#FBE3D3"
BAJA_GELAP = "#1F2A36"
BAJA = "#3B4A5A"
BAJA_MUDA = "#9AA7B4"
SENG = "#E9ECF0"
LATAR = "#F5F6F8"
EMAS = "#E8A33D"

# Warna untuk tiap jenis transaksi di grafik
WARNA_JENIS = {
    "PRODUKSI": BAJA,
    "PENGELUARAN": OREN,
    "BARANG MASUK": EMAS,
    "KOREKSI TAMBAH": BAJA_MUDA,
    "KOREKSI KURANG": "#B83227",
}

# Warna asli produk untuk grafik per warna
WARNA_PRODUK = {
    "MERAH": "#B83227",
    "COKLAT": "#7A4B2A",
    "HITAM": "#2B2B2B",
    "HIJAU": "#2E7D4F",
    "BIRU": "#2563A6",
}


def tanpa_pagar(warna):
    """Format warna untuk openpyxl (tanpa tanda pagar di depan)."""
    return warna.replace("#", "").upper()
