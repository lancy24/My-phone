import streamlit as st


st.header("Summary Statistics")

if "df" in st.session_state:
    st.dataframe(st.session_state["df"].describe())
else:
    st.info("Upload a CSV on the Data Explorer page first.")