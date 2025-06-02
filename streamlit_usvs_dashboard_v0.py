import streamlit as st
import pandas as pd

# --- Page Setup ---
st.set_page_config(page_title="Global USV's Dashboard", layout="wide")
st.title("📊 Global USV's Dashboard – Excel Viewer")

st.markdown("""
Use the filters below to interactively explore the dataset.  
All filters perform **keyword-based matching**, so partial values like `MBES` will still find matching rows.
""")

# --- Load Data ---
df = pd.read_csv("USVs_Summary_improve.csv")
df = df.dropna(how="all")
df.columns = df.columns.str.strip()

# --- Initialize session state
if "filters" not in st.session_state:
    st.session_state.filters = {}
if "reset_trigger" not in st.session_state:
    st.session_state.reset_trigger = False

# --- Sidebar Filters ---
with st.sidebar:
    st.subheader("🔍 Keyword Filters")

    if st.button("🔄 Clear All Filters"):
        st.session_state.filters = {}
        st.session_state.reset_trigger = True
        st.experimental_rerun()

    keyword_filters = {}
    for col in df.select_dtypes(include='object').columns:
        default_val = "" if st.session_state.reset_trigger else st.session_state.filters.get(col, "")
        user_input = st.text_input(f"{col} (keywords)", value=default_val, key=f"input_{col}")
        if user_input:
            keyword_filters[col] = user_input
            st.session_state.filters[col] = user_input

    st.session_state.reset_trigger = False

# --- Apply Keyword Filters (substring match)
filtered_df = df.copy()
for col, keyword in keyword_filters.items():
    keyword = keyword.lower()
    filtered_df = filtered_df[filtered_df[col].astype(str).str.lower().str.contains(keyword)]

# --- Setup clickable links in 'Spec Sheet (URL)' column
link_config = {}
if "Spec Sheet (URL)" in df.columns:
    link_config["Spec Sheet (URL)"] = st.column_config.LinkColumn(
        "Spec Sheet (URL)",
        help="Click to view manufacturer specifications"
    )

# --- Display Results
st.markdown(f"Loaded `{filtered_df.shape[0]}` rows × `{filtered_df.shape[1]}` columns")
st.markdown("### 📋 Filtered Results (Click 'Spec Sheet' to view links)")
st.dataframe(filtered_df, column_config=link_config, use_container_width=True)
