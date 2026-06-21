import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

class UserView(QWidget):
    minta_tambah  = Signal()
    minta_edit    = Signal(int)
    minta_hapus   = Signal(int)
    minta_refresh = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._semua_data = []
        self._bangun_ui()

    def _bangun_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        header = QHBoxLayout()
        header.setSpacing(8)
        col = QVBoxLayout()
        col.setSpacing(2)
        judul = QLabel('Kelola User')
        judul.setObjectName('judulModul')
        lbl_sub = QLabel('Manajemen akun owner dan kasir')
        lbl_sub.setObjectName('subJudul')
        col.addWidget(judul)
        col.addWidget(lbl_sub)
        header.addLayout(col)
        header.addStretch()
        root.addLayout(header)

        toolbar = QFrame()
        toolbar.setObjectName('toolbarPanel')
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(12, 8, 12, 8)
        tb.setSpacing(8)

        self.btn_tambah = QPushButton('+ Tambah User')
        self.btn_tambah.setObjectName('btnMulai')
        self.btn_tambah.clicked.connect(self.minta_tambah.emit)

        self.btn_edit = QPushButton('Edit')
        self.btn_edit.setObjectName('btnSecondary')
        self.btn_edit.setEnabled(False)
        self.btn_edit.clicked.connect(self._on_edit)

        self.btn_hapus = QPushButton('Hapus')
        self.btn_hapus.setObjectName('btnSelesai')
        self.btn_hapus.setEnabled(False)
        self.btn_hapus.clicked.connect(self._on_hapus)

        self.btn_refresh = QPushButton('Refresh')
        self.btn_refresh.setObjectName('btnRefresh')
        self.btn_refresh.clicked.connect(self.minta_refresh.emit)

        for btn in [self.btn_tambah, self.btn_edit, self.btn_hapus, self.btn_refresh]:
            tb.addWidget(btn)

        tb.addStretch()

        # Search box
        self.input_cari = QLineEdit()
        self.input_cari.setPlaceholderText('Cari nama atau username...')
        self.input_cari.setFixedWidth(220)
        self.input_cari.setFixedHeight(30)
        self.input_cari.textChanged.connect(self._on_cari)
        tb.addWidget(self.input_cari)

        root.addWidget(toolbar)

        self.tabel = QTableWidget()
        self.tabel.setColumnCount(6)
        self.tabel.setHorizontalHeaderLabels(['ID', 'Nama', 'Username', 'Role', 'Status', 'Aksi'])
        self.tabel.setColumnHidden(0, True)
        hh = self.tabel.horizontalHeader()
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.tabel.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabel.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabel.setAlternatingRowColors(True)
        self.tabel.verticalHeader().setDefaultSectionSize(32)
        self.tabel.verticalHeader().setVisible(False)
        self.tabel.setSortingEnabled(True)
        self.tabel.itemSelectionChanged.connect(self._on_pilih)
        root.addWidget(self.tabel)

    def _on_cari(self, teks: str):
        kata = teks.strip().lower()
        if not kata:
            self._render_tabel(self._semua_data)
            return
        hasil = [
            u for u in self._semua_data
            if kata in u['nama'].lower()
            or kata in u['username'].lower()
            or kata in u['role'].lower()
        ]
        self._render_tabel(hasil)

    def tampilkan_data(self, data: list, user_id_aktif: int = None):
        self._semua_data = data
        self._user_id_aktif = user_id_aktif
        kata = self.input_cari.text().strip().lower()
        if kata:
            data = [
                u for u in data
                if kata in u['nama'].lower()
                or kata in u['username'].lower()
                or kata in u['role'].lower()
            ]
        self._render_tabel(data, user_id_aktif)

    def _render_tabel(self, data: list, user_id_aktif: int = None):
        if user_id_aktif is None:
            user_id_aktif = getattr(self, '_user_id_aktif', None)
        self.tabel.setSortingEnabled(False)
        self.tabel.setRowCount(0)
        for user in data:
            r = self.tabel.rowCount()
            self.tabel.insertRow(r)
            vals = [
                str(user['id']),
                user['nama'],
                user['username'],
                user['role'].upper(),
                'Aktif' if user['aktif'] else 'Nonaktif',
                '',
            ]
            for k, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                if k == 3:
                    if user['role'] == 'owner':
                        item.setForeground(QColor('#1a1a1a'))
                        item.setBackground(QColor('#f5c800'))
                    else:
                        item.setForeground(QColor('#1a1a1a'))
                        item.setBackground(QColor('#bbf7d0'))
                if k == 4:
                    if user['aktif']:
                        item.setForeground(QColor('#059669'))
                    else:
                        item.setForeground(QColor('#dc2626'))
                if user['id'] == user_id_aktif:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                self.tabel.setItem(r, k, item)
        self.tabel.setSortingEnabled(True)

    def _id_terpilih(self) -> int | None:
        r = self.tabel.currentRow()
        if r < 0:
            return None
        item = self.tabel.item(r, 0)
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
