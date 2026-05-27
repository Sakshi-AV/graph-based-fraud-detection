"""Flask backend connecting the frontend to the trained fraud model."""

from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory, session

from app.anomaly import TransactionAnomalyDetector
from app.database import (
    authenticate_user,
    create_alert,
    create_user,
    get_top_risky_accounts,
    get_user_by_id,
    get_user_metrics,
    init_db,
    list_alerts,
    list_transactions,
    save_transaction,
)
from app.graph_visualizer import export_graph_html
from src.predict import initialize_graph, load_prediction_artifacts, predict_transaction


PROJECT_ROOT = Path(__file__).resolve().parent
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "GraphAdmin#2026"

app = Flask(__name__, static_folder=str(PROJECT_ROOT), static_url_path="")
app.secret_key = "dev-graph-fraud-session-key"

# Avoid startup failure when the training dataset is not present.
# UI/ML logic is unchanged; we only make graph initialization resilient.
DATASET_PATH = PROJECT_ROOT / "paysim_dataset.csv"


TRANSACTION_HISTORY: list[dict] = []
MODEL = None
FEATURE_COLUMNS = None
FRAUD_THRESHOLD = None
TRANSACTION_GRAPH = None
ANOMALY_DETECTOR = TransactionAnomalyDetector()


def load_runtime_artifacts() -> None:
    """Load model artifacts and the starter graph once for the web app."""
    global MODEL, FEATURE_COLUMNS, FRAUD_THRESHOLD, TRANSACTION_GRAPH

    if MODEL is None or FEATURE_COLUMNS is None or FRAUD_THRESHOLD is None:
        MODEL, FEATURE_COLUMNS, FRAUD_THRESHOLD = load_prediction_artifacts()

    if TRANSACTION_GRAPH is None:
        # If the training dataset is missing, keep the API usable by creating an empty graph.
        # This does not change ML/UI logic—only prevents startup/runtime crashes.
        try:
            TRANSACTION_GRAPH = initialize_graph(dataset_path=DATASET_PATH)
        except FileNotFoundError:
            import networkx as nx

            TRANSACTION_GRAPH = nx.DiGraph()


    init_db()


@app.route("/")
def home():
    return send_from_directory(PROJECT_ROOT, "index.html")


@app.route("/admin")
def admin():
    return send_from_directory(PROJECT_ROOT, "admin.html")


@app.route("/login")
def login_page():
    return send_from_directory(PROJECT_ROOT, "login.html")


@app.route("/register")
def register_page():
    return send_from_directory(PROJECT_ROOT, "register.html")


@app.route("/user-dashboard")
def user_dashboard_page():
    return send_from_directory(PROJECT_ROOT, "user-dashboard.html")


@app.route("/graph")
def graph_page():
    return send_from_directory(PROJECT_ROOT / "graph", "graph.html")


@app.route("/<path:filename>")
def static_files(filename: str):
    return send_from_directory(PROJECT_ROOT, filename)


@app.post("/api/predict")
def predict():
    """Predict fraud probability for a submitted transaction."""
    load_runtime_artifacts()
    payload = request.get_json(silent=True) or {}
    current_user = get_current_user()

    sender = current_user["account_id"] if current_user else str(payload.get("sender", "")).strip()
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
        threshold=FRAUD_THRESHOLD,
    )

    anomaly_result = ANOMALY_DETECTOR.score(amount)
    ANOMALY_DETECTOR.add_amount(amount)
    adjusted_probability = adjust_runtime_probability(
        model_probability=result["fraud_probability"],
        sender=sender,
        amount=amount,
        transaction_type=transaction_type,
        is_anomaly=bool(anomaly_result["is_anomaly"]),
    )
    adjusted_prediction = int(adjusted_probability > result["threshold"])
    risk_score = round(adjusted_probability * 100, 2)

    transaction = save_transaction(
        user_id=current_user["id"] if current_user else None,
        sender=sender,
        receiver=receiver,
        amount=amount,
        transaction_type=transaction_type,
        probability=adjusted_probability,
        prediction=adjusted_prediction,
        anomaly_score=float(anomaly_result["anomaly_score"]),
    )

    alerts = generate_alerts(transaction, bool(anomaly_result["is_anomaly"]))
    risky_accounts = get_risky_accounts()
    export_graph_html(TRANSACTION_GRAPH, risky_accounts=risky_accounts)

    response = format_transaction(transaction)
    response["risk_score"] = risk_score
    response["alerts"] = alerts
    response["threshold"] = result["threshold"]

    return jsonify(response)


@app.post("/api/register")
def register_user():
    payload = request.get_json(silent=True) or {}
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", ""))

    if len(username) < 3 or len(password) < 6:
        return jsonify({"error": "Username must be 3+ chars and password must be 6+ chars."}), 400

    ok, message, user = create_user(username, password)
    if not ok:
        return jsonify({"error": message}), 409

    session["user_id"] = user["id"]
    return jsonify({"registered": True, "user": public_user(user)})


@app.post("/api/login")
def login_user():
    payload = request.get_json(silent=True) or {}
    user = authenticate_user(
        str(payload.get("username", "")).strip(),
        str(payload.get("password", "")),
    )

    if not user:
        return jsonify({"error": "Invalid username or password."}), 401

    session["user_id"] = user["id"]
    return jsonify({"authenticated": True, "user": public_user(user)})


@app.post("/api/logout")
def logout_user():
    session.pop("user_id", None)
    return jsonify({"authenticated": False})


@app.get("/api/user/status")
def user_status():
    user = get_current_user()
    return jsonify({"authenticated": bool(user), "user": public_user(user) if user else None})


@app.get("/api/user/dashboard")
def user_dashboard():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User login required"}), 401

    transactions = list_transactions(user_id=user["id"])
    flagged = sum(1 for transaction in transactions if transaction["prediction"] == 1)
    average_probability = (
        sum(transaction["probability"] for transaction in transactions) / len(transactions)
        if transactions
        else 0
    )

    return jsonify({
        "user": public_user(user),
        "transactions": [format_transaction(transaction) for transaction in transactions],
        "metrics": {
            "total": len(transactions),
            "flagged": flagged,
            "personal_risk": round(average_probability * 100, 2),
        },
    })


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


def get_current_user() -> dict | None:
    user_id = session.get("user_id")
    return get_user_by_id(user_id) if user_id else None


def public_user(user: dict | None) -> dict | None:
    if not user:
        return None

    return {
        "id": user["id"],
        "username": user["username"],
        "account_id": user["account_id"],
        "created_at": user["created_at"],
    }


def format_transaction(transaction: dict) -> dict:
    probability = float(transaction["probability"])
    return {
        "id": transaction["id"],
        "timestamp": transaction["created_at"],
        "sender": transaction["sender"],
        "receiver": transaction["receiver"],
        "amount": transaction["amount"],
        "type": transaction["transaction_type"],
        "fraud_prediction": transaction["prediction"],
        "fraud_probability": probability,
        "risk_score": round(probability * 100, 2),
        "anomaly_score": transaction.get("anomaly_score", 0),
        "username": transaction.get("username"),
    }


def generate_alerts(transaction: dict, is_anomaly: bool) -> list[dict]:
    alerts = []

    if transaction["prediction"] == 1:
        alerts.append({
            "type": "High-risk transaction detected",
            "message": f"{transaction['sender']} sent {transaction['amount']:.2f} to {transaction['receiver']}.",
            "severity": "high",
        })

    if is_anomaly or transaction["amount"] >= 250000:
        alerts.append({
            "type": "Large transaction anomaly",
            "message": f"Amount {transaction['amount']:.2f} is unusual for recent runtime activity.",
            "severity": "medium",
        })

    sender_count = sum(1 for item in list_transactions(limit=50) if item["sender"] == transaction["sender"])
    if sender_count >= 3:
        alerts.append({
            "type": "Suspicious account cluster",
            "message": f"{transaction['sender']} has repeated transaction activity.",
            "severity": "medium",
        })

    for alert in alerts:
        create_alert(
            alert_type=alert["type"],
            message=alert["message"],
            severity=alert["severity"],
            transaction_id=transaction["id"],
            account_id=transaction["sender"],
        )

    return alerts


def adjust_runtime_probability(
    model_probability: float,
    sender: str,
    amount: float,
    transaction_type: str,
    is_anomaly: bool,
) -> float:
    """Blend model probability with runtime graph/anomaly signals."""
    runtime_probability = 0.0

    if amount >= 500000:
        runtime_probability += 0.32
    elif amount >= 100000:
        runtime_probability += 0.18

    if transaction_type in {"TRANSFER", "CASH_OUT"}:
        runtime_probability += 0.12

    if is_anomaly:
        runtime_probability += 0.18

    sender_count = sum(1 for item in list_transactions(limit=50) if item["sender"] == sender)
    if sender_count >= 3:
        runtime_probability += 0.12

    return min(0.99, max(float(model_probability), runtime_probability))


def get_risky_accounts() -> set[str]:
    transactions = list_transactions(limit=500)
    return {
        transaction["sender"]
        for transaction in transactions
        if transaction["prediction"] == 1 or transaction["probability"] > 0.20
    }


if __name__ == "__main__":
    load_runtime_artifacts()
    app.run(debug=True, use_reloader=False)
