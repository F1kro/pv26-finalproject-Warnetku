import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from database.db_manager import koneksi
from datetime import datetime

def catat_transaksi(sesi_id, jumlah, metode='Tunai', order_id=None, status='lunas'):
    now  = datetime.now().isoformat(timespec='seconds')
    conn = koneksi()
    conn.execute(
        'INSERT INTO transaksi (sesi_id, waktu, jumlah, metode, status, order_id) VALUES (?,?,?,?,?,?)',
        (sesi_id, now, jumlah, metode, status, order_id)
    )
    conn.commit()
    conn.close()

def ambil_hari_ini():
    conn  = koneksi()
    today = datetime.now().strftime('%Y-%m-%d')
    rows  = conn.execute(
        """SELECT t.id, t.sesi_id, t.waktu, t.jumlah, t.metode, t.status, t.order_id,
                  s.nama_pelanggan, s.paket, s.durasi_menit,
                  k.nama as nama_komputer,
                  u.nama as nama_kasir
           FROM transaksi t
           JOIN sesi s ON t.sesi_id = s.id
           JOIN komputer k ON s.komputer_id = k.id
           LEFT JOIN user u ON s.kasir_id = u.id
           WHERE DATE(t.waktu) = ?
           ORDER BY t.waktu DESC""",
        (today,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def ambil_rentang(tgl_mulai, tgl_selesai):
    conn = koneksi()
    rows = conn.execute(
        """SELECT t.id, t.sesi_id, t.waktu, t.jumlah, t.metode, t.status, t.order_id,
                  s.nama_pelanggan, s.paket, s.durasi_menit,
                  k.nama as nama_komputer,
                  u.nama as nama_kasir
           FROM transaksi t
           JOIN sesi s ON t.sesi_id = s.id
           JOIN komputer k ON s.komputer_id = k.id
           LEFT JOIN user u ON s.kasir_id = u.id
           WHERE DATE(t.waktu) BETWEEN ? AND ?
           ORDER BY t.waktu DESC""",
        (tgl_mulai, tgl_selesai)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def total_hari_ini():
    conn  = koneksi()
    today = datetime.now().strftime('%Y-%m-%d')
    row   = conn.execute(
        "SELECT COALESCE(SUM(jumlah),0) FROM transaksi WHERE DATE(waktu)=? AND status='lunas'",
        (today,)
    ).fetchone()
    conn.close()
    return row[0]

def pendapatan_per_kasir(tgl_mulai, tgl_selesai) -> list:
    conn = koneksi()
    rows = conn.execute(
        """SELECT COALESCE(u.nama, 'Tidak Diketahui') as nama_kasir,
                  SUM(t.jumlah) as total
           FROM transaksi t
           JOIN sesi s ON t.sesi_id = s.id
           LEFT JOIN user u ON s.kasir_id = u.id
           WHERE DATE(t.waktu) BETWEEN ? AND ?
             AND t.status = 'lunas'
           GROUP BY s.kasir_id
           ORDER BY total DESC""",
        (tgl_mulai, tgl_selesai)
    ).fetchall()
    conn.close()
    return [(r['nama_kasir'], r['total']) for r in rows]

def statistik_rentang(tgl_mulai, tgl_selesai) -> dict:
    conn = koneksi()
    row = conn.execute(
        """SELECT COALESCE(SUM(jumlah),0) as total, COUNT(*) as jml
           FROM transaksi
           WHERE DATE(waktu) BETWEEN ? AND ? AND status='lunas'""",
        (tgl_mulai, tgl_selesai)
    ).fetchone()
    total = row['total']
    jml   = row['jml']
    rata  = total / jml if jml else 0

    row_jam = conn.execute(
        """SELECT strftime('%H:00', waktu) as jam, COUNT(*) as cnt
           FROM transaksi
           WHERE DATE(waktu) BETWEEN ? AND ?
           GROUP BY jam ORDER BY cnt DESC LIMIT 1""",
        (tgl_mulai, tgl_selesai)
    ).fetchone()
    jam_sibuk = row_jam['jam'] if row_jam else '-'
    conn.close()
    return {'total': total, 'jml': jml, 'rata': rata, 'jam_sibuk': jam_sibuk}
