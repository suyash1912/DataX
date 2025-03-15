import os
import streamlit as st
st.set_page_config(page_title="DataX - AI Data Analyzer", layout="wide")  # ✅ First Streamlit command

import pandas as pd
import plotly.express as px
from openai import OpenAI
from pandasql import sqldf

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize Nebius AI client with Meta-Llama 3.1 70B Instruct
api_key = st.secrets.get("NEBIUS_API_KEY", os.getenv("NEBIUS_API_KEY"))  

if not api_key:
    st.error("🚨 API Key is missing! Set it in Streamlit Secrets or as an environment variable.")
else:
    client = OpenAI(
        base_url="https://api.studio.nebius.com/v1/",
        api_key=api_key
    )

# Streamlit UI Setup


st.title(" DataX: AI-Powered Data Analyzer")

# File Upload Section
uploaded_file = st.file_uploader(" Upload a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Read file into a DataFrame
    file_extension = uploaded_file.name.split(".")[-1]
    if file_extension == "csv":
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success(" File Uploaded Successfully!")

    # Show dataframe preview
    st.write("###  Data Preview")
    st.dataframe(df.head())

    # Display Available Column Names
    st.write(" **Column Names for Reference**")
    st.code(", ".join(f'"{col}"' for col in df.columns), language="sql")

    # 🔥 **AI-Powered Data Insights (Meta-Llama 3.1 70B)**
    st.subheader(" Ask AI About Your Data")
    ai_query = st.text_area("What do you want to know?", "Summarize this dataset")

    if st.button(" Get AI Insights"):
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
            st.error(f" Error: {e}")

    # 📝 **SQL Query Section**
    st.subheader(" Run SQL Queries on Data")
    query = st.text_area("Write your SQL query here", "SELECT * FROM df LIMIT 5")

    if st.button(" Run SQL Query"):
        try:
            # Execute the SQL query on the DataFrame
            query_result = sqldf(query, locals())

            # Display results
            st.write("###  Query Results")
            st.dataframe(query_result)

            # Visualization Option
            if st.checkbox(" Visualize Query Result"):
                columns = query_result.columns.tolist()
                x_axis = st.selectbox("Select X-axis", columns)
                y_axis = st.selectbox("Select Y-axis", columns)

                fig = px.bar(query_result, x=x_axis, y=y_axis, title="SQL Query Visualization")
                st.plotly_chart(fig)

        except Exception as e:
            st.error(f" Error in SQL Query: {e}")

# Footer
st.markdown("---")
st.markdown(" **DataX** - AI-Powered Data Analysis Tool 🚀")
