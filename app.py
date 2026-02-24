import streamlit as st
import pandas as pd
import plotly.express as px

# STEP 2 — Page Config
st.set_page_config(layout="wide")
st.title("Provisional Natality Data Dashboard")
st.subheader("Birth Analysis by State and Gender")

# STEP 3 — Load Data
try:
    df = pd.read_csv("Provisional_Natality_2025_CDC.csv")
except FileNotFoundError:
    st.error("Dataset file not found in repository.")
    st.stop()

# Normalize column names
df.columns = (
    df.columns.str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# Logical field mapping
required_fields = {
    "state_of_residence": None,
    "month": None,
    "sex_of_infant": None,
    "births": None,
}

for col in df.columns:
    if "state" in col and "residence" in col:
        required_fields["state_of_residence"] = col
    elif col == "month":
        required_fields["month"] = col
    elif "sex" in col:
        required_fields["sex_of_infant"] = col
    elif "birth" in col:
        required_fields["births"] = col

missing_fields = [k for k, v in required_fields.items() if v is None]

if missing_fields:
    st.error(f"Missing required logical fields: {missing_fields}")
    st.write("Available columns:", df.columns.tolist())
    st.stop()

# Rename dynamically matched columns to standard names
df = df.rename(columns={
    required_fields["state_of_residence"]: "state_of_residence",
    required_fields["month"]: "month",
    required_fields["sex_of_infant"]: "sex_of_infant",
    required_fields["births"]: "births",
})

# Convert births to numeric
df["births"] = pd.to_numeric(df["births"], errors="coerce")
df = df.dropna(subset=["births"])

# STEP 4 — Sidebar Filters
st.sidebar.header("Filters")

state_options = sorted(df["state_of_residence"].dropna().unique())
month_options = sorted(df["month"].dropna().unique())
gender_options = sorted(df["sex_of_infant"].dropna().unique())

selected_states = st.sidebar.multiselect(
    "Select State(s)",
    options=["All"] + state_options,
    default=["All"]
)

selected_months = st.sidebar.multiselect(
    "Select Month(s)",
    options=["All"] + month_options,
    default=["All"]
)

selected_genders = st.sidebar.multiselect(
    "Select Gender(s)",
    options=["All"] + gender_options,
    default=["All"]
)

# STEP 5 — Filtering Logic
filtered_df = df.copy()

if "All" not in selected_states:
    filtered_df = filtered_df[filtered_df["state_of_residence"].isin(selected_states)]

if "All" not in selected_months:
    filtered_df = filtered_df[filtered_df["month"].isin(selected_months)]

if "All" not in selected_genders:
    filtered_df = filtered_df[filtered_df["sex_of_infant"].isin(selected_genders)]

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# STEP 6 — Aggregation
agg_df = (
    filtered_df
    .groupby(["state_of_residence", "sex_of_infant"], as_index=False)["births"]
    .sum()
)

agg_df = agg_df.sort_values("state_of_residence")

# STEP 7 — Plot
fig = px.bar(
    agg_df,
    x="state_of_residence",
    y="births",
    color="sex_of_infant",
    title="Total Births by State and Gender",
)

fig.update_layout(
    legend_title="Gender",
    plot_bgcolor="white",
    paper_bgcolor="white",
    xaxis_title="State of Residence",
    yaxis_title="Total Births",
)

st.plotly_chart(fig, use_container_width=True)

# STEP 8 — Show Filtered Table
st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)
