import streamlit as st
import components.training as trainModel
import components.reports as reports
import subprocess
import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="GPS Guard", page_icon="🛡️", layout="wide")
    
    
# --- Sidebar ---
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)



# hide native sidebar
with st.sidebar:
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
            <span class="material-symbols-outlined" style="font-size:28px; color:#00e5cc;"></span>
            <div>
                <div style="font-size:16px; font-weight:700; color:white; line-height:1.1;">GPS Spoof Guard</div>
                <div style="font-size:12px; color:#00e5cc; font-weight:600;">MCX Studio</div>
            </div>
        </div>
        <hr style="border-color:#333; margin:12px 0;">
        """,
        unsafe_allow_html=True,
    )

    st.page_link("pages/uploadPage.py", label="Log Upload", icon=":material/upload_file:")
    st.page_link("pages/detectionCenter.py", label="Detection Center", icon=":material/manage_search:")
    st.page_link("pages/historyPage.py", label="Report History", icon=":material/history:")


def _precompute_charts(data: "pd.DataFrame") -> None:
    _MAX_POINTS = 250
    _N_BINS = 40

    # C/N0 over time
    chart_df = (
        data.groupby("TOW")
        .agg(c_n0_diff=("c_n0_diff", "mean"), prediction=("prediction", lambda s: int(s.mode()[0])))
        .reset_index()
    )
    if len(chart_df) > _MAX_POINTS:
        step = len(chart_df) // _MAX_POINTS
        chart_df = chart_df.iloc[::step].reset_index(drop=True)
    chart_df["Status"] = chart_df["prediction"].map({0: "Normal", 1: "Spoofed"})
    st.session_state.chart_df = chart_df

    # Doppler histogram
    bin_rows = []
    for _label, _status in [(0, "Normal"), (1, "Spoofed")]:
        vals = data.loc[data["prediction"] == _label, "doppler_diff"].dropna().values
        if len(vals) == 0:
            continue
        counts, edges = np.histogram(vals, bins=_N_BINS)
        for i, cnt in enumerate(counts):
            if cnt > 0:
                bin_rows.append({"bin_start": float(edges[i]), "bin_end": float(edges[i + 1]), "count": int(cnt), "Status": _status})
    st.session_state.hist_df = pd.DataFrame(bin_rows)


def _save_report(data, class_report, feat_imp, file_path, train_mode_used, saved_model_path=None):
    total_rows = len(data)
    spoofed_rows = int((data["prediction"] == 1).sum())
    spoof_pct = spoofed_rows / total_rows * 100 if total_rows > 0 else 0
    unique_prn = data["PRN"].nunique() if "PRN" in data.columns else 0

    mean_cn0_diff = float(data.loc[data["prediction"] == 1, "c_n0_diff"].mean()) if spoofed_rows else 0.0
    mean_doppler_diff = float(data.loc[data["prediction"] == 1, "doppler_diff"].mean()) if spoofed_rows else 0.0
    mean_rolling_std = float(data.loc[data["prediction"] == 1, "c_n0_rolling_std"].mean()) if spoofed_rows else 0.0

    if spoof_pct > 20:
        verdict_label = "SPOOFING ATTACK DETECTED"
    elif spoof_pct > 5:
        verdict_label = "SUSPICIOUS ACTIVITY DETECTED"
    else:
        verdict_label = "NO SPOOFING DETECTED"

    # Compute telemetry transitions for the log
    tow_col = "TOW" if "TOW" in data.columns else data.columns[0]
    events_df = (
        data.sort_values(tow_col)
        .groupby(tow_col)["prediction"]
        .agg(lambda s: int(s.mode()[0]))
        .reset_index()
    )
    events_df["prev"] = events_df["prediction"].shift(1, fill_value=events_df["prediction"].iloc[0])
    transitions = events_df[events_df["prediction"] != events_df["prev"]].head(8)

    log_entries = []
    for _, row in transitions.iterrows():
        tow_val = f"TOW {row[tow_col]:.0f}s"
        if row["prediction"] == 1:
            log_entries.append([tow_val, "warning", "Spoofing onset detected — prediction crossed to ANOMALOUS."])
        else:
            log_entries.append([tow_val, "success", "Signal returned to nominal — prediction crossed to NORMAL."])

    if not log_entries:
        if spoofed_rows == 0:
            log_entries.append(["All", "success", "No anomalous transitions detected. Signal nominal throughout."])
        else:
            log_entries.append(["All", "warning", f"{spoofed_rows:,} anomalous records present with no clear onset boundary."])

    payload = {
        "timestamp": datetime.now().isoformat(),
        "analyzed_file": file_path,
        "analyzed_file_basename": os.path.basename(file_path),
        "verdict_label": verdict_label,
        "spoof_pct": spoof_pct,
        "total_rows": total_rows,
        "spoofed_rows": spoofed_rows,
        "unique_prn": unique_prn,
        "train_mode_used": train_mode_used,
        "saved_model_path": saved_model_path,
        "class_report": class_report,
        "feat_imp": feat_imp.to_dict(orient="records") if feat_imp is not None else None,
        "mean_cn0_diff": mean_cn0_diff,
        "mean_doppler_diff": mean_doppler_diff,
        "mean_rolling_std": mean_rolling_std,
        "log_entries": log_entries,
    }
    reports.save_report(payload)


# --- Main Content ---
st.title("GPS Guard")

st.subheader("Upload GPS Logs")
st.caption("Upload GPS files to check them for anomalies.")

if "selected_file" not in st.session_state:
    st.session_state.selected_file = None

col_browse, col_clear = st.columns([2, 10])
with col_browse:
    if st.button("Browse File…", icon=":material/folder_open:", width='stretch'):
        _picker_script = (
            "import tkinter as tk;"
            "from tkinter import filedialog;"
            "root = tk.Tk();"
            "root.withdraw();"
            "root.wm_attributes('-topmost', True);"
            "f = filedialog.askopenfilename("
            "  title='Select a GPS log file',"
            "  filetypes=[('GPS logs', '*.bin *.csv'), ('All files', '*.*')]"
            ");"
            "print(f)"
        )
        result = subprocess.run(
            [sys.executable, "-c", _picker_script],
            capture_output=True,
            text=True,
        )
        path = result.stdout.strip()
        if path:
            st.session_state.selected_file = path
            st.rerun()

with col_clear:
    if st.session_state.selected_file:
        if st.button("Clear selection", icon=":material/delete:", type="tertiary"):
            st.session_state.selected_file = None
            st.rerun()

if st.session_state.selected_file:
    st.caption(f":material/description: {st.session_state.selected_file}")
else:
    st.info("No file selected. Click **Browse File…** to choose a .bin or .csv GPS log.", icon=":material/info:")

st.divider()

# --- Train model toggle ---
st.subheader("Model Options")
train_model = st.toggle("Train the model", value=True)

split_row = None
if train_model:
    split_row = st.number_input(
        "How many rows to train the model on",
        min_value=1,
        value=10000,
        step=1000,
        help="Rows up to this index are used for training; the rest are used for testing.",
    )
else:
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = None

    col_model_browse, col_model_clear = st.columns([2, 10])
    with col_model_browse:
        if st.button("Browse Model…", icon=":material/model_training:", width='stretch'):
            _model_picker = (
                "import tkinter as tk;"
                "from tkinter import filedialog;"
                "root = tk.Tk();"
                "root.withdraw();"
                "root.wm_attributes('-topmost', True);"
                "f = filedialog.askopenfilename("
                "  title='Select a trained model (.pkl)',"
                "  filetypes=[('Model files', '*.pkl'), ('All files', '*.*')]"
                ");"
                "print(f)"
            )
            res = subprocess.run([sys.executable, "-c", _model_picker], capture_output=True, text=True)
            mp = res.stdout.strip()
            if mp:
                st.session_state.selected_model = mp
                st.rerun()
    with col_model_clear:
        if st.session_state.get("selected_model"):
            if st.button("Clear model", icon=":material/delete:", type="tertiary"):
                st.session_state.selected_model = None
                st.rerun()

    if st.session_state.get("selected_model"):
        st.caption(f":material/model_training: {st.session_state.selected_model}")
    else:
        st.info("No model selected. Click **Browse Model…** to choose a .pkl file.", icon=":material/info:")

st.divider()

col1, col2 = st.columns([8, 2])
with col2:
    analyze = st.button("Analyze File", icon=":material/bar_chart:", type="primary", width='stretch')

if analyze:
    
    if not st.session_state.selected_file:
        st.warning("Please select a file before analyzing.")
        
    else:
        file_path = st.session_state.selected_file
        if train_model:
            with st.status("Analyzing file…", expanded=True) as status:
                st.write(":material/description: Loading and parsing file…")
                st.write(":material/model_training: Training model…")
                class_report, feat_imp, saved_model_path = trainModel.analyze_data(
                    file_path=file_path,
                    split_row=int(split_row),
                    output_model=True,
                )
                st.write(":material/bar_chart: Running predictions on full dataset…")
                data, _, _ = trainModel.run_model(file_path, saved_model_path)
                st.write(":material/query_stats: Pre-computing charts…")
                _precompute_charts(data)
                st.write(":material/save: Saving report…")
                _save_report(data, class_report, feat_imp, file_path, True, saved_model_path)
                status.update(label="Analysis complete!", state="complete", expanded=False)
            st.session_state.analysis_data = data
            st.session_state.class_report = class_report
            st.session_state.feat_imp = feat_imp
            st.session_state.analyzed_file = file_path
            st.session_state.saved_model_path = saved_model_path
            st.session_state.train_mode_used = True
            st.session_state.loaded_from_history = False
            st.switch_page("pages/detectionCenter.py")
        else:
            model_path = st.session_state.get("selected_model")
            if not model_path:
                st.warning("Please select a model file before analyzing.")
            elif not os.path.exists(model_path):
                st.error(f"Model file not found: `{model_path}`")
            else:
                with st.status("Analyzing file…", expanded=True) as status:
                    st.write(":material/description: Loading and parsing file…")
                    st.write(":material/bar_chart: Running predictions…")
                    data, class_report, feat_imp = trainModel.run_model(file_path, model_path)
                    st.write(":material/query_stats: Pre-computing charts…")
                    _precompute_charts(data)
                    st.write(":material/save: Saving report…")
                    _save_report(data, class_report, feat_imp, file_path, False)
                    status.update(label="Analysis complete!", state="complete", expanded=False)
                st.session_state.analysis_data = data
                st.session_state.class_report = class_report
                st.session_state.feat_imp = feat_imp
                st.session_state.analyzed_file = file_path
                st.session_state.train_mode_used = False
                st.session_state.loaded_from_history = False
                st.switch_page("pages/detectionCenter.py")
                