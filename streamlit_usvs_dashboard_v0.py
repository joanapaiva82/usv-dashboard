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

# --- Setup session_state for global state ---
if "global_keyword" not in st.session_state:
    st.session_state.global_keyword = ""

# --- Sidebar Filters ---
with st.sidebar:
    st.subheader("🔎 Keyword Filters")

    # --- Global Reset Button ---
    if st.button("🔄 Clear All Filters"):
        st.session_state.clear()
        st.rerun()

    # --- Global Keyword ---
    global_input = st.text_input("🌐 Global Keyword (search all fields)", key="global_keyword")

    # --- Dropdown filters ---
    dropdown_filters = {}
    for col in df.select_dtypes(include='object').columns:
        col_key = f"filter_{col}"
        options = sorted(df[col].dropna().unique().tolist())
        selected = st.multiselect(col, options, default=[], key=col_key)
        if selected:
            dropdown_filters[col] = selected

# --- Filtering ---
filtered_df = df.copy()

# Apply global keyword
if global_input:
    keyword = global_input.lower()
    mask = filtered_df.apply(lambda row: row.astype(str).str.lower().str.contains(keyword).any(), axis=1)
    filtered_df = filtered_df[mask]

# Apply dropdown filters (partial match)
for col, selected_vals in dropdown_filters.items():
    filtered_df = filtered_df[
        filtered_df[col].astype(str).apply(lambda x: any(val.lower() in x.lower() for val in selected_vals))
    ]

# --- Spec Sheet Links ---
link_config = {}
if "Spec Sheet (URL)" in df.columns:
    link_config["Spec Sheet (URL)"] = st.column_config.LinkColumn(
        "Spec Sheet (URL)",
        help="Click to view manufacturer specification"
    )

# --- Display Results ---
st.markdown(f"Loaded `{filtered_df.shape[0]}` rows × `{filtered_df.shape[1]}` columns")
st.markdown("### 📋 Filtered Results (Click 'Spec Sheet' to view links)")
st.dataframe(filtered_df, use_container_width=True, column_config=link_config)
