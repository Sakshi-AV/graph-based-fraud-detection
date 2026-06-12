# graph-based-fraud-detection
This project explores fraud detection using graph-based techniques and machine learning models, leveraging relationships between entities to uncover hidden patterns that traditional tabular approaches often miss.

## Current Features

- Flask backend connected to the trained fraud model
- User registration, login, logout, and user dashboard
- Admin login and protected admin dashboard
- SQLite persistence for users, transactions, and alerts
- Balanced Random Forest training with graph features
- Custom fraud threshold of `0.20`
- Isolation Forest runtime anomaly alerts
- PyVis graph export at `graph/graph.html`

## Project Structure

```text
backend/
  config.py
  factory.py
  runtime.py
  routes/
    admin.py
    auth.py
    pages.py
    transactions.py
  services/
    anomaly.py
    database.py
    graph_visualizer.py
    scoring.py

frontend/
  pages/
  static/
    css/
    js/

src/
  preprocessing.py
  graph_builder.py
  feature_engineering.py
  model.py
  predict.py
```

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Train the model:

```bash
python src/model.py
```

Start the app:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Auth Pages

User registration:

```text
http://127.0.0.1:5000/register
```

User login:

```text
http://127.0.0.1:5000/login
```

User dashboard:

```text
http://127.0.0.1:5000/user-dashboard
```

Admin dashboard:

```text
http://127.0.0.1:5000/admin
```

Development admin credentials:

```text
Username: admin
Password: GraphAdmin#2026
```

## SQLite Database

The database lives at:

```text
database/users.db
```

Tables:

- `users`
- `transactions`
- `alerts`

Runtime users are used only for app tracking and predictions. The ML model is trained only on the PaySim dataset.

## Week 1/2 ML Core

The ML pipeline uses the local PaySim CSV dataset with `nrows=100000`.

Pipeline:

```text
Dataset -> preprocessing -> graph construction -> graph features -> RandomForest model -> predict_transaction()
```

Project structure added for the ML core:

```text
data/
models/
notebooks/
src/
  preprocessing.py
  graph_builder.py
  feature_engineering.py
  model.py
  predict.py
requirements.txt
```

Train and save the baseline model:

```bash
python src/model.py
```

Run a sample prediction:

```bash
python src/predict.py
```

The trained baseline model is saved to `models/model.pkl`, and the matching feature order is saved to `models/feature_columns.pkl`.

## Run Frontend + Backend Together

Start the Flask backend from the project root:

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

The transaction form calls the trained model through `/api/predict`.

Admin page:

```text
http://127.0.0.1:5000/admin
```

Development admin credentials:

```text
Username: admin
Password: GraphAdmin#2026
```
