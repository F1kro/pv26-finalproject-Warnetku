import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

matplotlib.rcParams["font.family"] = "DejaVu Sans"

BG    = "#ffffff"
GRID  = "#f0ede6"
KUNING = "#f5c800"
HITAM  = "#1a1a1a"
HIJAU  = "#4ade80"
MERAH  = "#f87171"
ABU    = "#888888"
UNGU   = "#a78bfa"
PALETTE = [KUNING, HIJAU, MERAH, UNGU, "#60a5fa", "#fb923c"]


def _style_ax(ax, fig):
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.tick_params(colors=HITAM, labelsize=8)
    ax.xaxis.label.set_color(HITAM)
    ax.yaxis.label.set_color(HITAM)
    ax.title.set_color(HITAM)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(HITAM)
        spine.set_linewidth(1.5)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8, linestyle="--")
    ax.set_axisbelow(True)
    ax.xaxis.grid(False)


class KartuStat(QFrame):
    def __init__(self, judul, nilai="-", warna_aksen="#1a1a1a", kode=""):
        super().__init__()
        self.setObjectName("card")
        self.setMinimumWidth(140)
        self.setFixedHeight(88)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)

        if kode:
            lbl_kode = QLabel(kode)
            lbl_kode.setFixedSize(42, 20)
            lbl_kode.setAlignment(Qt.AlignCenter)
            lbl_kode.setObjectName("pillIcon")
            layout.addWidget(lbl_kode)

        self.lbl_nilai = QLabel(nilai)
        self.lbl_nilai.setStyleSheet(
            f"color:{warna_aksen}; font-size:20px; font-weight:900;"
        )
        layout.addWidget(self.lbl_nilai)

        lbl_judul = QLabel(judul)
        lbl_judul.setStyleSheet("color:#666666; font-size:10px; font-weight:700;")
        layout.addWidget(lbl_judul)

    def set_nilai(self, nilai):
        self.lbl_nilai.setText(nilai)


class ChartCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.fig = Figure(tight_layout=True)
        self.fig.patch.set_facecolor(BG)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setStyleSheet("background-color: #ffffff;")
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.canvas)

    def clear(self):
        self.fig.clear()

    def draw(self):
        self.canvas.draw()


class DashboardView(QWidget):
    minta_refresh = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._bangun_ui()

    def _bangun_ui(self):
        # Root layout — scroll area agar tidak terpotong
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

        inner = QWidget()
        scroll.setWidget(inner)

        root = QVBoxLayout(inner)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        # --- Header ---
        header = QHBoxLayout()
        header.setSpacing(8)

        col_judul = QVBoxLayout()
        col_judul.setSpacing(2)
        lbl_judul = QLabel("Overview")
        lbl_judul.setObjectName("judulModul")
        lbl_sub = QLabel("Ringkasan operasional, pendapatan, dan performa booking")
        lbl_sub.setObjectName("subJudul")
        col_judul.addWidget(lbl_judul)
        col_judul.addWidget(lbl_sub)
        header.addLayout(col_judul)
        header.addStretch()

        self.combo_periode = QComboBox()
        self.combo_periode.addItems(["7 Hari Terakhir", "30 Hari Terakhir", "Semua"])
        self.combo_periode.setFixedWidth(150)
        self.combo_periode.setFixedHeight(32)
        self.combo_periode.currentIndexChanged.connect(self.minta_refresh.emit)

        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setObjectName("btnRefresh")
        self.btn_refresh.setFixedHeight(32)
        self.btn_refresh.clicked.connect(self.minta_refresh.emit)

        header.addWidget(self.combo_periode)
        header.addWidget(self.btn_refresh)
        root.addLayout(header)

        # --- Hero banner (cuaca + title) ---
        hero = QFrame()
        hero.setObjectName("cardBlue")
        hero.setFixedHeight(100)
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(20, 14, 20, 14)
        hero_layout.setSpacing(0)

        col_hero = QVBoxLayout()
        col_hero.setSpacing(3)
        lbl_hero_title = QLabel("WarnetKu Live Operations")
        lbl_hero_title.setObjectName("heroTitle")
        lbl_hero_sub = QLabel("Status komputer, cuaca, transaksi, dan jam sibuk.")
        lbl_hero_sub.setObjectName("heroSub")
        col_hero.addWidget(lbl_hero_title)
        col_hero.addWidget(lbl_hero_sub)
        hero_layout.addLayout(col_hero)
        hero_layout.addStretch()

        col_cuaca = QVBoxLayout()
        col_cuaca.setSpacing(2)
        col_cuaca.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lbl_cuaca_suhu = QLabel("-- °C")
        self.lbl_cuaca_suhu.setObjectName("weatherTemp")
        self.lbl_cuaca_suhu.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lbl_cuaca_detail = QLabel("Memuat cuaca...")
        self.lbl_cuaca_detail.setObjectName("weatherDetail")
        self.lbl_cuaca_detail.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        col_cuaca.addWidget(self.lbl_cuaca_suhu)
        col_cuaca.addWidget(self.lbl_cuaca_detail)
        hero_layout.addLayout(col_cuaca)
        root.addWidget(hero)

        # --- Kartu operasional ---
        baris_op = QHBoxLayout()
        baris_op.setSpacing(10)
        self.kartu_pendapatan = KartuStat("Pendapatan Hari Ini", "Rp 0", "#059669", "SALES")
        self.kartu_aktif      = KartuStat("Sesi Aktif",          "0",     "#f5c800", "LIVE")
        self.kartu_kosong     = KartuStat("PC Tersedia",          "0",     "#4ade80", "READY")
        self.kartu_total_pc   = KartuStat("Total Komputer",       "0",     "#1a1a1a", "UNITS")
        for k in [self.kartu_pendapatan, self.kartu_aktif, self.kartu_kosong, self.kartu_total_pc]:
            baris_op.addWidget(k)
        root.addLayout(baris_op)

        # --- Kartu statistik periode ---
        baris_stat = QHBoxLayout()
        baris_stat.setSpacing(10)
        self.k_total    = KartuStat("Total Pendapatan", "Rp 0", "#1a1a1a", "TOTAL")
        self.k_sesi     = KartuStat("Total Sesi",       "0",    "#059669", "SESI")
        self.k_rata     = KartuStat("Rata-rata/Sesi",   "Rp 0", "#f5c800", "AVG")
        self.k_terlaris = KartuStat("Jam Tersibuk",     "-",    "#f87171", "PEAK")
        for k in [self.k_total, self.k_sesi, self.k_rata, self.k_terlaris]:
            baris_stat.addWidget(k)
        root.addLayout(baris_stat)

        # --- Charts 2 kolom ---
        grid_chart = QHBoxLayout()
        grid_chart.setSpacing(10)

        kiri = QVBoxLayout()
        kiri.setSpacing(10)
        self.chart_line = ChartCard()
        self.chart_line.setMinimumHeight(220)
        kiri.addWidget(self.chart_line)
        self.chart_bar_pc = ChartCard()
        self.chart_bar_pc.setMinimumHeight(200)
        kiri.addWidget(self.chart_bar_pc)

        kanan = QVBoxLayout()
        kanan.setSpacing(10)
        self.chart_pie = ChartCard()
        self.chart_pie.setMinimumHeight(220)
        kanan.addWidget(self.chart_pie)
        self.chart_bar_jam = ChartCard()
        self.chart_bar_jam.setMinimumHeight(200)
        kanan.addWidget(self.chart_bar_jam)

        grid_chart.addLayout(kiri, 3)
        grid_chart.addLayout(kanan, 2)
        root.addLayout(grid_chart)

    # ------------------------------------------------------------------ #
    # Update methods
    # ------------------------------------------------------------------ #

    def update_cuaca(self, data: dict):
        suhu = data.get("suhu", 0)
        kota = data.get("kota", "-")
        desk = data.get("deskripsi", "-")
        rh   = data.get("kelembaban", 0)
        self.lbl_cuaca_suhu.setText(f"{suhu:.0f} °C")
        self.lbl_cuaca_detail.setText(f"{kota}  |  {desk}  |  RH {rh}%")

    def update_pendapatan(self, total: float):
        self.kartu_pendapatan.set_nilai(f"Rp {total:,.0f}")

    def update_sesi_aktif(self, jumlah: int):
        self.kartu_aktif.set_nilai(str(jumlah))

    def update_total_pc(self, total: int, kosong: int):
        self.kartu_total_pc.set_nilai(str(total))
        self.kartu_kosong.set_nilai(str(kosong))

    def update_ringkasan(self, total, sesi, rata, jam_sibuk):
        self.k_total.set_nilai(f"Rp {total:,.0f}")
        self.k_sesi.set_nilai(str(sesi))
        self.k_rata.set_nilai(f"Rp {rata:,.0f}")
        self.k_terlaris.set_nilai(jam_sibuk)

    # ------------------------------------------------------------------ #
    # Chart renders
    # ------------------------------------------------------------------ #

    def render_line(self, labels, values, judul="Pendapatan Harian (Rp)"):
        self.chart_line.clear()
        ax = self.chart_line.fig.add_subplot(111)
        if not values:
            ax.text(0.5, 0.5, "Belum ada data", ha="center", va="center", color=ABU, fontsize=10)
        else:
            ax.plot(labels, values, color=HITAM, linewidth=2,
                    marker="o", markersize=5, markerfacecolor=KUNING,
                    markeredgecolor=HITAM, markeredgewidth=1.5, zorder=3)
            ax.fill_between(range(len(values)), values, alpha=0.1, color=KUNING)
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=8)
            ax.yaxis.set_major_formatter(
                plt.FuncFormatter(lambda x, _: f"Rp {x/1000:.0f}k" if x >= 1000 else f"Rp {x:.0f}")
            )
        ax.set_title(judul, fontsize=10, pad=8, color=HITAM, fontweight="bold")
        _style_ax(ax, self.chart_line.fig)
        self.chart_line.draw()

    def render_bar_pc(self, labels, values):
        self.chart_bar_pc.clear()
        ax = self.chart_bar_pc.fig.add_subplot(111)
        if not values:
            ax.text(0.5, 0.5, "Belum ada data", ha="center", va="center", color=ABU, fontsize=10)
        else:
            bars = ax.bar(labels, values, color=KUNING, width=0.6,
                          zorder=3, edgecolor=HITAM, linewidth=1.5)
            for bar in bars:
                h = bar.get_height()
                if h > 0:
                    ax.text(bar.get_x() + bar.get_width() / 2, h + 0.05,
                            str(int(h)), ha="center", va="bottom", fontsize=7, color=HITAM, fontweight="bold")
            plt.setp(ax.get_xticklabels(), rotation=20, ha="right", fontsize=8)
        ax.set_title("Sesi per Komputer", fontsize=10, pad=8, color=HITAM, fontweight="bold")
        _style_ax(ax, self.chart_bar_pc.fig)
        self.chart_bar_pc.draw()

    def render_pie(self, labels, values):
        self.chart_pie.clear()
        ax = self.chart_pie.fig.add_subplot(111)
        if not values or sum(values) == 0:
            ax.text(0.5, 0.5, "Belum ada data", ha="center", va="center", color=ABU, fontsize=10)
        else:
            wedges, texts, autotexts = ax.pie(
                values,
                labels=labels,
                autopct="%1.1f%%",
                colors=PALETTE[: len(values)],
                startangle=90,
                pctdistance=0.78,
                wedgeprops=dict(linewidth=2, edgecolor=HITAM),
            )
            for text in texts:
                text.set_color(HITAM)
                text.set_fontsize(8)
                text.set_fontweight("bold")
            for at in autotexts:
                at.set_color(HITAM)
                at.set_fontsize(8)
                at.set_fontweight("bold")
        ax.set_title("Metode Pembayaran", fontsize=10, pad=8, color=HITAM, fontweight="bold")
        self.chart_pie.fig.patch.set_facecolor(BG)
        self.chart_pie.draw()

    def render_bar_jam(self, labels, values):
        self.chart_bar_jam.clear()
        ax = self.chart_bar_jam.fig.add_subplot(111)
        if not values:
            ax.text(0.5, 0.5, "Belum ada data", ha="center", va="center", color=ABU, fontsize=10)
        else:
            colors = [HITAM if v == max(values) else KUNING for v in values]
            ec = [HITAM] * len(values)
            ax.bar(labels, values, color=colors, width=0.6,
                   zorder=3, edgecolor=ec, linewidth=1.5)
            plt.setp(ax.get_xticklabels(), fontsize=8)
        ax.set_title("Distribusi Sesi per Jam", fontsize=10, pad=8, color=HITAM, fontweight="bold")
        _style_ax(ax, self.chart_bar_jam.fig)
        self.chart_bar_jam.draw()
