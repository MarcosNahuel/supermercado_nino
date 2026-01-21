import streamlit as st
import runpy
from pathlib import Path

try:
    runpy.run_path(str(Path(__file__).with_name("dashboard_cientifico.py")), run_name="__main__")
except Exception as exc:
    st.error("Hay algo que est\u00e1 fallando al iniciar la app.")
    st.exception(exc)
    st.stop()
