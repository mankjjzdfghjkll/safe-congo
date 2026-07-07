"""
Calcule et affiche la performance globale combinée de tous les modèles
à partir du CSV model_performance_summary.csv et des matrices de confusion.
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import MODEL_RESULT_FILTERS

EVAL_DIR = ROOT / "models" / "evaluation"

# --- Charger le résumé de performance
perf_file = EVAL_DIR / "model_performance_summary.csv"
if not perf_file.exists():
    print(f"Fichier non trouvé : {perf_file}")
    sys.exit(1)

df = pd.read_csv(perf_file, encoding="utf-8-sig")
min_acceptable_r2 = float(MODEL_RESULT_FILTERS.get("min_acceptable_r2", 0.5))
if "R² (Best)" in df.columns:
    df = df[pd.to_numeric(df["R² (Best)"], errors="coerce") >= min_acceptable_r2].copy()
print(f"Données chargées : {len(df)} maladies")
print()

# --- Métriques de régression globales
r2_col   = "R² (Best)"
mape_col = "MAPE (Best)"
mae_col  = "MAE (Best)"
rmse_col = "RMSE (Best)"
cases_col = "Total cas"

r2_vals   = pd.to_numeric(df[r2_col], errors="coerce").dropna()
mape_vals = pd.to_numeric(df[mape_col], errors="coerce").dropna()
mae_vals  = pd.to_numeric(df[mae_col], errors="coerce").dropna()
cases_vals = pd.to_numeric(df[cases_col], errors="coerce").fillna(1)

# R² pondéré par volume de cas
weights = cases_vals.loc[r2_vals.index].values
r2_weighted = float(np.average(r2_vals.values, weights=weights))
r2_mean     = float(r2_vals.mean())
mape_mean   = float(mape_vals.mean())
total_cases = int(cases_vals.sum())

# --- F1 global via matrices de confusion individuelles
#     Classe positive = dernier niveau de chaque matrice ("Élevé")
micro_tp = micro_fp = micro_fn = 0.0
per_disease_f1 = []
diseases_with_cm = []

for _, row in df.iterrows():
    disease = row["Maladie"]
    slug = disease.lower()
    # normalisation du nom de fichier
    import re, unicodedata
    normalized = unicodedata.normalize("NFKD", slug).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", normalized).strip("_")
    cm_file = EVAL_DIR / f"{normalized}_confusion_matrix.csv"
    if not cm_file.exists():
        continue

    try:
        cm_df = pd.read_csv(cm_file, index_col=0, encoding="utf-8-sig")
        mat = cm_df.values.astype(float)
        n = mat.shape[0]
        if n < 2:
            continue
        pos_idx = n - 1
        tp = mat[pos_idx, pos_idx]
        fp = mat[:pos_idx, pos_idx].sum()   # autres → prédit positif
        fn = mat[pos_idx, :pos_idx].sum()   # positif → prédit autre
        denom = 2 * tp + fp + fn
        f1_d = (2 * tp / denom) if denom > 0 else 0.0
        per_disease_f1.append(f1_d)
        diseases_with_cm.append(disease)
        micro_tp += tp
        micro_fp += fp
        micro_fn += fn
    except Exception as e:
        print(f"  Avertissement matrice {disease}: {e}")

macro_f1 = float(np.mean(per_disease_f1)) if per_disease_f1 else np.nan
micro_denom = 2 * micro_tp + micro_fp + micro_fn
micro_f1 = float(2 * micro_tp / micro_denom) if micro_denom > 0 else np.nan

# --- Affichage
print("=" * 70)
print("PERFORMANCE GLOBALE — TOUTES MALADIES CONFONDUES")
print("=" * 70)
print(f"  Maladies modelisees            : {len(df)}")
print(f"  Total cas couverts             : {total_cases:,}")
print()
print("  [ REGRESSION — Prédiction du nombre de cas ]")
print(f"  R² moyen simple                : {r2_mean:.3f}  ({r2_mean * 100:.1f}%)")
print(f"  R² moyen pondéré (par volume)  : {r2_weighted:.3f}  ({r2_weighted * 100:.1f}%)")
print(f"  MAPE moyen global              : {mape_mean:.1f}%")
print()
print("  [ CLASSIFICATION — F1 sur niveaux d'alerte (Élevé = classe positive) ]")
print(f"  Maladies avec matrice          : {len(per_disease_f1)}")
print(f"  F1 Macro  (moy. par maladie)   : {macro_f1:.3f}  ({macro_f1 * 100:.1f}%)")
print(f"  F1 Micro  (agrégé global)      : {micro_f1:.3f}  ({micro_f1 * 100:.1f}%)")
print()

if per_disease_f1:
    f1_sorted = sorted(zip(diseases_with_cm, per_disease_f1), key=lambda x: x[1], reverse=True)
    print("  Top 5 maladies — F1 alerte le plus élevé :")
    for d, f in f1_sorted[:5]:
        print(f"    {d:<38} F1 = {f:.3f}  ({f*100:.1f}%)")
    print("  Bottom 5 maladies — F1 alerte le plus faible :")
    for d, f in f1_sorted[-5:]:
        print(f"    {d:<38} F1 = {f:.3f}  ({f*100:.1f}%)")

print("=" * 70)
