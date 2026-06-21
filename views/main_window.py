import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QMainWindow,
    QMenu, QPushButton, QStackedWidget, QStatusBar,
    QVBoxLayout, QWidget, QMessageBox,
)

from config import NAMA_WARNET
from models import auth_state
from views.booking_view import BookingView
from views.dashboard_view import DashboardView
from views.laporan_view import LaporanView
from views.pengaturan_view import PengaturanView
from views.user_view import UserView

ANGGOTA = [
    ('Fiqro Najiah',          'F1D02310051'),
    ('Kanda Rifqi Alfaz',     'F1D02310064'),
    ('Ayu Liza Putri Wiwaha', 'F1D02310003'),
]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(NAMA_WARNET)
        self.setMinimumSize(1180, 740)
        self._bangun_ui()
        self._bangun_menu_bar()

    def _bangun_menu_bar(self):
        mb = self.menuBar()

        # --- Menu File ---
        menu_file = mb.addMenu('File')

        act_logout = QAction('Logout', self)
        act_logout.triggered.connect(self._logout)
        menu_file.addAction(act_logout)

        menu_file.addSeparator()

        act_exit = QAction('Exit', self)
        act_exit.setShortcut('Ctrl+Q')
        act_exit.triggered.connect(self.close)
        menu_file.addAction(act_exit)

        # --- Menu Help ---
        menu_help = mb.addMenu('Help')

        act_about = QAction('About', self)
        act_about.triggered.connect(self._show_about)
        menu_help.addAction(act_about)

    def _show_about(self):
        anggota_str = '\n'.join(f'  {i+1}. {n}  —  {nim}' for i, (n, nim) in enumerate(ANGGOTA))
        QMessageBox.information(
            self, f'About {NAMA_WARNET}',
            f'{NAMA_WARNET} — Sistem Manajemen Warung Internet\n'
            f'Versi 1.0.0\n\n'
            f'Anggota Kelompok:\n{anggota_str}\n\n'
            f'Mata Kuliah: Pemrograman Visual\n'
            f'Semester Genap 2025/2026'
        )

    def _bangun_ui(self):
        pusat = QWidget()
        self.setCentralWidget(pusat)

        root = QHBoxLayout(pusat)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # --- Sidebar ---
        sidebar = QFrame()
        sidebar.setObjectName('sidebar')
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(0, 0, 0, 0)
        sb.setSpacing(0)

        lbl_logo = QLabel(f'  WK  {NAMA_WARNET}')
        lbl_logo.setObjectName('labelApp')
        lbl_logo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        lbl_logo.setFixedHeight(58)
        sb.addWidget(lbl_logo)

        lbl_sub = QLabel('  Control Center')
        lbl_sub.setObjectName('labelAppSub')
        sb.addWidget(lbl_sub)

        # Info user yang login
        nama   = auth_state.get_nama()
        role   = auth_state.get_role().upper()
        lbl_user = QLabel(f'  {nama}  [{role}]')
        lbl_user.setStyleSheet(
            'color:#f5c800; font-size:11px; font-weight:800;'
            'padding:6px 18px 6px 18px; background:#1a1a1a;'
        )
        sb.addWidget(lbl_user)
        sb.addSpacing(10)

        lbl_menu = QLabel('  MENU')
        lbl_menu.setObjectName('lblDivider')
        sb.addWidget(lbl_menu)

        self._tombol_nav = []
        menu = [
            ('  Overview',    0),
            ('  Booking PC',  1),
            ('  Laporan',     2),
            ('  Pengaturan',  3),
        ]
        # Owner dapat menu tambahan
        if auth_state.is_owner():
            menu.append(('  Kelola User', 4))

        for teks, idx in menu:
            btn = QPushButton(teks)
            btn.setObjectName('tombolNav')
            btn.setCheckable(True)
            btn.setFixedHeight(42)
            btn.clicked.connect(lambda _, i=idx: self._ganti_halaman(i))
            sb.addWidget(btn)
            self._tombol_nav.append((btn, idx))

        sb.addStretch()

        # Tombol logout
        btn_logout = QPushButton('  Logout')
        btn_logout.setObjectName('tombolNav')
        btn_logout.setFixedHeight(38)
        btn_logout.clicked.connect(self._logout)
        sb.addWidget(btn_logout)

        frame_bawah = QFrame()
        frame_bawah.setObjectName('sidebarFooter')
        bawah_layout = QVBoxLayout(frame_bawah)
        bawah_layout.setContentsMargins(16, 8, 16, 12)
        bawah_layout.setSpacing(2)
        lbl_ver = QLabel('v1.0.0 — WarnetKu')
        lbl_ver.setObjectName('footerText')
        lbl_anggota = QLabel('Kelompok Tugas Akhir')
        lbl_anggota.setObjectName('footerTextSmall')
        bawah_layout.addWidget(lbl_ver)
        bawah_layout.addWidget(lbl_anggota)
        sb.addWidget(frame_bawah)

        root.addWidget(sidebar)

        # --- Stack konten ---
        self.stack = QStackedWidget()
        self.stack.setObjectName('areaKonten')

        self.view_dashboard  = DashboardView()
        self.view_booking    = BookingView()
        self.view_laporan    = LaporanView()
        self.view_pengaturan = PengaturanView()
        self.view_user       = UserView()

        self.stack.addWidget(self.view_dashboard)   # 0
        self.stack.addWidget(self.view_booking)     # 1
        self.stack.addWidget(self.view_laporan)     # 2
        self.stack.addWidget(self.view_pengaturan)  # 3
        self.stack.addWidget(self.view_user)        # 4

        root.addWidget(self.stack)

        # --- Status Bar: nama & NIM semua anggota (permanen) ---
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        nim_label = QLabel(
            '  |  '.join(f'{n}  ({nim})' for n, nim in ANGGOTA)
        )
        nim_label.setStyleSheet('font-size:11px; color:#555555; padding: 0 8px;')
        self.status.addPermanentWidget(nim_label)
        self.status.showMessage(f'Selamat datang, {nama}!')

        self._ganti_halaman(0)

    def _ganti_halaman(self, idx):
        self.stack.setCurrentIndex(idx)
        for btn, i in self._tombol_nav:
            btn.setChecked(i == idx)

    def set_status(self, pesan: str):
        self.status.showMessage(pesan)

    def _logout(self):
        konfirmasi = QMessageBox.question(
            self, 'Logout',
            'Yakin ingin logout?',
            QMessageBox.Yes | QMessageBox.No
        )
        if konfirmasi != QMessageBox.Yes:
            return
        auth_state.logout()
        self.close()
        # Restart login
        from dialogs.login_dialog import DialogLogin
        dlg = DialogLogin()
        if dlg.exec():
            win = MainWindow()
            from utils.notif_helper import set_main_window
            set_main_window(win)
            win.show()
            # Re-init controllers
            from controllers.dashboard_controller import DashboardController
            from controllers.laporan_controller import LaporanController
            from controllers.pengaturan_controller import PengaturanController
            from controllers.statistik_controller import StatistikController
            from controllers.user_controller import UserController
            win._ctrl_dashboard  = DashboardController(win.view_booking, win, win.view_dashboard)
            win._ctrl_statistik  = StatistikController(win.view_dashboard, win)
            win._ctrl_laporan    = LaporanController(win.view_laporan, win)
            win._ctrl_pengaturan = PengaturanController(win.view_pengaturan, win)
            win._ctrl_user       = UserController(win.view_user, win)
