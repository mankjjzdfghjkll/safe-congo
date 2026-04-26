from __future__ import annotations

import argparse
import re
import unicodedata
from difflib import get_close_matches
from pathlib import Path

import numpy as np
import pandas as pd

OUTPUT_COLS = ["MALADIE", "DEBUTSEM", "PROVINCE", "ZONE_SANTE", "POP", "TOTALCAS", "TOTALDECES", "LETAL", "ATTAQ"]


def _normalize_key(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.upper()
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _clean_text(value) -> str | None:
    if pd.isna(value):
        return None
    text = str(value)
    text = text.replace("\u2019", "'")
    text = re.sub(r"[_\-]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return None
    return text.title()


RDC_PROVINCES = [
    "Bas Uele",
    "Equateur",
    "Haut Katanga",
    "Haut Lomami",
    "Haut Uele",
    "Ituri",
    "Kasai",
    "Kasai Central",
    "Kasai Oriental",
    "Kinshasa",
    "Kongo Central",
    "Kwango",
    "Kwilu",
    "Lomami",
    "Lualaba",
    "Mai Ndombe",
    "Maniema",
    "Mongala",
    "Nord Kivu",
    "Nord Ubangi",
    "Sankuru",
    "Sud Kivu",
    "Sud Ubangi",
    "Tanganyika",
    "Tshopo",
    "Tshuapa",
]

PROVINCE_CORRECTIONS = {
    "KIN": "Kinshasa",
    "KINSHASA": "Kinshasa",
    "VILLE DE KINSHASA": "Kinshasa",
    "KONGO CENTRAL": "Kongo Central",
    "BAS CONGO": "Kongo Central",
    "BAS-CONGO": "Kongo Central",
    "NORD KIVU": "Nord Kivu",
    "N KIVU": "Nord Kivu",
    "NORD-KIVU": "Nord Kivu",
    "SUD KIVU": "Sud Kivu",
    "S KIVU": "Sud Kivu",
    "SUD-KIVU": "Sud Kivu",
    "HAUT KATANGA": "Haut Katanga",
    "HAUT-KATANGA": "Haut Katanga",
    "KASA": "Kasai",
    "KASA CENTRAL": "Kasai Central",
    "KASA ORIENTAL": "Kasai Oriental",
    "KASAI": "Kasai",
    "KASAI CENTRAL": "Kasai Central",
    "KASAI ORIENTAL": "Kasai Oriental",
    "MAI NDOMBE": "Mai Ndombe",
    "MAI-NDOMBE": "Mai Ndombe",
    "NORD UBANGI": "Nord Ubangi",
    "SUD UBANGI": "Sud Ubangi",
    "HAUT UELE": "Haut Uele",
    "BAS UELE": "Bas Uele",
}

COMMON_ZONES = [
    "Kinshasa Centre",
    "Goma",
    "Bukavu",
    "Lubumbashi",
    "Masina",
    "Bandalungwa",
    "Kisantu",
    "Mbanza Ngungu",
    "Beni",
    "Butembo",
    "Uvira",
    "Kalemie",
    "Kananga",
    "Mbuji Mayi",
    "Kikwit",
    "Matadi",
]

ZONE_CORRECTIONS = {
    "KINSHASA CENTRE": "Kinshasa Centre",
    "KIN CENTRE": "Kinshasa Centre",
    "GOMA": "Goma",
    "BUKAVU": "Bukavu",
    "LUBUMBASHI": "Lubumbashi",
    "MBUJI MAYI": "Mbuji Mayi",
    "MBUJI-MAYI": "Mbuji Mayi",
    "KANANGA": "Kananga",
    "KIKWIT": "Kikwit",
    "MATADI": "Matadi",
    "BENI": "Beni",
    "BUTEMBO": "Butembo",
    "UVIRA": "Uvira",
    "LIKATI": "Likasi",
}


def _best_match(text: str, reference: list[str], cutoff: float = 0.85) -> str | None:
    if not text:
        return None
    ref_key_to_name = {_normalize_key(v): v for v in reference}
    guess = get_close_matches(_normalize_key(text), list(ref_key_to_name.keys()), n=1, cutoff=cutoff)
    if guess:
        return ref_key_to_name[guess[0]]
    return None


def standardize_province(value) -> str:
    clean = _clean_text(value)
    if not clean:
        return "Inconnu"

    key = _normalize_key(clean)
    if key in PROVINCE_CORRECTIONS:
        return PROVINCE_CORRECTIONS[key]

    direct = _best_match(clean, RDC_PROVINCES, cutoff=0.86)
    if direct:
        return direct

    return clean


def standardize_zone(value) -> str:
    clean = _clean_text(value)
    if not clean:
        return "Inconnu"

    key = _normalize_key(clean)
    if key in ZONE_CORRECTIONS:
        return ZONE_CORRECTIONS[key]

    common = _best_match(clean, COMMON_ZONES, cutoff=0.88)
    if common:
        return common

    return clean


def standardize_disease(value) -> str:
    clean = _clean_text(value)
    return clean if clean else "Inconnue"


def find_column(df: pd.DataFrame, expected: str, aliases: list[str]) -> str:
    all_aliases = [expected] + aliases
    normalized = {_normalize_key(col): col for col in df.columns}

    for candidate in all_aliases:
        k = _normalize_key(candidate)
        if k in normalized:
            return normalized[k]

    raise ValueError(f"Colonne introuvable pour {expected}. Colonnes disponibles: {list(df.columns)}")


def load_raw_data(input_path: Path) -> pd.DataFrame:
    if not input_path.exists():
        raise FileNotFoundError(f"Fichier introuvable: {input_path}")
    return pd.read_excel(input_path)


def build_clean_dataset(raw_df: pd.DataFrame) -> pd.DataFrame:
    col_map = {
        "MALADIE": find_column(raw_df, "MALADIE", ["MAL", "DISEASE"]),
        "DEBUTSEM": find_column(raw_df, "DEBUTSEM", ["DEBUT_SEM", "DATE_DEBUT_SEM", "DATE"]),
        "PROVINCE": find_column(raw_df, "PROVINCE", ["PROV", "PROVINCES"]),
        "ZONE_SANTE": find_column(raw_df, "ZONE_SANTE", ["ZONE DE SANTE", "ZONE_DE_SANTE", "ZS", "ZONE"]),
        "POP": find_column(raw_df, "POP", ["POPULATION", "POPUL"]),
        "TOTALCAS": find_column(raw_df, "TOTALCAS", ["TOTAL_CAS", "CAS", "NBRCAS", "NB_CAS"]),
        "TOTALDECES": find_column(raw_df, "TOTALDECES", ["TOTAL_DECES", "DECES", "NBRDECES", "NB_DECES"]),
        "LETAL": find_column(raw_df, "LETAL", ["LETALITE", "CASE_FATALITY_RATE"]),
        "ATTAQ": find_column(raw_df, "ATTAQ", ["TAUX_ATTAQUE", "ATTACK_RATE"]),
    }

    df = raw_df[list(col_map.values())].rename(columns={v: k for k, v in col_map.items()})

    df["MALADIE"] = df["MALADIE"].apply(standardize_disease)
    df["PROVINCE"] = df["PROVINCE"].apply(standardize_province)
    df["ZONE_SANTE"] = df["ZONE_SANTE"].apply(standardize_zone)

    df["DEBUTSEM"] = pd.to_datetime(df["DEBUTSEM"], errors="coerce")
    df = df.dropna(subset=["DEBUTSEM"])

    df["POP"] = pd.to_numeric(df["POP"], errors="coerce").fillna(0)
    df["TOTALCAS"] = pd.to_numeric(df["TOTALCAS"], errors="coerce").fillna(0)
    df["TOTALDECES"] = pd.to_numeric(df["TOTALDECES"], errors="coerce").fillna(0)
    df["LETAL"] = pd.to_numeric(df["LETAL"], errors="coerce").fillna(0)
    df["ATTAQ"] = pd.to_numeric(df["ATTAQ"], errors="coerce").fillna(0)

    # Corriger les valeurs négatives
    df["POP"] = np.where(df["POP"] < 0, 0, df["POP"])
    df["TOTALCAS"] = np.where(df["TOTALCAS"] < 0, 0, df["TOTALCAS"])
    df["TOTALDECES"] = np.where(df["TOTALDECES"] < 0, 0, df["TOTALDECES"])
    df["LETAL"] = np.where(df["LETAL"] < 0, 0, df["LETAL"])
    df["ATTAQ"] = np.where(df["ATTAQ"] < 0, 0, df["ATTAQ"])

    # Agréger et recalculer LETAL et ATTAQ à partir des totaux si nécessaire
    df = (
        df.groupby(["MALADIE", "DEBUTSEM", "PROVINCE", "ZONE_SANTE"], as_index=False)[
            ["POP", "TOTALCAS", "TOTALDECES", "LETAL", "ATTAQ"]
        ]
        .sum()
        .sort_values(["DEBUTSEM", "MALADIE", "PROVINCE", "ZONE_SANTE"])
        .reset_index(drop=True)
    )

    # Recalculer LETAL et ATTAQ après agrégation si POP > 0
    df["LETAL"] = np.where(
        df["TOTALCAS"] > 0,
        (df["TOTALDECES"] / df["TOTALCAS"] * 100).round(2),
        0,
    )
    df["ATTAQ"] = np.where(
        df["POP"] > 0,
        (df["TOTALCAS"] / df["POP"] * 100000).round(2),
        0,
    )

    df["DEBUTSEM"] = df["DEBUTSEM"].dt.strftime("%Y-%m-%d")
    return df[OUTPUT_COLS]


def main():
    parser = argparse.ArgumentParser(
        description="Nettoie drc-2023_sem08.xlsx et produit donnees_agregees_nettoyees.csv"
    )
    parser.add_argument("--input", default="data/drc-2023_sem08.xlsx", help="Chemin du fichier Excel brut")
    parser.add_argument("--output", default="data/donnees_agregees_nettoyees.csv", help="Chemin du CSV nettoye")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    raw = load_raw_data(input_path)
    clean = build_clean_dataset(raw)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(output_path, index=False, encoding="utf-8-sig")

    print("=" * 80)
    print("NETTOYAGE TERMINE")
    print("=" * 80)
    print(f"Fichier source : {input_path}")
    print(f"Fichier sortie : {output_path}")
    print(f"Lignes finales : {len(clean)}")
    print(f"Maladies      : {clean['MALADIE'].nunique()}")
    print(f"Provinces     : {clean['PROVINCE'].nunique()}")
    print(f"Zones sante   : {clean['ZONE_SANTE'].nunique()}")


if __name__ == "__main__":
    main()
