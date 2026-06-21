import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from PySide6.QtCore import QTimer, QObject, Signal
from datetime import datetime


class TimerSesi(QObject):
    """Timer per komputer. Emit tick setiap detik dengan info durasi & biaya."""
    tick    = Signal(int, int, float)   # komputer_id, detik_berjalan, biaya
    selesai = Signal(int)               # komputer_id — paket habis

    def __init__(self, komputer_id, sesi_id, mulai: datetime,
                 durasi_paket_menit=None, harga_paket=None,
                 harga_per_menit=None, parent=None):
        super().__init__(parent)
        self.komputer_id        = komputer_id
        self.sesi_id            = sesi_id
        self.mulai              = mulai
        self.durasi_paket_detik = durasi_paket_menit * 60 if durasi_paket_menit else None
        self.harga_paket        = harga_paket
        self.harga_per_menit    = harga_per_menit or 100
        self._detik             = 0

        self._qtimer = QTimer(self)
        self._qtimer.setInterval(1000)
        self._qtimer.timeout.connect(self._on_tick)

    def mulai_timer(self):
        self._qtimer.start()

    def stop(self):
        self._qtimer.stop()

    def _on_tick(self):
        self._detik += 1
        biaya = self._hitung_biaya()
        self.tick.emit(self.komputer_id, self._detik, biaya)

        # paket berbatas waktu — emit selesai saat habis
        if self.durasi_paket_detik and self._detik >= self.durasi_paket_detik:
            self._qtimer.stop()
            self.selesai.emit(self.komputer_id)

    def _hitung_biaya(self):
        if self.harga_paket is not None:
            return float(self.harga_paket)
        menit = self._detik / 60
        return round(menit * self.harga_per_menit, 0)

    @property
    def detik_berjalan(self):
        return self._detik

    @staticmethod
    def format_durasi(detik):
        j = detik // 3600
        m = (detik % 3600) // 60
        s = detik % 60
        return f'{j:02d}:{m:02d}:{s:02d}'
