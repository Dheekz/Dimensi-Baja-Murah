# Aplikasi Stok Baja Ringan

Aplikasi web berbasis Streamlit untuk mencatat produksi, pengeluaran, barang masuk dan stok real time barang baja ringan (GMP, Spandek, genteng CVDMS dan plat bahan bakunya). Database memakai Google Sheet, jadi datanya tetap bisa dibuka langsung di Google Sheet kapan saja.

## Isi menu

1. **Ringkasan**: total stok, barang yang perlu perhatian, stok per warna tiap kategori, grafik 30 hari.
2. **Input Transaksi**: catat Produksi, Pengeluaran, Barang Masuk. Bisa per nama barang (semua warna sekaligus) atau satu kategori penuh. Saat produksi, plat bahan bakunya otomatis berkurang.
3. **Stok Real Time**: pengganti sheet "Real Time" di Excel, bisa dilihat posisi per tanggal tertentu dan diunduh.
4. **Laporan Mingguan**: rekap Senin sampai Sabtu plus TOTAL PEKAN, persis susunan sheet Produksi, Pengeluaran, Barang masuk. Tombol unduh menghasilkan file Excel dengan sheet Real Time, Produksi, Pengeluaran, Barang masuk.
5. **Riwayat Transaksi**: cari dan batalkan transaksi yang salah input (tidak dihapus, hanya ditandai BATAL).
6. **Stok Opname**: cocokkan stok aplikasi dengan hitungan fisik gudang, selisihnya dicatat sebagai koreksi.
7. **Master Barang**: tambah barang atau kategori baru, atur plat bahan baku, stok awal dan stok minimum.
8. **Pengaturan**: status koneksi dan tombol isi data awal dari template Excel.

## Langkah 1: Siapkan Google Sheet

1. Buka sheets.google.com, buat spreadsheet kosong, beri nama misalnya **Database Stok Baja Ringan**.
2. Salin link spreadsheet tersebut dari address bar. Tab yang dibutuhkan (master_barang dan transaksi) dibuat otomatis oleh aplikasi.

## Langkah 2: Buat service account Google (sekali saja)

Service account adalah "akun robot" yang dipakai aplikasi untuk membaca dan menulis Google Sheet.

1. Buka console.cloud.google.com lalu buat project baru (misalnya **stok baja ringan**).
2. Di menu **APIs & Services > Library**, aktifkan **Google Sheets API** dan **Google Drive API**.
3. Di menu **IAM & Admin > Service Accounts**, tekan **Create service account**, isi nama bebas, lalu selesai.
4. Buka service account tersebut, tab **Keys > Add key > Create new key > JSON**. Sebuah file JSON akan terunduh. Simpan baik baik dan jangan dibagikan.

## Langkah 3: Bagikan Google Sheet ke service account

1. Buka file JSON tadi, cari baris `client_email` (bentuknya seperti nama@project.iam.gserviceaccount.com).
2. Di Google Sheet, tekan **Share / Bagikan**, tempel email tersebut, beri akses **Editor**.

## Langkah 4: Isi secrets

1. Di folder `.streamlit`, salin file `secrets.toml.contoh` menjadi `secrets.toml`.
2. Isi `spreadsheet` dengan link Google Sheet.
3. Isi bagian `[gcp_service_account]` dengan nilai dari file JSON (type, project_id, private_key_id, private_key, client_email, client_id, token_uri). Untuk `private_key`, salin persis seperti di file JSON, lengkap dengan tanda `\n` di dalamnya.
4. Isi `nama_usaha` dengan nama toko, dan `kata_sandi` bila ingin aplikasinya dikunci. Kosongkan `kata_sandi` bila tidak perlu login.

Bila secrets belum diisi, aplikasi tetap bisa dicoba dalam **mode lokal (demo)** yang menyimpan data di folder `data_lokal`.

## Langkah 5: Jalankan di komputer

Pastikan Python 3.10 atau yang lebih baru sudah terpasang, lalu buka terminal di folder aplikasi:

```
pip install streamlit gspread pandas openpyxl altair tzdata
streamlit run app.py
```

Browser akan terbuka di alamat localhost:8501.

## Langkah 6: Online supaya bisa dibuka dari HP

Cara paling mudah dan gratis adalah Streamlit Community Cloud:

1. Unggah folder aplikasi ke repository GitHub (boleh private). File `secrets.toml` tidak ikut terunggah karena sudah dikecualikan di `.gitignore`.
2. Buka share.streamlit.io, masuk dengan akun GitHub, tekan **Create app**, pilih repository, file utama `app.py`.
3. Buka **Advanced settings > Secrets**, tempel seluruh isi `secrets.toml`, lalu **Deploy**.
4. Link aplikasi bisa disimpan di layar utama HP seperti aplikasi biasa.

## Langkah 7: Pemakaian pertama

1. Buka menu **Pengaturan**, tekan **Isi data awal dari template Excel**. Semua barang GMP dan SPANDEK beserta stok awal dari file STOK_GMP dan STOK_SPANDEK akan masuk, termasuk transaksi 28 dan 29 Juli 2026.
2. Cek menu **Stok Real Time**. Angkanya sama dengan sheet Real Time di Excel (contoh: Spandek pasir 0.30 6m Merah 120, Hitam 36, Polosan 0.30 6m 470).
3. Bila stok di gudang sekarang sudah berbeda, lakukan **Stok Opname** sekali supaya angka aplikasi sama dengan kondisi nyata.

## Kebiasaan harian yang disarankan

1. Setiap ada produksi, pengeluaran atau kiriman plat: buka **Input Transaksi**, pilih jenis, isi jumlah, simpan.
2. Akhir minggu atau akhir bulan: buka **Laporan Mingguan**, unduh Excel untuk dilaporkan.
3. Rutin (misalnya tiap bulan): lakukan **Stok Opname**.
4. Atur **Stok Minimum** di Master Barang supaya peringatan stok menipis muncul di Ringkasan.

## Hal yang disesuaikan dari template Excel

1. Nama barang yang di Excel memakai tanda strip ditulis dengan spasi, contoh "Spandek pasir 0.30 6m".
2. Di Excel, plat untuk 1 STEP dan 2 STEP STD (GMP) belum punya rumus. Di aplikasi diasumsikan 1 STEP memakai PLAT GM 1 STEP, dan 2 STEP STD memakai PLAT GM STD. 2 STEP GLOSSY belum dihubungkan ke plat apa pun. Semua ini bisa diubah di **Master Barang** kolom Plat Bahan Baku.
3. Satu barang jadi diasumsikan memakai satu lembar plat (Rasio Plat = 1), sama seperti rumus di Excel.
4. Rumus Excel lama untuk Polosan 5m dan 4m mengambil kolom total pekan ke 4 saja, bukan total semua pekan. Di aplikasi semua pekan dihitung.

## Menambah fitur nanti

Struktur folder:

* `app.py` : titik masuk aplikasi
* `menu.py` : **daftar menu**. Tambah halaman baru cukup dengan satu baris di sini. Ganti `POSISI_MENU = "top"` bila ingin menu berbentuk tab di bagian atas layar
* `halaman/` : satu file untuk satu halaman. `templat_halaman_baru.py` bisa disalin sebagai awal halaman baru
* `inti/database.py` : baca tulis Google Sheet
* `inti/stok.py` : rumus stok
* `inti/laporan.py` dan `inti/ekspor.py` : laporan mingguan dan file Excel
* `inti/tema.py` dan `.streamlit/config.toml` : warna aplikasi
* `inti/konfigurasi.py` : nama aplikasi, zona waktu, nama tab database

Kategori baru (misalnya rangka baja ringan, reng, hollow) cukup ditambahkan lewat menu **Master Barang**. Tab kategori di Ringkasan, Input dan Laporan akan muncul sendiri tanpa mengubah kode.
