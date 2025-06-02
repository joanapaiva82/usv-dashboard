import streamlit as st
import pandas as pd

# === Page config ===
st.set_page_config(page_title="Global USV's Dashboard", layout="wide")
st.title("📊 Global USV's Dashboard – Excel Viewer")

st.markdown("""
Use the filters below to explore the dataset.  
- Type in the global **keyword box** to search across all columns  
- Use **dropdown filters** or **text search** per column  
- Click "Clear All Filters" to reset everything
""")

# === Load Excel ===
df = pd.read_excel("USVs_Summary_improve.xlsx", engine="openpyxl")
df = df.dropna(how="all")
df.columns = df.columns.str.strip()

# === Columns to filter ===
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

# === Convert Spec Sheet to clickable links ===
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

# === Sidebar filters ===
with st.sidebar:
    st.caption("🧾 Columns found in Excel:")
    st.code(", ".join(df.columns))

    st.subheader("🔧 Keyword Filters")

    # === Clear button ===
    if st.button("🔄 Clear All Filters"):
        # Reset all session states for filters
        st.session_state["global_keyword"] = ""
        for col in filter_columns:
            st.session_state[f"multi_{col}"] = []
            st.session_state[f"text_{col}"] = ""
        st.rerun()

    # === Global search box
    global_keyword = st.text_input("🔍 Global Keyword Search (any column)", "", key="global_keyword").strip().lower()

    # === Filters
    multiselect_filters = {}
    text_filters = {}

    for col in filter_columns:
        if col in df.columns:
            st.markdown(f"**{col}**")

            # Dropdown filter
            options = sorted(df[col].dropna().unique().tolist())
            selected = st.multiselect(f"{col} (select)", options, key=f"multi_{col}")
            if selected:
                multiselect_filters[col] = selected

            # Text input filter
            user_input = st.text_input(f"{col} (contains text)", key=f"text_{col}")
            if user_input.strip():
                text_filters[col] = user_input.strip().lower()
        else:
            st.warning(f"⚠️ Column not found in Excel: `{col}`", icon="⚠️")

# === Apply all filters ===
filtered_df = df.copy()

# Apply dropdown filters
for col, selected_values in multiselect_filters.items():
    filtered_df = filtered_df[filtered_df[col].isin(selected_values)]

# Apply text input filters
for col, keyword in text_filters.items():
    filtered_df = filtered_df[
        filtered_df[col].astype(str).str.lower().str.contains(keyword)
    ]

# Apply global keyword filter
if global_keyword:
    filtered_df = filtered_df[
        filtered_df.apply(lambda row: row.astype(str).str.lower().str.contains(global_keyword).any(), axis=1)
    ]

# === Display filtered results ===
st.markdown(f"Loaded `{filtered_df.shape[0]}` rows × `{filtered_df.shape[1]}` columns")
st.markdown("### 📋 Filtered Results (Click 'Spec Sheet' to view links)")

st.data_editor(
    filtered_df,
    column_config=link_config,
    use_container_width=True,
    disabled=True
)
