import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

matplotlib.rcParams['font.family'] = 'DejaVu Sans'

BG = '#ffffff'
GRID = '#e5e7eb'
BIRU = '#2563eb'
BIRU2 = '#38bdf8'
HIJAU = '#059669'
ORG = '#d97706'
ABU = '#475569'
PALETTE = [BIRU, BIRU2, '#10b981', '#f59e0b', '#64748b', '#94a3b8']


def _style_ax(ax, fig):
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.tick_params(colors='#64748b', labelsize=9)
    ax.xaxis.label.set_color('#64748b')
    ax.yaxis.label.set_color('#64748b')
    ax.title.set_color('#0f172a')
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8, linestyle='-')
    ax.set_axisbelow(True)
    ax.xaxis.grid(False)


class ChartCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('card')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.fig = Figure(tight_layout=True)
        self.fig.patch.set_facecolor(BG)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setStyleSheet('background-color: #ffffff;')
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.canvas)

    def clear(self):
        self.fig.clear()

    def draw(self):
        self.canvas.draw()


class StatistikView(QWidget):
    minta_refresh = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._bangun_ui()

    def _bangun_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 16)
        root.setSpacing(0)

        header = QHBoxLayout()
        col = QVBoxLayout()
        col.setSpacing(2)
        lbl = QLabel('Statistik')
        lbl.setObjectName('judulModul')
        lbl_sub = QLabel('Grafik penjualan dan performa warnet')
        lbl_sub.setObjectName('subJudul')
        col.addWidget(lbl)
        col.addWidget(lbl_sub)
        header.addLayout(col)
        header.addStretch()

        self.combo_periode = QComboBox()
        self.combo_periode.addItems(['7 Hari Terakhir', '30 Hari Terakhir', 'Semua'])
        self.combo_periode.setFixedWidth(160)
        self.combo_periode.currentIndexChanged.connect(self.minta_refresh.emit)

        self.btn_refresh = QPushButton('Refresh')
        self.btn_refresh.setObjectName('btnRefresh')
        self.btn_refresh.setFixedHeight(36)
        self.btn_refresh.clicked.connect(self.minta_refresh.emit)
        header.addWidget(self.combo_periode)
        header.addWidget(self.btn_refresh)
        root.addLayout(header)
        root.addSpacing(16)

        baris = QHBoxLayout()
        baris.setSpacing(12)
        self.k_total = self._kartu('Total Pendapatan', 'Rp 0', BIRU, 'Rp')
        self.k_sesi = self._kartu('Total Sesi', '0', HIJAU, 'ON')
        self.k_rata = self._kartu('Rata-rata/Sesi', 'Rp 0', ORG, 'AVG')
        self.k_terlaris = self._kartu('Jam Tersibuk', '-', ABU, 'TIME')
        for kartu in [self.k_total, self.k_sesi, self.k_rata, self.k_terlaris]:
            baris.addWidget(kartu)
        root.addLayout(baris)
        root.addSpacing(16)

        grid_chart = QHBoxLayout()
        grid_chart.setSpacing(12)

        kiri = QVBoxLayout()
        kiri.setSpacing(12)
        self.chart_line = ChartCard()
        self.chart_line.setMinimumHeight(240)
        kiri.addWidget(self.chart_line)
        self.chart_bar_pc = ChartCard()
        self.chart_bar_pc.setMinimumHeight(220)
        kiri.addWidget(self.chart_bar_pc)

        kanan = QVBoxLayout()
        kanan.setSpacing(12)
        self.chart_pie = ChartCard()
        self.chart_pie.setMinimumHeight(240)
        kanan.addWidget(self.chart_pie)
        self.chart_bar_jam = ChartCard()
        self.chart_bar_jam.setMinimumHeight(220)
        kanan.addWidget(self.chart_bar_jam)

        grid_chart.addLayout(kiri, 3)
        grid_chart.addLayout(kanan, 2)
        root.addLayout(grid_chart)

    def _kartu(self, judul, nilai, warna, kode):
        frame = QFrame()
        frame.setObjectName('card')
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        lbl_kode = QLabel(kode)
        lbl_kode.setFixedSize(42, 22)
        lbl_kode.setObjectName('pillIcon')
        layout.addWidget(lbl_kode)

        lbl_v = QLabel(nilai)
        lbl_v.setStyleSheet(f'color:{warna}; font-size:20px; font-weight:700;')
        lbl_v.setObjectName(f'stat_{judul.replace(" ", "_")}')
        layout.addWidget(lbl_v)

        lbl_j = QLabel(judul)
        lbl_j.setStyleSheet('color:#64748b; font-size:11px;')
        layout.addWidget(lbl_j)
        return frame

    def _set_kartu(self, judul, nilai):
        lbl = self.findChild(QLabel, f'stat_{judul.replace(" ", "_")}')
        if lbl:
            lbl.setText(nilai)

    def render_line(self, labels, values, judul='Pendapatan Harian (Rp)'):
        self.chart_line.clear()
        ax = self.chart_line.fig.add_subplot(111)
        if not values:
            ax.text(0.5, 0.5, 'Belum ada data', ha='center', va='center', color='#94a3b8')
        else:
            ax.plot(labels, values, color=BIRU, linewidth=2.4,
                    marker='o', markersize=5, markerfacecolor=BIRU2, zorder=3)
            ax.fill_between(range(len(values)), values, alpha=0.08, color=BIRU)
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=30, ha='right', fontsize=8)
            ax.yaxis.set_major_formatter(
                plt.FuncFormatter(lambda x, _: f'Rp {x/1000:.0f}k' if x >= 1000 else f'Rp {x:.0f}')
            )
        ax.set_title(judul, fontsize=11, pad=10, color='#0f172a', fontweight='bold')
        _style_ax(ax, self.chart_line.fig)
        self.chart_line.draw()

    def render_bar_pc(self, labels, values):
        self.chart_bar_pc.clear()
        ax = self.chart_bar_pc.fig.add_subplot(111)
        if not values:
            ax.text(0.5, 0.5, 'Belum ada data', ha='center', va='center', color='#94a3b8')
        else:
            bars = ax.bar(labels, values, color=BIRU2, width=0.6,
                          zorder=3, edgecolor='white', linewidth=0.5)
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width() / 2, height + 0.1,
                            str(int(height)), ha='center', va='bottom',
                            fontsize=8, color='#64748b')
            plt.setp(ax.get_xticklabels(), rotation=20, ha='right', fontsize=8)
        ax.set_title('Sesi per Komputer', fontsize=11, pad=10,
                     color='#0f172a', fontweight='bold')
        _style_ax(ax, self.chart_bar_pc.fig)
        self.chart_bar_pc.draw()

    def render_pie(self, labels, values):
        self.chart_pie.clear()
        ax = self.chart_pie.fig.add_subplot(111)
        if not values or sum(values) == 0:
            ax.text(0.5, 0.5, 'Belum ada data', ha='center', va='center', color='#94a3b8')
        else:
            wedges, texts, autotexts = ax.pie(
                values,
                labels=labels,
                autopct='%1.1f%%',
                colors=PALETTE[:len(values)],
                startangle=90,
                pctdistance=0.78,
                wedgeprops=dict(linewidth=2, edgecolor='white'),
            )
            for text in texts:
                text.set_color('#64748b')
                text.set_fontsize(9)
            for auto_text in autotexts:
                auto_text.set_color('white')
                auto_text.set_fontsize(8)
                auto_text.set_fontweight('bold')
        ax.set_title('Metode Pembayaran', fontsize=11, pad=10,
                     color='#0f172a', fontweight='bold')
        self.chart_pie.fig.patch.set_facecolor(BG)
        self.chart_pie.draw()

    def render_bar_jam(self, labels, values):
        self.chart_bar_jam.clear()
        ax = self.chart_bar_jam.fig.add_subplot(111)
        if not values:
            ax.text(0.5, 0.5, 'Belum ada data', ha='center', va='center', color='#94a3b8')
        else:
            colors = [BIRU if value == max(values) else '#93c5fd' for value in values]
            ax.bar(labels, values, color=colors, width=0.6,
                   zorder=3, edgecolor='white', linewidth=0.5)
            plt.setp(ax.get_xticklabels(), fontsize=8)
        ax.set_title('Distribusi Sesi per Jam', fontsize=11, pad=10,
                     color='#0f172a', fontweight='bold')
        _style_ax(ax, self.chart_bar_jam.fig)
        self.chart_bar_jam.draw()

    def update_ringkasan(self, total, sesi, rata, jam_sibuk):
        self._set_kartu('Total Pendapatan', f'Rp {total:,.0f}')
        self._set_kartu('Total Sesi', str(sesi))
        self._set_kartu('Rata-rata/Sesi', f'Rp {rata:,.0f}')
        self._set_kartu('Jam Tersibuk', jam_sibuk)
