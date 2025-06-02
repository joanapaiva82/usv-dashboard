import streamlit as st
import pandas as pd

# --- Page Setup ---
st.set_page_config(page_title="Global USV's Dashboard", layout="wide")
st.title("📊 Global USV's Dashboard – Excel Viewer")

st.markdown("""
Use the filters below to interactively explore the dataset.  
All filters support **keyword-based partial match**, so typing `MBES` will match all relevant entries.
""")

# --- Load Excel ---
df = pd.read_excel("USVs_Summary_improve.xlsx", engine="openpyxl")
df = df.dropna(how="all")
df.columns = df.columns.str.strip()

# --- Session states for filter memory ---
if "dropdown_filters" not in st.session_state:
    st.session_state.dropdown_filters = {}
if "global_keyword" not in st.session_state:
    st.session_state.global_keyword = ""
if "reset_triggered" not in st.session_state:
    st.session_state.reset_triggered = False

# --- Sidebar ---
with st.sidebar:
    st.subheader("🔎 Keyword Filters")

    # Clear all filters
    if st.button("🔄 Clear All Filters"):
        st.session_state.dropdown_filters = {}
        st.session_state.global_keyword = ""
        st.session_state.reset_triggered = True
        st.rerun()

    # Global keyword input
    global_input = st.text_input("🌐 Global Keyword (search all fields)", value=st.session_state.global_keyword)
    st.session_state.global_keyword = global_input

    # Per-column dropdown filters
    dropdown_filters = {}
    for col in df.select_dtypes(include='object').columns:
        options = sorted(df[col].dropna().unique().tolist())
        default = st.session_state.dropdown_filters.get(col, [])
        selection = st.multiselect(col, options, default=default)
        if selection:
            dropdown_filters[col] = selection
            st.session_state.dropdown_filters[col] = selection

# --- Filtering ---
filtered_df = df.copy()

# Apply global keyword search
if global_input:
    keyword = global_input.lower()
    mask = filtered_df.apply(lambda row: row.astype(str).str.lower().str.contains(keyword).any(), axis=1)
    filtered_df = filtered_df[mask]

# Apply dropdown column filters (partial match)
for col, selected_vals in dropdown_filters.items():
    partial_match = filtered_df[col].astype(str).apply(
        lambda x: any(sel.lower() in x.lower() for sel in selected_vals)
    )
    filtered_df = filtered_df[partial_match]

# --- Spec Sheet as clickable link ---
link_config = {}
if "Spec Sheet (URL)" in df.columns:
    link_config["Spec Sheet (URL)"] = st.column_config.LinkColumn(
        "Spec Sheet (URL)",
        help="Click to open manufacturer spec page"
    )

# --- Display Table ---
st.markdown(f"Loaded `{filtered_df.shape[0]}` rows × `{filtered_df.shape[1]}` columns")
st.markdown("### 📋 Filtered Results (Click 'Spec Sheet' to view links)")
st.dataframe(filtered_df, use_container_width=True, column_config=link_config)
