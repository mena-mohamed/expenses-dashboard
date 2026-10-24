import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Expenses Dashboard", page_icon="💰", layout="wide")

st.title("💰 لوحة متابعة مصاريفي الشهرية")
st.write("متابعة المصاريف اليومية والإحصاء الوصفي لها.")


@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"])
    return df


df = load_data("expenses.csv")

st.dataframe(df.head())
