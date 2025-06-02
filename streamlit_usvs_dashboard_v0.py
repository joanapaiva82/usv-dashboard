import streamlit as st
import pandas as pd

# --- Setup ---
st.set_page_config(page_title="Global USV's Dashboard", layout="wide")
st.title("📊 Global USV's Dashboard – Excel Viewer")

st.markdown("""
Use the filters below to interactively explore the dataset.  
All filters perform **keyword-based matching**, so partial values like `MBES` will still find matching rows.
""")

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("USVs_SUmmary_improve.csv")
    df = df.dropna(how="all")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# --- Session Filter State ---
if "filters" not in st.session_state:
    st.session_state.filters = {}
if "reset_trigger" not in st.session_state:
    st.session_state.reset_trigger = False

# --- Sidebar: Keyword Filters ---
with st.sidebar:
    st.subheader("🔍 Keyword Filters")
    
    if st.button("🔄 Clear All Filters"):
        st.session_state.filters = {}
        st.session_state.reset_trigger = True
        st.experimental_rerun()

    keyword_filters = {}
    for col in df.select_dtypes(include='object').columns:
        default_val = "" if st.session_state.reset_trigger else st.session_state.filters.get(col, "")
        user_input = st.text_input(f"{col} (keywords)", value=default_val, key=col)
        if user_input:
            keyword_filters[col] = user_input.strip()
            st.session_state.filters[col] = user_input.strip()

    st.session_state.reset_trigger = False

# --- Apply Keyword Filters (partial match)
filtered_df = df.copy()
for col, keyword in keyword_filters.items():
    keyword_lower = keyword.lower()
    filtered_df = filtered_df[filtered_df[col].astype(str).str.lower().str.contains(keyword_lower)]

# --- Configure clickable link for Spec Sheet column
link_config = {}
if "Spec Sheet (URL)" in df.columns:
    link_config["Spec Sheet (URL)"] = st.column_config.LinkColumn(
        label="Spec Sheet (URL)",
        help="Click to open official USV specification",
        validate="^https?://.*"
    )

# --- Display Results Table ---
st.markdown(f"Loaded `{filtered_df.shape[0]}` rows × `{filtered_df.shape[1]}` columns")
st.markdown("### 📋 Filtered Results (Click 'Spec Sheet' to view links)")

st.dataframe(
    filtered_df,
    use_container_width=True,
    column_config=link_config
)
