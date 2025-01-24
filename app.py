import streamlit as st
import pandas as pd
import json
import os
import time

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
    return '\n'.join(takeaways)

# Filter data based on the selected business area
def filter_data(df, business_area):
    df_filtered = df[df["Business Area"] == business_area]
    df_filtered["Key Takeaways"] = df_filtered["Description"].apply(generate_key_takeaways)
    df_filtered.reset_index(drop=True, inplace=True)  # Ensure proper numbering
    return df_filtered[["Term Type", "Sub-Type", "Key Takeaways", "Page #"]]

# Streamlit app
def main():
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
        if "ATENA" in uploaded_file.name.upper():
            st.session_state.data = load_atena_data()
            status_placeholder.success("Aetna annotations loaded successfully!")
        elif "BLUE" in uploaded_file.name.upper():
            st.session_state.data = load_bcbs_data()
            status_placeholder.success("BCBSA annotations loaded successfully!")
        else:
            status_placeholder.error("File name must contain either 'ATENA' or 'BLUE' to process.")
            return

        # Business area selection using checkboxes
        st.write("Select a Business Area:")
        operational_risk = st.checkbox("Operational Risk Management")
        financial_risk = st.checkbox("Financial Risk Management")

        # Button to generate the report
        if st.button("Generate Report"):
            # Determine selected business area
            selected_areas = []
            if operational_risk:
                selected_areas.append("Operational Risk Management")
            if financial_risk:
                selected_areas.append("Financial Risk Management")

            # Ensure at least one area is selected
            if not selected_areas:
                st.warning("Please select at least one business area.")
                return

            # Simulate generating the report
            with st.spinner("Generating report..."):
                time.sleep(10)

            # Generate and display the report
            report_frames = [filter_data(st.session_state.data, area) for area in selected_areas]
            full_report = pd.concat(report_frames, ignore_index=True)

            if not full_report.empty:
                st.write(f"### Report")
                st.table(full_report)
            else:
                st.warning("No data available for the selected business area.")

if __name__ == "__main__":
    main()
