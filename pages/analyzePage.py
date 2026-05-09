import streamlit as st
import os
import subprocess
import sys
from streamlit_elements import elements, mui

st.set_page_config(page_title="GPS Spoof Guard", page_icon="🛡️", layout="wide")

with open("data/style.css", "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if "file_path" not in st.session_state:
    st.session_state.file_path = ""
if "navigate_to" not in st.session_state:
    st.session_state.navigate_to = None

# Handle navigation triggered from element callbacks
if st.session_state.navigate_to == "log_upload":
    st.session_state.navigate_to = None
    st.switch_page("app.py")


def browse_file():
    result = subprocess.run(
        [
            sys.executable, "-c",
            "import tkinter as tk; from tkinter import filedialog; "
            "root = tk.Tk(); root.withdraw(); root.wm_attributes('-topmost', 1); "
            "print(filedialog.askopenfilename(title='Select GPS data file', "
            "filetypes=[('Supported formats', '*.bin *.csv), ('All files', '*.*')]))"
        ],
        capture_output=True, text=True
    )
    selected_path = result.stdout.strip()
    if selected_path:
        st.session_state.file_path = selected_path


def analyze_file():
    pass  # implementation here


def go_to_log_upload():
    st.session_state.navigate_to = "log_upload"


with elements("detection_center_page"):
    with mui.Box(sx={"display": "flex", "height": "100vh", "overflow": "hidden", "fontFamily": "Roboto, sans-serif", "bgcolor": "#1a1a1c"}):

        # Sidebar
        with mui.Box(sx={
            "flex": "0 0 260px",
            "overflowY": "auto",
            "bgcolor": "#2b2b2d",
            "color": "white",
            "p": 3,
            "display": "flex",
            "flexDirection": "column",
            "boxSizing": "border-box",
        }):
            with mui.Box(sx={"display": "flex", "alignItems": "flex-start", "mb": 5}):
                mui.icon.Security(sx={"color": "#4cf1d1", "fontSize": 28, "mr": 1.5, "mt": 0.5})
                with mui.Box():
                    mui.Typography("GPS Spoof", sx={"color": "#4cf1d1", "fontWeight": 700, "fontSize": 18, "lineHeight": 1.1})
                    mui.Typography("Guard", sx={"color": "#4cf1d1", "fontWeight": 700, "fontSize": 18, "lineHeight": 1.1})
                    mui.Typography("MCX Studio", sx={"color": "#81c784", "fontSize": 11, "mt": 0.5, "fontWeight": 600})

            # Log Upload
            with mui.Button(onClick=go_to_log_upload, fullWidth=True, sx={
                "bgcolor": "transparent", "color": "#ccc",
                "justifyContent": "flex-start", "textTransform": "none",
                "borderRadius": 2, "px": 2, "py": 1.2, "mb": 1,
                "&:hover": {"bgcolor": "#3a3a3a"},
            }):
                mui.icon.UploadFile(sx={"mr": 2, "fontSize": 20})
                mui.Typography("Log Upload", sx={"fontWeight": 400, "fontSize": 14})

            # Detection Center (active)
            with mui.Button(fullWidth=True, sx={
                "bgcolor": "#ff9800", "color": "#111",
                "justifyContent": "flex-start", "textTransform": "none",
                "borderRadius": 2, "px": 2, "py": 1.2,
                "&:hover": {"bgcolor": "#e68a00"},
            }):
                mui.icon.ErrorOutline(sx={"mr": 2, "fontSize": 20})
                mui.Typography("Detection Center", sx={"fontWeight": 600, "fontSize": 14})

        # Main content
        with mui.Box(sx={"flex": 1, "p": 4, "overflowY": "auto", "bgcolor": "#1a1a1c"}):
            mui.Typography("Log Analysis", sx={
                "color": "#4cf1d1", "fontWeight": 700, "fontSize": 28, "mb": 3,
            })

            with mui.Paper(elevation=0, sx={"bgcolor": "#2b2b2d", "borderRadius": 3, "p": 4}):
                mui.Typography("Detection Center", sx={
                    "color": "white", "fontWeight": 700, "fontSize": 20, "mb": 0.5,
                })
                mui.Typography(
                    "GPS spoofing detection results.",
                    sx={"color": "#aaa", "fontSize": 14, "mb": 3},
                )

                # File selection
                with mui.Box(sx={"mb": 3}):
                    mui.Typography("Select file for analysis:", sx={
                        "color": "#ccc", "fontSize": 14, "mb": 1,
                    })
                    with mui.Box(sx={"display": "flex", "alignItems": "center", "gap": 2}):
                        with mui.Button(onClick=browse_file, variant="outlined", sx={
                            "color": "#ccc", "borderColor": "#555",
                            "textTransform": "none", "borderRadius": 2,
                            "&:hover": {"borderColor": "#888", "bgcolor": "#333"},
                        }):
                            mui.icon.Folder(sx={"mr": 1, "fontSize": 18})
                            mui.Typography("Choose File", sx={"fontSize": 14})

                        if st.session_state.file_path:
                            with mui.Box(sx={"display": "flex", "alignItems": "center", "gap": 1}):
                                mui.icon.CheckCircle(sx={"color": "#81c784", "fontSize": 18})
                                mui.Typography(
                                    os.path.basename(st.session_state.file_path),
                                    sx={"color": "#81c784", "fontSize": 13},
                                )

                        with mui.Button(onClick=analyze_file, variant="contained",
                                        disabled=not bool(st.session_state.file_path),
                                        sx={
                            "bgcolor": "#4cf1d1", "color": "#111", "fontWeight": 700,
                            "textTransform": "none", "borderRadius": 2, "px": 3,
                            "&:hover": {"bgcolor": "#33d4b5"},
                            "&.Mui-disabled": {"bgcolor": "#2a5a54", "color": "#5a8a84"},
                        }):
                            mui.icon.Analytics(sx={"mr": 1, "fontSize": 18})
                            mui.Typography("Run Analysis", sx={"fontSize": 14, "fontWeight": 700})

                # Results placeholder
                if not st.session_state.file_path:
                    with mui.Box(sx={"textAlign": "center", "py": 8}):
                        with mui.Box(sx={
                            "bgcolor": "#3a3a3a", "borderRadius": "50%",
                            "width": 80, "height": 80,
                            "display": "flex", "alignItems": "center", "justifyContent": "center",
                            "mx": "auto", "mb": 3,
                        }):
                            mui.icon.Analytics(sx={"color": "#4cf1d1", "fontSize": 44})

                        mui.Typography("No data to display", sx={
                            "color": "white", "fontWeight": 700, "fontSize": 18, "mb": 1,
                        })
                        mui.Typography(
                            "Select a GPS file above and click Run Analysis to see results.",
                            sx={"color": "#666", "fontSize": 14},
                        )

