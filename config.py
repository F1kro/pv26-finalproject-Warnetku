# ============================================================
# WarnetKu - Konfigurasi
# ============================================================

# ------------------------------------------------------------
# TELEGRAM BOT — Cara Setup:
# 1. Chat @BotFather di Telegram -> /newbot
# 2. Copy token yang diberikan ke TELEGRAM_BOT_TOKEN
# 3. Chat bot kamu sekali, lalu buka:
#    https://api.telegram.org/bot<TOKEN>/getUpdates
# 4. Copy "id" dari "chat" ke TELEGRAM_CHAT_ID
# ------------------------------------------------------------
TELEGRAM_BOT_TOKEN = '8701642054:AAF82cS5ayizztgc6-ByG8j4A2Nc-mfnXe4'
TELEGRAM_CHAT_ID   = '1632382325'

# ------------------------------------------------------------
# CUACA — Open-Meteo (gratis, tanpa API key)
# Cukup isi nama kota di bawah
# ------------------------------------------------------------
WEATHER_CITY = 'Mataram'

# ------------------------------------------------------------
# WARNET
# ------------------------------------------------------------
NAMA_WARNET      = 'WarnetKu'
JUMLAH_KOMPUTER  = 12

# Paket sewa (nama, durasi_menit, harga)
PAKET = [
    ('Per Jam',    60,  5_000),
    ('2 Jam',     120,  8_000),
    ('3 Jam',     180, 11_000),
    ('5 Jam',     300, 18_000),
    ('Semalaman', 480, 25_000),
]

# Harga per menit untuk sesi open billing
HARGA_PER_MENIT = 100
