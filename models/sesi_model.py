import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from database.db_manager import koneksi
from datetime import datetime

def mulai_sesi(komputer_id, nama_pelanggan, paket, kasir_id=None):
    now  = datetime.now().isoformat(timespec='seconds')
    conn = koneksi()
    cur  = conn.cursor()
    cur.execute(
        'INSERT INTO sesi (komputer_id, kasir_id, nama_pelanggan, paket, mulai, status) VALUES (?,?,?,?,?,?)',
        (komputer_id, kasir_id, nama_pelanggan, paket, now, 'aktif')
    )
    sesi_id = cur.lastrowid
    conn.commit()
    conn.close()
    return sesi_id

def selesai_sesi(sesi_id, durasi_menit, biaya):
    now  = datetime.now().isoformat(timespec='seconds')
    conn = koneksi()
    conn.execute(
        'UPDATE sesi SET selesai=?, durasi_menit=?, biaya=?, status=? WHERE id=?',
        (now, durasi_menit, biaya, 'selesai', sesi_id)
    )
    conn.commit()
    conn.close()

def ambil_sesi_aktif(komputer_id):
    conn = koneksi()
    row  = conn.execute(
        "SELECT * FROM sesi WHERE komputer_id=? AND status='aktif' ORDER BY id DESC LIMIT 1",
        (komputer_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def ambil_semua_aktif():
    conn = koneksi()
    rows = conn.execute(
        """SELECT s.*, k.nama as nama_komputer,
                  u.nama as nama_kasir
           FROM sesi s
           JOIN komputer k ON s.komputer_id = k.id
           LEFT JOIN user u ON s.kasir_id = u.id
           WHERE s.status = 'aktif'
           ORDER BY s.mulai"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def ambil_riwayat(tanggal=None):
    conn = koneksi()
    if tanggal:
        rows = conn.execute(
            """SELECT s.*, k.nama as nama_komputer,
                      u.nama as nama_kasir
               FROM sesi s
               JOIN komputer k ON s.komputer_id = k.id
               LEFT JOIN user u ON s.kasir_id = u.id
               WHERE DATE(s.mulai) = ? AND s.status = 'selesai'
               ORDER BY s.mulai DESC""",
            (tanggal,)
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT s.*, k.nama as nama_komputer,
                      u.nama as nama_kasir
               FROM sesi s
               JOIN komputer k ON s.komputer_id = k.id
               LEFT JOIN user u ON s.kasir_id = u.id
               WHERE s.status = 'selesai'
               ORDER BY s.mulai DESC
               LIMIT 500"""
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def reset_semua_aktif():
    now  = datetime.now().isoformat(timespec='seconds')
    conn = koneksi()
    conn.execute(
        "UPDATE sesi SET selesai=?, status='selesai' WHERE status='aktif'",
        (now,)
    )
    conn.execute("UPDATE komputer SET status='kosong'")
    conn.commit()
    conn.close()
