import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PySide6.QtWidgets import QMessageBox
from views.user_view import UserView
from models import user_model, auth_state
from dialogs.user_dialog import DialogUser
from utils.notif_helper import notif_sukses, notif_error, notif_peringatan


class UserController:
    def __init__(self, view: UserView, main_window):
        self.view = view
        self.win  = main_window

        view.minta_tambah.connect(self._aksi_tambah)
        view.minta_edit.connect(self._aksi_edit)
        view.minta_hapus.connect(self._aksi_hapus)
        view.minta_refresh.connect(self._muat_data)

        self._muat_data()

    def _muat_data(self):
        data = user_model.ambil_semua()
        self.view.tampilkan_data(data, auth_state.get_kasir_id())

    def _aksi_tambah(self):
        dialog = DialogUser(self.win)
        if not dialog.exec():
            return
        data = dialog.ambil_data()
        ok = user_model.tambah(data['username'], data['password'], data['nama'], data['role'])
        if ok:
            self._muat_data()
            self.win.set_status(f'User "{data["nama"]}" berhasil ditambahkan.')
            notif_sukses(f'User "{data["nama"]}" berhasil ditambahkan')
        else:
            QMessageBox.critical(self.win, 'Gagal', 'Username sudah digunakan.')
            notif_error('Gagal tambah user — username sudah ada')

    def _aksi_edit(self, user_id: int):
        # Owner tidak bisa edit dirinya sendiri via tabel (gunakan menu profil)
        user = user_model.ambil_by_id(user_id)
        if not user:
            return
        dialog = DialogUser(self.win, data=user)
        if not dialog.exec():
            return
        data = dialog.ambil_data()
        try:
            user_model.update(
                user_id, data['nama'], data['username'],
                data['role'], data['aktif'], data['password']
            )
            self._muat_data()
            self.win.set_status(f'User "{data["nama"]}" berhasil diupdate.')
            notif_sukses(f'User "{data["nama"]}" diupdate')
        except Exception as e:
            QMessageBox.critical(self.win, 'Gagal', str(e))
            notif_error(f'Gagal update user: {e}')

    def _aksi_hapus(self, user_id: int):
        if user_id == auth_state.get_kasir_id():
            QMessageBox.warning(self.win, 'Tidak Bisa', 'Tidak bisa hapus akun yang sedang login.')
            notif_peringatan('Tidak bisa hapus akun yang sedang login')
            return
        user = user_model.ambil_by_id(user_id)
        if not user:
            return
        if user['role'] == 'owner':
            # Cek apakah ini satu-satunya owner
            semua = user_model.ambil_semua()
            jml_owner = sum(1 for u in semua if u['role'] == 'owner' and u['aktif'])
            if jml_owner <= 1:
                QMessageBox.warning(self.win, 'Tidak Bisa', 'Minimal harus ada 1 owner aktif.')
                return
        konfirmasi = QMessageBox.question(
            self.win, 'Konfirmasi Hapus',
            f'Yakin hapus user "{user["nama"]}" ({user["username"]})?',
            QMessageBox.Yes | QMessageBox.No
        )
        if konfirmasi != QMessageBox.Yes:
            return
        user_model.hapus(user_id)
        self._muat_data()
        self.win.set_status(f'User "{user["nama"]}" dihapus.')
        notif_sukses(f'User "{user["nama"]}" dihapus')
