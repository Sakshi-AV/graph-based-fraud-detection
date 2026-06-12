"""Admin authentication and analytics routes."""

from __future__ import annotations

from flask import Blueprint, jsonify, request, session

from backend.config import ADMIN_PASSWORD, ADMIN_USERNAME
from backend.presenters import format_transaction
from backend.services.database import get_top_risky_accounts, get_user_metrics, list_alerts, list_transactions


admin_bp = Blueprint("admin_api", __name__, url_prefix="/api/admin")


@admin_bp.post("/login")
def admin_login():
    payload = request.get_json(silent=True) or {}
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", ""))

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session["is_admin"] = True
        return jsonify({"authenticated": True})

    return jsonify({"authenticated": False, "error": "Invalid admin credentials"}), 401


@admin_bp.post("/logout")
def admin_logout():
    session.clear()
    return jsonify({"authenticated": False})


@admin_bp.get("/status")
def admin_status():
    return jsonify({"authenticated": bool(session.get("is_admin"))})


@admin_bp.get("/transactions")
def admin_transactions():
    if not session.get("is_admin"):
        return jsonify({"error": "Admin login required"}), 401

    transactions = list_transactions()
    total = len(transactions)
    flagged = sum(1 for transaction in transactions if transaction["prediction"] == 1)
    average_risk = (
        round(sum(transaction["probability"] * 100 for transaction in transactions) / total, 2)
        if total
        else 0
    )
    fraud_percentage = round((flagged / total) * 100, 2) if total else 0

    return jsonify({
        "transactions": [format_transaction(transaction) for transaction in transactions],
        "alerts": list_alerts(),
        "top_risky_accounts": get_top_risky_accounts(),
        "metrics": {
            "total": total,
            "flagged": flagged,
            "average_risk": average_risk,
            "fraud_percentage": fraud_percentage,
            **get_user_metrics(),
        },
    })

