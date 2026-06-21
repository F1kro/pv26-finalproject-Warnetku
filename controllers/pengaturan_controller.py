import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from PySide6.QtWidgets import QMessageBox
from views.pengaturan_view import PengaturanView
from models import komputer_model
from dialogs.tambah_komputer_dialog import DialogTambahKomputer
from utils.notif_helper import notif_sukses, notif_error, notif_info, notif_peringatan

class PengaturanController:
    def __init__(self, view: PengaturanView, main_window):
        self.view = view
        self.win  = main_window

        view.minta_tambah.connect(self._aksi_tambah)
        view.minta_edit.connect(self._aksi_edit)
        view.minta_hapus.connect(self._aksi_hapus)
        view.minta_reset_sesi.connect(self._aksi_reset_sesi)
        view.minta_refresh.connect(self._muat_data)

        self._muat_data()

    def _muat_data(self):
        self.view.tampilkan_data(komputer_model.ambil_semua())

    def _aksi_tambah(self):
        dialog = DialogTambahKomputer(self.win)
        if not dialog.exec():
            return
        data = dialog.ambil_data()
        try:
            komputer_model.tambah(data['nama'], data['spesifikasi'])
            self._muat_data()
            self._refresh_booking()
            self.win.set_status(f'Komputer {data["nama"]} berhasil ditambahkan.')
            notif_sukses(f'Komputer "{data["nama"]}" berhasil ditambahkan')
        except Exception as e:
            QMessageBox.critical(self.win, 'Error', f'Gagal menambah komputer:\n{e}')
            notif_error(f'Gagal tambah komputer: {e}')

    def _aksi_edit(self, komputer_id: int):
        komp = komputer_model.ambil_by_id(komputer_id)
        if not komp:
            return
        dialog = DialogTambahKomputer(self.win, data=komp)
        if not dialog.exec():
            return
        data = dialog.ambil_data()
        try:
            komputer_model.update(komputer_id, data['nama'], data['spesifikasi'])
            self._muat_data()
            self._refresh_booking()
            self.win.set_status(f'Komputer ID {komputer_id} berhasil diupdate.')
            notif_info(f'Komputer "{data["nama"]}" berhasil diupdate')
        except Exception as e:
            QMessageBox.critical(self.win, 'Error', f'Gagal update komputer:\n{e}')
            notif_error(f'Gagal update komputer: {e}')

    def _aksi_hapus(self, komputer_id: int):
        komp = komputer_model.ambil_by_id(komputer_id)
        if not komp:
            return
        if komp['status'] == 'aktif':
            QMessageBox.warning(self.win, 'Tidak Bisa', 'Komputer sedang aktif, tidak bisa dihapus.')
            notif_peringatan(f'Komputer "{komp["nama"]}" sedang aktif')
            return
        konfirmasi = QMessageBox.question(
            self.win, 'Konfirmasi Hapus',
            f'Yakin hapus komputer "{komp["nama"]}"?',
            QMessageBox.Yes | QMessageBox.No
        )
        if konfirmasi != QMessageBox.Yes:
            return
        komputer_model.hapus(komputer_id)
        self._muat_data()
        self._refresh_booking()
        self.win.set_status(f'Komputer {komp["nama"]} dihapus.')
        notif_info(f'Komputer "{komp["nama"]}" berhasil dihapus')

    def _aksi_reset_sesi(self):
        from models.sesi_model import reset_semua_aktif, ambil_semua_aktif
        aktif = ambil_semua_aktif()
        if not aktif:
            QMessageBox.information(self.win, 'Info', 'Tidak ada sesi aktif di database.')
            notif_info('Tidak ada sesi aktif yang perlu direset')
            return
        konfirmasi = QMessageBox.question(
            self.win, 'Reset Sesi Aktif',
            f'Ditemukan {len(aktif)} sesi aktif di database.\n\n'
            'Ini akan menutup paksa semua sesi tersebut dan mereset status komputer.\n'
            'Lakukan ini hanya jika ada data yang tidak sinkron.\n\n'
            'Lanjutkan?',
            QMessageBox.Yes | QMessageBox.No
        )
        if konfirmasi != QMessageBox.Yes:
            return
        reset_semua_aktif()
        self._muat_data()
        self._refresh_booking()
        self.win.set_status(f'{len(aktif)} sesi aktif berhasil direset.')
        notif_sukses(f'{len(aktif)} sesi aktif berhasil direset')
        QMessageBox.information(
            self.win, 'Selesai',
            f'{len(aktif)} sesi direset. Restart aplikasi untuk memperbarui tampilan dashboard.'
        )

    def _refresh_booking(self):
        controller = getattr(self.win, '_ctrl_dashboard', None)
        if controller and hasattr(controller, 'refresh_grid'):
            controller.refresh_grid()
