import pandas as pd, unicodedata

def _normalize(v):
    n = unicodedata.normalize("NFKD", str(v))
    a = n.encode("ascii", "ignore").decode("ascii")
    return " ".join(a.casefold().split())

# reference CSV diseases
ref = pd.read_csv("data/processed/donnees_agregees_nettoyees.csv")
print("=== REF CSV MALADIE column ===")
print(sorted(ref["MALADIE"].dropna().unique().tolist()))

# model summary
summary = pd.read_csv("models/evaluation/model_performance_summary.csv")
print("\n=== MODEL SUMMARY (normalized, R2) ===")
for _, row in summary.iterrows():
    r2 = row["R\u00b2 (Best)"]
    kept = "KEEP" if float(r2) >= 0.5 else "DROP"
    print(f"[{kept}] R2={r2:.3f}  raw='{row['Maladie']}'  norm='{_normalize(row['Maladie'])}'")
