import pandas as pd, joblib, unicodedata
from pathlib import Path

ROOT = Path(".")

def _normalize(v):
    n = unicodedata.normalize("NFKD", str(v))
    a = n.encode("ascii", "ignore").decode("ascii")
    return " ".join(a.casefold().split())

models_path = ROOT / "models" / "trained" / "models.pkl"
if models_path.exists():
    data = joblib.load(models_path)
    print("TYPE:", type(data))
    if isinstance(data, dict):
        print("KEYS:", sorted(data.keys()))
    elif isinstance(data, list):
        print("LIST LENGTH:", len(data))
        print("FIRST:", data[0] if data else "empty")
else:
    print("models.pkl NOT FOUND")
    for f in (ROOT / "models" / "trained").iterdir():
        print(f)
