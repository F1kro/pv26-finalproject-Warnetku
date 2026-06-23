import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel, QFrame, QVBoxLayout, QApplication

# Referensi main window — diset dari main.py
_main_window = None

# Daftar toast aktif
_aktif: list = []
_MARGIN  = 12
_SPACING = 6


def set_main_window(win):
    """Daftarkan main window agar toast diposisikan relatif ke window."""
    global _main_window
    _main_window = win


def _ref_rect():
    """Ambil rect referensi: window app kalau ada, fallback ke layar."""
    if _main_window is not None:
        return _main_window.geometry()
    return QApplication.primaryScreen().availableGeometry()


def _hitung_posisi(lebar: int, tinggi: int) -> tuple:
    rect = _ref_rect()
    y = rect.bottom() - _MARGIN
    for toast in _aktif:
        y -= toast.height() + _SPACING
    x = rect.right() - lebar - _MARGIN
    return x, y


def _reposisi_semua():
    rect = _ref_rect()
    y = rect.bottom() - _MARGIN
    for toast in reversed(_aktif):
        y -= toast.height() + _SPACING
        toast.move(rect.right() - toast.width() - _MARGIN, y)


class ToastNotif(QFrame):
    """Toast notifikasi stack di pojok kanan bawah app window."""

    TIPE = {
        'sukses':     ('#4ade80', '#1a1a1a', '\u2713'),
        'error':      ('#f87171', '#1a1a1a', '\u2717'),
        'info':       ('#f5c800', '#1a1a1a', '\u2139'),
        'peringatan': ('#fb923c', '#1a1a1a', '\u26a0'),
    }

    def __init__(self, pesan: str, tipe: str = 'sukses', durasi_ms: int = 3000):
        super().__init__(None)
        self.setWindowFlags(
            Qt.Window |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)

        bg, fg, ikon = self.TIPE.get(tipe, self.TIPE['info'])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(0)

        lbl = QLabel(f'{ikon}  {pesan}')
        lbl.setStyleSheet(
            f'color: {fg};'
            f'font-size: 12px;'
            f'font-weight: 800;'
            f'background: transparent;'
        )
        lbl.setWordWrap(True)
        lbl.setFixedWidth(280)
        layout.addWidget(lbl)

        self.setStyleSheet(
            'QFrame {'
            f'  background-color: {bg};'
            '   border: 2px solid #1a1a1a;'
            '   border-bottom: 4px solid #1a1a1a;'
            '   border-right: 4px solid #1a1a1a;'
            '}'
        )

        self.adjustSize()
        x, y = _hitung_posisi(self.width(), self.height())
        self.move(x, y)

        _aktif.append(self)
        self.show()
        self.raise_()

        QTimer.singleShot(durasi_ms, self._tutup)

    def _tutup(self):
        if self in _aktif:
            _aktif.remove(self)
        self.close()
        _reposisi_semua()


def notif(pesan: str, tipe: str = 'sukses', durasi_ms: int = 3000) -> ToastNotif:
    return ToastNotif(pesan, tipe, durasi_ms)

def notif_sukses(pesan: str)     -> ToastNotif: return notif(pesan, 'sukses',     3000)
def notif_error(pesan: str)      -> ToastNotif: return notif(pesan, 'error',      4500)
def notif_info(pesan: str)       -> ToastNotif: return notif(pesan, 'info',       3000)
def notif_peringatan(pesan: str) -> ToastNotif: return notif(pesan, 'peringatan', 3500)
