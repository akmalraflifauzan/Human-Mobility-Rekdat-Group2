"""Download all JogjaPulse files from Zenodo into data/ and verify MD5 checksums.

Usage:  python scripts/download_data.py
"""
import hashlib
from pathlib import Path

import requests

RECORD = "https://zenodo.org/records/23157460/files/"
FILES = {
    "README.md": "ac30f40e0e021cb2b131d529d782c75b",
    "presence_cell500m_daily.csv": "0b4d544e8c9ab26d69360821e9ebff27",
    "presence_kapanewon_hourly.csv": "90a4a8ae6eb68abc68f7a1021a51cce8",
    "od_home_visits_kapanewon_monthly.csv": "5857291c608dd5335f6d8833c1ec7b7a",
    "od_origin_homes_monthly.csv": "d14368c48d3937c9146ed9054aee3c79",
    "od_summary.csv": "139962d1c8101eb6873be6f902320efb",
    "home_maids_vs_population_kapanewon.csv": "0f01f7a3bb7027174cc1b5e1ad0e8224",
    "validation_night_presence_kapanewon.csv": "4a8d0f393fd6d4fa17fb0e60c6f7408e",
    "tier1_summary.csv": "d391339521ce3714f1616c430512b0e0",
}

out_dir = Path(__file__).resolve().parents[1] / "data"
out_dir.mkdir(exist_ok=True)

for name, md5 in FILES.items():
    target = out_dir / name
    if target.exists() and hashlib.md5(target.read_bytes()).hexdigest() == md5:
        print(f"[skip] {name} already downloaded")
        continue
    print(f"[get ] {name} ...", end=" ", flush=True)
    r = requests.get(RECORD + name, params={"download": 1}, timeout=300)
    r.raise_for_status()
    target.write_bytes(r.content)
    ok = hashlib.md5(r.content).hexdigest() == md5
    print("OK" if ok else "WARNING: checksum mismatch")

print(f"Done. Files are in {out_dir}")
