# graph-based-fraud-detection
This project explores fraud detection using graph-based techniques and machine learning models, leveraging relationships between entities to uncover hidden patterns that traditional tabular approaches often miss.

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
