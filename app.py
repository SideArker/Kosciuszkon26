from components.training import analyze_data
import streamlit as st

# App entrance
if __name__ == "__main__":

    st.set_page_config(page_title="GPS Guard", page_icon="🛡️", layout="wide")

    st.switch_page("pages/uploadPage.py")

    