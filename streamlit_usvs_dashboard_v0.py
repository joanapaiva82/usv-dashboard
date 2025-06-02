import streamlit as st
import pandas as pd

st.set_page_config(page_title="Global USV's Dashboard", layout="wide")
st.title("📊 Global USV's Dashboard – Excel Viewer")

st.markdown("""
Use the filters below to interactively explore the dataset.  
All columns are searchable and sortable. Filter by any category just like in Excel.
""")

# === Load and clean Excel ===
df = pd.read_excel("USVs_Summary_improve.xlsx", engine="openpyxl")
df = df.dropna(how="all")
df.columns = df.columns.str.strip()

# === Convert Spec Sheet column to Streamlit link config ===
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

# === Clear filter logic
if "clear_filters" not in st.session_state:
    st.session_state.clear_filters = False

# === Filters
with st.sidebar:
    st.subheader("🔍 Filters")
    if st.button("🔄 Clear All Filters"):
        st.session_state.clear_filters = True
        st.rerun()

    filters = {}
    for col in df.select_dtypes(include=['object', 'category']).columns:
        values = df[col].dropna().unique().tolist()
        if 1 < len(values) < 40:
            default = [] if st.session_state.clear_filters else None
            selected = st.multiselect(col, values, default=default, key=col)
            if selected:
                filters[col] = selected

    st.session_state.clear_filters = False

# === Apply Filters
filtered_df = df.copy()
for col, selected_vals in filters.items():
    filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]

# === Display Table with link rendering
st.markdown(f"Loaded `{filtered_df.shape[0]}` rows × `{filtered_df.shape[1]}` columns")
st.markdown("### 📋 Filtered Results (Click 'Spec Sheet' to view links)")
st.dataframe(filtered_df, column_config=link_config, use_container_width=True)
