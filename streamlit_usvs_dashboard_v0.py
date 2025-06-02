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

# --- Init session state
if "filters" not in st.session_state:
    st.session_state.filters = {}
if "trigger_reset" not in st.session_state:
    st.session_state.trigger_reset = False

# --- Sidebar Filters ---
with st.sidebar:
    st.subheader("🔍 Keyword Filters")

    if st.button("🔄 Clear All Filters"):
        st.session_state.filters = {}
        st.session_state.trigger_reset = True
        st.experimental_rerun()

    keyword_filters = {}
    for col in df.select_dtypes(include='object').columns:
        default_value = "" if st.session_state.trigger_reset else st.session_state.filters.get(col, "")
        input_val = st.text_input(f"{col} (keywords)", value=default_value, key=f"input_{col}")
        if input_val:
            keyword_filters[col] = input_val
            st.session_state.filters[col] = input_val

    st.session_state.trigger_reset = False

# --- Filter Logic (substring match)
filtered_df = df.copy()
for col, keyword in keyword_filters.items():
    keyword = keyword.lower()
    filtered_df = filtered_df[filtered_df[col].astype(str).str.lower().str.contains(keyword)]

# --- Configure clickable links in 'Spec Sheet (URL)'
link_config = {}
if "Spec Sheet (URL)" in df.columns:
    link_config["Spec Sheet (URL)"] = st.column_config.LinkColumn(
        "Spec Sheet (URL)",
        help="Click to view manufacturer specifications"
    )

# --- Show Results
st.markdown(f"Loaded `{filtered_df.shape[0]}` rows × `{filtered_df.shape[1]}` columns")
st.markdown("### 📋 Filtered Results (Click 'Spec Sheet' to view links)")
st.dataframe(filtered_df, column_config=link_config, use_container_width=True)
