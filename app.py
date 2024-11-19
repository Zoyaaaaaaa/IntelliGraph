import os
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
from pandasai import SmartDatalake
import plotly.express as px

# Set your PandasAI API key
load_dotenv()
os.environ["PANDASAI_API_KEY"] = os.getenv("PANDASAI_API_KEY") # Replace with your actual API key

# Streamlit app setup
st.set_page_config(page_title="Data Analysis Tool", page_icon="📊", layout="wide")

# Custom CSS for dark mode aesthetics
st.markdown("""
    <style>
    body {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    .title {
        font-size: 2.5rem;
        text-align: center;
        color: #ffffff;
        margin-bottom: 20px;
    }
    .header {
        background-color: #2d2d2d;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    .sidebar {
        background-color: #2d2d2d;
        border-radius: 8px;
        padding: 15px;
    }
    .button {
        background-color: #007BFF;
        color: white;
        border: None;
        border-radius: 5px;
        padding: 10px 15px;
        cursor: pointer;
    }
    .button:hover {
        background-color: #0056b3;
    }
    .instruction {
        font-size: 1.1rem;
        color: #ffffff;
        line-height: 1.8;
    }
    </style>
""", unsafe_allow_html=True)

# Main title
st.markdown('<h1 class="title">📊 Data Analysis Tool</h1>', unsafe_allow_html=True)

# Main features section
st.markdown("""
<div class="header">
    <h2>🌟 Features</h2>
    <p class="instruction">
        - 📁 Upload CSV or Excel Files: Easily upload your datasets.<br>
        - 🔍 Interactive Data Exploration: Ask questions about your data and get instant answers.<br>
        - 📊 Visualize Data: Create scatter plots, bar charts, line graphs, and pie charts to explore trends and distributions.<br>
        - 📈 Summary Statistics: Get descriptive statistics for your data at a glance.<br>
        - 🔗 Correlation Analysis: Visualize correlations between numeric variables with heatmaps.<br>
        - 💾 Download Cleaned Data: Download a cleaned version of your dataset for further analysis.<br>
    </p>
</div>
""", unsafe_allow_html=True)


# Sidebar for file upload
st.sidebar.header("Upload Your Data")

uploaded_file = st.sidebar.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])
st.sidebar.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    # Load the data
    if uploaded_file.name.endswith('.csv'):
        data = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        data = pd.read_excel(uploaded_file)
    
    # Display the uploaded data
    st.subheader("Uploaded Data")
    st.dataframe(data)

    # Create a SmartDatalake for analysis
    lake = SmartDatalake([data])

    # User query input
    st.sidebar.header("Ask a Question")
    user_question = st.sidebar.text_input("What do you want to know about the data?")

    if user_question:
        try:
            response = lake.chat(user_question)
            response_text = response[:400]

            st.sidebar.markdown(
                f"""
                <div style="background-color:#000000; padding: 10px; border-radius: 5px; color: white;">
                    <h4 style="margin: 0;">Response:</h4>
                    <p style="margin: 5px 0;">{response_text}</p>
                </div>
                """,
                unsafe_allow_html=True)
            # st.sidebar.markdown(f"**Response:** {response[:400]}")  # Limit response to 100 characters
        except Exception as e:
            st.sidebar.error(f"Error: {str(e)}")

    # Visualizations
    st.sidebar.subheader("Visualizations")
    
    if st.sidebar.checkbox("Show Plot"):
        if data.columns.size > 1:
            plot_type = st.sidebar.selectbox("Select Plot Type", options=["Scatter", "Bar", "Line", "Pie"])
            x_axis = st.sidebar.selectbox("Select X-axis", options=data.columns)
            y_axis = st.sidebar.selectbox("Select Y-axis", options=data.columns)

            if st.sidebar.button("Generate Plot", key="plot_button"):
                if plot_type == "Scatter":
                    fig = px.scatter(data, x=x_axis, y=y_axis, title=f"Scatter Plot of {y_axis} vs {x_axis}")
                elif plot_type == "Bar":
                    fig = px.bar(data, x=x_axis, y=y_axis, title=f"Bar Chart of {y_axis} by {x_axis}")
                elif plot_type == "Line":
                    fig = px.line(data, x=x_axis, y=y_axis, title=f"Line Chart of {y_axis} over {x_axis}")
                elif plot_type == "Pie":
                    fig = px.pie(data, names=x_axis, values=y_axis, title=f"Pie Chart of {y_axis} by {x_axis}")
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Not enough columns to create a plot.")

    # Display summary statistics
    if st.sidebar.checkbox("Show Summary Statistics"):
        st.subheader("Summary Statistics")
        st.write(data.describe())

    # Display correlation matrix
    if st.sidebar.checkbox("Show Correlation Matrix"):
        if data.select_dtypes(include='number').shape[1] > 1:
            correlation_matrix = data.corr()
            st.subheader("Correlation Matrix")
            st.write(correlation_matrix)
            st.subheader("Heatmap of Correlation")
            fig = px.imshow(correlation_matrix, text_auto=True, aspect="auto")
            st.plotly_chart(fig)
        else:
            st.warning("Not enough numeric columns to compute correlation.")

    # Allow download of cleaned data
    if st.sidebar.checkbox("Download Cleaned Data"):
        cleaned_data = data.dropna()  # Example cleaning step
        csv = cleaned_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Cleaned Data (CSV)",
            data=csv,
            file_name="cleaned_data.csv",
            mime="text/csv",
            key="download_cleaned_data"
        )

# Success message
st.success("Upload your data, ask questions, and visualize results!")

