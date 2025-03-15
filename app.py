import os
import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI
from pandasql import sqldf
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("NEBIUS_API_KEY")

if not api_key:
    st.error("API Key is missing! Set it as an environment variable in Render.")
else:
    client = OpenAI(
        base_url="https://api.studio.nebius.com/v1/",
        api_key=api_key
    )

# Streamlit UI Setup
st.set_page_config(page_title="DataX - AI Data Analyzer", layout="wide")
st.title("DataX: AI-Powered Data Analyzer")

# File Upload Section
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Read file into a DataFrame
    file_extension = uploaded_file.name.split(".")[-1]
    df = pd.read_csv(uploaded_file) if file_extension == "csv" else pd.read_excel(uploaded_file)
    st.success("File Uploaded Successfully!")

    # Show Data Preview
    st.write("### Data Preview")
    st.dataframe(df.head())

    # Display Column Names
    st.write("Column Names for Reference")
    st.code(", ".join(f'"{col}"' for col in df.columns), language="sql")

    # Organizing Layout with 50:50 division
    st.write("---")
    col1, col2 = st.columns([1, 1])  # 50:50 column division

    with col1:
        # AI Insights Section
        st.subheader("Ask AI About Your Data")
        ai_query = st.text_area("What do you want to know?")
        if st.button("Get AI Insights"):
            try:
                response = client.chat.completions.create(
                    model="meta-llama/Meta-Llama-3.1-70B-Instruct",
                    max_tokens=512,
                    temperature=0.6,
                    top_p=0.9,
                    extra_body={"top_k": 50},
                    messages=[
                        {"role": "system", "content": "You are an expert data analyst."},
                        {"role": "user", "content": f"Analyze the following dataset and answer this query: {ai_query}\n\n{df.head(10).to_string()}"}
                    ]
                )
                st.write("### AI Response")
                st.write(response.choices[0].message.content)

            except Exception as e:
                st.error(f"Error: {e}")
    
    with col2:
        # SQL Query Section
        st.subheader("Run SQL Queries on Data")
        query = st.text_area("Write your SQL query here")
        if st.button("Run SQL Query"):
            try:
                # Execute SQL query on DataFrame
                query_result = sqldf(query, {"df": df})

                # Display Results
                st.write("### Query Results")
                st.dataframe(query_result)

                # Visualization Option
                if st.checkbox("Visualize Query Result"):
                    columns = query_result.columns.tolist()
                    x_axis = st.selectbox("Select X-axis", columns)
                    y_axis = st.selectbox("Select Y-axis", columns)

                    fig = px.bar(query_result, x=x_axis, y=y_axis, title="SQL Query Visualization")
                    st.plotly_chart(fig)

            except Exception as e:
                st.error(f"Error in SQL Query: {e}")

    # Additional Visualization Section (Global for the Data)
    st.write("---")
    st.subheader("Visualize Your Data")
    visualize_option = st.selectbox("Select Chart Type", ["Bar Chart", "Line Chart", "Pie Chart", "Scatter Plot"])

    column = st.selectbox("Select Column for Visualization", df.columns)

    if visualize_option == "Bar Chart":
        fig = px.bar(df, x=column, title=f"Bar Chart of {column}")
        st.plotly_chart(fig)
    elif visualize_option == "Line Chart":
        fig = px.line(df, x=column, title=f"Line Chart of {column}")
        st.plotly_chart(fig)
    elif visualize_option == "Pie Chart":
        fig = px.pie(df, names=column, title=f"Pie Chart of {column}")
        st.plotly_chart(fig)
    elif visualize_option == "Scatter Plot":
        scatter_x = st.selectbox("Select X-axis for Scatter Plot", df.columns)
        scatter_y = st.selectbox("Select Y-axis for Scatter Plot", df.columns)
        fig = px.scatter(df, x=scatter_x, y=scatter_y, title=f"Scatter Plot of {scatter_x} vs {scatter_y}")
        st.plotly_chart(fig)

# Footer
st.markdown("---")
st.markdown("DataX - AI-Powered Data Analysis Tool")
