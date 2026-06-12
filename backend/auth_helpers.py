"""Session helper functions."""

from __future__ import annotations

from flask import session

from backend.services.database import get_user_by_id


def get_current_user() -> dict | None:
    user_id = session.get("user_id")
    return get_user_by_id(user_id) if user_id else None

