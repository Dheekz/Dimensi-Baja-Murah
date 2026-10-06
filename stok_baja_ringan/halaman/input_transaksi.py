"""Halaman Input Transaksi: mencatat produksi, pengeluaran dan barang masuk harian."""
import pandas as pd
import streamlit as st

from inti import database as db
from inti import stok as sk
from inti import tampilan as tp

LABEL_JENIS = {
    sk.PRODUKSI: "Produksi",
    sk.PENGELUARAN: "Pengeluaran",
    sk.BARANG_MASUK: "Barang Masuk",
}
TIPE_BOLEH = {
    sk.PRODUKSI: [sk.TIPE_JADI],
    sk.PENGELUARAN: [sk.TIPE_JADI, sk.TIPE_BAHAN],
    sk.BARANG_MASUK: [sk.TIPE_BAHAN, sk.TIPE_JADI],
}
PENJELASAN = {
    sk.PRODUKSI: "Barang jadi bertambah, plat bahan bakunya otomatis berkurang.",
    sk.PENGELUARAN: "Barang keluar dari gudang (terjual atau dikirim). Stok berkurang.",
    sk.BARANG_MASUK: "Kiriman dari supplier, biasanya plat polosan. Stok bertambah.",
}

st.session_state.setdefault("putaran_input", 0)

master = db.baca_master()
transaksi = db.baca_transaksi()
hari_ini = db.hari_ini()

tp.judul("Input Transaksi", "edit_note", "Catat produksi, pengeluaran dan barang masuk. Isi kolom Jumlah saja, baris yang kosong diabaikan.")
if not tp.butuh_data(master):
    st.stop()

data_stok = sk.hitung_stok(master, transaksi)
aktif = data_stok[data_stok["aktif"]]
kategori_list = list(dict.fromkeys(aktif["kategori"]))

k1, k2, k3 = st.columns([1, 2, 1])
tanggal = k1.date_input("Tanggal", value=hari_ini, max_value=hari_ini, format="DD/MM/YYYY")
jenis = k2.segmented_control("Jenis transaksi", list(LABEL_JENIS), default=sk.PRODUKSI,
                             format_func=LABEL_JENIS.get, required=True, width="stretch")
kategori = k3.selectbox("Kategori", kategori_list)
st.caption(f":material/info: {PENJELASAN[jenis]}")

pilihan = aktif[(aktif["kategori"] == kategori) & aktif["tipe"].isin(TIPE_BOLEH[jenis])]
if pilihan.empty:
    st.info("Tidak ada barang yang cocok untuk jenis transaksi ini di kategori tersebut.")
    st.stop()


def tabel_isian(daftar):
    df = daftar[["kode", "tipe", "nama_barang", "varian", "stok_rt"]].copy()
    df["jumlah"] = 0
    df["catatan"] = ""
    return df.reset_index(drop=True)


def editor(df, kunci):
    return st.data_editor(
        df,
        key=kunci,
        hide_index=True,
        width="stretch",
        height=min(38 * (len(df) + 1) + 4, 560),
        column_order=["nama_barang", "varian", "stok_rt", "jumlah", "catatan"],
        disabled=["kode", "tipe", "nama_barang", "varian", "stok_rt"],
        column_config={
            "nama_barang": "Nama Barang",
            "varian": "Warna / Ukuran",
            "stok_rt": tp.kolom_angka("Stok Saat Ini"),
            "jumlah": st.column_config.NumberColumn(f"Jumlah {LABEL_JENIS[jenis]}", min_value=0, step=1, format="%d"),
            "catatan": st.column_config.TextColumn("Catatan baris (opsional)"),
        },
    )


kunci_dasar = f"{jenis}_{kategori}_{st.session_state['putaran_input']}"
tab_barang, tab_kategori = st.tabs([":material/view_agenda: Per nama barang", ":material/view_list: Satu kategori penuh"])

with tab_barang:
    kelompok = pilihan.drop_duplicates(["supplier", "nama_barang"])
    label = {
        (r.supplier, r.nama_barang): f"{r.nama_barang}  ({r.supplier})" if r.supplier else r.nama_barang
        for r in kelompok.itertuples()
    }
    dipilih = st.selectbox("Nama barang", list(label), format_func=label.get)
    hasil_barang = editor(
        tabel_isian(pilihan[(pilihan["supplier"] == dipilih[0]) & (pilihan["nama_barang"] == dipilih[1])]),
        f"barang_{kunci_dasar}_{dipilih[1]}",
    )

with tab_kategori:
    st.caption("Semua barang di kategori ini dalam satu tabel, cocok untuk rekap akhir hari.")
    hasil_kategori = editor(tabel_isian(pilihan), f"kategori_{kunci_dasar}")

# Gabungkan isian dari kedua tab
terisi = pd.concat([hasil_barang, hasil_kategori], ignore_index=True)
terisi["jumlah"] = pd.to_numeric(terisi["jumlah"], errors="coerce").fillna(0)
terisi = terisi[terisi["jumlah"] > 0]
terisi["catatan"] = terisi["catatan"].fillna("").astype(str)
duplikat = terisi["kode"].duplicated(keep=False)

st.divider()
keterangan = st.text_input("Keterangan umum (opsional)", placeholder="Contoh: nomor nota, nama pelanggan, nomor surat jalan")

if terisi.empty:
    st.caption("Belum ada jumlah yang diisi.")
    st.stop()

if duplikat.any():
    st.warning("Ada barang yang diisi di kedua tab sekaligus. Keduanya akan disimpan sebagai transaksi terpisah.",
               icon=":material/content_copy:")

st.markdown(f"**Akan disimpan: {len(terisi)} baris, total {tp.angka(terisi['jumlah'].sum())}**")
boleh_simpan = True

if jenis == sk.PENGELUARAN:
    lebih = terisi.groupby("kode").agg(nama=("nama_barang", "first"), varian=("varian", "first"),
                                      stok=("stok_rt", "first"), jumlah=("jumlah", "sum"))
    lebih = lebih[lebih["jumlah"] > lebih["stok"]]
    if not lebih.empty:
        daftar = ", ".join(f"{r.nama} {r.varian} (stok {tp.angka(r.stok)}, keluar {tp.angka(r.jumlah)})" for r in lebih.itertuples())
        st.warning(f"Pengeluaran melebihi stok: {daftar}", icon=":material/warning:")
        boleh_simpan = st.checkbox("Saya sudah cek, tetap simpan")

if jenis == sk.PRODUKSI:
    pakai = terisi.merge(master[["kode", "bahan_baku", "rasio"]], on="kode", how="left")
    pakai = pakai[pakai["bahan_baku"].astype(str) != ""]
    if not pakai.empty:
        pakai["kebutuhan"] = pakai["jumlah"] * pakai["rasio"]
        rekap = pakai.groupby("bahan_baku", as_index=False)["kebutuhan"].sum()
        rekap = rekap.merge(data_stok[["kode", "nama_barang", "varian", "stok_rt"]],
                            left_on="bahan_baku", right_on="kode", how="left")
        rekap["sisa"] = rekap["stok_rt"].sub(rekap["kebutuhan"])
        st.markdown("**Plat bahan baku yang ikut berkurang**")
        st.dataframe(
            rekap[["nama_barang", "varian", "stok_rt", "kebutuhan", "sisa"]], hide_index=True, width="stretch",
            column_config={
                "nama_barang": "Plat", "varian": "Jenis", "stok_rt": tp.kolom_angka("Stok Plat"),
                "kebutuhan": tp.kolom_angka("Dipakai"), "sisa": tp.kolom_angka("Sisa Setelah Produksi"),
            },
        )
        if (rekap["sisa"] < 0).any():
            st.warning("Ada plat yang akan minus. Periksa apakah barang masuk plat sudah dicatat.", icon=":material/warning:")

awal_stok = master.set_index("kode")["tanggal_stok_awal"]
terlalu_awal = terisi[terisi["kode"].map(awal_stok) > pd.Timestamp(tanggal)]
if not terlalu_awal.empty:
    st.info("Sebagian barang punya tanggal stok awal setelah tanggal transaksi ini, "
            "sehingga transaksi tersebut tidak ikut menghitung stok.", icon=":material/event_busy:")

if st.button("Simpan transaksi", type="primary", icon=":material/save:", disabled=not boleh_simpan):
    if tp.butuh_petugas():
        daftar = [
            dict(tanggal=tanggal, jenis=jenis, kode=r.kode, jumlah=r.jumlah,
                 keterangan=" | ".join(x for x in (keterangan.strip(), str(r.catatan or "").strip()) if x))
            for r in terisi.itertuples()
        ]
        with st.spinner("Menyimpan ke database..."):
            jumlah = db.simpan_transaksi(daftar, tp.petugas())
        st.session_state["putaran_input"] += 1
        tp.titip_pesan(f"{jumlah} transaksi {LABEL_JENIS[jenis].lower()} tersimpan")
        st.rerun()
