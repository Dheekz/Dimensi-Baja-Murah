"""Halaman Master Barang: daftar barang, warna, plat bahan baku, stok awal dan stok minimum."""
import pandas as pd
import streamlit as st

from inti import database as db
from inti import konfigurasi as kf
from inti import stok as sk
from inti import tampilan as tp
from inti.data_awal import awalan_kode

master = db.baca_master()
transaksi = db.baca_transaksi()
hari_ini = db.hari_ini()

tp.judul("Master Barang", "category",
         "Daftar barang yang dipantau. Kategori baru otomatis muncul sebagai tab baru di Ringkasan dan Laporan.")

PEMISAH = " | "


def label_bahan(df):
    bahan = df[df["tipe"] == sk.TIPE_BAHAN]
    return {r.kode: f"{r.kode}{PEMISAH}{r.nama_barang} {r.varian}".strip() for r in bahan.itertuples()}


def kode_dari_label(teks):
    teks = str(teks or "").strip()
    return teks.split(PEMISAH)[0].strip() if teks else ""


def kode_berikut(df, kategori, jumlah):
    awal = awalan_kode(kategori)
    ada = df["kode"][df["kode"].str.startswith(awal)].str[len(awal):]
    nomor = pd.to_numeric(ada, errors="coerce").max()
    mulai = int(nomor) + 1 if pd.notna(nomor) else 1
    return [f"{awal}{n:03d}" for n in range(mulai, mulai + jumlah)]


tab_daftar, tab_tambah = st.tabs([":material/edit: Daftar dan edit", ":material/add_box: Tambah barang baru"])

with tab_daftar:
    if master.empty:
        st.info("Belum ada barang. Tambahkan lewat tab sebelah, atau isi data awal di menu Pengaturan.")
    else:
        kategori_list = list(dict.fromkeys(master["kategori"]))
        pilih = st.segmented_control("Kategori", kategori_list, default=kategori_list[0], required=True)
        peta_bahan = label_bahan(master)
        bagian = master[master["kategori"] == pilih].copy()
        bagian["bahan_baku"] = bagian["bahan_baku"].map(lambda k: peta_bahan.get(k, ""))
        bagian["tanggal_stok_awal"] = bagian["tanggal_stok_awal"].dt.date
        st.caption("Ubah langsung di tabel lalu tekan Simpan. Untuk menyesuaikan stok dengan hitungan gudang, "
                   "gunakan menu Stok Opname supaya riwayatnya tercatat. Barang yang sudah tidak dijual cukup "
                   "dinonaktifkan (hapus centang Aktif).")
        diedit = st.data_editor(
            bagian, hide_index=True, width="stretch", num_rows="fixed", height=tp.tinggi_tabel(len(bagian)),
            key=f"master_{pilih}",
            column_order=["kode", "supplier", "tipe", "nama_barang", "varian", "satuan", "bahan_baku", "rasio",
                          "stok_awal", "tanggal_stok_awal", "stok_minimum", "aktif"],
            disabled=["kode"],
            column_config={
                "kode": "Kode",
                "supplier": "Supp",
                "tipe": st.column_config.SelectboxColumn("Tipe", options=[sk.TIPE_JADI, sk.TIPE_BAHAN], required=True),
                "nama_barang": st.column_config.TextColumn("Nama Barang", required=True),
                "varian": "Warna / Ukuran",
                "satuan": "Satuan",
                "bahan_baku": st.column_config.SelectboxColumn(
                    "Plat Bahan Baku", options=[""] + list(peta_bahan.values()),
                    help="Plat yang otomatis berkurang saat barang ini diproduksi"),
                "rasio": st.column_config.NumberColumn("Rasio Plat", min_value=0, step=0.01,
                                                       help="Jumlah plat terpakai untuk 1 barang jadi"),
                "stok_awal": st.column_config.NumberColumn("Stok Awal", min_value=0, step=1, format="%d"),
                "tanggal_stok_awal": st.column_config.DateColumn("Tgl Stok Awal", format="DD/MM/YYYY"),
                "stok_minimum": st.column_config.NumberColumn("Stok Minimum", min_value=0, step=1, format="%d",
                                                             help="Bila stok di bawah angka ini, muncul peringatan"),
                "aktif": st.column_config.CheckboxColumn("Aktif"),
            },
        )
        if st.button("Simpan perubahan", type="primary", icon=":material/save:", key="simpan_master"):
            baru = diedit.copy()
            baru["bahan_baku"] = baru["bahan_baku"].map(kode_dari_label)
            baru["tanggal_stok_awal"] = pd.to_datetime(baru["tanggal_stok_awal"])
            if (baru["nama_barang"].fillna("").str.strip() == "").any():
                st.error("Nama barang tidak boleh kosong.")
            else:
                semua = pd.concat([master[master["kategori"] != pilih], baru], ignore_index=True)
                semua = semua.sort_values(["kategori", "urutan"], kind="stable")
                db.simpan_master(semua)
                tp.titip_pesan("Master barang tersimpan")
                st.rerun()

with tab_tambah:
    kategori_ada = list(dict.fromkeys(master["kategori"])) if not master.empty else []
    peta_bahan = label_bahan(master) if not master.empty else {}
    with st.form("form_tambah", clear_on_submit=False):
        a1, a2, a3 = st.columns(3)
        kategori_pilih = a1.selectbox("Kategori", kategori_ada + ["(Kategori baru)"])
        kategori_baru = a1.text_input("Nama kategori baru", placeholder="Isi bila memilih kategori baru")
        supplier = a2.text_input("Supplier", placeholder="contoh: WIJA")
        tipe = a3.selectbox("Tipe", [sk.TIPE_JADI, sk.TIPE_BAHAN])

        b1, b2 = st.columns([2, 1])
        nama = b1.text_input("Nama barang", placeholder="contoh: Spandek pasir 0.35 6m")
        satuan = b2.text_input("Satuan", value="lembar")

        warna = st.multiselect("Warna", kf.DAFTAR_WARNA, default=kf.DAFTAR_WARNA if tipe == sk.TIPE_JADI else [],
                               help="Satu baris barang dibuat untuk tiap warna")
        varian_lain = st.text_input("Varian lain (pisahkan dengan koma)",
                                    placeholder="contoh untuk plat: 6m, 5m, 4m. Kosongkan bila tidak ada")

        c1, c2, c3, c4 = st.columns(4)
        bahan = c1.selectbox("Plat bahan baku", [""] + list(peta_bahan.values()),
                             help="Hanya untuk barang jadi. Plat ini berkurang saat produksi.")
        rasio = c2.number_input("Rasio plat", min_value=0.0, value=1.0, step=0.01)
        stok_minimum = c3.number_input("Stok minimum", min_value=0, value=0, step=1)
        tanggal_awal = c4.date_input("Tanggal stok awal", value=hari_ini, format="DD/MM/YYYY")
        st.caption("Stok awal tiap varian bisa diisi setelah barang tersimpan (tab Daftar dan edit) atau lewat Stok Opname.")
        kirim = st.form_submit_button("Tambahkan barang", type="primary", icon=":material/add:")

    if kirim:
        kategori = (kategori_baru if kategori_pilih == "(Kategori baru)" else kategori_pilih).strip().upper()
        daftar_varian = list(warna) + [v.strip() for v in varian_lain.split(",") if v.strip()]
        if not daftar_varian:
            daftar_varian = [""]
        if not kategori:
            st.error("Isi nama kategori.")
        elif not nama.strip():
            st.error("Isi nama barang.")
        else:
            kembar = master[(master["kategori"] == kategori) & (master["nama_barang"].str.upper() == nama.strip().upper())
                            & master["varian"].isin(daftar_varian)] if not master.empty else master
            if not kembar.empty:
                st.error(f"Barang ini sudah ada: {', '.join(kembar['varian'])}")
            else:
                kode = kode_berikut(master if not master.empty else pd.DataFrame({"kode": pd.Series(dtype=str)}),
                                    kategori, len(daftar_varian))
                urut_awal = int(master["urutan"].max()) + 1 if not master.empty else 1
                baru = pd.DataFrame([
                    dict(kode=k, kategori=kategori, supplier=supplier.strip().upper(), tipe=tipe,
                         nama_barang=nama.strip(), varian=v, satuan=satuan.strip(),
                         bahan_baku=kode_dari_label(bahan) if tipe == sk.TIPE_JADI else "",
                         rasio=rasio, stok_awal=0, tanggal_stok_awal=pd.Timestamp(tanggal_awal),
                         stok_minimum=stok_minimum, urutan=urut_awal + i, aktif=True)
                    for i, (k, v) in enumerate(zip(kode, daftar_varian))
                ])
                db.simpan_master(pd.concat([master, baru], ignore_index=True))
                tp.titip_pesan(f"{len(baru)} barang baru ditambahkan ke {kategori}")
                st.rerun()
