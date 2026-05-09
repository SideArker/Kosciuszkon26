import streamlit as st
import os
import subprocess
import sys
import pandas as pd
import numpy as np


st.set_page_config(page_title="GPS Spoof Detector", page_icon=":smiley:", layout="wide")

st.title("GPS Spoof Detector")
st.write("This application detects GPS spoofing using machine learning models. Upload your GPS data to see if it is authentic or spoofed.")


if 'file_path' not in st.session_state:
    st.session_state.file_path = ""
    
if st.button("Browse for file"):
    result = subprocess.run(
        [
            sys.executable, "-c",
            "import tkinter as tk; from tkinter import filedialog; "
            "root = tk.Tk(); root.withdraw(); root.wm_attributes('-topmost', 1); "
            "print(filedialog.askopenfilename(title='Select GPS data file', "
            "filetypes=[('CSV files', '*.csv'), ('Binary files', '*.bin')]))"
        ],
        capture_output=True, text=True
    )
    selected_path = result.stdout.strip()
    if selected_path:
        st.session_state.file_path = selected_path
        
if st.session_state.file_path:
    st.info(f"Selected file: {st.session_state.file_path}")
        
        
if st.button("Run analysis"):
    file_path = st.session_state.file_path
    if not file_path or not os.path.exists(file_path):
        st.error("Please upload a valid file.")
    else:
        file_size = os.path.getsize(file_path)
        chunk_size = 1024 * 1024 * 50 # 50 MB