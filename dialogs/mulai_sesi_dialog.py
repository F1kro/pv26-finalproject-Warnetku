import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from config import PAKET

class DialogMulaiSesi(QDialog):
    def __init__(self, nama_komputer: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f'Mulai Sesi - {nama_komputer}')
        self.setMinimumWidth(420)
        self._bangun_ui(nama_komputer)

    def _bangun_ui(self, nama_komputer):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(18, 18, 18, 18)

        lbl = QLabel(f'Komputer: <b>{nama_komputer}</b>')
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setTextFormat(Qt.RichText)
        layout.addWidget(lbl)

        form = QFormLayout()
        form.setSpacing(10)

        self.input_nama = QLineEdit()
        self.input_nama.setPlaceholderText('Nama pelanggan (opsional)')
        self.input_nama.setText('Umum')

        self.combo_paket = QComboBox()
        for nama, durasi, harga in PAKET:
            label = f'{nama} - {durasi} mnt - Rp {harga:,}'
            self.combo_paket.addItem(label, (nama, durasi, harga))
        self.combo_paket.addItem('Open Billing (bayar di akhir, per menit)', ('Open Billing', None, None))
        self.combo_paket.currentIndexChanged.connect(self._on_paket_berubah)

        form.addRow('Pelanggan', self.input_nama)
        form.addRow('Paket', self.combo_paket)
        layout.addLayout(form)

        self.frame_info = QFrame()
        self.frame_info.setObjectName('frameInfo')
        info_layout = QVBoxLayout(self.frame_info)
        info_layout.setContentsMargins(12, 10, 12, 10)
        self.lbl_info_bayar = QLabel()
        self.lbl_info_bayar.setWordWrap(True)
        self.lbl_info_bayar.setTextFormat(Qt.RichText)
        info_layout.addWidget(self.lbl_info_bayar)
        layout.addWidget(self.frame_info)

        self.frame_metode = QFrame()
        metode_layout = QFormLayout(self.frame_metode)
        metode_layout.setContentsMargins(0, 0, 0, 0)
        self.combo_metode = QComboBox()
        self.combo_metode.addItems(['Tunai', 'QRIS'])
        metode_layout.addRow('Bayar via', self.combo_metode)
        layout.addWidget(self.frame_metode)

        tombol = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.btn_ok = tombol.button(QDialogButtonBox.Ok)
        self.btn_ok.setText('Bayar & Mulai Sesi')
        tombol.accepted.connect(self.accept)
        tombol.rejected.connect(self.reject)
        layout.addWidget(tombol)

        self._on_paket_berubah(0)

    def _on_paket_berubah(self, idx):
        paket = self.combo_paket.currentData()
        nama_paket, durasi, harga = paket
        is_open = durasi is None

        if is_open:
            self.lbl_info_bayar.setText(
                '<span style="color:#92400e;">Open Billing: biaya dihitung per menit, '
                'bayar saat sesi selesai.</span>'
            )
            self.frame_metode.setVisible(False)
            self.btn_ok.setText('Mulai Sesi')
        else:
            self.lbl_info_bayar.setText(
                f'<span style="color:#166534;">Paket <b>{nama_paket}</b>: '
                f'<b>Rp {harga:,}</b> dibayar di muka sebelum sesi dimulai.</span>'
            )
            self.frame_metode.setVisible(True)
            self.btn_ok.setText('Bayar & Mulai Sesi')

    def ambil_data(self):
        nama = self.input_nama.text().strip() or 'Umum'
        paket = self.combo_paket.currentData()
        nama_paket, durasi, harga = paket
        is_open = durasi is None
        # Cek dari data paket, bukan dari visibility widget
        metode = None if is_open else self.combo_metode.currentText()
        return nama, paket, metode

