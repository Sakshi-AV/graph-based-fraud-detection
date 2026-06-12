"""Page and static asset routes."""

from __future__ import annotations

from flask import Blueprint, send_from_directory, session

from backend.config import GRAPH_DIR, PAGES_DIR, STATIC_DIR, VENDOR_DIR


pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def home():
    if not session.get("user_id"):
        return send_from_directory(PAGES_DIR, "login.html"), 302, {"Location": "/login"}
    return send_from_directory(PAGES_DIR, "index.html")


@pages_bp.route("/admin")
def admin():
    return send_from_directory(PAGES_DIR, "admin.html")


@pages_bp.route("/login")
def login_page():
    return send_from_directory(PAGES_DIR, "login.html")


@pages_bp.route("/register")
def register_page():
    return send_from_directory(PAGES_DIR, "register.html")


@pages_bp.route("/user-dashboard")
def user_dashboard_page():
    if not session.get("user_id"):
        return send_from_directory(PAGES_DIR, "login.html"), 302, {"Location": "/login"}
    return send_from_directory(PAGES_DIR, "user-dashboard.html")


@pages_bp.route("/graph")
def graph_page():
    return send_from_directory(GRAPH_DIR, "graph.html")


@pages_bp.route("/static/<path:filename>")
def frontend_static(filename: str):
    return send_from_directory(STATIC_DIR, filename)


@pages_bp.route("/lib/<path:filename>")
def vendor_assets(filename: str):
    return send_from_directory(VENDOR_DIR, filename)
