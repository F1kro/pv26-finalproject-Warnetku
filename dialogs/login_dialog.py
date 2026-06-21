import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame,
)
from models import user_model
from models import auth_state
from config import NAMA_WARNET


class DialogLogin(QDialog):
    def __init__(self):
        super().__init__(None)
        self.setWindowTitle(f'Login — {NAMA_WARNET}')
        self.setFixedWidth(360)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self._bangun_ui()

    def _bangun_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet('background:#1a1a1a;')
        header.setFixedHeight(64)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(20, 0, 20, 0)
        lbl_title = QLabel(NAMA_WARNET)
        lbl_title.setStyleSheet('color:#f5c800; font-size:20px; font-weight:900;')
        lbl_sub = QLabel('Management System')
        lbl_sub.setStyleSheet('color:#888; font-size:11px;')
        col = QVBoxLayout()
        col.setSpacing(2)
        col.addWidget(lbl_title)
        col.addWidget(lbl_sub)
        hl.addLayout(col)
        layout.addWidget(header)

        # Body
        body = QFrame()
        body.setStyleSheet('background:#f5f0e8;')
        bl = QVBoxLayout(body)
        bl.setContentsMargins(24, 24, 24, 24)
        bl.setSpacing(12)

        lbl_login = QLabel('Silakan Login')
        lbl_login.setStyleSheet('font-size:15px; font-weight:900; color:#1a1a1a;')
        bl.addWidget(lbl_login)

        # Username
        lbl_u = QLabel('Username')
        lbl_u.setStyleSheet('font-size:11px; font-weight:700; color:#666;')
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText('')
        bl.addWidget(lbl_u)
        bl.addWidget(self.input_username)

        # Password
        lbl_p = QLabel('Password')
        lbl_p.setStyleSheet('font-size:11px; font-weight:700; color:#666;')
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText('')
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.returnPressed.connect(self._coba_login)
        bl.addWidget(lbl_p)
        bl.addWidget(self.input_password)

        # Error label
        self.lbl_error = QLabel('')
        self.lbl_error.setStyleSheet(
            'color:#1a1a1a; background:#f87171; border:2px solid #1a1a1a;'
            'padding:6px 10px; font-weight:800; font-size:11px;'
        )
        self.lbl_error.setVisible(False)
        self.lbl_error.setWordWrap(True)
        bl.addWidget(self.lbl_error)

        # Tombol login
        self.btn_login = QPushButton('Login')
        self.btn_login.setFixedHeight(38)
        self.btn_login.setStyleSheet(
            'QPushButton { background-color: #f5c800; color: #1a1a1a; border: 2px solid #1a1a1a;'
            '  border-radius: 0px; font-size: 13px; font-weight: 900; min-height: 38px; max-height: 38px; }'
            'QPushButton:hover { background-color: #e6b800; border-bottom: 4px solid #1a1a1a; border-right: 4px solid #1a1a1a; }'
            'QPushButton:pressed { background-color: #ccaa00; border: 2px solid #1a1a1a; }'
        )
        self.btn_login.clicked.connect(self._coba_login)
        bl.addWidget(self.btn_login)



        layout.addWidget(body)

    def _coba_login(self):
        username = self.input_username.text().strip()
        password = self.input_password.text()

        if not username or not password:
            self._show_error('Username dan password wajib diisi.')
            return

        user = user_model.login(username, password)
        if user:
            auth_state.set_user(user)
            self.accept()
        else:
            self._show_error('Username atau password salah.')
            self.input_password.clear()
            self.input_password.setFocus()

    def _show_error(self, pesan: str):
        self.lbl_error.setText(f'✗  {pesan}')
        self.lbl_error.setVisible(True)


