import streamlit as st
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="Global USV's Dashboard", layout="wide")
st.title("📊 Global USV's Dashboard – Excel Viewer")

st.markdown("""
Use the filters below to interactively explore the dataset.  
All filters perform **keyword-based matching**, so partial values like `MBES` will still find matching rows.
""")

# --- Load CSV file ---
df = pd.read_csv("USVs_SUmmary_improve.csv")
df = df.dropna(how="all")
df.columns = df.columns.str.strip()

# --- Session state to manage filters
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
        options = sorted(set(df[col].dropna()))
        placeholder = st.empty()
        default = "" if st.session_state.reset_trigger else st.session_state.filters.get(col, "")
        keyword = placeholder.text_input(f"{col} (keywords)", value=default, key=col)
        if keyword:
            keyword_filters[col] = keyword
            st.session_state.filters[col] = keyword

    st.session_state.reset_trigger = False

# --- Filter Logic: keyword-based (contains)
filtered_df = df.copy()
for col, keyword in keyword_filters.items():
    keyword = keyword.lower()
    filtered_df = filtered_df[filtered_df[col].astype(str).str.lower().str.contains(keyword)]

# --- Link rendering for Spec Sheet column
link_config = {}
if "Spec Sheet (URL)" in df.columns:
    link_config["Spec Sheet (URL)"] = st.column_config.LinkColumn(
        "Spec Sheet (URL)", help="Click to view manufacturer specifications"
    )

# --- Display Table
st.markdown(f"Loaded `{filtered_df.shape[0]}` rows × `{filtered_df.shape[1]}` columns")
st.markdown("### 📋 Filtered Results (Click 'Spec Sheet' to view links)")
st.dataframe(filtered_df, column_config=link_config, use_container_width=True)
