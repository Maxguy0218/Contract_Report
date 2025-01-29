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
    while len(takeaways) < 5:
        takeaways.append("• [No further details available]")
    return '<br>'.join(takeaways)

# Filter data based on the selected business area
def filter_data(df, business_area):
    df_filtered = df[df["Business Area"] == business_area]
    df_filtered["Key Takeaways"] = df_filtered["Description"].apply(generate_key_takeaways)
    df_filtered.reset_index(drop=True, inplace=True)
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
    fig.update_traces(textinfo="percent+label", pull=[0.1, 0], hole=0.2)
    fig.update_layout(height=700, width=700)
    return fig

# Streamlit app
def main():
    # Set wide layout
    st.set_page_config(layout="wide")
    
    # Custom Styling
    st.markdown("""
        <style>
            .main-title {
                font-size: 36px;
                font-weight: bold;
                color: #FF5733;
                display: flex;
                align-items: center;
            }
            .sidebar .css-1d391kg {
                width: 180px !important;
            }
            .report-container {
                max-width: 100%;
                margin: auto;
            }
            .stDataFrame div {
                overflow: hidden !important;
                white-space: normal !important;
                text-overflow: ellipsis !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Top-left branding
    logo_path = "logo.svg"  # Ensure this file exists in your working directory
    st.sidebar.image(logo_path, width=50)
    st.sidebar.markdown("<p class='main-title'>ContractIQ</p>", unsafe_allow_html=True)
    
    # Sidebar upload section
    uploaded_file = st.sidebar.file_uploader("Upload a contract file", type=["docx", "pdf", "txt"])
    
    status_placeholder = st.empty()
    
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None
    
    if uploaded_file:
        if st.session_state.uploaded_file != uploaded_file:
            st.session_state.uploaded_file = uploaded_file
            st.session_state.data = None
            st.session_state.business_area = None
        
        if "AETNA" in uploaded_file.name.upper():
            st.session_state.data = load_atena_data()
            status_placeholder.success("Aetna annotations loaded successfully!")
        elif "BLUE" in uploaded_file.name.upper():
            st.session_state.data = load_bcbs_data()
            status_placeholder.success("BCBSA annotations loaded successfully!")
        else:
            status_placeholder.error("ERROR.")
            return
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("Select Business Area")
        business_area = st.radio(
            "Select a Business Area",
            ["Operational Risk Management", "Financial Risk Management"]
        )
    
    with col2:
        if uploaded_file and st.session_state.data is not None:
            st.write("### Business Area Distribution")
            st.plotly_chart(plot_pie_chart(st.session_state.data), use_container_width=True)
    
    if st.button("Generate Report"):
        with st.spinner("Generating report..."):
            time.sleep(10)
        
        report = filter_data(st.session_state.data, business_area)
        
        if not report.empty:
            st.markdown("<div class='report-container'>", unsafe_allow_html=True)
            st.write(f"### Report for {business_area}")
            st.write(report.to_html(escape=False), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("No data available for the selected business area.")

if __name__ == "__main__":
    main()
