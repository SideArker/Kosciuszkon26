# GPS Guard — GPS Spoofing Detection System

A research project focused on detecting **GPS Spoofing attacks** using machine learning. The model analyses physical parameters of GNSS signals to distinguish authentic signals from simulated (spoofed) ones. A Streamlit web application provides a full analysis workflow — from file upload through model training or inference to a visual detection report with persistent history.

---

## How to Run

**Requirements:** Python 3.13+

```bash
pip install -r requirements.txt
streamlit run ./app.py
```

The app opens in your browser. Navigate using the sidebar.

---

## Application Structure

```
app.py                        # Entry point — redirects to the Upload page
requirements.txt

components/
    parser.py                 # Data ingestion and feature engineering
    training.py               # Model training (analyze_data) and inference (run_model)
    reports.py                # Report persistence — save/load/delete JSON reports

pages/
    uploadPage.py             # Log Upload — file picker, mode options, triggers analysis
    detectionCenter.py        # Detection Center — analysis results and verdict
    historyPage.py            # Report History — browse and reload past reports

data/
    reports/                  # Auto-created — saved analysis report JSON files
    *.csv                     # Dataset files (TEXBAT)
```

---

## Streamlit Web Application

The web app is a multi-page Streamlit application with three pages accessible from the sidebar:

### 🛡 Log Upload (`uploadPage.py`)
The starting point for every analysis run.
- **File picker** — uses a native OS dialog (tkinter) to select a `.bin` or `.csv` GPS log. Files are referenced by path, never buffered into memory, so files larger than 200 MB are handled without crashes.
- **Train model** toggle:
  - **On** — trains a new LightGBM classifier on the first *N* rows of the file (configurable), saves the model as `lgbm_gps_spoof_detector.pkl` next to the log file, then runs inference on the full dataset.
  - **Off** — opens a model picker to select an existing `.pkl` file and runs inference directly via `run_model`.
- After analysis completes the report is automatically saved and the app navigates to the Detection Center.

### 📊 Detection Center (`detectionCenter.py`)
Displays the results of the most recent analysis or a report loaded from history.
- **Final Verdict** — colour-coded: 🔴 Spoofing Attack Detected (>13%), 🟠 Suspicious Activity (>5%), 🟢 Clean.
- **Situation Summary** — natural language description of mean C/N0 differential, Doppler differential, and rolling standard deviation during anomalous periods.
- **C/N0 Differential Over Time** — bar chart (Normal / Spoofed) aggregated per Time of Week.
- **Feature Importance / Doppler Distribution** — feature importance when a model was trained on this run, Doppler histogram otherwise.
- **Stats row** — Total Records, Spoofed Records (%), Satellites Tracked, Model Accuracy or Mean C/N0 Std.
- **Classification Report** — precision, recall, F1, support per class (train mode only).
- **Download Model** button — available when a model was trained on this run.

### 🗂 Report History (`historyPage.py`)
A file-explorer-style log of every past analysis.
- Each card shows the verdict badge, source filename, timestamp, anomaly %, record count, and PRN count.
- **Load** — restores report metadata into session state and navigates to the Detection Center. Charts that require raw data show a placeholder; all stats, summaries, and the classification report are fully available.
- **Delete** — permanently removes the report JSON from `data/reports/`.

Reports are saved as JSON files in `data/reports/` (created automatically). Only metadata is persisted — no raw measurement data — keeping storage minimal.

---

## Feature Engineering

All features are computed per-satellite (grouped by PRN) to avoid cross-satellite contamination:

| Feature | Description |
|---|---|
| `c_n0_diff` | Per-PRN difference in Carrier-to-Noise density — detects sudden signal power jumps |
| `doppler_diff` | Per-PRN difference in Doppler frequency — detects unnatural frequency shifts |
| `c_n0_rolling_std` | Rolling standard deviation of C/N0 over a 5-sample window — detects unnaturally stable signals |

Training uses a time-series split: the model is trained on the first *N* rows and tested on the remainder, simulating a real attack scenario where future data is unknown at training time.

---

## Model

- **Algorithm:** LightGBM (`LGBMClassifier`) with balanced class weights
- **Serialisation:** Joblib `.pkl` containing the model and feature list
- **Current performance (TEXBAT dataset):** ~96% accuracy

---

## Data

Data used in this project were supposed to come from the **TEXBAT** (Texas Spoofing Test Battery) dataset, the internationally recognised standard for testing anti-spoofing systems, but data was too unbalanced, so we ended up with **Tuni2025 Datasets for GNSS - GPS Spoofing** and trained our model on:
- C-7 GPS Static No Multipath True Position – **Clear-sky** (no spoofers)    - Version-v13
- SS-18 GPS Static No Multipath True Position – **2 Spoofers**               - Version-v3


