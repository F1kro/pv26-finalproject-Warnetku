import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QDialogButtonBox, QMessageBox
)


class DialogTambahKomputer(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle('Tambah Komputer' if data is None else 'Edit Komputer')
        self.setMinimumWidth(320)
        self._bangun_ui(data)

    def _bangun_ui(self, data):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        form = QFormLayout()
        form.setSpacing(8)

        self.input_nama  = QLineEdit()
        self.input_nama.setPlaceholderText('Contoh: PC-13')
        self.input_spek  = QLineEdit()
        self.input_spek.setPlaceholderText('Contoh: Core i5, RAM 8GB, GTX 1050')

        form.addRow('Nama :', self.input_nama)
        form.addRow('Spesifikasi :', self.input_spek)
        layout.addLayout(form)

        if data:
            self.input_nama.setText(data.get('nama', ''))
            self.input_spek.setText(data.get('spesifikasi', ''))

        tombol = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        tombol.accepted.connect(self._validasi)
        tombol.rejected.connect(self.reject)
        layout.addWidget(tombol)

    def _validasi(self):
        if not self.input_nama.text().strip():
            QMessageBox.warning(self, 'Peringatan', 'Nama komputer wajib diisi!')
            return
        self.accept()

    def ambil_data(self):
        return {
            'nama':        self.input_nama.text().strip(),
            'spesifikasi': self.input_spek.text().strip(),
        }
