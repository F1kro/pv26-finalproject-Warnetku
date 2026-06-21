import sqlite3
import os
import hashlib

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'warnetku.db')

def koneksi():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def inisialisasi():
    conn = koneksi()
    cur  = conn.cursor()

    # tabel user
    cur.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL,
            nama     TEXT    NOT NULL,
            role     TEXT    NOT NULL DEFAULT 'kasir',
            aktif    INTEGER NOT NULL DEFAULT 1
        )
    ''')

    # tabel komputer
    cur.execute('''
        CREATE TABLE IF NOT EXISTS komputer (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nama        TEXT    NOT NULL UNIQUE,
            status      TEXT    NOT NULL DEFAULT 'kosong',
            spesifikasi TEXT    DEFAULT ''
        )
    ''')

    # tabel sesi — tambah kolom kasir_id
    cur.execute('''
        CREATE TABLE IF NOT EXISTS sesi (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            komputer_id    INTEGER NOT NULL,
            kasir_id       INTEGER,
            nama_pelanggan TEXT    NOT NULL DEFAULT 'Umum',
            paket          TEXT    NOT NULL,
            mulai          TEXT    NOT NULL,
            selesai        TEXT,
            durasi_menit   INTEGER DEFAULT 0,
            biaya          REAL    DEFAULT 0,
            status         TEXT    NOT NULL DEFAULT 'aktif',
            FOREIGN KEY (komputer_id) REFERENCES komputer(id),
            FOREIGN KEY (kasir_id)    REFERENCES user(id)
        )
    ''')

    # tabel transaksi
    cur.execute('''
        CREATE TABLE IF NOT EXISTS transaksi (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            sesi_id  INTEGER NOT NULL,
            waktu    TEXT    NOT NULL,
            jumlah   REAL    NOT NULL,
            metode   TEXT    NOT NULL DEFAULT 'Tunai',
            status   TEXT    NOT NULL DEFAULT 'lunas',
            order_id TEXT,
            FOREIGN KEY (sesi_id) REFERENCES sesi(id)
        )
    ''')

    conn.commit()

    # Migrasi: tambah kolom kasir_id ke sesi kalau belum ada
    cols = [r[1] for r in cur.execute("PRAGMA table_info(sesi)").fetchall()]
    if 'kasir_id' not in cols:
        cur.execute("ALTER TABLE sesi ADD COLUMN kasir_id INTEGER")
        conn.commit()

    # Seed owner default kalau belum ada user
    cur.execute("SELECT COUNT(*) FROM user")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO user (username, password, nama, role) VALUES (?,?,?,?)",
            ('owner', _hash_password('owner123'), 'Owner', 'owner')
        )
        conn.commit()

    # Seed komputer awal
    cur.execute('SELECT COUNT(*) FROM komputer')
    if cur.fetchone()[0] == 0:
        _seed_komputer(cur, conn)

    conn.close()

def _seed_komputer(cur, conn):
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from config import JUMLAH_KOMPUTER
    for i in range(1, JUMLAH_KOMPUTER + 1):
        cur.execute(
            'INSERT INTO komputer (nama, status) VALUES (?, ?)',
            (f'PC-{i:02d}', 'kosong')
        )
    conn.commit()
