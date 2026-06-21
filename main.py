# WarnetKu - Sistem Manajemen Warung Internet
# Anggota Kelompok:
#   1. Fiqro Najiah
#   2. Kanda Rifqi Alfaz
#   3. Ayu Liza Putri Wiwaha

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from PySide6.QtWidgets import QApplication

from database.db_manager import inisialisasi
from dialogs.login_dialog import DialogLogin
from models import auth_state


def _buat_window_dan_controller(app):
    from views.main_window import MainWindow
    from controllers.dashboard_controller import DashboardController
    from controllers.laporan_controller import LaporanController
    from controllers.pengaturan_controller import PengaturanController
    from controllers.statistik_controller import StatistikController
    from controllers.user_controller import UserController
    from utils.notif_helper import set_main_window

    window = MainWindow()
    set_main_window(window)

    window._ctrl_dashboard  = DashboardController(window.view_booking, window, window.view_dashboard)
    window._ctrl_statistik  = StatistikController(window.view_dashboard, window)
    window._ctrl_laporan    = LaporanController(window.view_laporan, window)
    window._ctrl_pengaturan = PengaturanController(window.view_pengaturan, window)
    window._ctrl_user       = UserController(window.view_user, window)

    return window


def main():
    inisialisasi()

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    qss_path = os.path.join(os.path.dirname(__file__), 'style.qss')
    with open(qss_path, 'r', encoding='utf-8') as f:
        app.setStyleSheet(f.read())

    # Loop login — kalau user close dialog login, app exit
    while True:
        dlg = DialogLogin()
        if not dlg.exec():
            break

        window = _buat_window_dan_controller(app)
        window.show()
        app.exec()

        # Kalau logout, _user di-reset oleh MainWindow._logout
        # Kalau close window tanpa logout, kita juga break
        if not auth_state.get_user():
            continue   # kembali ke login
        break


if __name__ == '__main__':
    main()
