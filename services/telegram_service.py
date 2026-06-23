import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, NAMA_WARNET
from PySide6.QtCore import QThread, Signal


def _is_telegram_configured() -> bool:
    return (
        TELEGRAM_BOT_TOKEN
        and 'XXXXX' not in TELEGRAM_BOT_TOKEN
        and TELEGRAM_CHAT_ID
        and TELEGRAM_CHAT_ID != '000000000'
    )


class TelegramWorker(QThread):
    sukses = Signal(str)
    error  = Signal(str)

    def __init__(self, pesan: str, parent=None):
        super().__init__(parent)
        self.pesan = pesan

    def run(self):
        if not _is_telegram_configured():
            self.error.emit('Telegram belum dikonfigurasi di config.py')
            return
        try:
            url  = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
            data = {
                'chat_id':    TELEGRAM_CHAT_ID,
                'text':       self.pesan,
                'parse_mode': 'HTML',
            }
            r = requests.post(url, data=data, timeout=10)
            if r.status_code == 200:
                self.sukses.emit('Notifikasi Telegram terkirim.')
            else:
                self.error.emit(f'Telegram error {r.status_code}: {r.text[:120]}')
        except requests.exceptions.ConnectionError:
            self.error.emit('Tidak ada koneksi internet.')
        except Exception as e:
            self.error.emit(str(e))


def kirim_notif(pesan: str) -> TelegramWorker:
    worker = TelegramWorker(pesan)
    worker.start()
    return worker


# ------------------------------------------------------------------ #
# Format pesan
# ------------------------------------------------------------------ #

def format_transaksi_baru(
    komputer: str,
    pelanggan: str,
    paket: str,
    total: float,
    metode: str,
    kasir: str,
) -> str:
    return (
        f'<b>💰 Transaksi Baru — {NAMA_WARNET}</b>\n'
        f'━━━━━━━━━━━━━━━━━━\n'
        f'🖥  Komputer  : <b>{komputer}</b>\n'
        f'👤 Pelanggan  : {pelanggan}\n'
        f'📦 Paket      : {paket}\n'
        f'💵 Total      : <b>Rp {total:,.0f}</b>\n'
        f'💳 Metode     : {metode}\n'
        f'👨‍💼 Kasir      : {kasir}\n'
    )


def format_sesi_mulai(
    komputer: str,
    pelanggan: str,
    paket: str,
    kasir: str,
) -> str:
    return (
        f'<b>▶️ Sesi Dimulai — {NAMA_WARNET}</b>\n'
        f'━━━━━━━━━━━━━━━━━━\n'
        f'🖥  Komputer  : <b>{komputer}</b>\n'
        f'👤 Pelanggan  : {pelanggan}\n'
        f'📦 Paket      : {paket}\n'
        f'👨‍💼 Kasir      : {kasir}\n'
    )


def format_laporan_harian(total, jumlah_sesi, tanggal) -> str:
    return (
        f'<b>📊 Laporan Harian — {NAMA_WARNET}</b>\n'
        f'━━━━━━━━━━━━━━━━━━\n'
        f'📅 Tanggal    : {tanggal}\n'
        f'🔢 Transaksi  : {jumlah_sesi} sesi\n'
        f'💰 Total      : <b>Rp {total:,.0f}</b>\n'
    )


def format_insight(
    periode: str,
    total: float,
    jml_sesi: int,
    rata: float,
    jam_sibuk: str,
    top_kasir: str,
    pendapatan_per_kasir: list,  # list of (nama_kasir, total)
) -> str:
    baris_kasir = ''
    for i, (nama, tot) in enumerate(pendapatan_per_kasir[:5], 1):
        baris_kasir += f'  {i}. {nama}: Rp {tot:,.0f}\n'
    if not baris_kasir:
        baris_kasir = '  (belum ada data)\n'

    return (
        f'<b>📈 Insight {periode} — {NAMA_WARNET}</b>\n'
        f'━━━━━━━━━━━━━━━━━━\n'
        f'💰 Total Pendapatan : <b>Rp {total:,.0f}</b>\n'
        f'🔢 Total Sesi       : {jml_sesi}\n'
        f'📊 Rata-rata/Sesi   : Rp {rata:,.0f}\n'
        f'⏰ Jam Tersibuk     : {jam_sibuk}\n'
        f'🏆 Kasir Terbaik    : {top_kasir}\n'
        f'\n<b>💼 Pendapatan per Kasir:</b>\n'
        f'{baris_kasir}'
    )
