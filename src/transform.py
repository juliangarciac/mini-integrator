import re
from datetime import datetime, timezone

_space_re = re.compile(r"\s+")
_multi_nl_re = re.compile(r"\n{2,}")


def now_iso_utc() -> str:
    # SQLite friendly ISO string
    return datetime.now(timezone.utc).isoformat()


def norm_text(s: str | None) -> str:
    s = (s or "").strip()
    s = _space_re.sub(" ", s)
    return s


def norm_lower(s: str | None) -> str:
    return norm_text(s).lower()


def clean_body(s: str | None) -> str:
    s = (s or "").strip()
    s = _multi_nl_re.sub("\n", s)
    s = _space_re.sub(" ", s)
    return s


def map_user(source: str, u: dict) -> dict:
    address = u.get("address") or {}
    return {
        "source": source,
        "external_id": int(u["id"]),
        "full_name": norm_text(u.get("name")),
        "username": u.get("username"),
        "username_norm": norm_lower(u.get("username")),
        "email": u.get("email"),
        "email_norm": norm_lower(u.get("email")),
        "city": address.get("city"),
        "synced_at": now_iso_utc(),
        "raw_payload": u,  # se serializa a JSON en repository
    }


def map_post(source: str, p: dict) -> dict:
    return {
        "source": source,
        "external_id": int(p["id"]),
        "external_user_id": int(p["userId"]),
        "title": p.get("title"),
        "title_norm": norm_lower(p.get("title")),
        "body_clean": clean_body(p.get("body")),
        "synced_at": now_iso_utc(),
        "raw_payload": p,  # se serializa a JSON en repository
    }