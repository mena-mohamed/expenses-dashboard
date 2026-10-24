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

# Sidebar
st.sidebar.header("⚙️ خيارات التصفية")

df["Month"] = df["Date"].dt.strftime("%Y-%m")

months = ["All"] + sorted(df["Month"].unique())
selected_month = st.sidebar.selectbox("اختاري الشهر", months)

categories = ["All"] + list(df["Category"].unique())
selected_cat = st.sidebar.selectbox("اختاري الفئة", categories)

filtered_df = df.copy()
if selected_month != "All":
    filtered_df = filtered_df[filtered_df["Month"] == selected_month]
if selected_cat != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_cat]

# KPIs
st.markdown("### 📊 الملخص")
col1, col2, col3, col4 = st.columns(4)

count = len(filtered_df)
total = filtered_df["Amount"].sum()
avg = filtered_df["Amount"].mean() if count > 0 else 0
top_cat = filtered_df.groupby("Category")["Amount"].sum().idxmax() if count > 0 else "-"

col1.metric("عدد العمليات", count)
col2.metric("إجمالي المصروفات", f"{total:,.0f} جنيه")
col3.metric("متوسط المصروف", f"{avg:.1f} جنيه")
col4.metric("أكبر فئة صرفاً", top_cat)
