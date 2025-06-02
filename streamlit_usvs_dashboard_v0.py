import streamlit as st
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="Global USV's Dashboard", layout="wide")
st.title("📊 Global USV's Dashboard – Excel Viewer")

st.markdown("""
Use the filters below to explore the dataset interactively.  
Each filter uses **keyword-based search**, so typing part of a value like `"MBES"` or `"diesel"` will return all matching entries.
""")

# --- Load the CSV ---
@st.cache_data
def load_data():
    df = pd.read_csv("USVs_SUmmary_improve.csv")
    df = df.dropna(how="all")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# --- Setup session state for filters ---
if "filters" not in st.session_state:
    st.session_state.filters = {col: "" for col in df.select_dtypes(include='object').columns}

if "reset_flag" not in st.session_state:
    st.session_state.reset_flag = False

# --- Sidebar Filters ---
with st.sidebar:
    st.subheader("🔍 Filter by Keyword")
    
    if st.button("🔄 Clear All Filters
