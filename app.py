import streamlit as st
import pandas as pd
import json
import os
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
    return '\n'.join(takeaways)

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
    fig.update_traces(textinfo="percent+label", pull=[0.1, 0])
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
                width: 200px !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Top-left branding
    logo_path = "logo.svg"  # Ensure this file exists in your working directory
    st.sidebar.image(logo_path, width=50)
    st.sidebar.markdown("<p class='main-title'>ContractIQ</p>", unsafe_allow_html=True)
    
    # Sidebar upload section
    uploaded_file = st.sidebar.file_uploader("Upload JSON File", type=["json"], key="file_uploader")
    
    # Main content layout
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("Contract Analysis Report")
        
        if uploaded_file:
            df = pd.read_json(uploaded_file)
            business_areas = df["Business Area"].unique()
            selected_area = st.selectbox("Select Business Area", business_areas)
            filtered_data = filter_data(df, selected_area)
            st.dataframe(filtered_data)
    
    with col2:
        if uploaded_file:
            st.plotly_chart(plot_pie_chart(df), use_container_width=True)

if __name__ == "__main__":
    main()
