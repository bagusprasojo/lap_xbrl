# IDX XBRL MVP

Website MVP untuk mengunggah file XBRL emiten IDX, menyimpan fakta mentah, dan menampilkan laporan keuangan komparatif sesuai SRS.

## Menjalankan Aplikasi

```bash
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
cd lapxbrl
python manage.py migrate
python manage.py createsuperuser  # akses admin untuk upload/template
python manage.py runserver
```

## Fitur Utama

- Upload file XBRL dan parsing konteks/fakta mentah, dengan opsi overwrite periode (`/dashboard/upload/`).
- Penyimpanan entitas: Emiten, Filing, Context, Fact, Template, Template Item (lihat `reports/models.py`).
- Manajemen template flat untuk Neraca, Laba Rugi, dan Arus Kas via UI sederhana (`/dashboard/templates/`) atau Django Admin.
- Tampilan publik memilih emiten + periode utama/pembanding dan tabel analisa selisih (`/`).
- Validasi minimal: konflik periode dan error parsing ditampilkan dalam pesan.

## Data Contoh

File `sample.xbrl` menyediakan contoh instansi sederhana, serta skrip `reports/services.py` dapat digunakan ulang untuk otomasi upload (lihat `README` ini untuk langkah manual).
"# lap_xbrl" 
