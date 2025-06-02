import streamlit as st
import pandas as pd

st.set_page_config(page_title="Global USV's Dashboard", layout="wide")

st.title("📊 Global USV's Dashboard – Excel Viewer")

st.markdown("""
Use the filters below to interactively explore the dataset.  
All columns are searchable and sortable. You can also download the filtered result as a CSV.
""")

# === Load Excel File ===
df = pd.read_excel("USVs_Summary_improve.xlsx", engine="openpyxl")
df.columns = df.columns.str.strip()  # Clean whitespace from headers

st.caption(f"Loaded `{df.shape[0]}` rows × `{df.shape[1]}` columns")

# === Filter UI in Sidebar ===
with st.sidebar:
    st.markdown("### 🔍 Filter Options")
    filter_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    filters = {}
    for col in filter_cols:
        unique_vals = df[col].dropna().unique().tolist()
        if 1 < len(unique_vals) < 40:  # skip free-text or too large domains
            selected = st.multiselect(f"{col}:", options=unique_vals, default=unique_vals)
            filters[col] = selected

# === Apply Filters ===
filtered_df = df.copy()
for col, selected_vals in filters.items():
    filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]

# === Display Table ===
st.markdown("### 📊 Filtered Data Table")
st.dataframe(filtered_df, use_container_width=True)

# === Download Button ===
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv,
    file_name="filtered_usv_summary.csv",
    mime="text/csv"
)
