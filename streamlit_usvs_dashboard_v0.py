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

# === Detect link columns and convert ===
if "Spec Sheet" in df.columns:
    df["Spec Sheet"] = df["Spec Sheet"].astype(str).apply(
        lambda x: f"[Spec Sheet]({x})" if x.startswith("http") else x
    )

# === Init session state for clearing filters ===
if "clear_filters" not in st.session_state:
    st.session_state.clear_filters = False

# === Sidebar filters ===
with st.sidebar:
    st.subheader("🧊 Filters")
    if st.button("🔄 Clear All Filters"):
        st.session_state.clear_filters = True
        st.rerun()

    filters = {}
    for col in df.select_dtypes(include=['object', 'category']).columns:
        options = df[col].dropna().unique().tolist()
        if 1 < len(options) < 40:
            default_vals = [] if st.session_state.clear_filters else None
            selected = st.multiselect(
                label=col,
                options=options,
                default=default_vals,
                key=col
            )
            if selected:
                filters[col] = selected

    st.session_state.clear_filters = False

# === Apply filters ===
filtered_df = df.copy()
for col, selected_vals in filters.items():
    filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]

# === Display as styled Markdown Table ===
st.markdown(f"Loaded `{filtered_df.shape[0]}` rows × `{filtered_df.shape[1]}` columns")
st.markdown("### 📋 Filtered Results (Click links to open spec sheets)")

# Convert to markdown with link formatting
st.markdown(filtered_df.to_markdown(index=False), unsafe_allow_html=True)
