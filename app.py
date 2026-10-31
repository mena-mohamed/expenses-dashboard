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

    # Insight للإحصاء
    if amount.mean() > amount.median() * 1.1:
        st.info(
            f"💡 Insight: المتوسط ({amount.mean():.0f}) أكبر من الوسيط ({amount.median():.0f}) "
            "بفرق واضح، يعني فيه مصاريف كبيرة بتشد المتوسط لفوق، والوسيط أصدق في تمثيل المصروف العادي."
        )
    else:
        st.info(
            f"💡 Insight: المتوسط ({amount.mean():.0f}) والوسيط ({amount.median():.0f}) قريبين من بعض، "
            "يعني المصاريف متوازنة ومفيش قيم كبيرة بتشد المتوسط."
        )

    # Histogram + Boxplot
    st.markdown("#### 📉 التوزيع والـ Outliers")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    sns.histplot(data=filtered_df, x="Amount", kde=True, bins=10, ax=axes[0], color="#C0714F")
    axes[0].set_title("Amount Distribution")
    sns.boxplot(data=filtered_df, x="Category", y="Amount", ax=axes[1], color="#E8C4A8")
    axes[1].set_title("Boxplot by Category")
    plt.tight_layout()
    st.pyplot(fig)

    cat_median = filtered_df.groupby("Category")["Amount"].median()
    if amount.skew() > 0.5:
        shape_txt = "أغلب المصاريف متكدسة عند القيم الصغيرة وفيه ذيل طويل ناحية القيم الكبيرة."
    else:
        shape_txt = "توزيع المصاريف متماثل تقريباً من غير ذيل واضح."
    st.info(
        f"💡 Insight: {shape_txt} "
        f"وأعلى وسيط كان لفئة {cat_median.idxmax()} ({cat_median.max():.0f} جنيه)."
    )

    # 1) المصاريف الشاذة (Outliers) بقاعدة IQR
    st.markdown("#### 🚨 المصاريف الشاذة (Outliers)")
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outliers = filtered_df[(filtered_df["Amount"] < lower) | (filtered_df["Amount"] > upper)]
    st.write(f"الحدود الطبيعية: من {lower:.0f} إلى {upper:.0f} جنيه، وعدد المصاريف الشاذة: {len(outliers)}")
    if not outliers.empty:
        st.dataframe(outliers[["Date", "Category", "Amount"]])
        share = len(outliers) / len(filtered_df) * 100
        st.info(
            f"💡 Insight: {len(outliers)} مصروف شاذ ({share:.1f}% من العمليات)، "
            f"وأكبرهم {outliers['Amount'].max():.0f} جنيه. "
            "الـ IQR بيتحسب على الفلتر الحالي، فاختاري فئة واحدة عشان الحدود تبقى أدق."
        )
    else:
        st.info("💡 Insight: مفيش مصاريف شاذة في الفلتر الحالي.")

    # 2) المصروف اليومي
    st.markdown("#### 📅 المصروف اليومي")
    daily = filtered_df.groupby("Date")["Amount"].sum()
    st.line_chart(daily)
    st.info(
        f"💡 Insight: أعلى يوم صرف كان {daily.idxmax().strftime('%Y-%m-%d')} "
        f"بمجموع {daily.max():.0f} جنيه، ومتوسط المصروف اليومي {daily.mean():.0f} جنيه."
    )

    # 3) إجمالي كل فئة
    st.markdown("#### 🗂️ إجمالي كل فئة")
    cat_total = filtered_df.groupby("Category")["Amount"].sum()
    st.bar_chart(cat_total)
    top_share = cat_total.max() / cat_total.sum() * 100
    st.info(
        f"💡 Insight: فئة {cat_total.idxmax()} هي الأكبر صرفاً بإجمالي "
        f"{cat_total.max():,.0f} جنيه ({top_share:.1f}% من الإجمالي)."
    )

    # 4) نسبة كل فئة من الإجمالي (Pie)
    st.markdown("#### 🥧 نسبة كل فئة من الإجمالي")
    pie_colors = ["#C0714F", "#E8C4A8", "#D9A066", "#8C5A3C", "#F2D4B7"]
    fig2, ax2 = plt.subplots(figsize=(5, 5))
    ax2.pie(
        cat_total,
        labels=cat_total.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=pie_colors[:len(cat_total)],
    )
    st.pyplot(fig2)
    st.info(
        f"💡 Insight: أصغر فئة هي {cat_total.idxmin()} "
        f"({cat_total.min() / cat_total.sum() * 100:.1f}% من الإجمالي)."
    )

    # 5) إجمالي كل شهر
    st.markdown("#### 📆 إجمالي كل شهر")
    month_total = filtered_df.groupby("Month")["Amount"].sum()
    st.bar_chart(month_total)
    if len(month_total) > 1:
        st.info(
            f"💡 Insight: أكتر شهر صرفاً هو {month_total.idxmax()} ({month_total.max():,.0f} جنيه). "
            "خدي بالك: الشهر الأخير ناقص لأن الداتا بتقف عند 22 أكتوبر."
        )

    # 6) المصاريف عبر الزمن (الشاذة بالأحمر)
    st.markdown("#### 🔴 المصاريف عبر الزمن (الشاذة بالأحمر)")
    normal = filtered_df.drop(outliers.index)
    fig3, ax3 = plt.subplots(figsize=(12, 4))
    ax3.scatter(normal["Date"], normal["Amount"], color="#C0714F", alpha=0.7, label="Normal")
    ax3.scatter(outliers["Date"], outliers["Amount"], color="red", label="Outlier")
    ax3.set_xlabel("Date")
    ax3.set_ylabel("Amount")
    ax3.legend()
    fig3.autofmt_xdate()
    plt.tight_layout()
    st.pyplot(fig3)
    if not outliers.empty:
        biggest = outliers.loc[outliers["Amount"].idxmax()]
        st.info(
            f"💡 Insight: أكبر مصروف شاذ كان في {biggest['Date'].strftime('%Y-%m-%d')} "
            f"({biggest['Category']}) بمبلغ {biggest['Amount']:.0f} جنيه."
        )

else:
    st.warning("لا توجد بيانات للفلتر الحالي.")

st.markdown("---")
if st.checkbox("📋 عرض السجل التفصيلي"):
    st.dataframe(filtered_df)


