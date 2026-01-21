import streamlit as st

try:
    import dashboard_cientifico  # noqa: F401
except Exception as exc:
    st.error("Error al iniciar la app.")
    st.exception(exc)
    st.stop()
