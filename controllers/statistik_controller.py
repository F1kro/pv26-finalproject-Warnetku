import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.db_manager import koneksi
from views.dashboard_view import DashboardView


def _ambil_data(hari=7):
    conn = koneksi()
    if hari == 0:
        rows = conn.execute(
            '''SELECT t.waktu, t.jumlah, t.metode, s.komputer_id, k.nama as nama_komputer
               FROM transaksi t
               JOIN sesi s ON t.sesi_id = s.id
               JOIN komputer k ON s.komputer_id = k.id
               WHERE t.status = 'lunas'
               ORDER BY t.waktu'''
        ).fetchall()
    else:
        since = (datetime.now() - timedelta(days=hari)).strftime('%Y-%m-%d')
        rows = conn.execute(
            '''SELECT t.waktu, t.jumlah, t.metode, s.komputer_id, k.nama as nama_komputer
               FROM transaksi t
               JOIN sesi s ON t.sesi_id = s.id
               JOIN komputer k ON s.komputer_id = k.id
               WHERE DATE(t.waktu) >= ? AND t.status = 'lunas'
               ORDER BY t.waktu''',
            (since,),
        ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


class StatistikController:
    def __init__(self, view: DashboardView, main_window):
        self.view = view
        self.win = main_window
        view.minta_refresh.connect(self._refresh)
        self._refresh()

    def _refresh(self):
        idx = self.view.combo_periode.currentIndex()
        hari = [7, 30, 0][idx]
        data = _ambil_data(hari)

        if not data:
            self.view.render_line([], [])
            self.view.render_bar_pc([], [])
            self.view.render_pie([], [])
            self.view.render_bar_jam([], [])
            self.view.update_ringkasan(0, 0, 0, '-')
            return

        from collections import defaultdict

        per_hari = defaultdict(float)
        per_pc = defaultdict(int)
        per_metode = defaultdict(int)
        per_jam = defaultdict(int)

        for row in data:
            tgl = str(row['waktu'])[:10]
            per_hari[tgl] += row['jumlah']
            per_pc[row['nama_komputer']] += 1
            per_metode[row['metode']] += 1
            try:
                jam = int(str(row['waktu'])[11:13])
                per_jam[jam] += 1
            except Exception:
                pass

        hari_sorted = sorted(per_hari.keys())

        def fmt_tgl(tanggal):
            try:
                return datetime.strptime(tanggal, '%Y-%m-%d').strftime('%d/%m')
            except Exception:
                return tanggal

        self.view.render_line(
            [fmt_tgl(tanggal) for tanggal in hari_sorted],
            [per_hari[tanggal] for tanggal in hari_sorted],
        )

        pc_sorted = sorted(per_pc.items(), key=lambda item: -item[1])[:10]
        self.view.render_bar_pc(
            [item[0] for item in pc_sorted],
            [item[1] for item in pc_sorted],
        )

        self.view.render_pie(
            list(per_metode.keys()),
            list(per_metode.values()),
        )

        jam_labels = [f'{jam:02d}:00' for jam in range(8, 24)]
        jam_values = [per_jam.get(jam, 0) for jam in range(8, 24)]
        self.view.render_bar_jam(jam_labels, jam_values)

        total = sum(row['jumlah'] for row in data)
        sesi = len(data)
        rata = total / sesi if sesi else 0
        jam_sibuk = '-'
        if per_jam:
            jam = max(per_jam, key=per_jam.get)
            jam_sibuk = f'{jam:02d}:00 - {jam + 1:02d}:00'

        self.view.update_ringkasan(total, sesi, rata, jam_sibuk)
        self.win.set_status(f'Dashboard diperbarui - {sesi} transaksi')
