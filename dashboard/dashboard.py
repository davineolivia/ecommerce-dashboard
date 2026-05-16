import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

def create_monthly_orders_df(df):
    df = df.copy()

    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"],
        errors="coerce"
    )

    df = df.dropna(subset=["order_purchase_timestamp"])

    df["month"] = (
        df["order_purchase_timestamp"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly_orders_df = df.groupby("month").agg({
        "order_id": "nunique",
        "payment_value": "sum"
    }).reset_index()

    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)

    return monthly_orders_df

def create_product_sales_df(df):
    product_sales_df = df.groupby(
        by='product_category_name_english'
    ).agg({
        'order_item_id': 'count',
        'payment_value': 'sum'
    }).reset_index()

    product_sales_df.rename(columns={
        'order_item_id': 'total_sales'
    }, inplace=True)

    return product_sales_df.sort_values(
        by='total_sales',
        ascending=False
    )

def create_customer_state_df(df):
    customer_state_df = df.groupby(
        by='customer_state'
    ).customer_unique_id.nunique().reset_index()

    customer_state_df.rename(columns={
        'customer_unique_id': 'customer_count'
    }, inplace=True)

    return customer_state_df.sort_values(
        by='customer_count',
        ascending=False
    )

def create_review_delivery_df(df):
    review_delivery_df = df.groupby(
        by='review_score'
    ).agg({
        'delivery_delay': 'mean'
    }).reset_index()

    return review_delivery_df

base_path = os.path.dirname(__file__)
csv_path = os.path.join(base_path, "all_data.csv")

df_all = pd.read_csv(csv_path)

datetime_columns = [
    "order_purchase_timestamp",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for column in datetime_columns:
    df_all[column] = pd.to_datetime(df_all[column], errors="coerce")

df_all["delivery_time"] = (
    df_all["order_delivered_customer_date"] -
    df_all["order_purchase_timestamp"]
).dt.days

df_all["delivery_delay"] = (
    df_all["order_delivered_customer_date"] -
    df_all["order_estimated_delivery_date"]
).dt.days

df_all.sort_values(by="order_purchase_timestamp", inplace=True)

min_date = df_all["order_purchase_timestamp"].min()
max_date = df_all["order_purchase_timestamp"].max()

with st.sidebar:
    st.header("E-Commerce Dashboard")

    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date.date(),
        max_value=max_date.date(),
        value=[min_date.date(), max_date.date()]
    )

main_df = df_all[
    (df_all["order_purchase_timestamp"] >= pd.to_datetime(start_date)) &
    (df_all["order_purchase_timestamp"] <= pd.to_datetime(end_date))
]

monthly_orders_df = create_monthly_orders_df(main_df)
product_sales_df = create_product_sales_df(main_df)
customer_state_df = create_customer_state_df(main_df)
review_delivery_df = create_review_delivery_df(main_df)

st.header("E-Commerce Public Dataset")

st.subheader("Order Performance")

col1, col2 = st.columns(2)

with col1:
    total_orders = monthly_orders_df.order_count.sum()
    st.metric("Total Orders", value=total_orders)

with col2:
    total_revenue = round(monthly_orders_df.revenue.sum(), 2)
    st.metric("Total Revenue", value=f"R$ {total_revenue}")

fig, ax = plt.subplots(figsize=(16, 8))

ax.plot(
    monthly_orders_df["month"],
    monthly_orders_df["order_count"],
    marker='o',
    linewidth=2
)

ax.set_title("Monthly Orders", fontsize=20)
st.pyplot(fig)

st.subheader("Delivery Performance")

fig, ax = plt.subplots(figsize=(10, 5))

sns.histplot(
    data=main_df,
    x='delivery_time',
    bins=30,
    ax=ax
)

ax.set_title("Distribution of Delivery Time")

st.pyplot(fig)

st.subheader("Review Score vs Delivery Delay")

fig, ax = plt.subplots(figsize=(10,5))

sns.barplot(
    data=review_delivery_df,
    x='review_score',
    y='delivery_delay',
    ax=ax
)

ax.set_title("Average Delivery Delay by Review Score")

st.pyplot(fig)

st.subheader("Top Product Categories")

fig, ax = plt.subplots(figsize=(12,6))

sns.barplot(
    data=product_sales_df.head(10),
    y='product_category_name_english',
    x='total_sales',
    ax=ax
)

ax.set_title("Top Selling Product Categories")

st.pyplot(fig)

st.subheader("Customer Distribution by State")

fig, ax = plt.subplots(figsize=(12,6))

sns.barplot(
    data=customer_state_df.head(10),
    y='customer_state',
    x='customer_count',
    ax=ax
)

ax.set_title("Top Customer States")

st.pyplot(fig)


st.caption("Copyright © Viaa Project") 