import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="GPS Guard", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
        [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
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

# --- Page Title ---
st.title(":material/shield: GPS Guard — Detection Center")
st.divider()

loaded_from_history: bool = st.session_state.get("loaded_from_history", False)

# --- Guard: no analysis yet ---
if not loaded_from_history and ("analysis_data" not in st.session_state or st.session_state.analysis_data is None):
    st.info(
        "No analysis results available. Go to **Log Upload** and analyze a file first.",
        icon=":material/info:",
    )
    st.stop()

# --- Load session data ---
class_report: dict | None = st.session_state.get("class_report")
_feat_imp_raw = st.session_state.get("feat_imp")
feat_imp: pd.DataFrame | None = (
    pd.DataFrame(_feat_imp_raw) if isinstance(_feat_imp_raw, list) else _feat_imp_raw
)
analyzed_file: str = st.session_state.get("analyzed_file", "Unknown")
train_mode: bool = st.session_state.get("train_mode_used", False)

features = ["c_n0_diff", "doppler_diff", "c_n0_rolling_std"]

if loaded_from_history:
    data = None
    total_rows = st.session_state.get("h_total_rows", 0)
    spoofed_rows = st.session_state.get("h_spoofed_rows", 0)
    clean_rows = total_rows - spoofed_rows
    spoof_pct = st.session_state.get("h_spoof_pct", 0.0)
    unique_prn = st.session_state.get("h_unique_prn", 0)
    verdict_label = st.session_state.get("h_verdict_label", "UNKNOWN")
    mean_cn0_diff = st.session_state.get("h_mean_cn0_diff", 0.0)
    mean_doppler_diff = st.session_state.get("h_mean_doppler_diff", 0.0)
    mean_rolling_std = st.session_state.get("h_mean_rolling_std", 0.0)
    precomputed_log_entries = st.session_state.get("h_log_entries", [])
else:
    data = st.session_state.analysis_data
    total_rows = len(data)
    spoofed_rows = int((data["prediction"] == 1).sum())
    clean_rows = total_rows - spoofed_rows
    spoof_pct = spoofed_rows / total_rows * 100 if total_rows > 0 else 0
    unique_prn = data["PRN"].nunique() if "PRN" in data.columns else 0
    mean_cn0_diff = data.loc[data["prediction"] == 1, "c_n0_diff"].mean() if spoofed_rows else 0
    mean_doppler_diff = data.loc[data["prediction"] == 1, "doppler_diff"].mean() if spoofed_rows else 0
    mean_rolling_std = data.loc[data["prediction"] == 1, "c_n0_rolling_std"].mean() if spoofed_rows else 0
    precomputed_log_entries = None
    if spoof_pct > 20:
        verdict_label = "SPOOFING ATTACK DETECTED"
    elif spoof_pct > 5:
        verdict_label = "SUSPICIOUS ACTIVITY DETECTED"
    else:
        verdict_label = "NO SPOOFING DETECTED"

# Verdict markdown (shared)
if "ATTACK" in verdict_label:
    verdict_md = f"### :red[{verdict_label}]"
elif "SUSPICIOUS" in verdict_label:
    verdict_md = f"### :orange[{verdict_label}]"
else:
    verdict_md = f"### :green[{verdict_label}]"

# --- Final Verdict ---
col_verdict, col_score = st.columns([6, 2])
with col_verdict:
    st.caption("FINAL VERDICT")
    st.markdown(verdict_md)
    st.write(
        f"**{spoofed_rows:,}** of **{total_rows:,}** measurement rows flagged as spoofed "
        f"(**{spoof_pct:.1f}%**) across **{unique_prn}** tracked satellites. "
        f"File analyzed: `{analyzed_file}`"
    )
with col_score:
    st.metric("Anomaly Rate", f"{spoof_pct:.1f}%")
    if train_mode:
        saved_model_path: str | None = st.session_state.get("saved_model_path")
        if saved_model_path and __import__("os").path.exists(saved_model_path):
            with open(saved_model_path, "rb") as _f:
                st.download_button(
                    label="Download Model",
                    data=_f,
                    file_name=__import__("os").path.basename(saved_model_path),
                    mime="application/octet-stream",
                    icon=":material/download:",
                    width="stretch",
                )

st.divider()

# --- Situation Summary ---
with st.container(border=True):
    st.markdown(":material/summarize: **Situation Summary**")
    col_left, col_right = st.columns(2)

    with col_left:
        if spoofed_rows:
            st.write(
                f"Analysis identified **{spoofed_rows:,} anomalous measurement rows** "
                f"({spoof_pct:.1f}% of the dataset). "
                f"The mean C/N0 differential during flagged segments was "
                f"**{mean_cn0_diff:.3f} dB-Hz**, indicating abnormal signal power fluctuations "
                f"inconsistent with natural atmospheric conditions."
            )
        else:
            st.write(
                "No spoofing indicators detected. All measurements fall within expected "
                "signal characteristics for genuine GNSS reception."
            )
    with col_right:
        if spoofed_rows:
            st.write(
                f"Secondary indicators: mean Doppler differential of **{mean_doppler_diff:.3f} Hz** "
                f"and C/N0 rolling standard deviation of **{mean_rolling_std:.3f} dB-Hz** "
                f"during anomalous periods. These deviations suggest coordinated signal manipulation "
                f"rather than multipath or atmospheric interference."
            )
        else:
            st.write(
                f"All {unique_prn} tracked satellites show consistent Doppler profiles and "
                "stable carrier-to-noise density throughout the observation window."
            )
    if loaded_from_history:
        st.caption(":material/info: This is a historical report. Re-analyze the file to access live charts.")

# --- Charts Row ---
col_chart, col_feat = st.columns([3, 2])

with col_chart:
    with st.container(border=True):
        hdr_c, hdr_badge = st.columns([3, 1])
        with hdr_c:
            st.markdown(":material/show_chart: **C/N0 Differential Over Time**")
        with hdr_badge:
            badge_text = ":red[Anomalous]" if spoof_pct > 20 else (":orange[Suspicious]" if spoof_pct > 5 else ":green[Normal]")
            st.markdown(badge_text)

        if data is None:
            st.info("Chart not available for historical reports — raw measurement data was not persisted.", icon=":material/info:")
        else:
            chart_df = (
                data.groupby("TOW")
                .agg(c_n0_diff=("c_n0_diff", "mean"), prediction=("prediction", lambda s: int(s.mode()[0])))
                .reset_index()
            )
            chart_df["Status"] = chart_df["prediction"].map({0: "Normal", 1: "Spoofed"})
            bar = (
                alt.Chart(chart_df)
                .mark_bar()
                .encode(
                    x=alt.X("TOW:Q", title="Time of Week (s)", axis=alt.Axis(labelAngle=-30)),
                    y=alt.Y("c_n0_diff:Q", title="Mean C/N0 Diff (dB-Hz)"),
                    color=alt.Color(
                        "Status:N",
                        scale=alt.Scale(domain=["Normal", "Spoofed"], range=["#00c9b1", "#e07b00"]),
                        legend=alt.Legend(orient="bottom"),
                    ),
                    tooltip=["TOW", alt.Tooltip("c_n0_diff:Q", format=".4f"), "Status"],
                )
                .properties(height=240)
            )
            st.altair_chart(bar, width='stretch')

with col_feat:
    with st.container(border=True):
        if feat_imp is not None:
            st.markdown(":material/bar_chart: **Feature Importance**")
            fi_chart = (
                alt.Chart(feat_imp)
                .mark_bar()
                .encode(
                    x=alt.X("Ważność:Q", title="Importance"),
                    y=alt.Y("Cecha:N", sort="-x", title="Feature"),
                    color=alt.value("#00c9b1"),
                    tooltip=["Cecha", alt.Tooltip("Ważność:Q", format=".4f")],
                )
                .properties(height=240)
            )
            st.altair_chart(fi_chart, width='stretch')
        elif data is not None:
            st.markdown(":material/insights: **Doppler Differential Distribution**")
            hist_data = data[["doppler_diff", "prediction"]].copy()
            hist_data["Status"] = hist_data["prediction"].map({0: "Normal", 1: "Spoofed"})
            hist = (
                alt.Chart(hist_data)
                .mark_bar(opacity=0.75, binSpacing=0)
                .encode(
                    x=alt.X("doppler_diff:Q", bin=alt.Bin(maxbins=40), title="Doppler Diff (Hz)"),
                    y=alt.Y("count()", title="Count"),
                    color=alt.Color(
                        "Status:N",
                        scale=alt.Scale(domain=["Normal", "Spoofed"], range=["#00c9b1", "#e07b00"]),
                        legend=alt.Legend(orient="bottom"),
                    ),
                )
                .properties(height=240)
            )
            st.altair_chart(hist, width='stretch')
        else:
            st.markdown(":material/insights: **Doppler Differential Distribution**")
            st.info("Chart not available for historical reports.", icon=":material/info:")

# --- Stats Row ---
st.divider()
s1, s2, s3, s4 = st.columns(4)
with s1:
    with st.container(border=True):
        st.metric("Total Records", f"{total_rows:,}")
with s2:
    with st.container(border=True):
        st.metric("Spoofed Records", f"{spoofed_rows:,} ({spoof_pct:.1f}%)")
with s3:
    with st.container(border=True):
        st.metric("Satellites Tracked", str(unique_prn))
with s4:
    with st.container(border=True):
        if class_report and "accuracy" in class_report:
            st.metric("Model Accuracy", f"{class_report['accuracy']*100:.1f}%")
        elif data is not None:
            mean_std = data["c_n0_rolling_std"].mean()
            st.metric("Mean C/N0 Std", f"{mean_std:.4f}")
        else:
            st.metric("Mean C/N0 Std", "N/A")

# --- Classification Report (train mode) ---
if class_report:
    st.divider()
    with st.container(border=True):
        st.markdown(":material/fact_check: **Classification Report**")
        report_rows = []
        for label, vals in class_report.items():
            if isinstance(vals, dict):
                report_rows.append({
                    "Class": label,
                    "Precision": f"{vals.get('precision', 0):.3f}",
                    "Recall": f"{vals.get('recall', 0):.3f}",
                    "F1-Score": f"{vals.get('f1-score', 0):.3f}",
                    "Support": int(vals.get("support", 0)),
                })
        st.dataframe(pd.DataFrame(report_rows), width='stretch', hide_index=True)
