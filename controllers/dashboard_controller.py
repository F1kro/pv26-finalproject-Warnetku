import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox

from config import HARGA_PER_MENIT
from dialogs.bayar_dialog import DialogBayar
from dialogs.mulai_sesi_dialog import DialogMulaiSesi
from models import komputer_model, sesi_model, transaksi_model
from services.timer_service import TimerSesi
from services.weather_service import WeatherWorker
from views.booking_view import BookingView
from utils.notif_helper import notif_sukses, notif_info, notif_peringatan, notif_error
from services.telegram_service import kirim_notif, format_transaksi_baru, format_sesi_mulai

class DashboardController:
    def __init__(self, view: BookingView, main_window, summary_view=None):
        self.view = view
        self.win = main_window
        self.summary_view = summary_view
        self._timer_map: dict[int, TimerSesi] = {}
        self._sesi_map: dict[int, dict] = {}
        self._workers = []

        self._init_grid()
        self._pulihkan_sesi_aktif()
        self._muat_cuaca()
        self._refresh_ringkasan()

        self.view.minta_refresh.connect(self._on_refresh_manual)

        self._timer_refresh = QTimer()
        self._timer_refresh.setInterval(30_000)
        self._timer_refresh.timeout.connect(self._refresh_ringkasan)
        self._timer_refresh.start()

    def _init_grid(self):
        komputer = komputer_model.ambil_semua()
        self.view.bangun_grid_komputer(komputer)
        self._update_total_pc(komputer)
        for komp in komputer:
            kartu = self.view.kartu(komp['id'])
            if kartu:
                kartu.klik_mulai.connect(self._on_mulai)
                kartu.klik_selesai.connect(self._on_selesai)

    def refresh_grid(self):
        self._init_grid()
        for komputer_id, sesi in self._sesi_map.items():
            kartu = self.view.kartu(komputer_id)
            timer = self._timer_map.get(komputer_id)
            if kartu:
                kartu.set_aktif(sesi.get('nama_pelanggan', ''), is_open=sesi.get('is_open', False))
                if timer:
                    kartu.update_timer(timer.detik_berjalan, timer._hitung_biaya())
        self._refresh_ringkasan()

    def _pulihkan_sesi_aktif(self):
        aktif = sesi_model.ambil_semua_aktif()
        for sesi in aktif:
            kid = sesi['komputer_id']
            mulai = datetime.fromisoformat(sesi['mulai'])
            detik_sudah = int((datetime.now() - mulai).total_seconds())

            paket_nama = sesi['paket']
            durasi_mnt = harga_paket = None
            from config import PAKET
            for nama, durasi, harga in PAKET:
                if nama == paket_nama:
                    durasi_mnt = durasi
                    harga_paket = harga
                    break

            timer = TimerSesi(
                kid,
                sesi['id'],
                mulai,
                durasi_paket_menit=durasi_mnt,
                harga_paket=harga_paket,
                harga_per_menit=HARGA_PER_MENIT,
            )
            timer._detik = detik_sudah
            timer.tick.connect(self._on_tick)
            timer.selesai.connect(self._on_paket_habis)
            timer.mulai_timer()

            self._timer_map[kid] = timer
            self._sesi_map[kid] = sesi

            kartu = self.view.kartu(kid)
            if kartu:
                is_open = sesi.get('paket', '') == 'Open Billing'
                kartu.set_aktif(sesi.get('nama_pelanggan', ''), is_open=is_open)
                kartu.update_timer(detik_sudah, timer._hitung_biaya())

    def _on_mulai(self, komputer_id: int):
        komp = komputer_model.ambil_by_id(komputer_id)
        if not komp:
            return
        dialog = DialogMulaiSesi(komp['nama'], self.win)
        if not dialog.exec():
            return

        nama_pelanggan, paket, metode_bayar = dialog.ambil_data()
        paket_nama, durasi_mnt, harga_paket = paket
        is_open = durasi_mnt is None

        if not is_open:
            # Pass metode_bayar dari dialog pertama langsung ke DialogBayar
            dialog_bayar = DialogBayar(
                komp['nama'], None, 0,
                harga_paket, paket_nama, nama_pelanggan,
                metode_bayar=metode_bayar,
                parent=self.win,
            )

            bayar_ok = [False]
            metode_final = [metode_bayar]

            def on_bayar(metode):
                bayar_ok[0] = True
                metode_final[0] = metode

            dialog_bayar.pembayaran_selesai.connect(on_bayar)
            dialog_bayar.exec()

            if not bayar_ok[0]:
                return
        else:
            metode_final = [None]

        from models.auth_state import get_kasir_id
        sesi_id = sesi_model.mulai_sesi(komputer_id, nama_pelanggan, paket_nama, kasir_id=get_kasir_id())
        komputer_model.set_status(komputer_id, 'aktif')

        if not is_open:
            transaksi_model.catat_transaksi(sesi_id, harga_paket, metode_final[0])

        timer = TimerSesi(
            komputer_id,
            sesi_id,
            datetime.now(),
            durasi_paket_menit=durasi_mnt,
            harga_paket=harga_paket,
            harga_per_menit=HARGA_PER_MENIT,
        )
        timer.tick.connect(self._on_tick)
        timer.selesai.connect(self._on_paket_habis)
        timer.mulai_timer()

        self._timer_map[komputer_id] = timer
        self._sesi_map[komputer_id] = {
            'id': sesi_id,
            'nama_pelanggan': nama_pelanggan,
            'paket': paket_nama,
            'komputer_id': komputer_id,
            'is_open': is_open,
            'harga_paket': harga_paket,
        }

        kartu = self.view.kartu(komputer_id)
        if kartu:
            kartu.set_aktif(nama_pelanggan, is_open=is_open)

        self._refresh_ringkasan()
        self.win.set_status(f'{komp["nama"]} - sesi dimulai untuk {nama_pelanggan}')
        notif_sukses(f'Sesi dimulai: {komp["nama"]} — {nama_pelanggan}')
        from models.auth_state import get_nama
        _pesan_tg = format_sesi_mulai(komp['nama'], nama_pelanggan, paket_nama, get_nama())
        self._workers.append(kirim_notif(_pesan_tg))

    def _on_tick(self, komputer_id: int, detik: int, biaya: float):
        kartu = self.view.kartu(komputer_id)
        if kartu:
            kartu.update_timer(detik, biaya)

    def _on_paket_habis(self, komputer_id: int):
        komp = komputer_model.ambil_by_id(komputer_id)
        nama = komp['nama'] if komp else f'PC-{komputer_id}'
        notif_peringatan(f'Paket {nama} habis — silakan bayar')
        QMessageBox.information(
            self.win,
            'Paket Habis',
            f'Paket sesi {nama} telah habis.\nSilakan lakukan pembayaran.',
        )
        self._on_selesai(komputer_id)

    def _on_selesai(self, komputer_id: int):
        timer = self._timer_map.get(komputer_id)
        sesi = self._sesi_map.get(komputer_id)
        if not timer or not sesi:
            return

        timer.stop()
        detik = timer.detik_berjalan
        biaya = timer._hitung_biaya()
        komp = komputer_model.ambil_by_id(komputer_id)
        is_open = sesi.get('is_open', True)

        if is_open:
            # Open billing: user pilih metode di DialogBayar (default Tunai)
            dialog = DialogBayar(
                komp['nama'] if komp else '',
                sesi['id'], detik, biaya,
                sesi['paket'], sesi['nama_pelanggan'],
                metode_bayar='Tunai',
                parent=self.win,
            )
            # Untuk open billing, tampilkan combo metode via flag
            dialog._show_metode_combo()
            dialog.pembayaran_selesai.connect(
                lambda metode: self._proses_bayar(komputer_id, sesi['id'], detik, biaya, metode)
            )
            if not dialog.exec():
                timer.mulai_timer()
        else:
            self._proses_selesai_tanpa_bayar(komputer_id, sesi['id'], detik, biaya)

    def _proses_bayar(self, komputer_id, sesi_id, detik, biaya, metode):
        durasi_mnt = detik // 60
        sesi_model.selesai_sesi(sesi_id, durasi_mnt, biaya)
        transaksi_model.catat_transaksi(sesi_id, biaya, metode)
        komputer_model.set_status(komputer_id, 'kosong')

        # Ambil info sesi SEBELUM dihapus dari map
        _sesi_info = self._sesi_map.get(komputer_id) or {}
        komp = komputer_model.ambil_by_id(komputer_id)

        del self._timer_map[komputer_id]
        del self._sesi_map[komputer_id]

        kartu = self.view.kartu(komputer_id)
        if kartu:
            kartu.set_kosong()

        self._refresh_ringkasan()
        self.win.set_status(f'Sesi selesai - Rp {biaya:,.0f} via {metode}')
        notif_sukses(f'Pembayaran selesai  Rp {biaya:,.0f} via {metode}')
        from models.auth_state import get_nama
        _pesan_tg = format_transaksi_baru(
            komp['nama'] if komp else f'PC-{komputer_id}',
            _sesi_info.get('nama_pelanggan', '-'),
            _sesi_info.get('paket', '-'),
            biaya, metode, get_nama()
        )
        self._workers.append(kirim_notif(_pesan_tg))

    def _proses_selesai_tanpa_bayar(self, komputer_id, sesi_id, detik, biaya):
        durasi_mnt = detik // 60
        sesi_model.selesai_sesi(sesi_id, durasi_mnt, biaya)
        komputer_model.set_status(komputer_id, 'kosong')

        _sesi_cache = self._sesi_map.get(komputer_id) or {}
        del self._timer_map[komputer_id]
        del self._sesi_map[komputer_id]

        kartu = self.view.kartu(komputer_id)
        if kartu:
            kartu.set_kosong()

        self._refresh_ringkasan()
        self.win.set_status('Sesi selesai - paket sudah dibayar di muka')
        notif_info('Sesi selesai — paket sudah dibayar di muka')
        from models.auth_state import get_nama
        komp = komputer_model.ambil_by_id(komputer_id)
        _pesan_tg = format_transaksi_baru(
            komp['nama'] if komp else f'PC-{komputer_id}',
            _sesi_cache.get('nama_pelanggan', '-'),
            _sesi_cache.get('paket', '-'),
            biaya, 'Prabayar', get_nama()
        )
        self._workers.append(kirim_notif(_pesan_tg))

    def _refresh_ringkasan(self):
        if not self.summary_view:
            return
        total = transaksi_model.total_hari_ini()
        aktif = len(self._timer_map)
        komputer = komputer_model.ambil_semua()
        self.summary_view.update_pendapatan(total)
        self.summary_view.update_sesi_aktif(aktif)
        self._update_total_pc(komputer)

    def _on_refresh_manual(self):
        self.refresh_grid()
        self.win.set_status('Booking diperbarui.')

    def _muat_cuaca(self):
        worker = WeatherWorker()
        if self.summary_view:
            worker.hasil.connect(self.summary_view.update_cuaca)
            worker.error.connect(
                lambda e: self.summary_view.lbl_cuaca_detail.setText('Cuaca tidak tersedia')
            )
        worker.finished.connect(lambda: self._workers.remove(worker) if worker in self._workers else None)
        self._workers.append(worker)
        worker.start()

    def _update_total_pc(self, komputer):
        if not self.summary_view:
            return
        total = len(komputer)
        kosong = sum(1 for komp in komputer if komp.get('status') == 'kosong')
        self.summary_view.update_total_pc(total, kosong)






