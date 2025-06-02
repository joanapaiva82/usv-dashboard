import streamlit as st
import pandas as pd

# --- Setup page ---
st.set_page_config(page_title="Global USV's Dashboard", layout="wide")
st.title("📊 Global USV's Dashboard – Excel Viewer")

with st.expander("📌 Disclaimer (click to expand)"):
    st.markdown("""
    The information presented on this page has been compiled solely for **academic and research purposes** in support of a postgraduate dissertation in **MSc Hydrography at the University of Plymouth**.

    All specifications, features, and descriptions of Uncrewed Surface Vessels (USVs) are based on **publicly available sources** and **have not been independently verified**.

    **⚠️ This content is not intended to serve as an official or authoritative source.**  
    Do not rely on this data for operational, procurement, or technical decisions.  
    Please consult the original manufacturers for validated information.

    ---
    **Author:** Joana Paiva  
    **Email:** [joana.paiva82@outlook.com](mailto:joana.paiva82@outlook.com)
    """)

# --- Load Excel ---
df = pd.read_excel("USVs_Summary_improve.xlsx", engine="openpyxl")
df = df.dropna(how="all")
df.columns = df.columns.str.strip()

# --- Reset trigger
if "reset_counter" not in st.session_state:
    st.session_state.reset_counter = 0

# --- Sidebar Filters ---
with st.sidebar:
    st.subheader("🔎 Keyword Filters")

    # Global reset button (increases a counter to remount widgets)
    if st.button("🔄 Clear All Filters"):
        st.session_state.global_keyword = ""
        st.session_state.reset_counter += 1

    # Global keyword search input
    global_keyword = st.text_input("🌐 Global Keyword (search all fields)", key=f"global_keyword_{st.session_state.reset_counter}")

    # Dropdown filter state
    dropdown_filters = {}
    for col in df.select_dtypes(include="object").columns:
        options = sorted(df[col].dropna().unique().tolist())
        selected = st.multiselect(
            col,
            options,
            default=[],
            key=f"{col}_{st.session_state.reset_counter}"
        )
        if selected:
            dropdown_filters[col] = selected

# --- Filtering Logic ---
filtered_df = df.copy()

# Apply global keyword filter
if global_keyword:
    keyword = global_keyword.lower()
    mask = filtered_df.apply(lambda row: row.astype(str).str.lower().str.contains(keyword).any(), axis=1)
    filtered_df = filtered_df[mask]

# Apply dropdown filters (keyword-based partial match)
for col, selected_vals in dropdown_filters.items():
    filtered_df = filtered_df[
        filtered_df[col].astype(str).apply(lambda x: any(val.lower() in x.lower() for val in selected_vals))
    ]

# --- Spec Sheet as clickable link
link_config = {}
if "Spec Sheet (URL)" in df.columns:
    link_config["Spec Sheet (URL)"] = st.column_config.LinkColumn(
        "Spec Sheet (URL)",
        help="Click to open manufacturer spec page"
    )

# --- Display Results ---
st.markdown(f"Loaded `{filtered_df.shape[0]}` rows × `{filtered_df.shape[1]}` columns")
st.markdown("### 📋 Filtered Results (Click 'Spec Sheet' to view links)")
st.dataframe(filtered_df, use_container_width=True, column_config=link_config)

