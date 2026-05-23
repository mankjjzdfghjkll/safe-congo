"""EDA complet SAFE CONGO a partir du dataset nettoye.

Sorties dans logs/eda/:
- tableaux CSV
- graphiques HTML interactifs
- resume texte pour le memoire
"""

from pathlib import Path

import pandas as pd
import plotly.express as px


def safe_write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    data_path = base / "data" / "processed" / "dataset_propre.csv"
    out_dir = base / "logs" / "eda"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not data_path.exists():
        raise FileNotFoundError(f"Dataset introuvable: {data_path}")

    df = pd.read_csv(data_path)
    df["Date_debut"] = pd.to_datetime(df["Date_debut"], errors="coerce")

    # Tableaux EDA
    missing = df.isna().sum().sort_values(ascending=False).rename("missing_count").reset_index()
    missing.columns = ["column", "missing_count"]
    safe_write_csv(missing, out_dir / "missing_counts.csv")

    disease_counts = (
        df["Maladie"].value_counts().rename("n_rows").reset_index().rename(columns={"index": "Maladie"})
    )
    safe_write_csv(disease_counts, out_dir / "disease_counts.csv")

    year_counts = (
        df["Date_debut"].dt.year.value_counts(dropna=False).sort_index().rename("n_rows").reset_index()
    )
    year_counts.columns = ["Annee", "n_rows"]
    safe_write_csv(year_counts, out_dir / "year_counts.csv")

    weekly = (
        df.groupby("Date_debut", as_index=False)["Total_cas"].sum().sort_values("Date_debut")
    )
    safe_write_csv(weekly, out_dir / "weekly_total_cases.csv")

    describe = df["Total_cas"].describe(percentiles=[0.5, 0.9, 0.95, 0.99]).reset_index()
    describe.columns = ["metric", "value"]
    safe_write_csv(describe, out_dir / "total_cases_describe.csv")

    # Anomalies temporelles
    years = df["Date_debut"].dt.year
    invalid_dates = int(df["Date_debut"].isna().sum())
    abnormal_year_rows = int(((years < 2020) | (years > 2026)).fillna(False).sum())

    # Graphiques
    fig_hist = px.histogram(df, x="Total_cas", nbins=80, title="Distribution de Total_cas")
    fig_hist.write_html(out_dir / "hist_total_cases.html")

    top10 = df["Maladie"].value_counts().head(10).index
    fig_box = px.box(
        df[df["Maladie"].isin(top10)],
        x="Maladie",
        y="Total_cas",
        points=False,
        title="Dispersion de Total_cas par maladie (Top 10)",
    )
    fig_box.update_xaxes(tickangle=35)
    fig_box.write_html(out_dir / "box_total_cases_top10.html")

    fig_week = px.line(weekly, x="Date_debut", y="Total_cas", title="Evolution hebdomadaire du total des cas")
    fig_week.write_html(out_dir / "trend_weekly_total_cases.html")

    top5 = df["Maladie"].value_counts().head(5).index
    top5_ts = (
        df[df["Maladie"].isin(top5)]
        .groupby(["Date_debut", "Maladie"], as_index=False)["Total_cas"].sum()
        .sort_values("Date_debut")
    )
    fig_top5 = px.line(
        top5_ts,
        x="Date_debut",
        y="Total_cas",
        color="Maladie",
        title="Tendance hebdomadaire des cas (Top 5 maladies)",
    )
    fig_top5.write_html(out_dir / "trend_top5_diseases.html")

    corr_cols = [c for c in ["Total_cas", "Total_deces", "Taux_letalite_pct", "Mois"] if c in df.columns]
    corr = df[corr_cols].corr(numeric_only=True)
    safe_write_csv(corr.reset_index().rename(columns={"index": "feature"}), out_dir / "numeric_correlation.csv")

    fig_corr = px.imshow(corr, text_auto=True, aspect="auto", title="Matrice de correlation (variables numeriques)")
    fig_corr.write_html(out_dir / "corr_numeric_heatmap.html")

    summary = []
    summary.append("SAFE CONGO - RAPPORT EDA (DATASET_PROPRE)")
    summary.append("=" * 55)
    summary.append(f"Lignes: {len(df):,} | Colonnes: {df.shape[1]}")
    summary.append(f"Maladies: {df['Maladie'].nunique()}")
    summary.append(f"Periode: {df['Date_debut'].min()} -> {df['Date_debut'].max()}")
    summary.append(f"Dates invalides: {invalid_dates}")
    summary.append(f"Lignes annees anormales (<2020 ou >2026): {abnormal_year_rows}")
    q90 = df["Total_cas"].quantile(0.90)
    q95 = df["Total_cas"].quantile(0.95)
    q99 = df["Total_cas"].quantile(0.99)
    summary.append(f"Quantiles Total_cas: q90={q90:.2f}, q95={q95:.2f}, q99={q99:.2f}")
    summary.append("Top 10 maladies (nb lignes):")
    for _, row in disease_counts.head(10).iterrows():
        summary.append(f"- {row['Maladie']}: {int(row['n_rows'])}")

    (out_dir / "eda_summary.txt").write_text("\n".join(summary), encoding="utf-8")

    print(f"EDA termine. Sorties: {out_dir}")


if __name__ == "__main__":
    main()
