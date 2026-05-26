"""Baseline Random Forest fraud detection model."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

try:
    from .feature_engineering import add_graph_features
    from .preprocessing import DEFAULT_DATASET_PATH, preprocess_dataset
except ImportError:
    from feature_engineering import add_graph_features
    from preprocessing import DEFAULT_DATASET_PATH, preprocess_dataset


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "model.pkl"
FEATURE_COLUMNS_PATH = PROJECT_ROOT / "models" / "feature_columns.pkl"
MODEL_METADATA_PATH = PROJECT_ROOT / "models" / "model_metadata.pkl"
TARGET_COLUMN = "isFraud"
NON_FEATURE_COLUMNS = {"nameOrig", "nameDest", TARGET_COLUMN}
FRAUD_THRESHOLD = 0.20


def prepare_training_data(dataset_path: str | Path = DEFAULT_DATASET_PATH, nrows: int = 100000) -> tuple[pd.DataFrame, pd.Series]:
    """Create model-ready features and labels from the raw dataset."""
    transactions, _ = preprocess_dataset(dataset_path=dataset_path, nrows=nrows)
    featured_transactions = add_graph_features(transactions)
    balanced_transactions = create_balanced_dataset(featured_transactions)

    y = balanced_transactions[TARGET_COLUMN]
    X = balanced_transactions.drop(columns=[column for column in NON_FEATURE_COLUMNS if column in balanced_transactions.columns])

    return X, y


def create_balanced_dataset(data: pd.DataFrame, random_state: int = 42) -> pd.DataFrame:
    """Balance fraud data with a 1:3 fraud-to-normal sample."""
    fraud = data[data[TARGET_COLUMN] == 1]
    normal = data[data[TARGET_COLUMN] == 0]

    if fraud.empty:
        raise ValueError("No fraud rows found in the training sample.")

    normal_sample_size = min(len(normal), len(fraud) * 3)
    normal_sample = normal.sample(normal_sample_size, random_state=random_state)
    balanced_data = pd.concat([fraud, normal_sample], ignore_index=True)

    return balanced_data.sample(frac=1, random_state=random_state).reset_index(drop=True)


def train_model(X: pd.DataFrame, y: pd.Series) -> RandomForestClassifier:
    """Train a baseline RandomForestClassifier."""
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )
    model.fit(X, y)
    return model


def evaluate_model(model: RandomForestClassifier, X_test: pd.DataFrame, y_test: pd.Series) -> dict[str, float]:
    """Evaluate with precision, recall, and f1-score."""
    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities > FRAUD_THRESHOLD).astype(int)

    metrics = {
        "precision": precision_score(y_test, predictions, zero_division=0),
        "recall": recall_score(y_test, predictions, zero_division=0),
        "f1_score": f1_score(y_test, predictions, zero_division=0),
    }

    print(classification_report(y_test, predictions, zero_division=0))
    print("Confusion matrix:")
    print(confusion_matrix(y_test, predictions))
    return metrics


def save_model(model: RandomForestClassifier, feature_columns: list[str]) -> None:
    """Save the trained model and feature column order for prediction."""
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(feature_columns, FEATURE_COLUMNS_PATH)
    joblib.dump({"fraud_threshold": FRAUD_THRESHOLD}, MODEL_METADATA_PATH)


def train_and_save_model(dataset_path: str | Path = DEFAULT_DATASET_PATH, nrows: int = 100000) -> dict[str, float]:
    """Run the full Week 2 training pipeline and persist the model."""
    X, y = prepare_training_data(dataset_path=dataset_path, nrows=nrows)

    stratify = y if y.nunique() > 1 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=stratify,
    )

    model = train_model(X_train, y_train)
    metrics = evaluate_model(model, X_test, y_test)
    save_model(model, list(X.columns))

    return metrics


if __name__ == "__main__":
    evaluation_metrics = train_and_save_model()
    print("Evaluation metrics:", evaluation_metrics)
    print(f"Saved model to: {MODEL_PATH}")
