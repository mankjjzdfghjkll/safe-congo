"""EDA complet SAFE CONGO (2022 + 2023).

Produit:
- tableaux CSV
- graphiques HTML interactifs (Plotly)
- synthese texte exploitable pour le memoire
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px

# Ajouter la racine du projet pour les imports src.*
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline.data_cleaner import DataCleaner


def safe_write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    out_dir = base_dir / "logs" / "eda"
    out_dir.mkdir(parents=True, exist_ok=True)

    file_2023 = base_dir / "data" / "raw" / "drc-2023_sem08.xlsx"
    file_2022 = base_dir / "data" / "raw" / "drc-2022_sem40.xlsx"

    if not file_2023.exists():
        raise FileNotFoundError(f"Fichier manquant: {file_2023}")

    cleaner = DataCleaner(
        str(file_2023),
        file_path_2022=str(file_2022) if file_2022.exists() else None,
    )

    raw = cleaner.load_data().copy()

    # EDA RAW
    raw_dates = pd.to_datetime(raw.get("DEBUTSEM"), errors="coerce")
    raw_invalid_dates = int(raw_dates.isna().sum())
    raw_years = raw_dates.dt.year
    raw_outlier_years = int(((raw_years < 2020) | (raw_years > 2026)).fillna(False).sum())

    raw_missing = raw.isna().sum().sort_values(ascending=False).rename("missing_count").reset_index()
    raw_missing.columns = ["column", "missing_count"]
    safe_write_csv(raw_missing, out_dir / "raw_missing_counts.csv")

    raw_disease_counts = (
        raw["MALADIE"].value_counts(dropna=False).rename("n_rows").reset_index().rename(columns={"index": "MALADIE"})
    )
    safe_write_csv(raw_disease_counts, out_dir / "raw_disease_counts.csv")

    # Nettoyage pipeline
    clean = cleaner.clean_data().copy()

    # EDA CLEAN
    clean_dates = pd.to_datetime(clean["DEBUTSEM"], errors="coerce")
    clean_years = clean_dates.dt.year
    clean_outlier_years = int(((clean_years < 2020) | (clean_years > 2026)).fillna(False).sum())

    key_cols = [c for c in ["DEBUTSEM", "MALADIE", "ZS", "PROV"] if c in clean.columns]
    clean_dupes_key = int(clean.duplicated(subset=key_cols).sum()) if key_cols else 0

    clean_disease_counts = (
        clean["MALADIE"].value_counts().rename("n_rows").reset_index().rename(columns={"index": "MALADIE"})
    )
    safe_write_csv(clean_disease_counts, out_dir / "clean_disease_counts.csv")

    year_counts = (
        clean_years.value_counts(dropna=False).sort_index().rename("n_rows").reset_index().rename(columns={"DEBUTSEM": "year", "index": "year"})
    )
    safe_write_csv(year_counts, out_dir / "clean_year_counts.csv")

    # Serie hebdo globale
    weekly_total = (
        clean.groupby("DEBUTSEM", as_index=False)["TOTALCAS"].sum().sort_values("DEBUTSEM")
    )
    safe_write_csv(weekly_total, out_dir / "weekly_total_cases.csv")

    # Distribution cible
    totalcas_desc = clean["TOTALCAS"].describe(percentiles=[0.5, 0.9, 0.95, 0.99]).to_frame("value")
    totalcas_desc.index.name = "metric"
    safe_write_csv(totalcas_desc.reset_index(), out_dir / "clean_totalcas_describe.csv")

    # Graphiques
    fig_hist = px.histogram(
        clean,
        x="TOTALCAS",
        nbins=80,
        title="Distribution de TOTALCAS (donnees nettoyees)",
    )
    fig_hist.write_html(out_dir / "hist_totalcas_clean.html")

    top10 = clean["MALADIE"].value_counts().head(10).index.tolist()
    box_df = clean[clean["MALADIE"].isin(top10)].copy()
    fig_box = px.box(
        box_df,
        x="MALADIE",
        y="TOTALCAS",
        points=False,
        title="Dispersion TOTALCAS par maladie (Top 10 frequences)",
    )
    fig_box.update_xaxes(tickangle=35)
    fig_box.write_html(out_dir / "box_totalcas_top10_diseases.html")

    fig_weekly = px.line(
        weekly_total,
        x="DEBUTSEM",
        y="TOTALCAS",
        title="Evolution hebdomadaire du total des cas (global)",
    )
    fig_weekly.write_html(out_dir / "trend_weekly_total_cases.html")

    # Tendances top 5 maladies
    top5 = clean["MALADIE"].value_counts().head(5).index.tolist()
    top5_ts = (
        clean[clean["MALADIE"].isin(top5)]
        .groupby(["DEBUTSEM", "MALADIE"], as_index=False)["TOTALCAS"].sum()
        .sort_values("DEBUTSEM")
    )
    fig_top5 = px.line(
        top5_ts,
        x="DEBUTSEM",
        y="TOTALCAS",
        color="MALADIE",
        title="Tendance hebdomadaire des cas (Top 5 maladies)",
    )
    fig_top5.write_html(out_dir / "trend_top5_diseases.html")

    # Correlation features numeriques principales
    num_cols = [c for c in ["TOTALCAS", "TOTALDECES", "POP"] if c in clean.columns]
    for age_col in [
        "C011MOIS", "D011MOIS", "C1259MOIS", "D1259MOIS", "C515ANS", "D515ANS", "CP15ANS", "DP15ANS"
    ]:
        if age_col in clean.columns:
            num_cols.append(age_col)
    corr_df = clean[num_cols].corr(numeric_only=True)
    safe_write_csv(corr_df.reset_index().rename(columns={"index": "feature"}), out_dir / "clean_numeric_correlation.csv")

    fig_corr = px.imshow(
        corr_df,
        text_auto=True,
        aspect="auto",
        title="Matrice de correlation (variables numeriques)",
    )
    fig_corr.write_html(out_dir / "corr_numeric_heatmap.html")

    # Synthese texte
    lines = []
    lines.append("SAFE CONGO - RAPPORT EDA")
    lines.append("=" * 50)
    lines.append(f"Raw shape: {raw.shape[0]:,} lignes x {raw.shape[1]} colonnes")
    lines.append(f"Clean shape: {clean.shape[0]:,} lignes x {clean.shape[1]} colonnes")
    lines.append(f"Maladies raw: {raw['MALADIE'].nunique(dropna=True)}")
    lines.append(f"Maladies clean: {clean['MALADIE'].nunique(dropna=True)}")
    lines.append(f"Dates invalides raw: {raw_invalid_dates}")
    lines.append(f"Lignes annees anormales raw (<2020 ou >2026): {raw_outlier_years}")
    lines.append(f"Lignes annees anormales clean (<2020 ou >2026): {clean_outlier_years}")
    lines.append(f"Doublons sur cle temporelle clean: {clean_dupes_key}")

    min_date = clean_dates.min()
    max_date = clean_dates.max()
    lines.append(f"Periode clean: {min_date} -> {max_date}")

    q90 = clean["TOTALCAS"].quantile(0.90)
    q95 = clean["TOTALCAS"].quantile(0.95)
    q99 = clean["TOTALCAS"].quantile(0.99)
    lines.append(f"TOTALCAS quantiles: q90={q90:.2f}, q95={q95:.2f}, q99={q99:.2f}")

    lines.append("Top 10 maladies (clean, nb lignes):")
    for _, row in clean_disease_counts.head(10).iterrows():
        lines.append(f"- {row['MALADIE']}: {int(row['n_rows'])}")

    summary_path = out_dir / "eda_summary.txt"
    summary_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"EDA termine. Sorties: {out_dir}")


if __name__ == "__main__":
    main()
