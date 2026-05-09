import streamlit as st

st.set_page_config(page_title="GPS Guard", page_icon="🛡️", layout="wide")

# --- Sidebar ---

# hide native sidebar
with st.sidebar:
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] { display: none; }
        </style>
    """, unsafe_allow_html=True)
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

# --- Main Content ---
st.title("GPS Guard")

st.subheader("Upload GPS Logs")
st.caption("Upload GPS files to check them for anomalies.")

uploaded_files = st.file_uploader(
    label="Drag and drop files here or click to browse local files",
    accept_multiple_files=True,
    type=["bin", "csv"],
    label_visibility="visible",
    help="Supported formats: .bin, .csv",
)

st.divider()

col1, col2 = st.columns([8, 2])
with col2:
    analyze = st.button("Analyze Files", icon=":material/bar_chart:", type="primary", use_container_width=True)

if analyze:
    if not uploaded_files:
        st.warning("Please upload at least one file before analyzing.")
    else:
        st.success(f"Analyzing {len(uploaded_files)} file(s)...")
