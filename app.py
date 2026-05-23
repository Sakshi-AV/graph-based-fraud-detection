"""Flask backend connecting the frontend to the trained fraud model."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, request, send_from_directory, session

from src.predict import initialize_graph, load_prediction_artifacts, predict_transaction


PROJECT_ROOT = Path(__file__).resolve().parent
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "GraphAdmin#2026"

app = Flask(__name__, static_folder=str(PROJECT_ROOT), static_url_path="")
app.secret_key = "dev-graph-fraud-session-key"

TRANSACTION_HISTORY: list[dict] = []
MODEL = None
FEATURE_COLUMNS = None
TRANSACTION_GRAPH = None


def load_runtime_artifacts() -> None:
    """Load model artifacts and the starter graph once for the web app."""
    global MODEL, FEATURE_COLUMNS, TRANSACTION_GRAPH

    if MODEL is None or FEATURE_COLUMNS is None:
        MODEL, FEATURE_COLUMNS = load_prediction_artifacts()

    if TRANSACTION_GRAPH is None:
        TRANSACTION_GRAPH = initialize_graph()


@app.route("/")
def home():
    return send_from_directory(PROJECT_ROOT, "index.html")


@app.route("/admin")
def admin():
    return send_from_directory(PROJECT_ROOT, "admin.html")


@app.route("/<path:filename>")
def static_files(filename: str):
    return send_from_directory(PROJECT_ROOT, filename)


@app.post("/api/predict")
def predict():
    """Predict fraud probability for a submitted transaction."""
    load_runtime_artifacts()
    payload = request.get_json(silent=True) or {}

    sender = str(payload.get("sender", "")).strip()
    receiver = str(payload.get("receiver", "")).strip()
    transaction_type = str(payload.get("type", "PAYMENT")).strip().upper()

    try:
        amount = float(payload.get("amount", 0))
    except (TypeError, ValueError):
        amount = 0.0

    if not sender or not receiver or amount <= 0:
        return jsonify({"error": "sender, receiver, and positive amount are required"}), 400

    result = predict_transaction(
        sender=sender,
        receiver=receiver,
        amount=amount,
        transaction_type=transaction_type,
        graph=TRANSACTION_GRAPH,
        model=MODEL,
        feature_columns=FEATURE_COLUMNS,
    )

    risk_score = round(result["fraud_probability"] * 100, 2)
    record = {
        "id": str(uuid4())[:8],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sender": sender,
        "receiver": receiver,
        "amount": amount,
        "type": transaction_type,
        "fraud_prediction": result["fraud_prediction"],
        "fraud_probability": result["fraud_probability"],
        "risk_score": risk_score,
    }
    TRANSACTION_HISTORY.insert(0, record)

    return jsonify(record)


@app.post("/api/admin/login")
def admin_login():
    payload = request.get_json(silent=True) or {}
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", ""))

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session["is_admin"] = True
        return jsonify({"authenticated": True})

    return jsonify({"authenticated": False, "error": "Invalid admin credentials"}), 401


@app.post("/api/admin/logout")
def admin_logout():
    session.clear()
    return jsonify({"authenticated": False})


@app.get("/api/admin/status")
def admin_status():
    return jsonify({"authenticated": bool(session.get("is_admin"))})


@app.get("/api/admin/transactions")
def admin_transactions():
    if not session.get("is_admin"):
        return jsonify({"error": "Admin login required"}), 401

    total = len(TRANSACTION_HISTORY)
    flagged = sum(1 for transaction in TRANSACTION_HISTORY if transaction["fraud_prediction"] == 1)
    average_risk = (
        round(sum(transaction["risk_score"] for transaction in TRANSACTION_HISTORY) / total, 2)
        if total
        else 0
    )

    return jsonify({
        "transactions": TRANSACTION_HISTORY,
        "metrics": {
            "total": total,
            "flagged": flagged,
            "average_risk": average_risk,
        },
    })


if __name__ == "__main__":
    load_runtime_artifacts()
    app.run(debug=True, use_reloader=False)
