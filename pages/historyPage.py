import streamlit as st
import pandas as pd
import components.reports as reports

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
st.title(":material/history: Report History")
st.caption("Browse all previously generated analysis reports. Click **Load** to view a report in the Detection Center.")
st.divider()

# --- Load reports ---
all_reports = reports.load_all_reports()

if not all_reports:
    st.info(
        "No reports saved yet. Go to **Log Upload**, analyze a file, and reports will appear here automatically.",
        icon=":material/info:",
    )
    st.stop()

st.write(f"**{len(all_reports)} report(s)** found.")

for report in all_reports:
    report_id = report.get("id", "unknown")
    verdict_label = report.get("verdict_label", "UNKNOWN")
    spoof_pct = report.get("spoof_pct", 0.0)
    total_rows = report.get("total_rows", 0)
    spoofed_rows = report.get("spoofed_rows", 0)
    unique_prn = report.get("unique_prn", 0)
    analyzed_file = report.get("analyzed_file_basename", report.get("analyzed_file", "Unknown"))
    timestamp = report.get("timestamp", "")
    train_mode = report.get("train_mode_used", False)

    # Format timestamp
    try:
        from datetime import datetime
        ts_display = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d  %H:%M:%S")
    except Exception:
        ts_display = timestamp

    # Verdict 
    if "ATTACK" in verdict_label:
        verdict_badge = f":red[{verdict_label}]"
    elif "SUSPICIOUS" in verdict_label:
        verdict_badge = f":orange[{verdict_label}]"
    else:
        verdict_badge = f":green[{verdict_label}]"

    with st.container(border=True):
        col_info, col_stats, col_actions = st.columns([5, 3, 2])

        with col_info:
            st.markdown(f"**{verdict_badge}**")
            st.caption(f":material/description: `{analyzed_file}`")
            st.caption(f":material/schedule: {ts_display}")
            if train_mode:
                st.caption(":material/model_training: Model Training Used")

        with col_stats:
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Anomaly", f"{spoof_pct:.1f}%")
            with m2:
                st.metric("Records", f"{total_rows:,}")
            with m3:
                st.metric("PRNs", str(unique_prn))

        with col_actions:
            if st.button("Load", key=f"load_{report_id}", icon=":material/open_in_new:", width="stretch", type="primary"):
                # Restore session state from report metadata
                st.session_state.loaded_from_history = True
                st.session_state.analysis_data = None
                st.session_state.class_report = report.get("class_report")
                feat_imp_records = report.get("feat_imp")
                st.session_state.feat_imp = pd.DataFrame(feat_imp_records) if feat_imp_records else None
                st.session_state.analyzed_file = report.get("analyzed_file", "Unknown")
                st.session_state.train_mode_used = train_mode
                st.session_state.saved_model_path = report.get("saved_model_path")
                st.session_state.h_total_rows = report.get("total_rows", 0)
                st.session_state.h_spoofed_rows = report.get("spoofed_rows", 0)
                st.session_state.h_spoof_pct = report.get("spoof_pct", 0.0)
                st.session_state.h_unique_prn = report.get("unique_prn", 0)
                st.session_state.h_verdict_label = report.get("verdict_label", "UNKNOWN")
                st.session_state.h_mean_cn0_diff = report.get("mean_cn0_diff", 0.0)
                st.session_state.h_mean_doppler_diff = report.get("mean_doppler_diff", 0.0)
                st.session_state.h_mean_rolling_std = report.get("mean_rolling_std", 0.0)
                st.session_state.h_log_entries = report.get("log_entries", [])
                st.switch_page("pages/detectionCenter.py")

            if st.button("Delete", key=f"del_{report_id}", icon=":material/delete:", width="stretch", type="tertiary"):
                reports.delete_report(report_id)
                st.rerun()
