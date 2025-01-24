import streamlit as st
import pandas as pd
import json
import os

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

# Generate a holistic summary of the description
def summarize_description(description):
    sentences = description.split('. ')
    return '. '.join(sentences[:2]) + ('...' if len(sentences) > 2 else '')

# Filter data based on the selected business area
def filter_data(df, business_area):
    df_filtered = df[df["Business Area"] == business_area]
    df_filtered["Summary"] = df_filtered["Description"].apply(summarize_description)
    df_filtered.reset_index(drop=True, inplace=True)  # Ensure proper numbering
    return df_filtered[["Term Type", "Sub-Type", "Summary", "Page #"]]

# Streamlit app
def main():
    st.title("Contract Analysis Report")
    st.write("Upload a contract file and select a business area to generate a report.")

    # File upload
    uploaded_file = st.file_uploader("Upload a contract file", type=["docx", "pdf", "txt"])

    if uploaded_file:
        # Determine which dataset to load based on the file name
        if "ATENA" in uploaded_file.name.upper():
            data = load_atena_data()
            st.success("Aetna annotations loaded successfully!")
        elif "BLUE" in uploaded_file.name.upper():
            data = load_bcbs_data()
            st.success("BCBSA annotations loaded successfully!")
        else:
            st.error("File name must contain either 'ATENA' or 'BLUE' to process.")
            return

        # User selects the business area
        business_area = st.selectbox(
            "Select a Business Area",
            ["Operational Risk Management", "Financial Risk Management"]
        )

        # Filter and display the report
        if business_area:
            report = filter_data(data, business_area)
            if not report.empty:
                st.write(f"### Report for {business_area}")
                st.table(report)  # Display a static, scroll-free table
            else:
                st.warning("No data available for the selected business area.")

if __name__ == "__main__":
    main()
