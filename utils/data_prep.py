from typing import Iterable, Optional

import pandas as pd


def prepare_periodic_entries(
    entries_df: pd.DataFrame,
    required_columns: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    required = {"year", "week", "total_cases"} | set(required_columns or [])
    if entries_df.empty or not required.issubset(entries_df.columns):
        return pd.DataFrame()

    prepared = entries_df.copy()
    prepared["year"] = pd.to_numeric(prepared["year"], errors="coerce")
    prepared["week"] = pd.to_numeric(prepared["week"], errors="coerce")
    prepared["total_cases"] = pd.to_numeric(prepared["total_cases"], errors="coerce").fillna(0)
    if "total_deaths" in prepared.columns:
        prepared["total_deaths"] = pd.to_numeric(prepared["total_deaths"], errors="coerce").fillna(0)
    prepared = prepared.dropna(subset=["year", "week"])
    prepared["year"] = prepared["year"].astype(int)
    prepared["week"] = prepared["week"].astype(int)
    prepared["period"] = prepared["year"].astype(str) + "-S" + prepared["week"].astype(str).str.zfill(2)
    return prepared


def prepare_periodic_alerts(
    alerts_df: pd.DataFrame,
    required_columns: Optional[Iterable[str]] = None,
    require_period: bool = True,
) -> pd.DataFrame:
    required = {"current_cases", "predicted_cases", "growth_rate", "alert_level"} | set(required_columns or [])
    if require_period:
        required |= {"year", "week"}
    if alerts_df.empty or not required.issubset(alerts_df.columns):
        return pd.DataFrame()

    prepared = alerts_df.copy()
    if {"year", "week"}.issubset(prepared.columns):
        prepared["year"] = pd.to_numeric(prepared["year"], errors="coerce")
        prepared["week"] = pd.to_numeric(prepared["week"], errors="coerce")
        prepared = prepared.dropna(subset=["year", "week"])
        prepared["year"] = prepared["year"].astype(int)
        prepared["week"] = prepared["week"].astype(int)
        prepared["period"] = prepared["year"].astype(str) + "-S" + prepared["week"].astype(str).str.zfill(2)
    prepared["current_cases"] = pd.to_numeric(prepared["current_cases"], errors="coerce").fillna(0)
    prepared["predicted_cases"] = pd.to_numeric(prepared["predicted_cases"], errors="coerce").fillna(0)
    prepared["growth_rate"] = pd.to_numeric(prepared["growth_rate"], errors="coerce").fillna(0)
    prepared["alert_level"] = prepared["alert_level"].astype(str).str.upper().str.strip()
    return prepared