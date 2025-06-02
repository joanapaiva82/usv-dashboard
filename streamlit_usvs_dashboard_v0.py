import streamlit as st
import pandas as pd

# --- Page Setup ---
st.set_page_config(page_title="Global USV's Dashboard", layout="wide")
st.title("📊 Global USV's Dashboard – Excel Viewer")

st.markdown("""
Use the filters below to interactively explore the dataset.  
You can apply specific filters using the dropdowns below or perform a full-table search with the global keyword input.
""")

# --- Load Data ---
df = pd.read_excel("USVs_Summary_improve.xlsx", engine="openpyxl")
df = df.dropna(how="all")
df.columns = df.columns.str.strip()

# --- Initialize Session State ---
if "filters" not in st.session_state:
    st.session_state.filters = {}
if "global_keyword" not in st.session_state:
    st.session_state.global_keyword = ""

# --- Sidebar Filters ---
with st.sidebar:
    st.subheader("🔍 Keyword Filters")

    # Global keyword input at top
    global_kw = st.text_input("🌐 Global Keyword (search all fields)", value=st.session_state.global_keyword)
    st.session_state.global_keyword = global_kw

    # Clear All Filters
    if st.button("🔄 Clear All Filters"):
        st.session_state.filters = {}
        st.session_state.global_keyword = ""
        st.experimental_rerun()

    # Dropdown filters (one selection per column)
    for col in df.select_dtypes(include="object").columns:
        options = sorted(df[col].dropna().unique())
        options.insert(0, "All")
        default = st.session_state.filters.get(col, "All")
        selection = st.selectbox(f"{col}", options, index=options.index(default) if default in options else 0, key=col)
        st.session_state.filters[col] = selection

# --- Apply Filters ---
filtered_df = df.copy()

# Apply global keyword (partial match on all object columns)
if st.session_state.global_keyword:
    keyword = st.session_state.global_keyword.lower()
    mask = pd.Series([False] * len(filtered_df))
    for col in filtered_df.select_dtypes(include="object").columns:
        mask |= filtered_df[col].astype(str).str.lower().str.contains(keyword, na=False)
    filtered_df = filtered_df[mask]

# Apply dropdown filters
for col, selected_val in st.session_state.filters.items():
    if selected_val and selected_val != "All":
        filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(selected_val, case=False, na=False)]

# --- Configure Link Column ---
link_config = {}
if "Spec Sheet" in df.columns:
    df["Spec Sheet"] = df["Spec Sheet"].astype(str).apply(lambda x: x if x.startswith("http") else "")
    link_config["Spec Sheet"] = st.column_config.LinkColumn(
        "Spec Sheet", help="Click to view official product/spec page"
    )

# --- Display Results ---
st.markdown(f"Loaded `{filtered_df.shape[0]}` rows × `{filtered_df.shape[1]}` columns")
st.markdown("### 📋 Filtered Results (Click 'Spec Sheet' to view links)")
st.dataframe(filtered_df, column_config=link_config, use_container_width=True)
