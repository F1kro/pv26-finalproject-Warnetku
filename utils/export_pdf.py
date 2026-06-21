import os
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False


def export_transaksi(data: list, path: str, nama_warnet='WarnetKu') -> tuple:
    """
    Export transaksi ke PDF menggunakan ReportLab.
    Return (sukses: bool, pesan: str)
    """
    if not REPORTLAB_OK:
        return False, 'ReportLab belum terinstall. Jalankan: pip install reportlab'

    try:
        doc    = SimpleDocTemplate(path, pagesize=A4,
                                   leftMargin=2*cm, rightMargin=2*cm,
                                   topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story  = []

        # judul
        judul_style = ParagraphStyle('judul', parent=styles['Title'], fontSize=16, spaceAfter=6)
        story.append(Paragraph(f'Laporan Transaksi — {nama_warnet}', judul_style))
        story.append(Paragraph(
            f'Dicetak: {datetime.now().strftime("%d %B %Y %H:%M")}',
            styles['Normal']
        ))
        story.append(Spacer(1, 0.5*cm))

        if not data:
            story.append(Paragraph('Tidak ada data transaksi.', styles['Normal']))
        else:
            # header tabel
            header = ['No', 'Waktu', 'Komputer', 'Pelanggan', 'Paket', 'Durasi', 'Metode', 'Total']
            rows   = [header]
            total_pendapatan = 0
            for i, t in enumerate(data, 1):
                rows.append([
                    str(i),
                    str(t.get('waktu', ''))[:16],
                    str(t.get('nama_komputer', '')),
                    str(t.get('nama_pelanggan', '')),
                    str(t.get('paket', '')),
                    f"{t.get('durasi_menit', 0)} mnt",
                    str(t.get('metode', '')),
                    f"Rp {t.get('jumlah', 0):,.0f}",
                ])
                total_pendapatan += t.get('jumlah', 0)

            # baris total
            rows.append(['', '', '', '', '', '', 'TOTAL', f'Rp {total_pendapatan:,.0f}'])

            col_widths = [1*cm, 3.5*cm, 2*cm, 3*cm, 2.5*cm, 2*cm, 2*cm, 3*cm]
            tabel = Table(rows, colWidths=col_widths, repeatRows=1)
            tabel.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a5f')),
                ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
                ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE',   (0,0), (-1,-1), 8),
                ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
                ('ALIGN',      (7,1), (7,-1), 'RIGHT'),
                ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#f0f4f8')]),
                ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#d4edda')),
                ('FONTNAME',   (0,-1), (-1,-1), 'Helvetica-Bold'),
                ('GRID',       (0,0), (-1,-1), 0.4, colors.HexColor('#cccccc')),
                ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(tabel)

        doc.build(story)
        return True, f'PDF disimpan ke {path}'
    except Exception as e:
        return False, str(e)


def nama_file_default(prefix='laporan'):
    tgl = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f'{prefix}_{tgl}.pdf'
