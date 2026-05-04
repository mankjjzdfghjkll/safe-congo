# Models — SAFE CONGO

This folder contains all machine learning artifacts produced by the SAFE CONGO epidemiological surveillance system.

## Structure

```
models/
├── trained/            ← Serialized trained models (joblib/pickle)
│   └── models.pkl      ← Active production model (Random Forest per disease)
│
└── evaluation/         ← Model performance evaluation artifacts
    ├── confusion_matrix_summary.csv            ← Consolidated performance table
    ├── confusion_matrices_combined.png         ← Visual overview (all diseases)
    ├── paludisme_confirme_confusion_matrix.csv
    ├── paludisme_suspect_confusion_matrix.csv
    ├── diarrhee_aqueuse_confusion_matrix.csv
    ├── fievre_typhoide_confusion_matrix.csv
    ├── grippe_confusion_matrix.csv
    ├── infection_respiratoire_aigue_confusion_matrix.csv
    ├── pneumonie_confusion_matrix.csv
    └── rougeole_confusion_matrix.csv
```

## Reference Benchmark (XGBoost — Classification géolocalisée)

| Model | Accuracy | F1-Score |
|---|---|---|
| **XGBoost** | **0.816 (81.6%)** | **0.458** |
| Hist Gradient Boosting | 0.803 | 0.393 |
| Logistic Regression | 0.773 | 0.256 |
| Random Forest | 0.753 | 0.004 |
| Extra Trees | 0.753 | 0.000 |

> Dataset: 27 671 lignes · 27 maladies · 26 provinces · 517 zones de santé (DRC 2023)
> Full benchmark log: [`logs/train_run.log`](../logs/train_run.log)

## How to retrain

```bash
# From project root
python scripts/train.py
```

This will:
1. Load raw data from `data/raw/drc-2023_sem08.xlsx`
2. Clean and aggregate by week/disease
3. Train a Random Forest per disease
4. Save the model to `models/trained/models.pkl`

To run the full advanced pipeline (all algorithms + confusion matrices):

```bash
python -c "from src.train_models import run_training_pipeline; run_training_pipeline()"
```

## Notes

- `models.pkl` is a dict keyed by disease name, each containing the fitted model, feature list, MAE and R² metrics.
- Confusion matrices use tertile binning (Faible / Modéré / Élevé) on continuous case counts.
- Do **not** commit model files from experimental runs — only commit after a validated training run.
