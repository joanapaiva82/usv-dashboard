import streamlit as st
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="Global USV's Dashboard", layout="wide")
st.title("📊 Global USV's Dashboard – Excel Viewer")

st.markdown("""
Use the filters below to interactively explore the dataset.  
All filters support **keyword-based matching**, so partial values like `"MBES"` will find matches even in multi-entry fields.
""")

# --- Load Excel ---
df = pd.read_excel("USVs_Summary_improve.xlsx", engine="openpyxl")
df = df.dropna(how="all")
df.columns = df.columns.str.strip()

# --- Prepare Spec Sheet column as LinkColumn
link_config = {}
if "Spec Sheet" in df.columns:
    df["Spec Sheet"] = df["Spec Sheet"].astype(str).apply(
        lambda x: x if x.startswith("http") else ""
    )
    link_config["Spec Sheet"] = st.column_config.LinkColumn(
        "Spec Sheet",
        help="Click to view full spec sheet",
        validate="^https?:\\/\\/.+$"
    )

# --- Initialize filters state
if "keyword_filters" not in st.session_state:
    st.session_state.keyword_filters = {}

# --- Sidebar filters
with st.sidebar:
    st.subheader("🔍 Keyword Filters")
    if st.button("🔄 Clear All Filters"):
        st.session_state.keyword_filters = {}
        st.experimental_rerun()

    filters = {}
    for col in df.select_dtypes(include=['object', 'category']).columns:
        default_value = st.session_state.keyword_filters.get(col, "")
        keyword = st.text_input(f"{col}", value=default_value, key=col)
        if keyword:
            filters[col] = keyword
            st.session_state.keyword_filters[col] = keyword

# --- Apply keyword filters
filtered_df = df.copy()
for col, keyword in filters.items():
    keyword = keyword.lower().strip()
    filtered_df = filtered_df[filtered_df[col].astype(str).str.lower().str.contains(keyword)]

# --- Show Table
st.markdown(f"Loaded `{filtered_df.shape[0]}` rows × `{filtered_df.shape[1]}` columns")
st.markdown("### 📋 Filtered Results (Click 'Spec Sheet' to view links)")
st.dataframe(filtered_df, column_config=link_config, use_container_width=True)
