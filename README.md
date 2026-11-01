# AI Network Guardian

A reproducible, leakage-safe data-preparation pipeline for network-traffic classification. It turns a raw flow capture into clean, enriched train/test datasets and a fitted preprocessing model, while keeping every transformation auditable.

## Overview

The pipeline takes `data/raw/network_traffic.csv` (10,005 labelled network flows, 12 columns) and produces:

- Cleaned and typed flow tables
- Stratified train/test splits with no feature overlap
- Flow-level enrichment features (rates, ratios, port/time/network context)
- A preprocessor fitted on the training split only
- Reports documenting cleaning decisions, outliers, and the feature dictionary

The target column is `label` (binary: `0` = benign, `1` = malicious/anomalous).

## Pipeline

The four notebooks run in order and share a namespace via `scripts/run_pipeline.py`.

| Stage | Notebook | Input | Output |
| --- | --- | --- | --- |
| 1. Cleaning | `01_data_cleaning.ipynb` | `data/raw/network_traffic.csv` | `flows_clean.csv`, `cleaning_log.json`, `outlier_summary.csv` |
| 2. Transformation | `02_data_transformation.ipynb` | `flows_clean.csv` | `flows_transformed.csv` |
| 3. Integration | `03_data_integration.ipynb` | `flows_transformed.csv` | `train.csv`, `test.csv`, `X_train.csv`, `X_test.csv`, `y_train.csv`, `y_test.csv`, `feature_plan.json` |
| 4. Enrichment | `04_data_enrichment.ipynb` | Split tables | Derived features, `models/preprocessor.joblib`, `feature_dictionary.csv` |

### Stage details

1. **Cleaning** — Validates the fixed schema, preserves row IDs for traceability, converts invalid cells to missing values, and reports outliers per class without removing them.
2. **Transformation** — Enforces dtypes and canonical column definitions.
3. **Integration** — Creates a stratified 80/20 train/test split (`random_state=42`) and an explicit feature plan that separates model features from context/identifier columns.
4. **Enrichment** — Derives `total_bytes`, `out_in_byte_ratio`, `packets_per_sec`, port ranges, time features (`hour`, `day_of_week`, `is_weekend`), and private/subnet flags. Preprocessing (median imputation, skew-aware `log1p`, scaling) is fitted on TRAIN only.

## Leakage safeguards

- Train/test split is stratified and verified to have zero feature twins.
- Single-feature predictive power is checked on TRAIN only; features above `0.95` are flagged.
- All imputation, skew decisions, and scaling are learned from TRAIN and applied to TEST.
- IP identifiers, ports, timestamps, and `row_id` are excluded from model features and retained only as context.
- Outliers are reported, never silently dropped.

## Repository layout

```
.
├── data/
│   ├── raw/                 # network_traffic.csv (source data)
│   └── processed/           # clean, transformed, split, and feature tables
├── models/                  # preprocessor.joblib (fit on TRAIN)
├── notebooks/               # 01-04 pipeline notebooks
├── reports/                 # cleaning log, outlier summary, feature dictionary
├── scripts/run_pipeline.py  # executes all notebooks and writes proof artifacts
├── src/config.py            # shared paths, schema, and split settings
└── requirements.txt
```

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Place the raw capture at `data/raw/network_traffic.csv`, then run the full pipeline:

```bash
python scripts/run_pipeline.py
```

The script executes every notebook headlessly, saves figures to `build/`, and writes `build/pipeline_success.json` with the list of completed notebooks, generated graphs, and output files.

You can also open the notebooks individually in Jupyter and run them top to bottom.

## Outputs

- `data/processed/flows_clean.csv` — cleaned flows
- `data/processed/flows_transformed.csv` — typed flows
- `data/processed/train.csv`, `test.csv` — full split tables
- `data/processed/X_train.csv`, `X_test.csv`, `y_train.csv`, `y_test.csv` — model-ready split
- `data/processed/feature_plan.json` — feature/context/exclusion decisions
- `data/processed/feature_names.json` — ordered model feature names
- `models/preprocessor.joblib` — train-fitted preprocessing pipeline
- `reports/cleaning_log.json` — row/column counts and cleaning actions
- `reports/outlier_summary.csv` — outliers by class
- `reports/feature_dictionary.csv` — derived feature formulas and missing/zero handling

## Requirements

Python 3.10+ with `pandas`, `numpy`, `scikit-learn`, `joblib`, `matplotlib`, and `seaborn`.
