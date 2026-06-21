# Singleton session state — simpan user yang sedang login
_user = None

def set_user(user: dict):
    global _user
    _user = user

def get_user() -> dict | None:
    return _user

def logout():
    global _user
    _user = None

def is_owner() -> bool:
    return _user is not None and _user.get("role") == "owner"

def is_kasir() -> bool:
    return _user is not None and _user.get("role") == "kasir"

def get_kasir_id() -> int | None:
    return _user["id"] if _user else None

def get_nama() -> str:
    return _user["nama"] if _user else "?"

def get_role() -> str:
    return _user["role"] if _user else ""
