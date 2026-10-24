import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Expenses Dashboard", page_icon="💰", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');

html, body, [class*="css"], h1, h2, h3, h4, p {
    font-family: 'Amiri', serif;
}

[data-testid="stMetric"] {
    background-color: #F5E6D8;
    border-radius: 12px;
    padding: 14px 18px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}
</style>
""", unsafe_allow_html=True)

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

# الإحصاء الوصفي
st.markdown("---")
st.subheader("📈 الإحصاء الوصفي والتوزيعات")

if not filtered_df.empty:
    amount = filtered_df["Amount"]
    q1 = amount.quantile(0.25)
    q3 = amount.quantile(0.75)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 🔹 النزعة المركزية")
        st.write(f"- المتوسط (Mean): {amount.mean():.2f}")
        st.write(f"- الوسيط (Median): {amount.median():.2f}")
        st.write(f"- المنوال (Mode): {amount.mode().iloc[0]}")

        st.markdown("#### 🔹 التشتت")
        st.write(f"- الانحراف المعياري (Std): {amount.std():.2f}")
        st.write(f"- المدى الربيعي (IQR): {q3 - q1:.2f}")

    with col_b:
        st.markdown("#### 🔹 مقارنة الفئات")
        summary = filtered_df.groupby("Category")["Amount"].agg(["count", "mean", "median", "std"])
        st.dataframe(summary.round(2))

    st.markdown("#### 📉 التوزيع والـ Outliers")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    sns.histplot(data=filtered_df, x="Amount", kde=True, bins=10, ax=axes[0], color="#C0714F")
    axes[0].set_title("Amount Distribution")
    sns.boxplot(data=filtered_df, x="Category", y="Amount", ax=axes[1], color="#E8C4A8")
    axes[1].set_title("Boxplot by Category")
    plt.tight_layout()
    st.pyplot(fig)
else:
    st.warning("لا توجد بيانات للفلتر الحالي.")

st.markdown("---")
if st.checkbox("📋 عرض السجل التفصيلي"):
    st.dataframe(filtered_df)

