"""JSON presenter helpers shared by API routes."""

from __future__ import annotations


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

