import streamlit as st
import pandas as pd
import json
import os
import time
import plotly.express as px

# Define the paths for the JSON files and logo
ATENA_JSON_PATH = os.path.join(os.getcwd(), "atena_annotations_fixed.json")
BCBS_JSON_PATH = os.path.join(os.getcwd(), "bcbs_annotations_fixed.json")
LOGO_PATH = "logo.svg"  # Ensure this file is in your project directory

# Load the annotated data from JSON files
def load_atena_data():
    with open(ATENA_JSON_PATH, "r") as f:
        return pd.DataFrame(json.load(f))

def load_bcbs_data():
    with open(BCBS_JSON_PATH, "r") as f:
        return pd.DataFrame(json.load(f))

# Generate key takeaways from the description
def generate_key_takeaways(description):
    sentences = description.split('. ')
    takeaways = [f"• {sentence.strip()}" for sentence in sentences[:5]]
    while len(takeaways) < 5:  # Ensure exactly 5 bullet points
        takeaways.append("• [No further details available]")
    return '\n'.join(takeaways)

# Filter data based on the selected business area
def filter_data(df, business_area):
    df_filtered = df[df["Business Area"] == business_area]
    df_filtered["Key Takeaways"] = df_filtered["Description"].apply(generate_key_takeaways)
    df_filtered.reset_index(drop=True, inplace=True)  # Ensure proper numbering
    return df_filtered[["Term Type", "Sub-Type", "Key Takeaways", "Page #"]]

# Plot pie chart using Plotly
def plot_pie_chart(data):
    counts = data["Business Area"].value_counts()
    fig = px.pie(
        names=counts.index,
        values=counts.values,
        title="Business Area Distribution",
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    fig.update_traces(textinfo="percent+label", pull=[0.1, 0])  # Add interaction effects
    return fig

# Streamlit app
def main():
    # Set wide layout
    st.set_page_config(layout="wide")

    # Custom CSS for jazzy styling
    st.markdown(
        """
        <style>
            .report-container {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .header-container {
                display: flex;
                align-items: center;
            }
            .header-container img {
                width: 50px;
                margin-right: 10px;
            }
            .upload-container {
                display: flex;
                align-items: center;
                gap: 40px;
            }
            .stButton>button {
                background: linear-gradient(135deg, #ff416c, #ff4b2b);
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 16px;
            }
            .stRadio>div {
                display: flex;
                justify-content: center;
                gap: 20px;
            }
            .stTable {
                font-size: 14px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Header with Logo + ContractIQ
    st.markdown(
        f"""
        <div class="header-container">
            <img src="{LOGO_PATH}" alt="Logo">
            <h1 style="display:inline;">ContractIQ</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("### Upload a contract file and analyze business risks")

    # Layout for Upload & Pie Chart (Side by Side)
    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader("Upload a contract file", type=["docx", "pdf", "txt"])

    with col2:
        if uploaded_file:
            st.write("### Business Area Distribution")
            if "AETNA" in uploaded_file.name.upper():
                data = load_atena_data()
            elif "BLUE" in uploaded_file.name.upper():
                data = load_bcbs_data()
            else:
                st.error("ERROR. Unsupported file type.")
                return

            pie_chart = plot_pie_chart(data)
            st.plotly_chart(pie_chart, use_container_width=True)  # Right-aligned pie chart

    if uploaded_file:
        # Determine which dataset to load based on the file name
        if "AETNA" in uploaded_file.name.upper():
            st.session_state.data = load_atena_data()
            st.success("Aetna annotations loaded successfully!")
        elif "BLUE" in uploaded_file.name.upper():
            st.session_state.data = load_bcbs_data()
            st.success("BCBSA annotations loaded successfully!")
        else:
            st.error("ERROR.")
            return

        # Business area selection using radio buttons
        business_area = st.radio(
            "Select a Business Area",
            ["Operational Risk Management", "Financial Risk Management"]
        )

        # Button to generate the report
        if st.button("Generate Report"):
            # Simulate generating the report
            with st.spinner("Generating report..."):
                time.sleep(10)

            # Generate and display the report
            report = filter_data(st.session_state.data, business_area)

            if not report.empty:
                st.write(f"### Report for {business_area}")
                st.table(report)  # Expanded table width
            else:
                st.warning("No data available for the selected business area.")

if __name__ == "__main__":
    main()
