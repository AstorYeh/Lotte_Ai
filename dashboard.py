import streamlit as st

st.set_page_config(page_title="Test")
st.title("Hello World")
st.write("If you see this, Streamlit is working.")
try:
    import pandas
    st.write("Pandas imported successfully")
except ImportError as e:
    st.error(f"Pandas failed: {e}")

from pathlib import Path
st.write(f"Current Directory: {Path.cwd()}")
st.write(f"Files in current dir: {[f.name for f in Path.cwd().iterdir()]}")
