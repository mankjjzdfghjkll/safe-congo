# src/pipeline/data_cleaner.py
"""Module de nettoyage des données pour SAFE CONGO — pipeline ML complet"""

import warnings

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings("ignore")


class DataCleaner:
    """Nettoyage et feature engineering pour les données épidémiologiques RDC."""

    # Colonnes techniques sans valeur prédictive
    _COLS_TO_DROP = [
        "NUM", "C328TNN", "DTNN",
        "C011MOIS", "D011MOIS",
        "C1259MOIS", "D1259MOIS",
        "C515ANS", "D515ANS",
        "CP15ANS", "DP15ANS",
        "RecStatus",
    ]

    # Normalisation des noms de maladies (codes bruts → noms lisibles)
    _DISEASE_MAPPING = {
        "PALUDISME SUSP": "Paludisme (suspect)",
        "PALUDISME CONF": "Paludisme (confirmé)",
        "DIARRHEE DHY M5": "Diarrhée aqueuse",
        "DIARR SANGLANTE": "Diarrhée sanglante",
        "FIEVRE TYPHOIDE": "Fièvre typhoïde",
        "GRIPPE": "Grippe",
        "IRA": "Infection respiratoire aiguë",
        "MENINGITE": "Méningite",
        "ROUGEOLE": "Rougeole",
        "CHOLERA": "Choléra",
        "MONKEYPOX": "Monkeypox",
        "COVID-19": "COVID-19",
    }

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.raw_data: pd.DataFrame | None = None
        self.cleaned_data: pd.DataFrame | None = None
        self.label_encoder: LabelEncoder = LabelEncoder()
        self._disease_labels_fitted: bool = False

    # ------------------------------------------------------------------
    # 1. CHARGEMENT
    # ------------------------------------------------------------------
    def load_data(self) -> pd.DataFrame:
        print("Chargement des données...")
        self.raw_data = pd.read_excel(self.file_path, sheet_name=0)
        print(f"  {self.raw_data.shape[0]:,} lignes | {self.raw_data.shape[1]} colonnes chargées")
        return self.raw_data

    # ------------------------------------------------------------------
    # 2. NETTOYAGE COMPLET
    # ------------------------------------------------------------------
    def clean_data(self) -> pd.DataFrame:
        print("\nNettoyage des données...")
        df = self.raw_data.copy()
        before = len(df)

        # — Suppression colonnes inutiles
        df.drop(columns=[c for c in self._COLS_TO_DROP if c in df.columns],
                errors="ignore", inplace=True)

        # — Conversion et validation des dates
        if "DEBUTSEM" in df.columns:
            df["DEBUTSEM"] = pd.to_datetime(df["DEBUTSEM"], errors="coerce")
            nat_count = df["DEBUTSEM"].isna().sum()
            if nat_count:
                print(f"  Dates invalides supprimées : {nat_count}")
            df.dropna(subset=["DEBUTSEM"], inplace=True)

        # — Normalisation noms de maladies
        if "MALADIE" in df.columns:
            df["MALADIE"] = df["MALADIE"].replace(self._DISEASE_MAPPING)
            df.dropna(subset=["MALADIE"], inplace=True)

        # — Nettoyage valeurs numériques
        for col in ["TOTALCAS", "TOTALDECES"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).clip(lower=0)

        # — Suppression des doublons exacts (même semaine / maladie / zone)
        # Les noms de colonnes réels dans le fichier sont ZS (zone de santé) et PROV (province)
        key_cols = [c for c in ["DEBUTSEM", "MALADIE", "ZS", "PROV", "ZONE_SANTE", "PROVINCE"] if c in df.columns]
        dupes = df.duplicated(subset=key_cols).sum()
        if dupes:
            print(f"  Doublons supprimés : {dupes}")
            df.drop_duplicates(subset=key_cols, inplace=True)

        # — Filtrage lignes négatives résiduelles
        df = df[df["TOTALCAS"] >= 0]

        self.cleaned_data = df
        print(f"  Nettoyage terminé : {before:,} → {len(df):,} lignes "
              f"(−{before - len(df):,})")
        return df

    # ------------------------------------------------------------------
    # 3. AGRÉGATION NATIONALE PAR SEMAINE/MALADIE
    # ------------------------------------------------------------------
    def aggregate_by_week_disease(self) -> pd.DataFrame:
        agg = (
            self.cleaned_data
            .groupby(["DEBUTSEM", "MALADIE"], as_index=False)
            .agg({"TOTALCAS": "sum", "TOTALDECES": "sum"})
            .sort_values(["MALADIE", "DEBUTSEM"])
            .reset_index(drop=True)
        )
        return agg

    # ------------------------------------------------------------------
    # 4. TRAITEMENT DES OUTLIERS (par maladie, IQR capping)
    # ------------------------------------------------------------------
    def _cap_outliers(self, series: pd.Series, iqr_factor: float = 3.0) -> pd.Series:
        """
        Plafonne les valeurs aberrantes via la méthode IQR.
        On utilise un facteur de 3.0 (conservateur) pour conserver les vrais
        pics épidémiques tout en éliminant les erreurs de saisie.
        """
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - iqr_factor * iqr
        upper = q3 + iqr_factor * iqr
        return series.clip(lower=max(lower, 0), upper=upper)

    def remove_outliers(self, agg_data: pd.DataFrame) -> pd.DataFrame:
        """Applique le capping IQR sur TOTALCAS par maladie."""
        print("\nTraitement des outliers...")
        result = agg_data.copy()
        capped_total = 0
        for disease in result["MALADIE"].unique():
            mask = result["MALADIE"] == disease
            original = result.loc[mask, "TOTALCAS"].copy()
            result.loc[mask, "TOTALCAS"] = self._cap_outliers(original)
            capped = (result.loc[mask, "TOTALCAS"] != original).sum()
            capped_total += capped
        print(f"  {capped_total} valeurs aberrantes plafonnées (IQR ×3)")
        return result

    # ------------------------------------------------------------------
    # 5. GESTION DES SÉRIES CREUSES (zéros consécutifs = absence de rapport)
    # ------------------------------------------------------------------
    def handle_sparse_series(self, agg_data: pd.DataFrame,
                             max_zero_ratio: float = 0.7) -> pd.DataFrame:
        """
        Supprime les maladies dont plus de `max_zero_ratio` des semaines
        sont à zéro cas — ce sont des absences de signalement, pas de
        vraies observations, et elles faussent les modèles.
        Interpole linéairement les petites séquences de zéros isolés (≤2 semaines)
        pour les maladies conservées.
        """
        print("\nGestion des séries creuses...")
        result = agg_data.copy()
        diseases_before = result["MALADIE"].nunique()
        removed = []

        for disease in result["MALADIE"].unique():
            mask = result["MALADIE"] == disease
            series = result.loc[mask, "TOTALCAS"]
            zero_ratio = (series == 0).mean()

            if zero_ratio > max_zero_ratio:
                result = result[~mask]
                removed.append(disease)
            else:
                # Interpolation des petits trous (zéros isolés ≤ 2 semaines)
                idx = result[result["MALADIE"] == disease].index
                vals = result.loc[idx, "TOTALCAS"].replace(0, np.nan)
                vals_interp = vals.interpolate(method="linear", limit=2)
                # Ne pas remplacer les zéros en début/fin de série
                result.loc[idx, "TOTALCAS"] = vals_interp.fillna(0)

        if removed:
            print(f"  Maladies trop creuses supprimées ({len(removed)}) : "
                  f"{', '.join(removed)}")
        print(f"  {diseases_before} → {result['MALADIE'].nunique()} maladies conservées")
        return result

    # ------------------------------------------------------------------
    # 6. ENCODAGE DES VARIABLES CATÉGORIELLES
    # ------------------------------------------------------------------
    def encode_disease_labels(self, feature_data: pd.DataFrame) -> pd.DataFrame:
        """
        Encode la colonne MALADIE en entier numérique via LabelEncoder.
        Conserve MALADIE_LABEL (original) pour la lisibilité et ajoute
        MALADIE_CODE (entier) pour les modèles qui en ont besoin.
        Le LabelEncoder est mémorisé pour décodage ultérieur.
        """
        df = feature_data.copy()
        if "MALADIE" not in df.columns:
            return df

        df["MALADIE_LABEL"] = df["MALADIE"]  # garder le nom lisible
        df["MALADIE_CODE"] = self.label_encoder.fit_transform(df["MALADIE"])
        self._disease_labels_fitted = True
        print(f"\nEncodage MALADIE : {df['MALADIE'].nunique()} classes "
              f"→ codes 0–{df['MALADIE_CODE'].max()}")
        return df

    def decode_disease_label(self, code: int) -> str:
        """Convertit un code numérique en nom de maladie."""
        if not self._disease_labels_fitted:
            return str(code)
        return self.label_encoder.inverse_transform([code])[0]

    # ------------------------------------------------------------------
    # 7. FEATURE ENGINEERING (sans data leakage)
    # ------------------------------------------------------------------
    def create_features_for_ml(self, agg_data: pd.DataFrame) -> pd.DataFrame:
        """
        Construit les features de séries temporelles par maladie.
        Les moyennes mobiles sont calculées uniquement avec les valeurs
        passées (min_periods=1, shift appliqué avant rolling) pour éviter
        tout data leakage vers les données de test.
        """
        print("\nCréation des features ML...")
        feature_data = []

        for disease in agg_data["MALADIE"].unique():
            data = (
                agg_data[agg_data["MALADIE"] == disease]
                .copy()
                .sort_values("DEBUTSEM")
                .reset_index(drop=True)
            )

            if len(data) < 5:
                continue

            # Lags (1 à 4 semaines) — information strictement passée
            for lag in [1, 2, 3, 4]:
                data[f"lag_{lag}"] = data["TOTALCAS"].shift(lag)

            # Moyennes mobiles causales : shift(1) avant rolling
            # → la valeur de la semaine courante n'est jamais incluse
            shifted = data["TOTALCAS"].shift(1)
            for window in [2, 3, 4]:
                data[f"ma_{window}"] = shifted.rolling(window, min_periods=1).mean()

            # Taux de croissance — protection contre division par zéro et infinis
            prev = data["TOTALCAS"].shift(1).replace(0, np.nan)
            data["growth_rate"] = (
                (data["TOTALCAS"] - data["TOTALCAS"].shift(1)) / prev
            ).replace([np.inf, -np.inf], 0).fillna(0).clip(-5, 5)

            # Volatilité récente (écart-type sur 4 semaines passées)
            data["volatility_4w"] = shifted.rolling(4, min_periods=2).std().fillna(0)

            # Tendance : différence semaine vs moyenne des 4 dernières
            data["trend"] = data["TOTALCAS"] - data["ma_4"]

            # Variables temporelles
            data["week_rank"] = range(len(data))
            data["month"] = data["DEBUTSEM"].dt.month
            data["quarter"] = data["DEBUTSEM"].dt.quarter

            # Supprimer uniquement les lignes avec NaN sur les features lag
            # (les premières semaines de la série)
            lag_cols = [f"lag_{i}" for i in [1, 2, 3, 4]]
            data.dropna(subset=lag_cols, inplace=True)

            if len(data) >= 10:
                feature_data.append(data)

        if feature_data:
            result = pd.concat(feature_data, ignore_index=True)
            print(f"  {len(result):,} lignes de features créées "
                  f"pour {len(feature_data)} maladies")
            return result
        return pd.DataFrame()


# ------------------------------------------------------------------
# 8. EXPORT DATASET LISIBLE (pour analyse humaine)
# ------------------------------------------------------------------
    def export_clean_dataset(self, agg_data: pd.DataFrame,
                             output_path: str = "data/processed/dataset_propre.csv") -> pd.DataFrame:
        """
        Exporte le dataset agrégé et nettoyé sous une forme facile à lire.

        Colonnes produites (en français clair) :
        ──────────────────────────────────────────────────────────────────
        Semaine          — Étiquette lisible ex. "2023-S08"
        Date_debut       — Date ISO du premier jour de la semaine
        Mois             — 1–12
        Trimestre        — Q1–Q4
        Maladie          — Nom normalisé de la maladie
        Total_cas        — Nombre total de cas signalés (après nettoyage)
        Total_deces      — Nombre total de décès signalés
        Taux_letalite_pct — (décès / cas) × 100, arrondi à 2 décimales
        ──────────────────────────────────────────────────────────────────
        Le fichier est trié par Maladie puis par Date pour une lecture
        chronologique immédiate.
        """
        df = agg_data.copy()

        # Étiquette de semaine "AAAA-S##"
        df["Semaine"] = df["DEBUTSEM"].dt.strftime("%Y-S%W")
        df["Date_debut"] = df["DEBUTSEM"].dt.strftime("%Y-%m-%d")
        df["Mois"] = df["DEBUTSEM"].dt.month
        df["Trimestre"] = "Q" + df["DEBUTSEM"].dt.quarter.astype(str)

        # Taux de létalité (protégé contre division par zéro)
        df["Taux_letalite_pct"] = (
            (df["TOTALDECES"] / df["TOTALCAS"].replace(0, np.nan)) * 100
        ).fillna(0).round(2)

        readable = df.rename(columns={
            "MALADIE":    "Maladie",
            "TOTALCAS":   "Total_cas",
            "TOTALDECES": "Total_deces",
        })[[
            "Semaine", "Date_debut", "Mois", "Trimestre",
            "Maladie", "Total_cas", "Total_deces", "Taux_letalite_pct",
        ]].sort_values(["Maladie", "Date_debut"]).reset_index(drop=True)

        from pathlib import Path
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        readable.to_csv(out, index=False, encoding="utf-8-sig")
        print(f"\nDataset propre exporté → {out}")
        print(f"  {len(readable):,} lignes | {readable['Maladie'].nunique()} maladies "
              f"| {readable['Semaine'].nunique()} semaines")
        return readable


# ------------------------------------------------------------------
# TEST DIRECT
# ------------------------------------------------------------------
if __name__ == "__main__":
    print("Test du module data_cleaner...")
    test_path = "data/raw/drc-2023_sem08.xlsx"
    cleaner = DataCleaner(test_path)
    cleaner.load_data()
    cleaner.clean_data()
    agg = cleaner.aggregate_by_week_disease()
    agg = cleaner.remove_outliers(agg)
    agg = cleaner.handle_sparse_series(agg)
    features = cleaner.create_features_for_ml(agg)
    features = cleaner.encode_disease_labels(features)
    print(f"\nFeatures shape: {features.shape}")
    print(f"Colonnes: {list(features.columns)}")
    print("Module fonctionne correctement!")