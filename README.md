# Sleman as the Daytime Engine: Regional Connectivity in Yogyakarta from JogjaPulse Mobility Data

Group project, Project Data Engineering, Universitas Gadjah Mada (DTETI).

**Team:** Akmal Rafli Fauzan, Deva, Diffie, Musa

## Overview

Yogyakarta is often pictured as one city centred on Kota Yogyakarta. Using aggregated mobile-device data for the Special Region of Yogyakarta (DIY), 1 December 2021 to 30 April 2022, we ask how the regions of DIY actually connect during the day and which areas act as activity hubs.

| Part | Notebook | Question | Owner |
|---|---|---|---|
| Context | `01_temporal_patterns.ipynb`, `03_spatial_hotspots.ipynb` | When and where are people present, and why must the data be normalised? | Deva |
| Regional functions | `02_day_night_functional_zones.ipynb` | Which kapanewon are daytime activity centres and which are residential or night-heavy? | Diffie |
| Core: regional flows | `04_regional_flows.ipynb` | Where do residents of each regency go during the day, and which kapanewon are hubs? | Akmal |
| Self-containment and validation | `05_self_containment_validation.ipynb` | Who stays local, how stable are flows to the city, and can the data be trusted? | Musa |

## Data

[JogjaPulse: An Aggregated Spatio-Temporal Mobility Dataset for Yogyakarta, Indonesia](https://doi.org/10.5281/zenodo.23157460) (Widyawan et al., 2026, CC BY 4.0).

| File | Used in |
|---|---|
| `presence_kapanewon_hourly.csv` | 01, 02 |
| `tier1_summary.csv` | 01 |
| `presence_cell500m_daily.csv` | 03 |
| `od_home_visits_kapanewon_monthly.csv` | 04, 05 |
| `od_origin_homes_monthly.csv` | 04, 05 |
| `od_summary.csv` | 04 |
| `home_maids_vs_population_kapanewon.csv` | 05 |

The CSV files are not committed to this repository.

## How to run

**Google Colab (easiest):** open any notebook in [Google Colab](https://colab.research.google.com) and choose Runtime > Run all. The first cell downloads the data from Zenodo automatically, and the last cell downloads all figures as `figures.zip`.

**Locally:**

```bash
pip install -r requirements.txt
python scripts/download_data.py      # downloads the CSVs into data/ and checks MD5
jupyter lab                          # then run the notebooks in notebooks/
```

All figures are saved to `figures/` (PNG for slides, HTML for interactive maps).

## Repository structure

```
.
├── data/                 # CSV files from Zenodo (ignored by git)
├── figures/              # generated charts and maps
├── notebooks/            # 01 to 05, see the table above
├── scripts/download_data.py
├── src/jogjapulse.py     # shared loaders and normalisation helpers
└── requirements.txt
```

## Methodological notes

- **Normalisation.** The number of observed devices falls from roughly 87,000 per day (Dec 2021) to roughly 9,000 (Apr 2022) because the supplier's device panel changed, not because people moved less. All comparisons across time use shares, never raw counts.
- **Suppression.** Rows with fewer than 5 devices were removed by the data publisher (k-anonymity, k = 5). A missing row means "fewer than 5", not zero.
- **Distinct counts are not additive.** `n_maids` is never summed to get a total number of people; `n_pings` is used for regional totals.
- **OD quality.** OD flows for March and April 2022 are flagged as reduced quality, so the flow analysis focuses on December 2021 to February 2022.
- **Devices are not people.** The sample covers devices with location-enabled apps and is not a random sample of the population.

## Citation

Widyawan, Pratama, A. R., Ariansyah, A., Farda, N. M., Pramana, S., & Miller, O. (2026). *JogjaPulse: An Aggregated Spatio-Temporal Mobility Dataset for Yogyakarta, Indonesia* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23157460
