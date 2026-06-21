# WarnetKu — Sistem Manajemen Warung Internet

Aplikasi desktop berbasis **PySide6 (Qt for Python)** untuk mengelola operasional warung internet secara menyeluruh, mulai dari manajemen sesi komputer, transaksi pembayaran, laporan keuangan, hingga notifikasi real-time via Telegram.

---

## 👥 Anggota Kelompok

| No | Nama | NIM |
|----|------|-----|
| 1 | Fiqro Najiah | F1D02310051 |
| 2 | Kanda Rifqi Alfaz | F1D023100 |
| 3 | Ayu Liza Putri Wiwaha | F1D023100 |

---

## 📋 Deskripsi Proyek

**WarnetKu** adalah aplikasi manajemen warung internet (warnet) yang dibangun menggunakan Python dan framework PySide6. Aplikasi ini dirancang untuk memudahkan pengelola dan kasir warnet dalam mengelola seluruh aktivitas operasional secara digital dan terintegrasi.

Proyek ini merupakan bagian dari mata kuliah **Pemrograman Visual** Semester 6, yang menerapkan konsep arsitektur **MVC (Model-View-Controller)**, pemrograman berbasis event (signal & slot), serta integrasi layanan eksternal seperti Telegram Bot API dan Open-Meteo Weather API.

---

## ✨ Fitur Utama

- **Manajemen Sesi Komputer** — Mulai, pantau, dan akhiri sesi pemakaian komputer secara real-time dengan timer otomatis.
- **Sistem Paket Sewa** — Mendukung berbagai paket waktu (Per Jam, 2 Jam, 3 Jam, 5 Jam, Semalaman) serta mode *open billing* per menit.
- **Transaksi & Pembayaran** — Pencatatan pembayaran tunai beserta riwayat lengkap setiap transaksi.
- **Dashboard & Statistik** — Visualisasi data pendapatan, jumlah sesi, jam tersibuk, dan performa kasir.
- **Laporan Keuangan** — Ekspor laporan transaksi dalam format **PDF** dan **CSV**.
- **Manajemen Pengguna** — Sistem role berbasis *owner* dan *kasir* dengan autentikasi login.
- **Notifikasi Telegram** — Kirim notifikasi otomatis ke Telegram Bot saat sesi dimulai, transaksi selesai, atau laporan harian dikirim.
- **Info Cuaca** — Menampilkan informasi cuaca kota secara real-time menggunakan Open-Meteo API (tanpa API key).
- **Antarmuka Modern** — Tampilan GUI dengan tema gelap menggunakan Qt Style Sheet (QSS).

---

## 🗂️ Struktur Proyek

```
app/ProjectFix/
├── main.py                  # Entry point aplikasi
├── config.py                # Konfigurasi warnet, paket, Telegram, cuaca
├── style.qss                # Stylesheet tema gelap
├── warnetku.db              # Database SQLite
├── models/                  # Model data (komputer, sesi, transaksi, user)
├── views/                   # Tampilan UI (dashboard, booking, laporan, dll.)
├── controllers/             # Logika bisnis & penghubung model-view
├── dialogs/                 # Dialog popup (login, mulai sesi, bayar, dll.)
├── services/                # Layanan eksternal (Telegram, cuaca, timer, QR)
├── database/                # Manajer koneksi & inisialisasi SQLite
└── utils/                   # Utilitas ekspor PDF, CSV, dan notifikasi
```

---

## 🛠️ Teknologi yang Digunakan

| Teknologi | Keterangan |
|-----------|------------|
| Python 3.10 | Bahasa pemrograman utama |
| PySide6 | Framework GUI berbasis Qt 6 |
| SQLite | Database lokal untuk penyimpanan data |
| ReportLab | Generasi laporan dalam format PDF |
| Requests | HTTP client untuk Telegram Bot & cuaca |
| Open-Meteo API | Data cuaca real-time (gratis, tanpa API key) |
| Telegram Bot API | Notifikasi transaksi & laporan harian |
| PyInstaller | Kompilasi aplikasi menjadi file `.exe` |

---

## 🚀 Cara Menjalankan

### Prasyarat

- Python 3.10 atau lebih baru
- Virtual environment (disarankan)

### Instalasi

```bash
# Clone repositori
git clone <url-repositori>
cd belajar-pyside6

# Aktifkan virtual environment
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/macOS

# Install dependensi
pip install PySide6 requests reportlab
```

### Menjalankan Aplikasi

```bash
cd app/ProjectFix
python main.py
```

### Login Default

| Username | Password | Role |
|----------|----------|------|
| `owner` | `owner123` | Owner |

---

## ⚙️ Konfigurasi

Buka file `app/ProjectFix/config.py` untuk menyesuaikan pengaturan:

```python
NAMA_WARNET     = 'WarnetKu'       # Nama warnet
JUMLAH_KOMPUTER = 12               # Jumlah unit komputer
WEATHER_CITY    = 'Mataram'        # Kota untuk info cuaca

# Telegram Bot (opsional)
TELEGRAM_BOT_TOKEN = '<token-bot>'
TELEGRAM_CHAT_ID   = '<chat-id>'
```

---

## 📦 Build Executable

Untuk mengompilasi aplikasi menjadi file `.exe` yang dapat dijalankan tanpa Python:

```bash
cd app/ProjectFix
pyinstaller --onefile --windowed main.py
```

File hasil build tersedia di folder `app/dist/`.

---

## 📄 Lisensi

Proyek ini dibuat untuk keperluan akademik dalam rangka pemenuhan tugas mata kuliah Pemrograman Visual, Program Studi Informatika, Universitas Mataram.
