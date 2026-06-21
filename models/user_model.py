import sys, os, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from database.db_manager import koneksi

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def login(username: str, password: str) -> dict | None:
    conn = koneksi()
    row = conn.execute(
        "SELECT * FROM user WHERE username=? AND password=? AND aktif=1",
        (username, _hash(password))
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def ambil_semua() -> list:
    conn = koneksi()
    rows = conn.execute("SELECT * FROM user ORDER BY role, nama").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def ambil_by_id(user_id: int) -> dict | None:
    conn = koneksi()
    row = conn.execute("SELECT * FROM user WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def tambah(username: str, password: str, nama: str, role: str = 'kasir') -> bool:
    try:
        conn = koneksi()
        conn.execute(
            "INSERT INTO user (username, password, nama, role) VALUES (?,?,?,?)",
            (username, _hash(password), nama, role)
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def update(user_id: int, nama: str, username: str, role: str, aktif: int, password: str = None):
    conn = koneksi()
    if password:
        conn.execute(
            "UPDATE user SET nama=?, username=?, role=?, aktif=?, password=? WHERE id=?",
            (nama, username, role, aktif, _hash(password), user_id)
        )
    else:
        conn.execute(
            "UPDATE user SET nama=?, username=?, role=?, aktif=? WHERE id=?",
            (nama, username, role, aktif, user_id)
        )
    conn.commit()
    conn.close()

def hapus(user_id: int):
    conn = koneksi()
    conn.execute("DELETE FROM user WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

def ambil_kasir_aktif() -> list:
    conn = koneksi()
    rows = conn.execute(
        "SELECT * FROM user WHERE role='kasir' AND aktif=1 ORDER BY nama"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
