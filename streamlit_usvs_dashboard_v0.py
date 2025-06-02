import streamlit as st
import pandas as pd

# --- Page Setup ---
st.set_page_config(page_title="Global USV's Dashboard", layout="wide")
st.title("📊 Global USV's Dashboard – Excel Viewer")

st.markdown("""
Use the filters below to interactively explore the dataset.  
All filters support **keyword-based partial match**, so typing `MBES` will match all relevant entries.
""")

# --- Load Data ---
df = pd.read_excel("USVs_Summary_improve.xlsx", engine="openpyxl")
df = df.dropna(how="all")
df.columns = df.columns.str.strip()

# --- Session State Init ---
if "filters" not in st.session_state:
    st.session_state.filters = {}
if "global_keyword" not in st.session_state:
    st.session_state.global_keyword = ""

# --- Sidebar Filters ---
with st.sidebar:
    st.subheader("🔎 Filters")

    if st.button("🔄 Clear All Filters"):
        st.session_state.filters = {}
        st.session_state.global_keyword = ""

    # Global keyword input
    global_kw = st.text_input("🌐 Global Keyword (search all fields)", value=st.session_state.global_keyword)
    st.session_state.global_keyword = global_kw

    # Per-column dropdown filters
    for col in df.select_dtypes('object').columns:
        options = sorted(set(df[col].dropna()))
        selected = st.multiselect(f"{col}", options, default=st.session_state.filters.get(col, []), key=col)
        if selected:
            st.session_state.filters[col] = selected
        else:
            st.session_state.filters[col] = []

# --- Filtering logic ---
filtered_df = df.copy()

# Global keyword filter
if st.session_state.global_keyword:
    mask = pd.Series([False] * len(filtered_df))
    for col in filtered_df.select_dtypes('object').columns:
        mask |= filtered_df[col].astype(str).str.lower().str.contains(st.session_state.global_keyword.lower())
    filtered_df = filtered_df[mask]

# Per-column filters (multi-select)
for col, selected_vals in st.session_state.filters.items():
    if selected_vals:
        col_mask = pd.Series([False] * len(filtered_df))
        for val in selected_vals:
            col_mask |= filtered_df[col].astype(str).str.contains(val, case=False, na=False)
        filtered_df = filtered_df[col_mask]

# --- Spec Sheet Links ---
link_config = {}
if "Spec Sheet" in df.columns:
    df["Spec Sheet"] = df["Spec Sheet"].astype(str).apply(lambda x: x if x.startswith("http") else "")
    link_config["Spec Sheet"] = st.column_config.LinkColumn(
        "Spec Sheet", help="Click to view specification page"
    )

# --- Results ---
st.markdown(f"Loaded `{filtered_df.shape[0]}` rows × `{filtered_df.shape[1]}` columns")
st.markdown("### 📋 Filtered Results (Click 'Spec Sheet' to open)")
st.dataframe(filtered_df, column_config=link_config, use_container_width=True)
