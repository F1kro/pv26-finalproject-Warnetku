import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from database.db_manager import koneksi


def ambil_semua():
    conn = koneksi()
    rows = conn.execute('SELECT * FROM komputer ORDER BY nama').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def ambil_by_id(id):
    conn = koneksi()
    row  = conn.execute('SELECT * FROM komputer WHERE id=?', (id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def tambah(nama, spesifikasi=''):
    conn = koneksi()
    conn.execute('INSERT INTO komputer (nama, spesifikasi) VALUES (?,?)', (nama, spesifikasi))
    conn.commit()
    conn.close()


def update(id, nama, spesifikasi):
    conn = koneksi()
    conn.execute('UPDATE komputer SET nama=?, spesifikasi=? WHERE id=?', (nama, spesifikasi, id))
    conn.commit()
    conn.close()


def set_status(id, status):
    """status: 'kosong' | 'aktif'"""
    conn = koneksi()
    conn.execute('UPDATE komputer SET status=? WHERE id=?', (status, id))
    conn.commit()
    conn.close()


def hapus(id):
    conn = koneksi()
    conn.execute('DELETE FROM komputer WHERE id=?', (id,))
    conn.commit()
    conn.close()
