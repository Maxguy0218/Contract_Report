import streamlit as st
import pandas as pd
import json
import os
import time
import plotly.express as px
import base64

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
def plot_pie_chart(data, show_labels=True):
    counts = data["Business Area"].value_counts()
    fig = px.pie(
        names=counts.index,
        values=counts.values,
        title="Business Area Distribution",
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    textinfo = "percent+label" if show_labels else "none"
    fig.update_traces(textinfo=textinfo, pull=[0.1, 0], hole=0.2)
    fig.update_layout(height=600, width=850, margin=dict(l=150, r=150, t=50, b=50))
    return fig

# Function to encode the logo in Base64
def get_base64_image(file_path):
    with open(file_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Streamlit app
def main():
    # Set wide layout
    st.set_page_config(layout="wide")
    
    # Custom Styling
    st.markdown("""
        <style>
            .header-container {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .main-title {
                font-size: 48px;
                font-weight: bold;
                color: #FF5733;
            }
            .sidebar-title {
                font-size: 24px;
                font-weight: bold;
                color: #FF5733;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .sidebar .css-1d391kg {
                width: 180px !important;
            }
            .report-container {
                max-width: 100%;
                margin: auto;
            }
            th {
                text-align: left !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Branding in sidebar and main page
    logo_path = "logo.svg"
    if os.path.exists(logo_path):
        logo_base64 = get_base64_image(logo_path)
        logo_img = f'<img src="data:image/svg+xml;base64,{logo_base64}" alt="Logo" style="width: 50px; vertical-align: middle;">'
    else:
        logo_img = "[Logo Missing]"

    st.sidebar.markdown(
        f"""
        <div class="sidebar-title">
            {logo_img}
            ContractIQ
        </div>
        """, unsafe_allow_html=True
    )
    
    st.markdown(
        f"""
        <div class="header-container">
            <img src="data:image/svg+xml;base64,{logo_base64}" alt="Logo" style="width: 80px; vertical-align: middle;">
            <span class="main-title">ContractIQ</span>
        </div>
        """, unsafe_allow_html=True
    )
    
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
        
        time.sleep(4)
        status_placeholder.empty()
    
    col1, col2 = st.columns([2, 4])
    
    with col1:
        st.subheader("Select Business Area")
        business_area = st.radio(
            "Select a Business Area",
            ["Operational Risk Management", "Financial Risk Management"]
        )
        
        if st.button("Generate Report"):
            with st.spinner("Generating report..."):
                time.sleep(10)
            
            report = filter_data(st.session_state.data, business_area)
    
    with col2:
        if uploaded_file and st.session_state.data is not None:
            show_labels = not st.sidebar.expander("Options").checkbox("Hide Sidebar Labels")
            pie_chart_placeholder = st.empty()
            pie_chart_placeholder.write("Generating graphics...")
            time.sleep(4)
            pie_chart_placeholder.empty()
            st.write("### Business Area Distribution")
            st.plotly_chart(plot_pie_chart(st.session_state.data, show_labels=show_labels), use_container_width=True)
    
    # Ensure report is displayed below pie chart
    if "report" in locals() and not report.empty:
        st.markdown("<div class='report-container'>", unsafe_allow_html=True)
        st.write(f"### Report for {business_area}")
        st.write(report.to_html(escape=False), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    elif "report" in locals():
        st.warning("No data available for the selected business area.")

if __name__ == "__main__":
    main()
