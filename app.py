import streamlit as st
import pandas as pd
import json
import os
import time
from fpdf import FPDF

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

# Generate PDF for download
def generate_pdf(dataframe, business_area):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Contract Analysis Report: {business_area}", ln=True, align='C')
    pdf.ln(10)
    for i, row in dataframe.iterrows():
        pdf.set_font("Arial", style="B", size=11)
        pdf.cell(200, 10, txt=f"Record #{i+1}", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt=f"Term Type: {row['Term Type']}", ln=True)
        pdf.cell(200, 10, txt=f"Sub-Type: {row['Sub-Type']}", ln=True)
        pdf.multi_cell(0, 10, txt=f"Key Takeaways:\n{row['Key Takeaways']}")
        pdf.cell(200, 10, txt=f"Page #: {row['Page #']}", ln=True)
        pdf.ln(5)
    return pdf.output(dest="S").encode("latin1")

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
            status_placeholder.error("File name must contain either 'ATENA' or 'BLUE' to process.")
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

                # PDF download
                pdf_data = generate_pdf(report, business_area)
                st.download_button(
                    label="Download Report as PDF",
                    data=pdf_data,
                    file_name="Contract_Analysis_Report.pdf",
                    mime="application/pdf"
                )
            else:
                st.warning("No data available for the selected business area.")

if __name__ == "__main__":
    main()
