import streamlit as st
import pandas as pd

# --- Page Setup ---
st.set_page_config(page_title="Global USV's Dashboard", layout="wide")
st.title("📊 Global USV's Dashboard – Excel Viewer")

st.markdown("""
Use the filters below to interactively explore the dataset.  
All filters support **keyword-based partial match**, so typing `MBES` will match all relevant entries.
""")

# --- Load Excel File ---
df = pd.read_excel("USVs_Summary_improve.xlsx", engine="openpyxl")
df = df.dropna(how="all")
df.columns = df.columns.str.strip()

# --- Sidebar ---
with st.sidebar:
    st.subheader("🔎 Keyword Filters")

    # --- Clear All Filters Logic ---
    if st.button("🔄 Clear All Filters"):
        for key in list(st.session_state.keys()):
            if key.startswith("filter_") or key == "global_keyword":
                del st.session_state[key]
        st.rerun()

    # --- Global Keyword ---
    global_keyword = st.text_input("🌐 Global Keyword (search all fields)", key="global_keyword")

    # --- Dropdown Filters per Column ---
    dropdown_filters = {}
    for col in df.select_dtypes(include='object').columns:
        options = sorted(df[col].dropna().unique().tolist())
        selected = st.multiselect(col, options, key=f"filter_{col}")
        if selected:
            dropdown_filters[col] = selected

# --- Apply Filters ---
filtered_df = df.copy()

# Apply global keyword (partial match across all columns)
if global_keyword:
    keyword = global_keyword.lower()
    mask = filtered_df.apply(lambda row: row.astype(str).str.lower().str.contains(keyword).any(), axis=1)
    filtered_df = filtered_df[mask]

# Apply dropdown filters (partial match in cell)
for col, selected_vals in dropdown_filters.items():
    filtered_df = filtered_df[
        filtered_df[col].astype(str).apply(lambda x: any(sel.lower() in x.lower() for sel in selected_vals))
    ]

# --- Spec Sheet Link Column ---
link_config = {}
if "Spec Sheet (URL)" in df.columns:
    link_config["Spec Sheet (URL)"] = st.column_config.LinkColumn(
        "Spec Sheet (URL)",
        help="Click to open manufacturer specification link"
    )

# --- Display Results ---
st.markdown(f"Loaded `{filtered_df.shape[0]}` rows × `{filtered_df.shape[1]}` columns")
st.markdown("### 📋 Filtered Results (Click 'Spec Sheet' to view links)")
st.dataframe(filtered_df, use_container_width=True, column_config=link_config)
