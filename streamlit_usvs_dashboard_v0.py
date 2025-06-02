import streamlit as st
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="Global USV's Dashboard", layout="wide")
st.title("📊 Global USV's Dashboard – Excel Viewer")

st.markdown("""
Use the filters below to interactively explore the dataset.  
All filters perform **keyword-based matching**, so partial values like `MBES` or `Diesel` will still find matching rows.
""")

# --- Load CSV File ---
@st.cache_data
def load_data():
    df = pd.read_csv("USVs_Summary_improve.csv")
    df = df.dropna(how="all")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# --- Session State for Filter Management ---
if "filters" not in st.session_state:
    st.session_state.filters = {}
if "reset_filters" not in st.session_state:
    st.session_state.reset_filters = False

# --- Sidebar Filters ---
with st.sidebar:
    st.subheader("🔍 Keyword Filters")

    # Button to clear filters
    if st.button("🔄 Clear All Filters"):
        st.session_state.filters = {}
        st.session_state.reset_filters = True
        st.experimental_rerun()

    # Create keyword filters
    keyword_filters = {}
    for col in df.select_dtypes(include='object').columns:
        default_val = "" if st.session_state.reset_filters else st.session_state.filters.get(col, "")
        user_input = st.text_input(f"{col} (keywords)", value=default_val, key=f"filter_{col}")
        if user_input:
            keyword_filters[col] = user_input.strip()
            st.session_state.filters[col] = user_input.strip()

    st.session_state.reset_filters = False

# --- Apply Filters
filtered_df = df.copy()
for col, keyword in keyword_filters.items():
    keyword_lower = keyword.lower()
    filtered_df = filtered_df[
        filtered_df[col].astype(str).str.lower().str.contains(keyword_lower, na=False)
    ]

# --- Configure Clickable Link for Spec Sheet ---
link_config = {}
if "Spec Sheet (URL)" in df.columns:
    link_config["Spec Sheet (URL)"] = st.column_config.LinkColumn(
        label="Spec Sheet (URL)",
        help="Click to view the official manufacturer page",
        validate="^https?://.*"
    )

# --- Display Results
st.markdown(f"✅ Showing `{filtered_df.shape[0]}` matching rows out of `{df.shape[0]}` total USVs.")
st.markdown("### 📋 Filtered USV List")

st.dataframe(
    filtered_df,
    column_config=link_config,
    use_container_width=True
)
