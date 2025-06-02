import streamlit as st
import pandas as pd

st.set_page_config(page_title="Global USV's Dashboard", layout="wide")
st.title("📊 Global USV's Dashboard – Excel Viewer")

st.markdown("""
Use the filters below to interactively explore the dataset.  
All filters perform keyword-based matching, so partial values like `MBES` will still find matching rows.
""")

# === Load dataset ===
df = pd.read_csv("USVs_SUmmary.csv")
df = df.dropna(how="all")
df.columns = df.columns.str.strip()

# === Ensure Spec Sheet links are clean ===
link_config = {}
if "Spec Sheet" in df.columns:
    df["Spec Sheet"] = df["Spec Sheet"].astype(str).apply(
        lambda x: x if x.startswith("http") else ""
    )
    link_config["Spec Sheet"] = st.column_config.LinkColumn(
        "Spec Sheet", help="Click to view spec sheet", validate="^https?:\\/\\/.+$"
    )

# === Session filter tracking ===
if "clear_filters" not in st.session_state:
    st.session_state.clear_filters = False

# === Sidebar filters ===
with st.sidebar:
    st.subheader("🔍 Keyword Filters")

    if st.button("🔄 Clear All Filters"):
        for col in df.columns:
            if df[col].dtype == "object":
                st.session_state[col] = ""
        st.rerun()

    filters = {}
    for col in df.columns:
        if df[col].dtype == "object":
            current_value = st.session_state.get(col, "")
            search_input = st.text_input(f"{col} (keywords)", value=current_value, key=col)
            if search_input.strip():
                filters[col] = search_input.lower().split(",")

# === Apply keyword filters ===
filtered_df = df.copy()
for col, keywords in filters.items():
    filtered_df = filtered_df[filtered_df[col].astype(str).str.lower().apply(
        lambda cell: any(keyword.strip() in cell for keyword in keywords)
    )]

# === Display summary and table ===
st.markdown(f"Loaded **{filtered_df.shape[0]}** rows × **{filtered_df.shape[1]}** columns")
st.markdown("### 📋 Filtered Results (Click 'Spec Sheet' to view links)")
st.dataframe(filtered_df, column_config=link_config, use_container_width=True)
