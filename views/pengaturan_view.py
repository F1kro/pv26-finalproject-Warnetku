import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class PengaturanView(QWidget):
    minta_tambah     = Signal()
    minta_edit       = Signal(int)
    minta_hapus      = Signal(int)
    minta_reset_sesi = Signal()
    minta_refresh    = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._bangun_ui()

    def _bangun_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        # --- Header ---
        header = QHBoxLayout()
        header.setSpacing(8)
        col = QVBoxLayout()
        col.setSpacing(2)
        judul = QLabel('Pengaturan Komputer')
        judul.setObjectName('judulModul')
        lbl_sub = QLabel('Kelola daftar komputer dan reset sesi')
        lbl_sub.setObjectName('subJudul')
        col.addWidget(judul)
        col.addWidget(lbl_sub)
        header.addLayout(col)
        header.addStretch()

        self.btn_reset = QPushButton('Reset Sesi Aktif')
        self.btn_reset.setObjectName('btnSelesai')
        self.btn_reset.setFixedHeight(32)
        self.btn_reset.setToolTip('Paksa tutup semua sesi yang masih aktif di database')
        self.btn_reset.clicked.connect(self.minta_reset_sesi.emit)
        header.addWidget(self.btn_reset)

        root.addLayout(header)

        # --- Toolbar aksi ---
        frame_toolbar = QFrame()
        frame_toolbar.setObjectName('toolbarPanel')
        tb = QHBoxLayout(frame_toolbar)
        tb.setContentsMargins(12, 10, 12, 10)
        tb.setSpacing(8)

        self.btn_tambah = QPushButton('+ Tambah Komputer')
        self.btn_tambah.setObjectName('btnMulai')
        self.btn_tambah.setFixedHeight(32)
        self.btn_tambah.clicked.connect(self.minta_tambah.emit)

        self.btn_edit = QPushButton('Edit')
        self.btn_edit.setObjectName('btnSecondary')
        self.btn_edit.setFixedHeight(32)
        self.btn_edit.setEnabled(False)
        self.btn_edit.clicked.connect(self._on_edit)

        self.btn_hapus = QPushButton('Hapus')
        self.btn_hapus.setObjectName('btnSelesai')
        self.btn_hapus.setFixedHeight(32)
        self.btn_hapus.setEnabled(False)
        self.btn_hapus.clicked.connect(self._on_hapus)

        self.btn_refresh_peng = QPushButton('Refresh')
        self.btn_refresh_peng.setObjectName('btnRefresh')
        self.btn_refresh_peng.setFixedHeight(32)
        self.btn_refresh_peng.clicked.connect(self.minta_refresh.emit)

        for btn in [self.btn_tambah, self.btn_edit, self.btn_hapus, self.btn_refresh_peng]:
            tb.addWidget(btn)
        tb.addStretch()
        root.addWidget(frame_toolbar)

        # --- Tabel ---
        self.tabel = QTableWidget()
        self.tabel.setColumnCount(4)
        self.tabel.setHorizontalHeaderLabels(['ID', 'Nama', 'Status', 'Spesifikasi'])
        self.tabel.setColumnHidden(0, True)
        self.tabel.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabel.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabel.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tabel.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabel.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabel.setAlternatingRowColors(True)
        self.tabel.verticalHeader().setDefaultSectionSize(32)
        self.tabel.verticalHeader().setVisible(False)
        self.tabel.itemSelectionChanged.connect(self._on_pilih)
        root.addWidget(self.tabel)

    def tampilkan_data(self, data: list):
        self.tabel.setRowCount(0)
        for komp in data:
            r = self.tabel.rowCount()
            self.tabel.insertRow(r)
            values = [komp['id'], komp['nama'], komp['status'], komp.get('spesifikasi', '')]
            for k, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                if k == 2:
                    item.setForeground(QColor('#059669' if value == 'kosong' else '#d97706'))
                self.tabel.setItem(r, k, item)

    def _id_terpilih(self):
        baris = self.tabel.currentRow()
        if baris < 0:
            return None
        item = self.tabel.item(baris, 0)
        return int(item.text()) if item else None

    def _on_pilih(self):
        ada = self.tabel.currentRow() >= 0
        self.btn_edit.setEnabled(ada)
        self.btn_hapus.setEnabled(ada)

    def _on_edit(self):
        id_ = self._id_terpilih()
        if id_:
            self.minta_edit.emit(id_)

    def _on_hapus(self):
        id_ = self._id_terpilih()
        if id_:
            self.minta_hapus.emit(id_)
