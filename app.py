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
if st.session_state.navigate_to == "detection_center":
    st.session_state.navigate_to = None
    st.switch_page("pages/1_Detection_Center.py")


def browse_file():
    result = subprocess.run(
        [
            sys.executable, "-c",
            "import tkinter as tk; from tkinter import filedialog; "
            "root = tk.Tk(); root.withdraw(); root.wm_attributes('-topmost', 1); "
            "print(filedialog.askopenfilename(title='Select GPS data file', "
            "filetypes=[('Supported formats', '*.bin *.csv'), ('All files', '*.*')]))"
        ],
        capture_output=True, text=True
    )
    selected_path = result.stdout.strip()
    if selected_path:
        st.session_state.file_path = selected_path


def analyze_file():
    pass  # implementation here


def go_to_detection_center():
    st.session_state.navigate_to = "detection_center"


with elements("log_upload_page"):
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

            # Log Upload (active)
            with mui.Button(fullWidth=True, sx={
                "bgcolor": "#ff9800", "color": "#111",
                "justifyContent": "flex-start", "textTransform": "none",
                "borderRadius": 2, "px": 2, "py": 1.2, "mb": 1,
                "&:hover": {"bgcolor": "#e68a00"},
            }):
                mui.icon.UploadFile(sx={"mr": 2, "fontSize": 20})
                mui.Typography("Log Upload", sx={"fontWeight": 600, "fontSize": 14})

            # Detection Center
            with mui.Button(onClick=go_to_detection_center, fullWidth=True, sx={
                "bgcolor": "transparent", "color": "#ccc",
                "justifyContent": "flex-start", "textTransform": "none",
                "borderRadius": 2, "px": 2, "py": 1.2,
                "&:hover": {"bgcolor": "#3a3a3a"},
            }):
                mui.icon.ErrorOutline(sx={"mr": 2, "fontSize": 20})
                mui.Typography("Detection Center", sx={"fontWeight": 400, "fontSize": 14})

        # Main content
        with mui.Box(sx={"flex": 1, "p": 4, "overflowY": "auto", "bgcolor": "#1a1a1c"}):
            mui.Typography("Log Analysis", sx={
                "color": "#4cf1d1", "fontWeight": 700, "fontSize": 28, "mb": 3,
            })

            with mui.Paper(elevation=0, sx={"bgcolor": "#2b2b2d", "borderRadius": 3, "p": 4}):
                mui.Typography("GPS Log Upload", sx={
                    "color": "white", "fontWeight": 700, "fontSize": 20, "mb": 0.5,
                })
                mui.Typography(
                    "Upload GPS log files to check them for spoofing anomalies.",
                    sx={"color": "#aaa", "fontSize": 14, "mb": 3},
                )

                # Drop zone
                with mui.Box(onClick=browse_file, sx={
                    "border": "2px dashed #444", "borderRadius": 2,
                    "p": 6, "textAlign": "center", "mb": 3, "cursor": "pointer",
                    "&:hover": {"borderColor": "#4cf1d1"},
                }):
                    with mui.Box(sx={
                        "bgcolor": "#3a3a3a", "borderRadius": "50%",
                        "width": 64, "height": 64,
                        "display": "flex", "alignItems": "center", "justifyContent": "center",
                        "mx": "auto", "mb": 2,
                    }):
                        mui.icon.CloudUpload(sx={"color": "#4cf1d1", "fontSize": 36})

                    mui.Typography("Drag and drop files here", sx={
                        "color": "white", "fontWeight": 700, "fontSize": 18, "mb": 0.5,
                    })
                    mui.Typography("or click to browse local files", sx={
                        "color": "#aaa", "fontSize": 14, "mb": 1,
                    })
                    mui.Typography(
                        "Supported formats: .bin, .csv",
                        sx={"color": "#666", "fontSize": 12, "mb": 2},
                    )

                    with mui.Button(onClick=browse_file, variant="outlined", sx={
                        "color": "#ccc", "borderColor": "#555",
                        "textTransform": "none", "borderRadius": 2,
                        "&:hover": {"borderColor": "#888", "bgcolor": "#333"},
                    }):
                        mui.icon.Folder(sx={"mr": 1, "fontSize": 18})
                        mui.Typography("Choose File", sx={"fontSize": 14})

                # Analyze button
                with mui.Box(sx={"display": "flex", "justifyContent": "flex-end"}):
                    with mui.Button(onClick=analyze_file, variant="contained", sx={
                        "bgcolor": "#4cf1d1", "color": "#111", "fontWeight": 700,
                        "textTransform": "none", "borderRadius": 2, "px": 3, "py": 1.2,
                        "&:hover": {"bgcolor": "#33d4b5"},
                    }):
                        mui.icon.Analytics(sx={"mr": 1, "fontSize": 20})
                        mui.Typography("Analyze Files", sx={"fontSize": 14, "fontWeight": 700})
