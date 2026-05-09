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

# --- Page Title ---
st.title(":material/shield: GPS Guard")
st.divider()

# --- Final Verdict ---
col_icon, col_verdict, col_score = st.columns([0.4, 5.6, 2])

with col_verdict:
    st.caption("FINAL VERDICT")
    st.markdown("### :orange[SPOOFING ATTACK DETECTED]")
    st.write(
        "High-probability signal manipulation identified. Telemetry indicates "
        "synchronized deviation across L1 and L2 frequencies inconsistent with "
        "natural atmospheric interference."
    )

with col_score:
    st.metric("Confidence Score", "98.7%")

st.divider()

# --- Situation Summary ---
with st.container(border=True):
    st.markdown(":material/summarize: **Situation Summary**")
    col_left, col_right = st.columns(2)
    with col_left:
        st.write(
            "Analysis of the uploaded dataset reveals critical anomalies beginning at UTC 14:22:05. "
            "The primary indicator is an unnatural step-function increase in Carrier-to-Noise density "
            "(C/N0) across multiple tracked satellites simultaneously, highly characteristic of a "
            "localized overpowered transmitter suppressing genuine signals."
        )
    with col_right:
        st.write(
            "Secondary indicators include severe clock bias drift and an unphysical trajectory shift. "
            "The reported position jumped 4.2 kilometers over a 2-second interval, exceeding maximum "
            "theoretical velocity constraints of the host platform."
        )

# --- Charts Row ---
col_chart, col_map = st.columns([3, 2])

with col_chart:
    with st.container(border=True):
        hdr_c, hdr_badge = st.columns([3, 1])
        with hdr_c:
            st.markdown(":material/show_chart: **C/N0 Variance (L1/L2)**")
        with hdr_badge:
            st.markdown(":orange[Anomalous Spike]")

        chart_df = pd.DataFrame({
            "Time":  ["T-10m", "T-8m", "T-6m", "T-4m", "T-2m", "Event 4:22:35", "Now-2m", "Now-1m", "Now"],
            "C/N0":  [38, 40, 37, 39, 36, 22, 18, 20, 19],
            "Phase": ["Normal", "Normal", "Normal", "Normal", "Normal",
                      "Anomalous", "Anomalous", "Anomalous", "Anomalous"],
        })
        # Preserve x-axis order
        time_order = chart_df["Time"].tolist()

        bar = (
            alt.Chart(chart_df)
            .mark_bar()
            .encode(
                x=alt.X("Time:N", sort=time_order, axis=alt.Axis(labelAngle=0)),
                y=alt.Y("C/N0:Q", title="C/N0 (dB-Hz)"),
                color=alt.Color(
                    "Phase:N",
                    scale=alt.Scale(
                        domain=["Normal", "Anomalous"],
                        range=["#00c9b1", "#e07b00"],
                    ),
                    legend=None,
                ),
                tooltip=["Time", "C/N0", "Phase"],
            )
            .properties(height=220)
        )
        st.altair_chart(bar, use_container_width=True)

with col_map:
    with st.container(border=True):
        st.markdown(":material/map: **Trajectory Shift**")
        traj_df = pd.DataFrame({
            "lat": [37.7749, 37.8011],
            "lon": [-122.4194, -122.3985],
        })
        st.map(traj_df, zoom=11, use_container_width=True)
        st.caption(":material/location_on: 4.2km Deviation detected")

# --- Stats Row ---
st.divider()
s1, s2, s3 = st.columns(3)
with s1:
    with st.container(border=True):
        st.metric("Receiver Clock Bias", "1.2 ms/s")
with s2:
    with st.container(border=True):
        st.metric("Satellites Tracked", "12", delta="-4 dropped", delta_color="inverse")
with s3:
    with st.container(border=True):
        st.metric("AGC Level (Auth)", "-32 dBm")

# --- System Telemetry Log ---
st.divider()
with st.container(border=True):
    st.markdown(":material/history: **System Telemetry Log**")

    log_entries = [
        ("14:22:08", "info",    "Automatic alert dispatched to C2 center."),
        ("14:22:05", "warning", "Spoofing threshold exceeded. Primary lock compromised."),
        ("14:21:59", "info",    "Rapid C/N0 divergence detected on PRN 14, 22, 31."),
        ("14:15:00", "success", "Routine hourly integrity check passed. Environment baseline established."),
    ]

    for ts, level, msg in log_entries:
        col_t, col_m = st.columns([1, 8])
        with col_t:
            st.markdown(f"`{ts}`")
        with col_m:
            if level == "warning":
                st.markdown(f":material/warning: :orange[**{msg}**]")
            elif level == "success":
                st.markdown(f":material/check_circle: :green[{msg}]")
            else:
                st.markdown(f":material/info: {msg}")
