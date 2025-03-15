import streamlit as st

st.write("🔍 Checking Streamlit Secrets...")
st.write(st.secrets)

api_key = st.secrets.get("NEBIUS_API_KEY", "❌ NOT FOUND")
st.write(f"NEBIUS_API_KEY: {api_key}")
