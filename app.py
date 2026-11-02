
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="E-Commerce BI Dashboard",
    page_icon="🛒",
    layout="wide"
)
# VINTAGE THEME STYLING

st.markdown("""
<style>

.stApp {
    background-color: #F5F0E7;
    color: #49392F;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #E8DECE;
    border-right: 1px solid #D5C7B5;
}

/* Headings */
h1, h2, h3 {
    color: #49392F !important;
    font-family: Georgia, serif !important;
}

/* Text */
p, label {
    color: #625246;
}

/* KPI cards */
[data-testid="stMetric"] {
    background-color: #FFFDF8;
    border: 1px solid #E3D8C8;
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 3px 10px rgba(73,57,47,0.05);
}

/* Metric text */
[data-testid="stMetricLabel"] {
    color: #817461 !important;
}

[data-testid="stMetricValue"] {
    color: #49392F !important;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button {
    background-color: #879078;
    color: white;
    border: none;
    border-radius: 9px;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background-color: #6F7A64;
    color: white;
}

/* Data table */
[data-testid="stDataFrame"] {
    border: 1px solid #E3D8C8;
    border-radius: 10px;
}

/* Divider */
hr {
    border-color: #DED3C3;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)
st.title("🛒 E-Commerce Business Intelligence Dashboard")
st.write("Analyze sales, revenue, orders, and customer behavior.")

# Load sales data
df = pd.read_csv("sales_data.csv")
df["Revenue"] = df["Quantity"] * df["Price"]

df["Cost"] = df["Quantity"] * df["Unit_Cost"]
df["Profit"] = df["Revenue"] - df["Cost"]

df["Order_Date"] = pd.to_datetime(df["Order_Date"])

# Interactive Filters
st.sidebar.header("Sales Filters")

categories = ["All"] + sorted(df["Category"].unique().tolist())
selected_category = st.sidebar.selectbox(
    "Select Category", categories
)

cities = ["All"] + sorted(df["City"].unique().tolist())
selected_city = st.sidebar.selectbox(
    "Select City", cities
)

min_date = df["Order_Date"].min().date()
max_date = df["Order_Date"].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

filtered_df = df.copy()

if selected_category != "All":
    filtered_df = filtered_df[
        filtered_df["Category"] == selected_category
    ]

if selected_city != "All":
    filtered_df = filtered_df[
        filtered_df["City"] == selected_city
    ]

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df["Order_Date"].dt.date >= start_date) &
        (filtered_df["Order_Date"].dt.date <= end_date)
    ]

# Sidebar
st.sidebar.header("Dashboard Menu")
page = st.sidebar.selectbox(
    "Choose a section",
    ["Overview", "Sales Analysis", "Customer Analysis"]
)
# Use filtered data throughout the dashboard
df = filtered_df
if page == "Overview":
    st.subheader("Business Overview")
    st.write(
        "This dashboard analyzes business performance using "
        "sales revenue, profit, customer behavior, and payment trends."
    )
    total_revenue = df["Revenue"].sum()
    total_orders = df["Order_ID"].nunique()
    total_products = df["Product"].nunique()
    total_customers = df["Customer"].nunique()


    total_profit = df["Profit"].sum()
    profit_margin = (
    (total_profit / total_revenue) * 100
    if total_revenue > 0 else 0
)
    
    st.subheader("Business Performance")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("💰 Total Revenue", f"₹{total_revenue:,.0f}")

    with col2:
        st.metric("📈 Total Profit", f"₹{total_profit:,.0f}")

    with col3:
        st.metric("📦 Total Orders", total_orders)

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric("🛍️ Products Sold", int(df["Quantity"].sum()))

    with col5:
        st.metric("👥 Unique Customers", total_customers)

    with col6:
        st.metric("🌿 Profit Margin", f"{profit_margin:.2f}%")

    if profit_margin >= 20:
        st.success("Sales Performance: Good profit margin")
    elif profit_margin > 0:
        st.info("Sales Performance: Positive profit, but improvement is possible")
    else:
        st.warning("Sales Performance: No profit recorded")
    
    st.subheader("Revenue Trend")

    daily_revenue = df.groupby(
        df["Order_Date"].dt.date
    )["Revenue"].sum()

    st.line_chart(
        daily_revenue,
        color="#879078",
        height=350
    )

    st.subheader("Revenue by City")

    city_revenue = df.groupby("City")["Revenue"].sum()
    city_revenue = city_revenue.sort_values(ascending=False)

    st.bar_chart(
        city_revenue,
        color="#B47D5C",
        horizontal=True,
        height=350
    )


   
    st.subheader("Recent Sales Data")

    display_df = df.copy()

    display_df["Order_Date"] = (
        display_df["Order_Date"].dt.strftime("%d %b %Y")
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


    csv_data = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Sales Report (CSV)",
        data=csv_data,
        file_name="sales_report.csv",
        mime="text/csv"
    )

   
    st.subheader("💡 Business Insights")

    if not df.empty:
        best_category = df.groupby("Category")["Revenue"].sum().idxmax()
        best_city = df.groupby("City")["Revenue"].sum().idxmax()
        best_product = df.groupby("Product")["Quantity"].sum().idxmax()

        best_profit_category = df.groupby("Category")["Profit"].sum().idxmax()

        popular_payment = (
            df.groupby("Payment_Method")["Order_ID"]
            .nunique()
            .idxmax()
        )

        lowest_city = df.groupby("City")["Revenue"].sum().idxmin()

        average_order_value = (
            total_revenue / total_orders if total_orders > 0 else 0
        )

        st.success(f"🏆 Top revenue-generating category: {best_category}")
        st.info(f"📍 Highest revenue-generating city: {best_city}")
        st.success(f"💰 Most profitable category: {best_profit_category}")
        st.info(f"🛍️ Best-selling product: {best_product}")
        st.info(f"💳 Most popular payment method: {popular_payment}")
        st.warning(f"📉 Lowest revenue-generating city: {lowest_city}")

        st.write(f"Average Order Value: ₹{average_order_value:,.2f}")

    else:
        st.warning("No sales records match the selected filters.")



elif page == "Sales Analysis":
    st.subheader("Sales Analysis")

    st.write("### Monthly Revenue")

    monthly_sales = df.groupby(
        df["Order_Date"].dt.to_period("M")
    )["Revenue"].sum()

    monthly_sales.index = monthly_sales.index.astype(str)

    st.bar_chart(
        monthly_sales,
        color="#879078",
        height=350
    )
    st.bar_chart(
        monthly_sales,
        color="#879078",
        height=350
    )

    st.write("### Revenue by Category")

    category_sales = df.groupby("Category")["Revenue"].sum()

    st.bar_chart(
        category_sales,
        color="#B47D5C",
        height=350
    )

    st.write("### Profit by Category")
    st.write("### Profit Alerts")

    if not df.empty:
        lowest_profit_category = (
            df.groupby("Category")["Profit"].sum().idxmin()
        )
        st.warning(
            f"Monitor this category: {lowest_profit_category}"
        )
    else:
        st.info("No data available for the selected filters.")

    category_profit = df.groupby("Category")["Profit"].sum()
    category_profit = category_profit.sort_values(ascending=False)

    st.bar_chart(
        category_profit,
        color="#879078",
        height=350
    )

    st.write("### Top-Selling Products")

    product_sales = df.groupby("Product")["Quantity"].sum()
    product_sales = product_sales.sort_values(ascending=False)

    st.bar_chart(
        product_sales.head(10),
        color="#C5A77D",
        height=350
    )

    st.write("### Revenue vs Cost")

    comparison = df.groupby("Category")[["Revenue", "Cost"]].sum()

    st.bar_chart(comparison, height=350)

    st.write("### Monthly Profit Trend")

    monthly_profit = df.groupby(
        df["Order_Date"].dt.to_period("M")
    )["Profit"].sum()

    monthly_profit.index = monthly_profit.index.astype(str)

    st.line_chart(
        monthly_profit,
        color="#A68B78",
        height=350
    )

    st.write("### Top 5 Products by Revenue")

    top_products = (
        df.groupby("Product")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )

    st.bar_chart(
        top_products,
        color="#B47D5C",
        height=350
    )

    st.write("### Daily Sales Summary")

    daily_sales = df.groupby(
        df["Order_Date"].dt.date
    ).agg(
        Total_Revenue=("Revenue", "sum"),
        Total_Profit=("Profit", "sum"),
        Total_Orders=("Order_ID", "nunique")
    )

    st.dataframe(daily_sales, use_container_width=True)


elif page == "Customer Analysis":
    st.subheader("Customer Analysis")

    customer_sales = df.groupby("Customer")["Revenue"].sum()
    customer_sales = customer_sales.sort_values(ascending=False)

    st.write("### Revenue by Customer")
    st.bar_chart(customer_sales, color="#879078")

    st.write("### Orders by City")
    city_orders = df.groupby("City")["Order_ID"].nunique()
    st.bar_chart(city_orders, color="#B47D5C")

    st.write("### Revenue by Payment Method")
    payment_revenue = df.groupby("Payment_Method")["Revenue"].sum()
    payment_revenue = payment_revenue.sort_values(ascending=False)
    st.bar_chart(payment_revenue, color="#C5A77D")

    st.write("### Orders by Payment Method")
    payment_orders = df.groupby("Payment_Method")["Order_ID"].nunique()
    payment_orders = payment_orders.sort_values(ascending=False)
    st.bar_chart(payment_orders, color="#A68B78")

    st.write("### Top 5 Customers by Spending")
    top_customers = customer_sales.head(5)
    st.bar_chart(top_customers, color="#879078")

    customer_report = (
        df.groupby("Customer")
        .agg(
            Total_Revenue=("Revenue", "sum"),
            Total_Orders=("Order_ID", "nunique"),
            Total_Quantity=("Quantity", "sum")
        )
        .reset_index()
    )

    st.download_button(
        label="Download Customer Report (CSV)",
        data=customer_report.to_csv(index=False).encode("utf-8"),
        file_name="customer_report.csv",
        mime="text/csv"
    )
