import streamlit as st
import pandas as pd

# === Page setup ===
st.set_page_config(page_title="Global USV's Dashboard", layout="wide")
st.title("📊 Global USV's Dashboard – Excel Viewer")

st.markdown("""
Use the filters below to explore the dataset.  
You can:
- Type in the global **keyword box** to search across all columns  
- Use **dropdown filters** for quick selection  
- Or apply **free-text search** per column
""")

# === Load and clean Excel file ===
df = pd.read_excel("USVs_Summary_improve.xlsx", engine="openpyxl")
df = df.dropna(how="all")
df.columns = df.columns.str.strip()

# === Show columns for debugging (sidebar) ===
st.sidebar.caption("🧾 Columns found in Excel:")
st.sidebar.code(", ".join(df.columns))

# === Convert 'Spec Sheet' to clickable link ===
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

# === Column filters ===
filter_columns = [
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

# === Clear button
if "clear_filters" not in st.session_state:
    st.session_state.clear_filters = False

# === Global keyword box ===
global_keyword = st.text_input("🔍 Global Keyword Search (any column)", "").strip().lower()

# === Sidebar filters ===
with st.sidebar:
    st.subheader("🔧 Advanced Column Filters")

    if st.button("🔄 Clear All Filters"):
        st.session_state.clear_filters = True
        st.rerun()

    multiselect_filters = {}
    text_filters = {}

    for col in filter_columns:
        if col in df.columns:
            st.markdown(f"**{col}**")

            # Dropdown
            unique_values = sorted(df[col].dropna().unique().tolist())
            default_multi = [] if st.session_state.clear_filters else None
            selected = st.multiselect(f"{col} (select)", unique_values, default=default_multi, key=f"multi_{col}")
            if selected:
                multiselect_filters[col] = selected

            # Text input
            user_input = st.text_input(f"{col} (contains text)", "", key=f"text_{col}")
            if user_input.strip():
                text_filters[col] = user_input.strip().lower()
        else:
            st.warning(f"⚠️ Column not found in file: `{col}`", icon="⚠️")

    st.session_state.clear_filters = False

# === Apply filters ===
filtered_df = df.copy()

# Dropdown filters
for col, values in multiselect_filters.items():
    filtered_df = filtered_df[filtered_df[col].isin(values)]

# Text input filters
for col, keyword in text_filters.items():
    filtered_df = filtered_df[filtered_df[col].astype(str).str.lower().str.contains(keyword)]

# Global keyword search across all columns
if global_keyword:
    filtered_df = filtered_df[
        filtered_df.apply(lambda row: row.astype(str).str.lower().str.contains(global_keyword).any(), axis=1)
    ]

# === Display table ===
st.markdown(f"Loaded `{filtered_df.shape[0]}` rows × `{filtered_df.shape[1]}` columns")
st.markdown("### 📋 Filtered Results (Click 'Spec Sheet' to view links)")

st.data_editor(
    filtered_df,
    column_config=link_config,
    use_container_width=True,
    disabled=True
)
