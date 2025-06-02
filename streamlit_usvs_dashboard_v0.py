import streamlit as st
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="Global USV's Dashboard", layout="wide")
st.title("📊 Global USV's Dashboard – Excel Viewer")

st.markdown("""
Use the filters below to interactively explore the dataset.  
All filters support **keyword-based matching**, so typing `MBES` will find it even within long strings.
""")

# --- Load Data ---
df = pd.read_excel("USVs_Summary_improve.xlsx", engine="openpyxl")
df = df.dropna(how="all")
df.columns = df.columns.str.strip()

# --- Initialize session state
if "filters" not in st.session_state:
    st.session_state.filters = {col: "" for col in df.select_dtypes('object').columns}

# --- Sidebar filters
with st.sidebar:
    st.subheader("🔎 Keyword Filters")

    if st.button("🔄 Clear All Filters"):
        for col in st.session_state.filters:
            st.session_state.filters[col] = ""

    for col in df.select_dtypes('object').columns:
        current_value = st.session_state.filters.get(col, "")
        new_value = st.text_input(f"{col} (keyword)", value=current_value, key=col)
        st.session_state.filters[col] = new_value

# --- Keyword Filtering Logic
filtered_df = df.copy()
for col, keyword in st.session_state.filters.items():
    if keyword:
        filtered_df = filtered_df[filtered_df[col].astype(str).str.lower().str.contains(keyword.lower())]

# --- Format Spec Sheet column as link
link_config = {}
if "Spec Sheet" in df.columns:
    df["Spec Sheet"] = df["Spec Sheet"].astype(str).apply(lambda x: x if x.startswith("http") else "")
    link_config["Spec Sheet"] = st.column_config.LinkColumn(
        "Spec Sheet", help="Click to view manufacturer specs"
    )

# --- Display Data
st.markdown(f"Loaded `{filtered_df.shape[0]}` rows × `{filtered_df.shape[1]}` columns")
st.markdown("### 📋 Filtered Results (Click 'Spec Sheet' to view links)")
st.dataframe(filtered_df, column_config=link_config, use_container_width=True)
