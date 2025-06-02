import streamlit as st
import pandas as pd

st.set_page_config(page_title="Global USV's Dashboard", layout="wide")
st.title("📊 Global USV's Dashboard – Excel Viewer")

st.markdown("""
Use the filters below to interactively explore the dataset.  
All columns are searchable and sortable. You can also download filtered results as a CSV.
""")

# === Load Excel & clean ===
df = pd.read_excel("USVs_Summary_improve.xlsx", engine="openpyxl")
df = df.dropna(how="all")  # remove completely empty rows
df.columns = df.columns.str.strip()

# === Detect and format link columns ===
link_cols = [col for col in df.columns if df[col].astype(str).str.startswith("http").any()]
if link_cols:
    st.markdown("🔗 Clickable links detected in:")
    for col in link_cols:
        df[col] = df[col].astype(str).apply(lambda x: f"[Open]({x})" if x.startswith("http") else x)
        st.markdown(f"- **{col}**")

st.caption(f"Loaded `{df.shape[0]}` rows × `{df.shape[1]}` columns")

# === Setup session state for clear button ===
if "clear" not in st.session_state:
    st.session_state["clear"] = False

# === Sidebar Filters ===
with st.sidebar:
    st.markdown("### 🎛️ Filters")
    if st.button("🔄 Clear All Filters"):
        st.session_state["clear"] = True
        st.experimental_rerun()

    filter_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    filters = {}

    for col in filter_cols:
        unique_vals = df[col].dropna().unique().tolist()
        if 1 < len(unique_vals) < 40:
            default_vals = [] if st.session_state["clear"] else unique_vals
            selected = st.multiselect(f"{col}:", options=unique_vals, default=default_vals, key=col)
            if selected:
                filters[col] = selected

    if st.session_state["clear"]:
        st.session_state["clear"] = False

# === Apply Filters ===
filtered_df = df.copy()
for col, selected_vals in filters.items():
    filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]

# === Display Results ===
st.markdown("### 📊 Filtered Results")
st.dataframe(filtered_df, use_container_width=True)

# === Download Button ===
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download as CSV", data=csv, file_name="filtered_usv_data.csv", mime="text/csv")
