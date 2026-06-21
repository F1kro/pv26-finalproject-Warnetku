import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel,
    QLineEdit, QComboBox, QCheckBox, QPushButton,
    QHBoxLayout, QFrame,
)


class DialogUser(QDialog):
    def __init__(self, parent=None, data: dict = None):
        super().__init__(parent)
        self._edit_mode = data is not None
        self._data = data
        self.setWindowTitle('Edit User' if self._edit_mode else 'Tambah User')
        self.setFixedWidth(380)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self._bangun_ui()
        if self._edit_mode:
            self._isi_data(data)

    def _bangun_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        lbl_judul = QLabel('Edit User' if self._edit_mode else 'Tambah User Baru')
        lbl_judul.setObjectName('dialogTitle')
        layout.addWidget(lbl_judul)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignLeft)

        self.input_nama = QLineEdit()
        self.input_nama.setPlaceholderText('Nama lengkap')
        form.addRow('Nama', self.input_nama)

        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText('Username untuk login')
        form.addRow('Username', self.input_username)

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText(
            'Kosongkan jika tidak diubah' if self._edit_mode else 'Password'
        )
        self.input_password.setEchoMode(QLineEdit.Password)
        form.addRow('Password', self.input_password)

        self.combo_role = QComboBox()
        self.combo_role.addItems(['kasir', 'owner'])
        form.addRow('Role', self.combo_role)

        self.chk_aktif = QCheckBox('Akun aktif')
        self.chk_aktif.setChecked(True)
        form.addRow('Status', self.chk_aktif)

        layout.addLayout(form)

        self.lbl_error = QLabel('')
        self.lbl_error.setStyleSheet(
            'color:#1a1a1a; background:#f87171; border:2px solid #1a1a1a;'
            'padding:5px 8px; font-weight:800; font-size:11px;'
        )
        self.lbl_error.setVisible(False)
        self.lbl_error.setWordWrap(True)
        layout.addWidget(self.lbl_error)

        baris = QHBoxLayout()
        baris.setSpacing(8)
        self.btn_simpan = QPushButton('Simpan')
        self.btn_simpan.setObjectName('btnMulai')
        self.btn_simpan.clicked.connect(self._validasi)
        self.btn_batal = QPushButton('Batal')
        self.btn_batal.setObjectName('btnSecondary')
        self.btn_batal.clicked.connect(self.reject)
        baris.addWidget(self.btn_simpan)
        baris.addWidget(self.btn_batal)
        layout.addLayout(baris)

    def _isi_data(self, data: dict):
        self.input_nama.setText(data.get('nama', ''))
        self.input_username.setText(data.get('username', ''))
        idx = self.combo_role.findText(data.get('role', 'kasir'))
        if idx >= 0:
            self.combo_role.setCurrentIndex(idx)
        self.chk_aktif.setChecked(bool(data.get('aktif', 1)))

    def _validasi(self):
        nama     = self.input_nama.text().strip()
        username = self.input_username.text().strip()
        password = self.input_password.text()

        if not nama:
            self.lbl_error.setText('✗  Nama wajib diisi.')
            self.lbl_error.setVisible(True)
            return
        if not username:
            self.lbl_error.setText('✗  Username wajib diisi.')
            self.lbl_error.setVisible(True)
            return
        if not self._edit_mode and not password:
            self.lbl_error.setText('✗  Password wajib diisi untuk user baru.')
            self.lbl_error.setVisible(True)
            return

        self.lbl_error.setVisible(False)
        self.accept()

    def ambil_data(self) -> dict:
        return {
            'nama':     self.input_nama.text().strip(),
            'username': self.input_username.text().strip(),
            'password': self.input_password.text() or None,
            'role':     self.combo_role.currentText(),
            'aktif':    1 if self.chk_aktif.isChecked() else 0,
        }
