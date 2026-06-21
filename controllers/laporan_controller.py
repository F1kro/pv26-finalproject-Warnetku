import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFileDialog, QMessageBox
from datetime import datetime

from views.laporan_view import LaporanView
from models import transaksi_model, sesi_model
from models.transaksi_model import pendapatan_per_kasir, statistik_rentang
from utils import export_csv, export_pdf
from services.telegram_service import kirim_notif, format_laporan_harian, format_insight
from services.timer_service import TimerSesi
from config import NAMA_WARNET
from utils.notif_helper import notif_sukses, notif_error, notif_info

class LaporanController:
    def __init__(self, view: LaporanView, main_window):
        self.view      = view
        self.win       = main_window
        self._data     = []
        self._workers  = []
        self._tgl_mulai   = datetime.now().strftime('%Y-%m-%d')
        self._tgl_selesai = datetime.now().strftime('%Y-%m-%d')

        view.minta_filter.connect(self._muat_data)
        view.minta_csv.connect(self._export_csv)
        view.minta_pdf.connect(self._export_pdf)
        view.minta_telegram.connect(self._kirim_telegram)
        view.minta_insight.connect(self._kirim_insight)
        view.minta_refresh.connect(self._on_refresh)

        # Timer refresh live setiap 10 detik (update durasi sesi aktif)
        self._timer_live = QTimer()
        self._timer_live.setInterval(10_000)
        self._timer_live.timeout.connect(self._on_refresh)
        self._timer_live.start()

        # Muat data hari ini saat pertama buka
        self._muat_data(self._tgl_mulai, self._tgl_selesai)

    def _on_refresh(self):
        self._muat_data(self._tgl_mulai, self._tgl_selesai)

    def _muat_data(self, tgl_mulai: str, tgl_selesai: str):
        self._tgl_mulai   = tgl_mulai
        self._tgl_selesai = tgl_selesai

        # Transaksi selesai — paket & durasi sudah ada di query join
        transaksi = transaksi_model.ambil_rentang(tgl_mulai, tgl_selesai)

        self._data = []
        for t in transaksi:
            self._data.append({
                'id':             t['id'],
                'waktu':          t['waktu'],
                'nama_komputer':  t.get('nama_komputer', ''),
                'nama_pelanggan': t.get('nama_pelanggan', ''),
                'paket':          t.get('paket', '—'),
                'durasi_menit':   t.get('durasi_menit', 0),
                'metode':         t['metode'],
                'jumlah':         t['jumlah'],
                'status':         t.get('status', 'lunas'),
                'sesi_id':        t['sesi_id'],
                'sesi_aktif':     False,
            })

        # Sesi aktif (open billing belum bayar — tampilkan sebagai baris live)
        sesi_aktif_list = sesi_model.ambil_semua_aktif()
        now = datetime.now()
        for sesi in sesi_aktif_list:
            mulai = datetime.fromisoformat(sesi['mulai'])
            detik = int((now - mulai).total_seconds())
            durasi_live = TimerSesi.format_durasi(detik)
            self._data.append({
                'id':             f"S{sesi['id']}",
                'waktu':          sesi['mulai'],
                'nama_komputer':  sesi.get('nama_komputer', ''),
                'nama_pelanggan': sesi.get('nama_pelanggan', ''),
                'paket':          sesi.get('paket', '—'),
                'durasi_menit':   detik // 60,
                'durasi_live':    durasi_live,
                'metode':         '—',
                'jumlah':         0,
                'status':         'aktif',
                'sesi_id':        sesi['id'],
                'sesi_aktif':     True,
            })

        self.view.tampilkan_data(self._data)
        n_selesai = sum(1 for d in self._data if not d.get('sesi_aktif'))
        n_aktif   = sum(1 for d in self._data if d.get('sesi_aktif'))
        self.win.set_status(
            f'Laporan {tgl_mulai} s.d. {tgl_selesai} — {n_selesai} transaksi, {n_aktif} sesi aktif'
        )

    def _export_csv(self):
        data_export = [d for d in self._data if not d.get('sesi_aktif')]
        if not data_export:
            QMessageBox.information(self.win, 'Info', 'Tidak ada data untuk diekspor.')
            return
        nama_default = export_csv.nama_file_default('laporan')
        path, _ = QFileDialog.getSaveFileName(self.win, 'Simpan CSV', nama_default, 'CSV (*.csv)')
        if not path:
            return
        ok = export_csv.export_transaksi(data_export, path)
        if ok:
            QMessageBox.information(self.win, 'Berhasil', f'CSV disimpan ke:\n{path}')
            self.win.set_status(f'CSV diekspor: {path}')
            notif_sukses(f'Laporan CSV berhasil disimpan')
        else:
            QMessageBox.critical(self.win, 'Gagal', 'Gagal menyimpan CSV.')
            notif_error('Gagal menyimpan CSV')

    def _export_pdf(self):
        data_export = [d for d in self._data if not d.get('sesi_aktif')]
        if not data_export:
            QMessageBox.information(self.win, 'Info', 'Tidak ada data untuk diekspor.')
            return
        nama_default = export_pdf.nama_file_default('laporan')
        path, _ = QFileDialog.getSaveFileName(self.win, 'Simpan PDF', nama_default, 'PDF (*.pdf)')
        if not path:
            return
        ok, pesan = export_pdf.export_transaksi(data_export, path, NAMA_WARNET)
        if ok:
            QMessageBox.information(self.win, 'Berhasil', pesan)
            self.win.set_status(f'PDF diekspor: {path}')
            notif_sukses('Laporan PDF berhasil disimpan')
        else:
            QMessageBox.critical(self.win, 'Gagal', pesan)
            notif_error(f'Gagal simpan PDF: {pesan}')

    def _kirim_insight(self):
        stat  = statistik_rentang(self._tgl_mulai, self._tgl_selesai)
        kasir = pendapatan_per_kasir(self._tgl_mulai, self._tgl_selesai)
        top   = kasir[0][0] if kasir else '-'
        periode = f'{self._tgl_mulai} s.d. {self._tgl_selesai}'
        pesan = format_insight(
            periode, stat['total'], stat['jml'], stat['rata'],
            stat['jam_sibuk'], top, kasir
        )
        worker = kirim_notif(pesan)
        worker.sukses.connect(lambda m: (
            self.win.set_status('Insight terkirim ke Telegram'),
            notif_sukses('Insight berhasil dikirim ke Telegram')
        ))
        worker.error.connect(lambda e: QMessageBox.warning(self.win, 'Telegram Error', e))
        self._workers.append(worker)

    def _kirim_telegram(self):
        data_lunas = [d for d in self._data if not d.get('sesi_aktif')]
        total = sum(d['jumlah'] for d in data_lunas)
        pesan = format_laporan_harian(total, len(data_lunas), self._tgl_mulai)
        worker = kirim_notif(pesan)
        worker.sukses.connect(lambda m: (
            QMessageBox.information(self.win, 'Telegram', m),
            self.win.set_status(m),
            notif_sukses('Laporan terkirim ke Telegram')
        ))
        worker.error.connect(lambda e: QMessageBox.warning(self.win, 'Telegram Error', e))
        self._workers.append(worker)



