<div align="center">

# AI Network Guardian

### A reproducible, leakage-safe network-flow data preparation pipeline

Clean raw traffic captures, derive useful flow features, and produce model-ready
train/test data without fitting preprocessing on information from the test set.

<p>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10 or newer">
  <img src="https://img.shields.io/badge/Notebooks-4-F37626?logo=jupyter&logoColor=white" alt="Four Jupyter notebooks">
  <img src="https://img.shields.io/badge/Status-reproducible-2ea44f" alt="Reproducible pipeline">
</p>

</div>

---

## What this project does

AI Network Guardian prepares labelled network-flow data for downstream
classification experiments. It is intentionally focused on **data quality,
feature construction, and leakage prevention**; it does not train a classifier
or provide a live network-monitoring service.

Starting with `data/raw/network_traffic.csv`, the pipeline:

1. validates and cleans the input schema;
2. canonicalizes types and column definitions;
3. creates a reproducible, stratified 80/20 train/test split;
4. enriches each flow with rate, ratio, time, port, and network-context features;
5. fits the preprocessing pipeline on **TRAIN only**; and
6. writes datasets and proof artifacts for inspection.

The target is `label`:

| Value | Meaning |
| ---: | --- |
| `0` | Benign traffic |
| `1` | Malicious or anomalous traffic |

## Why the pipeline is safe for experimentation

The notebooks make the boundaries between raw context, model features, and the
target explicit:

- **Stratified split:** 10,005 flows become 8,004 training rows and 2,001 test rows.
- **Deterministic split:** `random_state=42` and `test_size=0.20`.
- **No feature twins:** train/test overlap checks report zero identical feature rows.
- **Train-only fitting:** imputation, skew handling, and scaling decisions are
  learned from training data and then applied to test data.
- **Identifier control:** IP addresses, ports, timestamps, and `row_id` remain
  available as context but are excluded from model features.
- **Outlier transparency:** outliers are reported by class; they are not silently
  discarded.
- **Leakage check:** single-feature predictive power is checked on TRAIN only,
  with features above `0.95` flagged for review.

## Pipeline stages

Run the notebooks in this order. `scripts/run_pipeline.py` executes them
headlessly in a shared namespace and captures generated plots.

| Stage | Notebook | What it does | Main outputs |
| --- | --- | --- | --- |
| 1. Cleaning | [`01_data_cleaning.ipynb`](notebooks/01_data_cleaning.ipynb) | Validates the fixed schema, preserves row identity, coerces invalid cells to missing values, and records outliers. | `flows_clean.csv`, `cleaning_log.json`, `outlier_summary.csv` |
| 2. Transformation | [`02_data_transformation.ipynb`](notebooks/02_data_transformation.ipynb) | Applies canonical dtypes and column definitions. | `flows_transformed.csv` |
| 3. Integration | [`03_data_integration.ipynb`](notebooks/03_data_integration.ipynb) | Builds the stratified split and records the feature/context plan. | `train.csv`, `test.csv`, `X_*.csv`, `y_*.csv`, `feature_plan.json` |
| 4. Enrichment | [`04_data_enrichment.ipynb`](notebooks/04_data_enrichment.ipynb) | Derives flow features, checks leakage, and fits the train-only preprocessor. | `preprocessor.joblib`, `feature_names.json`, `feature_dictionary.csv` |

### Derived features

The enrichment stage adds:

- **Volume and rate:** `total_bytes`, `total_bytes_per_packet`,
  `packets_per_sec`, `bytes_sent_per_sec`, `bytes_received_per_sec`,
  `total_bytes_per_sec`
- **Ratios and flags:** `out_in_byte_ratio`, `is_zero_duration`
- **Port context:** `src_port_range`, `dst_port_range`
- **Time context:** `hour`, `day_of_week`, `is_weekend`
- **Network context:** `src_is_private`, `dst_is_private`, `same_subnet_24`

The final model matrix combines original numeric flow measurements, derived
numeric context, and one-hot encoded `protocol`, `src_port_range`, and
`dst_port_range` values. The exact selected order is recorded in
[`feature_names.json`](data/processed/feature_names.json).

## Quick start

### 1. Create an environment

Python 3.10 or newer is required.

```bash
python -m venv .venv
```

Activate it:

```bash
# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Provide the raw capture

Place the input file at:

```text
data/raw/network_traffic.csv
```

The expected 12-column schema is:

```text
time, source_ip_int, destination_ip_int, source_port, destination_port,
protocol, duration, packet_count, bytes_sent, bytes_received, label,
bytes_per_packet
```

### 4. Run the complete pipeline

```bash
python scripts/run_pipeline.py
```

On success, the command writes `build/pipeline_success.json`, including the
completed notebooks, generated graphs, processed outputs, and model outputs.

To explore a stage interactively, open the notebooks in Jupyter and run the
cells from top to bottom. The runner is the recommended path when you need a
repeatable, headless execution.

## Repository layout

```text
.
├── data/
│   ├── raw/                 # Source network-traffic capture
│   └── processed/           # Cleaned, split, and model-ready tables
├── models/                  # Train-fitted preprocessing artifacts
├── notebooks/               # Ordered pipeline stages
├── plots/                   # Persisted figures from the runner
├── reports/                 # Cleaning, exclusion, outlier, and feature reports
├── scripts/
│   └── run_pipeline.py      # Headless pipeline entry point
├── src/
│   └── config.py            # Shared paths, schema, and split settings
├── requirements.txt
└── README.md
```

## Output reference

### Processed data

| File | Description |
| --- | --- |
| `flows_clean.csv` | Input after schema validation and cleaning |
| `flows_transformed.csv` | Clean data with canonical types |
| `train.csv`, `test.csv` | Full stratified split tables, including context |
| `X_train.csv`, `X_test.csv` | Model feature matrices |
| `y_train.csv`, `y_test.csv` | Target vectors |
| `feature_plan.json` | Feature, context, exclusion, and split decisions |
| `feature_names.json` | Ordered names of the final model features |

### Reports and models

| File | Description |
| --- | --- |
| `reports/cleaning_log.json` | Row/column counts and cleaning actions |
| `reports/outlier_summary.csv` | Outlier counts grouped by class |
| `reports/excluded_columns.csv` | Why each input column is included or excluded |
| `reports/feature_dictionary.csv` | Derived-feature definitions and zero/missing handling |
| `models/preprocessor.joblib` | Preprocessor fitted on training data only |
| `build/pipeline_success.json` | Execution manifest written by the runner |
| `plots/graph_*.png` | Figures captured during headless execution |

## Configuration

Shared settings live in [`src/config.py`](src/config.py):

- `RANDOM_STATE = 42`
- `TEST_SIZE = 0.20`
- `SPLIT_STRATEGY = "stratified"`
- `INCLUDE_IDENTIFIERS = False`

Keep the split seed and feature plan stable when comparing experiments. If the
input schema changes, update the shared configuration and the cleaning stage
together so the generated reports remain trustworthy.

## Reproducibility checklist

Before using a generated dataset in an experiment:

1. confirm the raw file is the intended capture;
2. run `python scripts/run_pipeline.py` from the repository root;
3. inspect `build/pipeline_success.json`;
4. review `reports/cleaning_log.json` and `reports/outlier_summary.csv`;
5. verify `feature_plan.json` matches the experiment design; and
6. load the preprocessor from `models/preprocessor.joblib` rather than fitting
   a second preprocessor on combined train/test data.

## Limitations

- The repository prepares data; it does not train, evaluate, or serve a
  classifier.
- The pipeline expects the fixed CSV schema above.
- The preprocessor is an experiment artifact, not a production model registry
  entry.
- Results depend on the supplied capture and the versions installed from
  `requirements.txt`.

## License

No license file is currently included. Treat this repository as
all-rights-reserved unless the project owner provides separate permission.
