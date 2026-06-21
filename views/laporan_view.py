import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

class LaporanView(QWidget):
    minta_filter   = Signal(str, str)
    minta_csv      = Signal()
    minta_pdf      = Signal()
    minta_telegram = Signal()
    minta_insight  = Signal()
    minta_refresh  = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._semua_data = []
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
        judul = QLabel('Laporan Transaksi')
        judul.setObjectName('judulModul')
        lbl_sub = QLabel('Riwayat transaksi dan ekspor laporan')
        lbl_sub.setObjectName('subJudul')
        col.addWidget(judul)
        col.addWidget(lbl_sub)
        header.addLayout(col)
        header.addStretch()

        self.btn_csv      = QPushButton('Export CSV')
        self.btn_pdf      = QPushButton('Export PDF')
        self.btn_telegram = QPushButton('Laporan Harian')
        self.btn_insight  = QPushButton('Kirim Insight')
        for btn, sig in [(self.btn_csv, self.minta_csv),
                         (self.btn_pdf, self.minta_pdf),
                         (self.btn_telegram, self.minta_telegram),
                         (self.btn_insight, self.minta_insight)]:
            btn.setObjectName('btnSecondary')
            btn.clicked.connect(sig.emit)
            header.addWidget(btn)
        root.addLayout(header)

        # --- Toolbar filter ---
        frame_filter = QFrame()
        frame_filter.setObjectName('toolbarPanel')
        fl = QHBoxLayout(frame_filter)
        fl.setContentsMargins(12, 8, 12, 8)
        fl.setSpacing(8)

        fl.addWidget(QLabel('Dari'))
        self.date_mulai = QDateEdit(QDate.currentDate())
        self.date_mulai.setCalendarPopup(True)
        self.date_mulai.setDisplayFormat('dd/MM/yyyy')
        fl.addWidget(self.date_mulai)

        fl.addWidget(QLabel('s/d'))
        self.date_selesai = QDateEdit(QDate.currentDate())
        self.date_selesai.setCalendarPopup(True)
        self.date_selesai.setDisplayFormat('dd/MM/yyyy')
        fl.addWidget(self.date_selesai)

        self.btn_filter = QPushButton('Tampilkan')
        self.btn_filter.setObjectName('btnMulai')
        self.btn_filter.clicked.connect(self._on_filter)
        fl.addWidget(self.btn_filter)

        self.btn_refresh_lap = QPushButton('Refresh')
        self.btn_refresh_lap.setObjectName('btnRefresh')
        self.btn_refresh_lap.clicked.connect(self.minta_refresh.emit)
        fl.addWidget(self.btn_refresh_lap)

        fl.addStretch()

        # Search box
        self.input_cari = QLineEdit()
        self.input_cari.setPlaceholderText('Cari komputer, pelanggan, paket...')
        self.input_cari.setFixedWidth(260)
        self.input_cari.setFixedHeight(30)
        self.input_cari.textChanged.connect(self._on_cari)
        fl.addWidget(self.input_cari)

        root.addWidget(frame_filter)

        # --- Kartu ringkasan ---
        baris_kartu = QHBoxLayout()
        baris_kartu.setSpacing(10)
        self.kartu_total     = self._buat_kartu('Total Pendapatan', 'Rp 0',  '#059669', 'k_total')
        self.kartu_transaksi = self._buat_kartu('Jumlah Transaksi', '0',     '#1a1a1a', 'k_transaksi')
        self.kartu_rata      = self._buat_kartu('Rata-rata / Sesi', 'Rp 0',  '#f5c800', 'k_rata')
        self.kartu_aktif     = self._buat_kartu('Sesi Berlangsung', '0',     '#3b82f6', 'k_aktif')
        for k in [self.kartu_total, self.kartu_transaksi, self.kartu_rata, self.kartu_aktif]:
            baris_kartu.addWidget(k)
        root.addLayout(baris_kartu)

        # --- Tabel ---
        self.tabel = QTableWidget()
        self.tabel.setColumnCount(9)
        self.tabel.setHorizontalHeaderLabels([
            'ID', 'Waktu', 'Komputer', 'Pelanggan',
            'Paket', 'Durasi', 'Metode', 'Total', 'Status'
        ])
        self.tabel.setColumnHidden(0, True)
        hh = self.tabel.horizontalHeader()
        hh.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.Stretch)
        hh.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(8, QHeaderView.ResizeToContents)
        self.tabel.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabel.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabel.setAlternatingRowColors(True)
        self.tabel.verticalHeader().setDefaultSectionSize(30)
        self.tabel.verticalHeader().setVisible(False)
        self.tabel.setSortingEnabled(True)
        root.addWidget(self.tabel)

    def _buat_kartu(self, judul, nilai, warna, key=None):
        frame = QFrame()
        frame.setObjectName('card')
        frame.setFixedHeight(72)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(3)
        lbl_j = QLabel(judul)
        lbl_j.setStyleSheet('color:#666666; font-size:10px; font-weight:700;')
        lbl_v = QLabel(nilai)
        lbl_v.setStyleSheet(f'color:{warna}; font-size:17px; font-weight:900;')
        if key is None:
            key = judul.replace(' ', '_').replace('/', '_')
        lbl_v.setObjectName(f'kartu_{key}')
        layout.addWidget(lbl_j)
        layout.addWidget(lbl_v)
        return frame

    def _on_filter(self):
        self.minta_filter.emit(
            self.date_mulai.date().toString('yyyy-MM-dd'),
            self.date_selesai.date().toString('yyyy-MM-dd'),
        )

    def _on_cari(self, teks: str):
        kata = teks.strip().lower()
        if not kata:
            self._render_tabel(self._semua_data)
            return
        hasil = [
            row for row in self._semua_data
            if kata in str(row.get('nama_komputer', '')).lower()
            or kata in str(row.get('nama_pelanggan', '')).lower()
            or kata in str(row.get('paket', '')).lower()
            or kata in str(row.get('metode', '')).lower()
        ]
        self._render_tabel(hasil)

    def tampilkan_data(self, data: list):
        self._semua_data = data
        kata = self.input_cari.text().strip().lower()
        if kata:
            data = [
                row for row in data
                if kata in str(row.get('nama_komputer', '')).lower()
                or kata in str(row.get('nama_pelanggan', '')).lower()
                or kata in str(row.get('paket', '')).lower()
                or kata in str(row.get('metode', '')).lower()
            ]
        self._render_tabel(data)

    def _render_tabel(self, data: list):
        self.tabel.setSortingEnabled(False)
        self.tabel.setRowCount(0)
        total_lunas = 0
        jml_aktif   = 0

        for row in data:
            r = self.tabel.rowCount()
            self.tabel.insertRow(r)

            durasi_mnt = row.get('durasi_menit', 0)
            durasi_str = f'{durasi_mnt} mnt' if durasi_mnt else '—'
            if row.get('sesi_aktif'):
                durasi_str = row.get('durasi_live', '—')

            status   = row.get('status', 'lunas')
            is_aktif = row.get('sesi_aktif', False)

            vals = [
                str(row.get('id', '')),
                str(row.get('waktu', ''))[:16],
                str(row.get('nama_komputer', '')),
                str(row.get('nama_pelanggan', '')),
                str(row.get('paket', '')),
                durasi_str,
                str(row.get('metode', '—')),
                f"Rp {row.get('jumlah', 0):,.0f}",
                'AKTIF' if is_aktif else ('LUNAS' if status == 'lunas' else 'BELUM'),
            ]

            for k, value in enumerate(vals):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)

                if k == 8:
                    if is_aktif:
                        item.setForeground(QColor('#1a1a1a'))
                        item.setBackground(QColor('#f5c800'))
                    elif status == 'lunas':
                        item.setForeground(QColor('#1a1a1a'))
                        item.setBackground(QColor('#bbf7d0'))
                    else:
                        item.setForeground(QColor('#1a1a1a'))
                        item.setBackground(QColor('#fecaca'))

                if is_aktif:
                    font = item.font()
                    font.setItalic(True)
                    item.setFont(font)

                self.tabel.setItem(r, k, item)

            if not is_aktif and status == 'lunas':
                total_lunas += row.get('jumlah', 0)
            if is_aktif:
                jml_aktif += 1

        n_transaksi = sum(1 for d in data if not d.get('sesi_aktif'))
        rata = total_lunas / n_transaksi if n_transaksi else 0

        self._set_kartu('k_total',     f'Rp {total_lunas:,.0f}')
        self._set_kartu('k_transaksi', str(n_transaksi))
        self._set_kartu('k_rata',      f'Rp {rata:,.0f}')
        self._set_kartu('k_aktif',     str(jml_aktif))

        self.tabel.setSortingEnabled(True)

    def update_row_durasi(self, sesi_id: int, durasi_live: str):
        for r in range(self.tabel.rowCount()):
            item_id = self.tabel.item(r, 0)
            if item_id and item_id.data(Qt.UserRole) == sesi_id:
                item_dur = self.tabel.item(r, 5)
                if item_dur:
                    item_dur.setText(durasi_live)
                break

    def _set_kartu(self, key, nilai):
        lbl = self.findChild(QLabel, f'kartu_{key}')
        if lbl:
            lbl.setText(nilai)
