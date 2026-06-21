import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from config import NAMA_WARNET
from services import qr_service

DURASI_QR = 120

class DialogBayar(QDialog):
    pembayaran_selesai = Signal(str)

    def __init__(self, komputer_nama, sesi_id, durasi_detik, biaya,
                 paket, nama_pelanggan, metode_bayar='Tunai', parent=None):
        super().__init__(parent)
        self.setWindowTitle('Pembayaran')
        self.setFixedWidth(500)
        self.setWindowFlags(
            self.windowFlags()
            & ~Qt.WindowMaximizeButtonHint
            & ~Qt.WindowMinimizeButtonHint
        )

        self.komputer_nama  = komputer_nama
        self.sesi_id        = sesi_id
        self.durasi_detik   = durasi_detik
        self.biaya          = biaya
        self.paket          = paket
        self.nama_pelanggan = nama_pelanggan
        self.metode_bayar   = metode_bayar or 'Tunai'
        self._order_id      = None
        self._is_open_billing = False

        self._is_qris = 'QRIS' in self.metode_bayar

        self._sim_timer = QTimer(self)
        self._sim_timer.setSingleShot(True)
        self._sim_timer.setInterval(DURASI_QR * 1_000)
        self._sim_timer.timeout.connect(self._auto_regenerate)

        self._countdown_timer = QTimer(self)
        self._countdown_timer.setInterval(1_000)
        self._countdown_timer.timeout.connect(self._tick_countdown)
        self._sisa_detik = DURASI_QR

        self._bangun_ui()

    def _show_metode_combo(self):
        self._is_open_billing = True
        self.frame_metode_combo.setVisible(True)
        self.lbl_metode_badge.setVisible(False)
        self._on_metode_combo_berubah(self.combo_metode.currentText())

    def _bangun_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

        inner = QWidget()
        scroll.setWidget(inner)
        layout = QVBoxLayout(inner)
        layout.setSpacing(12)
        layout.setContentsMargins(18, 18, 18, 18)

        lbl_judul = QLabel('Konfirmasi Pembayaran')
        lbl_judul.setObjectName('dialogTitle')
        layout.addWidget(lbl_judul)

        self.lbl_metode_badge = QLabel(f'Metode: {self.metode_bayar}')
        self.lbl_metode_badge.setObjectName('metodeBadge')
        self.lbl_metode_badge.setAlignment(Qt.AlignCenter)
        self.lbl_metode_badge.setVisible(not self._is_open_billing)
        layout.addWidget(self.lbl_metode_badge)

        self.frame_metode_combo = QFrame()
        metode_form = QFormLayout(self.frame_metode_combo)
        metode_form.setContentsMargins(0, 0, 0, 0)
        self.combo_metode = QComboBox()
        self.combo_metode.addItems(['Tunai', 'QRIS'])
        self.combo_metode.currentTextChanged.connect(self._on_metode_combo_berubah)
        metode_form.addRow('Metode Bayar', self.combo_metode)
        self.frame_metode_combo.setVisible(False)
        layout.addWidget(self.frame_metode_combo)

        frame_info = QFrame()
        frame_info.setObjectName('frameInfo')
        info_layout = QFormLayout(frame_info)
        info_layout.setContentsMargins(12, 10, 12, 10)

        def _row(label, value):
            l = QLabel(label)
            l.setObjectName('infoLabel')
            v = QLabel(str(value))
            v.setObjectName('infoValue')
            info_layout.addRow(l, v)

        _row('Komputer',  self.komputer_nama)
        _row('Pelanggan', self.nama_pelanggan)
        _row('Paket',     self.paket)
        _row('Durasi',    f'{self.durasi_detik // 60} menit')
        lbl_biaya = QLabel(f'Rp {self.biaya:,.0f}')
        lbl_biaya.setObjectName('infoBiaya')
        lbl_biaya.setAlignment(Qt.AlignRight)
        info_layout.addRow(QLabel('Total'), lbl_biaya)
        layout.addWidget(frame_info)

        self.frame_qris = QFrame()
        qris_layout = QVBoxLayout(self.frame_qris)
        qris_layout.setSpacing(8)

        lbl_qr_title = QLabel('QRIS Payment')
        lbl_qr_title.setObjectName('sectionTitle')
        lbl_qr_title.setAlignment(Qt.AlignCenter)
        qris_layout.addWidget(lbl_qr_title)

        self.lbl_qr = QLabel('Klik tombol di bawah untuk generate QR Code')
        self.lbl_qr.setFixedSize(280, 280)
        self.lbl_qr.setAlignment(Qt.AlignCenter)
        self.lbl_qr.setStyleSheet('QLabel { background: #f3f4f6; border: 2px dashed #d1d5db; border-radius: 12px; }')
        qris_layout.addWidget(self.lbl_qr, alignment=Qt.AlignHCenter)

        self.lbl_order_id = QLabel('')
        self.lbl_order_id.setObjectName('orderId')
        self.lbl_order_id.setAlignment(Qt.AlignCenter)
        qris_layout.addWidget(self.lbl_order_id)

        self.lbl_status_qr = QLabel('')
        self.lbl_status_qr.setObjectName('statusQR')
        self.lbl_status_qr.setAlignment(Qt.AlignCenter)
        self.lbl_status_qr.setWordWrap(True)
        qris_layout.addWidget(self.lbl_status_qr)

        self.lbl_countdown = QLabel('')
        self.lbl_countdown.setObjectName('countdown')
        self.lbl_countdown.setAlignment(Qt.AlignCenter)
        self.lbl_countdown.setVisible(False)
        qris_layout.addWidget(self.lbl_countdown)

        self.btn_generate = QPushButton('Generate QRIS')
        self.btn_generate.setObjectName('btnPrimary')
        self.btn_generate.clicked.connect(self._generate_qr)
        qris_layout.addWidget(self.btn_generate)

        self.btn_konfirmasi_sim = QPushButton('Konfirmasi Pembayaran')
        self.btn_konfirmasi_sim.setObjectName('btnSuccess')
        self.btn_konfirmasi_sim.setVisible(False)
        self.btn_konfirmasi_sim.clicked.connect(self._bayar_selesai)
        qris_layout.addWidget(self.btn_konfirmasi_sim)

        self.frame_qris.setVisible(self._is_qris)
        layout.addWidget(self.frame_qris)

        self.frame_tunai = QFrame()
        tunai_layout = QVBoxLayout(self.frame_tunai)
        self.btn_konfirmasi_tunai = QPushButton('Konfirmasi Pembayaran Tunai')
        self.btn_konfirmasi_tunai.setObjectName('btnSuccess')
        self.btn_konfirmasi_tunai.clicked.connect(self._konfirmasi_tunai)
        tunai_layout.addWidget(self.btn_konfirmasi_tunai)
        self.frame_tunai.setVisible(not self._is_qris)
        layout.addWidget(self.frame_tunai)

        btn_close = QPushButton('Tutup')
        btn_close.setObjectName('btnSecondary')
        btn_close.clicked.connect(self.reject)
        layout.addWidget(btn_close)

        layout.addStretch()

    def _on_metode_combo_berubah(self, text):
        is_qris = 'QRIS' in text
        self.frame_qris.setVisible(is_qris)
        self.frame_tunai.setVisible(not is_qris)
        self._is_qris = is_qris
        if is_qris:
            self._reset_qris_section()

    def _reset_qris_section(self):
        self.lbl_qr.clear()
        self.lbl_qr.setText('Klik tombol di bawah untuk generate QR Code')
        self.lbl_qr.setFixedSize(280, 280)
        self.lbl_order_id.setText('')
        self.lbl_status_qr.setText('')
        self.lbl_countdown.setVisible(False)
        self.btn_konfirmasi_sim.setVisible(False)
        self.btn_generate.setText('Generate QRIS')
        self.btn_generate.setEnabled(True)

    def _generate_qr(self):
        self.btn_generate.setEnabled(False)
        self._order_id = qr_service.generate_order_id(self.komputer_nama)
        payload = qr_service.buat_data_qris_simulasi(
            self._order_id, int(self.biaya), NAMA_WARNET
        )
        pix = qr_service.buat_qr_pixmap(payload, ukuran=256)
        self.lbl_qr.setPixmap(pix)
        self.lbl_qr.setAlignment(Qt.AlignCenter)
        self.lbl_order_id.setText(f'Order: {self._order_id}')
        self.lbl_status_qr.setText(f'Total: Rp {self.biaya:,.0f}  |  Scan QR di atas')

        self._sisa_detik = DURASI_QR
        self._update_countdown()
        self.lbl_countdown.setVisible(True)
        self.btn_konfirmasi_sim.setVisible(True)
        self.btn_generate.setText('Regenerate QR')

        self._sim_timer.start()
        self._countdown_timer.start()

    def _tick_countdown(self):
        self._sisa_detik -= 1
        if self._sisa_detik > 0:
            self._update_countdown()
        else:
            self._countdown_timer.stop()

    def _update_countdown(self):
        menit = self._sisa_detik // 60
        detik = self._sisa_detik % 60
        self.lbl_countdown.setText(f'QR kadaluarsa dalam  {menit:02d}:{detik:02d}  \u2014 klik konfirmasi jika sudah bayar')

    def _auto_regenerate(self):
        self._countdown_timer.stop()
        self.lbl_status_qr.setText('QR kadaluarsa \u2014 regenerate otomatis...')
        self.lbl_countdown.setVisible(False)
        self.btn_generate.setEnabled(True)
        self._generate_qr()

    def _bayar_selesai(self):
        self._sim_timer.stop()
        self._countdown_timer.stop()
        self.lbl_countdown.setVisible(False)
        self.btn_konfirmasi_sim.setVisible(False)
        self.lbl_status_qr.setText('Pembayaran berhasil!')
        metode = 'QRIS'
        self.pembayaran_selesai.emit(metode)
        self.accept()

    def _konfirmasi_tunai(self):
        self.pembayaran_selesai.emit(self.metode_bayar)
        self.accept()

    def closeEvent(self, event):
        self._sim_timer.stop()
        self._countdown_timer.stop()
        super().closeEvent(event)
