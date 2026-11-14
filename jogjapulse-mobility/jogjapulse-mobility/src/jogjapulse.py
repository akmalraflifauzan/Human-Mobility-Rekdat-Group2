"""
Shared helpers for the JogjaPulse human mobility project.

All notebooks import from here so that loading, cleaning and normalisation
are done the same way everywhere.

Dataset: Widyawan et al. (2026). JogjaPulse: An Aggregated Spatio-Temporal
Mobility Dataset for Yogyakarta, Indonesia. Zenodo.
https://doi.org/10.5281/zenodo.23157460  (CC BY 4.0)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
FIG_DIR = ROOT / "figures"
FIG_DIR.mkdir(exist_ok=True)

# --------------------------------------------------------------------------
# Constants from the dataset README
# --------------------------------------------------------------------------
GOOD_PERIOD_END = "2022-02-28"      # OD flows after this are reduced quality
SAMPLE_BREAKS = ["2022-01-01", "2022-02-16"]  # abrupt drops in device sample
ANOMALY_DAYS = ["2022-03-08"]       # one-day delivery issue
NIGHT_HOURS = list(range(0, 6))     # 00:00-05:59 WIB
DAY_HOURS = list(range(10, 17))     # 10:00-16:59 WIB
HOLIDAY_WINDOW = ("2021-12-24", "2022-01-02")  # Christmas and New Year
KAB_ORDER = ["YOGYAKARTA", "SLEMAN", "BANTUL", "KULON PROGO", "GUNUNGKIDUL"]
DOW_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _path(name: str) -> Path:
    p = DATA_DIR / name
    if not p.exists():
        raise FileNotFoundError(
            f"{p} not found. Run `python scripts/download_data.py` first "
            "or download the CSV files from Zenodo into the data/ folder."
        )
    return p


# --------------------------------------------------------------------------
# Loaders
# --------------------------------------------------------------------------
def load_hourly(drop_anomalies: bool = True) -> pd.DataFrame:
    """Kapanewon x hour presence (n_maids, n_pings)."""
    df = pd.read_csv(_path("presence_kapanewon_hourly.csv"),
                     dtype={"kab_code": str, "kapanewon_code": str})
    df["date"] = pd.to_datetime(df["date"])
    if drop_anomalies:
        df = df[~df["date"].isin(pd.to_datetime(ANOMALY_DAYS))]
    df["dow"] = df["date"].dt.dayofweek          # 0 = Monday
    df["is_weekend"] = df["dow"] >= 5
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df


def load_cells(drop_anomalies: bool = True) -> pd.DataFrame:
    """500 m grid cell x day presence (n_maids)."""
    df = pd.read_csv(_path("presence_cell500m_daily.csv"))
    df["date"] = pd.to_datetime(df["date"])
    if drop_anomalies:
        df = df[~df["date"].isin(pd.to_datetime(ANOMALY_DAYS))]
    return df


def load_od() -> pd.DataFrame:
    """Monthly home-based OD visitor counts, joined with origin denominators."""
    od = pd.read_csv(_path("od_home_visits_kapanewon_monthly.csv"),
                     dtype={"origin_code": str, "dest_code": str,
                            "origin_kab_code": str, "dest_kab_code": str})
    org = pd.read_csv(_path("od_origin_homes_monthly.csv"),
                      dtype={"origin_code": str, "origin_kab_code": str})
    od = od.merge(org[["month", "origin_code", "n_homed_maids",
                       "n_homed_maids_daytime"]],
                  on=["month", "origin_code"], how="left")
    od["share"] = od["n_maids"] / od["n_homed_maids_daytime"]
    od["is_internal"] = od["origin_code"] == od["dest_code"]
    od["reduced_quality"] = od["reduced_quality"].astype(str).str.lower() == "true"
    return od


def load_origins() -> pd.DataFrame:
    return pd.read_csv(_path("od_origin_homes_monthly.csv"),
                       dtype={"origin_code": str, "origin_kab_code": str})


def load_home_vs_population() -> pd.DataFrame:
    return pd.read_csv(_path("home_maids_vs_population_kapanewon.csv"))


def load_night_validation() -> pd.DataFrame:
    return pd.read_csv(_path("validation_night_presence_kapanewon.csv"))


# --------------------------------------------------------------------------
# Normalisation (README section 6: the device sample shrinks over time,
# so raw counts must never be compared across dates)
# --------------------------------------------------------------------------
def add_hourly_share(df: pd.DataFrame) -> pd.DataFrame:
    """Share of each kapanewon in the regional total of the same hour.

    Note: n_maids is a distinct count, so the regional sum is not the exact
    number of distinct devices. It is used here only as a common denominator
    that removes the effect of the shrinking sample.
    """
    out = df.copy()
    tot = out.groupby(["date", "hour"])["n_maids"].transform("sum")
    out["share_hour"] = out["n_maids"] / tot
    return out


def add_daily_share(cells: pd.DataFrame) -> pd.DataFrame:
    """Share of each grid cell in the total presence of the same day."""
    out = cells.copy()
    out["share_day"] = out["n_maids"] / out.groupby("date")["n_maids"].transform("sum")
    return out


def hourly_profile(df: pd.DataFrame, value: str = "n_pings") -> pd.DataFrame:
    """Percentage of each day's activity that falls in each hour.

    n_pings is additive, so it is the correct variable for regional totals.
    Returns one row per date with 24 hour columns.
    """
    daily = df.groupby(["date", "hour"])[value].sum().unstack("hour").fillna(0)
    return daily.div(daily.sum(axis=1), axis=0) * 100


def kapanewon_profiles(df: pd.DataFrame) -> pd.DataFrame:
    """24-hour shape per kapanewon (each row sums to 1), based on the mean
    hourly share. Used for functional-zone clustering."""
    s = add_hourly_share(df)
    prof = s.groupby(["kapanewon", "hour"])["share_hour"].mean().unstack("hour")
    prof = prof.reindex(columns=range(24))
    prof = prof.interpolate(axis=1, limit_direction="both")
    return prof.div(prof.sum(axis=1), axis=0)


def savefig(fig, name: str, dpi: int = 200) -> Path:
    path = FIG_DIR / name
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    return path
