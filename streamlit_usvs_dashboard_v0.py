import streamlit as st
import pandas as pd

# === Page setup ===
st.set_page_config(page_title="Global USV's Dashboard", layout="wide")
st.title("📊 Global USV's Dashboard – Excel Viewer")

st.markdown("""
Use the filters below to explore the dataset.

- Use the **Global Keyword Search** above to search across all columns  
- Use the **dropdown filters** on the left to refine your search  
- Click "Clear All Filters" to reset everything  
""")

# === Load Excel ===
df = pd.read_excel("USVs_Summary_improve.xlsx", engine="openpyxl")
df = df.dropna(how="all")
df.columns = df.columns.str.strip()

# === Columns to filter (only those present) ===
available_columns = df.columns.tolist()
filter_columns = [
    col for col in [
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
    ] if col in available_columns
]

# === Register global keyword early so it’s safe to reset
global_keyword = st.text_input("🔍 Global Keyword Search (any column)", "", key="global_keyword").strip().lower()

# === Convert Spec Sheet to clickable links
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

# === Session state reset logic ===
if "clear_filters" not in st.session_state:
    st.session_state.clear_filters = False

# === Sidebar filters ===
with st.sidebar:
    st.subheader("🛠️ Advanced Column Filters")

    if st.button("🔄 Clear All Filters"):
        # ✅ SAFELY reset values only after keys exist
        st.session_state["global_keyword"] = ""
        for col in filter_columns:
            st.session_state[f"multi_{col}"] = []
        st.rerun()

    multiselect_filters = {}
    for col in filter_columns:
        options = sorted(df[col].dropna().unique().tolist())
        selected = st.multiselect(f"{col}", options, key=f"multi_{col}")
        if selected:
            multiselect_filters[col] = selected

# === Apply filters
filtered_df = df.copy()

for col, selected_values in multiselect_filters.items():
    filtered_df = filtered_df[filtered_df[col].isin(selected_values)]

if global_keyword:
    filtered_df = filtered_df[
        filtered_df.apply(lambda row: row.astype(str).str.lower().str.contains(global_keyword).any(), axis=1)
    ]

# === Display filtered results
st.markdown(f"Loaded `{filtered_df.shape[0]}` rows × `{filtered_df.shape[1]}` columns")
st.markdown("### 📋 Filtered Results (Click 'Spec Sheet' to view links)")

st.data_editor(
    filtered_df,
    column_config=link_config,
    use_container_width=True,
    disabled=True
)
