import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class KartuKomputer(QFrame):
    klik_mulai = Signal(int)
    klik_selesai = Signal(int)

    def __init__(self, komputer_id: int, nama: str, parent=None):
        super().__init__(parent)
        self.komputer_id = komputer_id
        self.nama = nama
        self._aktif = False
        self.setObjectName('kartuKomputer')
        self.setFixedSize(196, 218)
        self._bangun_ui()
        self.set_kosong()

    def _bangun_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 14)
        layout.setSpacing(6)

        header = QHBoxLayout()
        self.lbl_nama = QLabel(self.nama)
        self.lbl_nama.setObjectName('lblNamaKomputer')

        self.badge = QLabel('Kosong')
        self.badge.setFixedHeight(22)
        self.badge.setAlignment(Qt.AlignCenter)
        self.badge.setObjectName('badgeKosong')

        header.addWidget(self.lbl_nama)
        header.addStretch()
        header.addWidget(self.badge)
        layout.addLayout(header)

        self.lbl_ikon = QLabel('READY')
        self.lbl_ikon.setObjectName('pcIcon')
        self.lbl_ikon.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_ikon)

        self.lbl_pelanggan = QLabel('-')
        self.lbl_pelanggan.setAlignment(Qt.AlignCenter)
        self.lbl_pelanggan.setWordWrap(True)
        self.lbl_pelanggan.setObjectName('lblPelanggan')
        layout.addWidget(self.lbl_pelanggan)

        self.lbl_timer = QLabel('00:00:00')
        self.lbl_timer.setAlignment(Qt.AlignCenter)
        self.lbl_timer.setObjectName('lblTimer')
        layout.addWidget(self.lbl_timer)

        self.lbl_biaya = QLabel('Rp 0')
        self.lbl_biaya.setAlignment(Qt.AlignCenter)
        self.lbl_biaya.setObjectName('lblBiaya')
        layout.addWidget(self.lbl_biaya)

        layout.addStretch()

        self.btn_aksi = QPushButton('Mulai Sesi')
        self.btn_aksi.setObjectName('btnMulai')
        self.btn_aksi.setFixedHeight(36)
        self.btn_aksi.clicked.connect(self._on_klik)
        layout.addWidget(self.btn_aksi)

    def _on_klik(self):
        if self._aktif:
            self.klik_selesai.emit(self.komputer_id)
        else:
            self.klik_mulai.emit(self.komputer_id)

    def set_kosong(self):
        self._aktif = False
        self.badge.setText('Kosong')
        self.badge.setObjectName('badgeKosong')
        self.lbl_ikon.setText('READY')
        self.lbl_ikon.setProperty('state', 'idle')
        self.lbl_pelanggan.setText('-')
        self.lbl_pelanggan.setProperty('state', 'idle')
        self.lbl_timer.setProperty('state', 'idle')
        self.lbl_biaya.setProperty('state', 'idle')
        self.btn_aksi.setText('Mulai Sesi')
        self.btn_aksi.setObjectName('btnMulai')
        for widget in [self.badge, self.lbl_ikon, self.lbl_pelanggan,
                       self.lbl_timer, self.lbl_biaya, self.btn_aksi]:
            self._repolish(widget)

    def set_aktif(self, nama_pelanggan='', is_open=False):
        self._aktif = True
        self.badge.setText('Aktif')
        self.badge.setObjectName('badgeAktif')
        self.lbl_ikon.setText('LIVE')
        self.lbl_ikon.setProperty('state', 'active')
        label = nama_pelanggan if nama_pelanggan and nama_pelanggan != 'Umum' else 'Pelanggan'
        self.lbl_pelanggan.setText(label)
        self.lbl_pelanggan.setProperty('state', 'active')
        self.lbl_timer.setProperty('state', 'active')
        self.lbl_biaya.setProperty('state', 'active')
        teks_btn = 'Bayar' if is_open else 'Selesai'
        self.btn_aksi.setText(teks_btn)
        self.btn_aksi.setObjectName('btnSelesai')
        for widget in [self.badge, self.lbl_ikon, self.lbl_pelanggan,
                       self.lbl_timer, self.lbl_biaya, self.btn_aksi]:
            self._repolish(widget)

    def update_timer(self, detik: int, biaya: float):
        from services.timer_service import TimerSesi

        self.lbl_timer.setText(TimerSesi.format_durasi(detik))
        self.lbl_biaya.setText(f'Rp {biaya:,.0f}')

    def _repolish(self, widget):
        widget.style().unpolish(widget)
        widget.style().polish(widget)


class BookingView(QWidget):
    minta_refresh = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._kartu_map: dict[int, KartuKomputer] = {}
        self._daftar_komputer = []
        self._bangun_ui()

    def _bangun_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 20)
        root.setSpacing(0)

        header = QHBoxLayout()
        col_judul = QVBoxLayout()
        col_judul.setSpacing(2)
        lbl_judul = QLabel('Booking PC')
        lbl_judul.setObjectName('judulModul')
        lbl_sub = QLabel('Pilih PC kosong untuk mulai sesi atau selesaikan pembayaran')
        lbl_sub.setObjectName('subJudul')
        col_judul.addWidget(lbl_judul)
        col_judul.addWidget(lbl_sub)
        header.addLayout(col_judul)
        header.addStretch()

        self.btn_refresh = QPushButton('Refresh')
        self.btn_refresh.setObjectName('btnRefresh')
        self.btn_refresh.setFixedHeight(36)
        self.btn_refresh.clicked.connect(self.minta_refresh.emit)
        header.addWidget(self.btn_refresh)
        root.addLayout(header)
        root.addSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._container = QWidget()
        self.grid = QGridLayout(self._container)
        self.grid.setSpacing(12)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        scroll.setWidget(self._container)
        root.addWidget(scroll)

    def bangun_grid_komputer(self, daftar_komputer: list):
        self._daftar_komputer = daftar_komputer
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._kartu_map.clear()

        cols = self._hitung_kolom()
        for i, komp in enumerate(daftar_komputer):
            kartu = KartuKomputer(komp['id'], komp['nama'])
            if komp['status'] == 'aktif':
                kartu.set_aktif()
            self._kartu_map[komp['id']] = kartu
            self.grid.addWidget(kartu, i // cols, i % cols)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._daftar_komputer:
            self._susun_ulang_grid()

    def _susun_ulang_grid(self):
        widgets = []
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                widgets.append(item.widget())

        cols = self._hitung_kolom()
        for i, widget in enumerate(widgets):
            self.grid.addWidget(widget, i // cols, i % cols)

    def _hitung_kolom(self):
        lebar = max(1, self.width() - 56)
        return max(1, lebar // 208)

    def kartu(self, komputer_id: int) -> KartuKomputer:
        return self._kartu_map.get(komputer_id)


