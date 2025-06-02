import streamlit as st
import pandas as pd

# === Page setup ===
st.set_page_config(page_title="Global USV's Dashboard", layout="wide")
st.title("📊 Global USV's Dashboard – Excel Viewer")

st.markdown("""
Use the filters below to interactively explore the dataset.  
All filters support **free text**, so partial values like `MBES` or `solar` will match all relevant rows.
""")

# === Load and clean Excel file ===
df = pd.read_excel("USVs_Summary_improve.xlsx", engine="openpyxl")
df = df.dropna(how="all")
df.columns = df.columns.str.strip()

# === Convert 'Spec Sheet' to clickable links ===
link_config = {}
if "Spec Sheet" in df.columns:
    df["Spec Sheet"] = df["Spec Sheet"].astype(str).apply(
        lambda x: x if x.startswith("http") else ""
    )
    link_config["Spec Sheet"] = st.column_config.LinkColumn(
        label="Spec Sheet",
        help="Click to view full spec sheet",
        validate="^https?:\\/\\/.+$"
    )

# === Filter logic ===
if "clear_filters" not in st.session_state:
    st.session_state.clear_filters = False

# === Sidebar: free-text keyword filters ===
with st.sidebar:
    st.subheader("🔍 Keyword Filters")

    if st.button("🔄 Clear All Filters"):
        st.session_state.clear_filters = True
        st.rerun()

    keyword_filters = {}
    text_filter_columns = [
        "Name & Manufacturer",
        "Main Application",
        "Dimensions & Weight",
        "Endurance & Speed",
        "Sensor Suite",
        "Propulsion & Power",
        "Certifications",
        "Autonomy Level",
        "Applications",
        "Country of Origin"
    ]

    for col in text_filter_columns:
        user_input = st.text_input(f"{col} (contains)", "", key=col)
        if user_input.strip():
            keyword_filters[col] = user_input.strip().lower()

    st.session_state.clear_filters = False

# === Apply filters ===
filtered_df = df.copy()
for col, keyword in keyword_filters.items():
    filtered_df = filtered_df[
        filtered_df[col].astype(str).str.lower().str.contains(keyword)
    ]

# === Display results ===
st.markdown(f"Loaded `{filtered_df.shape[0]}` rows × `{filtered_df.shape[1]}` columns")
st.markdown("### 📋 Filtered Results (Click 'Spec Sheet' to view links)")

st.data_editor(
    filtered_df,
    column_config=link_config,
    use_container_width=True,
    disabled=True
)
