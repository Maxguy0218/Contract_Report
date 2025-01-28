import streamlit as st
import pandas as pd
import json
import os
import time
import plotly.express as px

# Define the paths for the JSON files relative to the script
ATENA_JSON_PATH = os.path.join(os.getcwd(), "atena_annotations_fixed.json")
BCBS_JSON_PATH = os.path.join(os.getcwd(), "bcbs_annotations_fixed.json")

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

    st.title("Contract Analysis Report")
    st.write("Upload a contract file and select a business area to generate a report.")
    
    # Placeholder for status messages
    status_placeholder = st.empty()

    # File upload
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None

    uploaded_file = st.file_uploader("Upload a contract file", type=["docx", "pdf", "txt"])

    if uploaded_file:
        if st.session_state.uploaded_file != uploaded_file:
            # Flush previous data if a new file is uploaded
            st.session_state.uploaded_file = uploaded_file
            st.session_state.data = None
            st.session_state.business_area = None

        # Determine which dataset to load based on the file name
        if "AETNA" in uploaded_file.name.upper():
            st.session_state.data = load_atena_data()
            status_placeholder.success("Aetna annotations loaded successfully!")
        elif "BLUE" in uploaded_file.name.upper():
            st.session_state.data = load_bcbs_data()
            status_placeholder.success("BCBSA annotations loaded successfully!")
        else:
            status_placeholder.error("ERROR.")
            return

        # Display integrated pie chart for business area distribution
        st.write("### Business Area Distribution")
        pie_chart = plot_pie_chart(st.session_state.data)
        st.plotly_chart(pie_chart, use_container_width=True)  # Fully integrated with Streamlit UI

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
