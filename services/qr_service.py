import sys, os, io, uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import qrcode
from qrcode.image.pil import PilImage
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt

def buat_qr_pixmap(data: str, ukuran: int = 220) -> QPixmap:
    """Generate QR code dari string data, return QPixmap siap tampil di QLabel."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img: PilImage = qr.make_image(fill_color='black', back_color='white')

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    raw = buf.read()

    qt_img = QImage.fromData(raw)
    pix = QPixmap.fromImage(qt_img).scaled(
        ukuran, ukuran,
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation,
    )
    return pix

def buat_data_qris_simulasi(order_id: str, jumlah: int, nama_warnet: str) -> str:
    """
    Buat string payload QRIS simulasi (format EMV QRIS sederhana).
    Format payload QRIS offline.
    """
    payload = (
        f"WARNETKU-PAYMENT\n"
        f"Order  : {order_id}\n"
        f"Warnet : {nama_warnet}\n"
        f"Total  : Rp {jumlah:,}\n"
        f"Status : SIMULASI"
    )
    return payload

def generate_order_id(komputer_nama: str) -> str:
    return f'WARNET-{komputer_nama}-{uuid.uuid4().hex[:8].upper()}'
