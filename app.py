import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data(path="sales_data.csv"):
    df = pd.read_csv(path, parse_dates=["order_date"]) 
    return df


def main():
    st.set_page_config(page_title="Sales Dashboard", layout="wide")
    # Trim Streamlit's default top padding and heading margins so the
    # whole dashboard fits on one screen without scrolling.
    st.markdown(
        """
        <style>
        div.block-container {padding-top: 1.2rem; padding-bottom: 1rem;}
        h1 {font-size: 1.9rem; margin-bottom: 0.3rem;}
        [data-testid="stMetricValue"] {font-size: 1.4rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("Sales Dashboard")

    df = load_data()

    # Sidebar filters
    st.sidebar.header("Filters")
    min_date = df["order_date"].min()
    max_date = df["order_date"].max()
    date_range = st.sidebar.date_input("Order date range", [min_date, max_date])

    regions = st.sidebar.multiselect("Region", options=sorted(df["region"].unique()), default=sorted(df["region"].unique()))
    categories = st.sidebar.multiselect("Category", options=sorted(df["category"].unique()), default=sorted(df["category"].unique()))
    segments = st.sidebar.multiselect("Customer segment", options=sorted(df["customer_segment"].unique()), default=sorted(df["customer_segment"].unique()))
    product_search = st.sidebar.text_input("Search product name (contains)")

    # Apply filters
    if len(date_range) != 2:
        st.info("Select a start and end date.")
        st.stop()
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    mask = (
        (df["order_date"] >= start_date) &
        (df["order_date"] <= end_date) &
        (df["region"].isin(regions)) &
        (df["category"].isin(categories)) &
        (df["customer_segment"].isin(segments))
    )
    df_filtered = df.loc[mask].copy()
    if product_search:
        df_filtered = df_filtered[df_filtered["product_name"].str.contains(product_search, case=False, na=False)]

    # KPIs
    total_sales = df_filtered["sales"].sum()
    total_profit = df_filtered["profit"].sum()
    avg_discount = df_filtered["discount"].mean()
    total_qty = df_filtered["quantity"].sum()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Sales", f"${total_sales:,.2f}")
    k2.metric("Total Profit", f"${total_profit:,.2f}")
    avg_discount = 0 if pd.isna(avg_discount) else avg_discount
    k3.metric("Avg Discount", f"{avg_discount*100:.1f}%")
    k4.metric("Total Quantity", int(total_qty or 0))

    # Charts - laid out as a 2x2 grid so everything fits on one screen
    CHART_HEIGHT = 230

    def style(fig):
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=CHART_HEIGHT)
        return fig

    if not df_filtered.empty:
        row1_left, row1_right = st.columns(2)
        with row1_left:
            st.markdown("**Sales Over Time**")
            sales_time = df_filtered.groupby("order_date")["sales"].sum().reset_index()
            fig_time = px.line(sales_time, x="order_date", y="sales")
            st.plotly_chart(style(fig_time), use_container_width=True)

        with row1_right:
            st.markdown("**Sales by Region**")
            sales_region = df_filtered.groupby("region")["sales"].sum().reset_index().sort_values("sales", ascending=False)
            fig_region = px.bar(sales_region, x="region", y="sales")
            st.plotly_chart(style(fig_region), use_container_width=True)

        row2_left, row2_right = st.columns(2)
        with row2_left:
            st.markdown("**Sales by Category**")
            sales_cat = df_filtered.groupby("category")["sales"].sum().reset_index().sort_values("sales", ascending=False)
            fig_cat = px.pie(sales_cat, names="category", values="sales")
            st.plotly_chart(style(fig_cat), use_container_width=True)

        with row2_right:
            st.markdown("**Top Products**")
            top_products = df_filtered.groupby("product_name")["sales"].sum().reset_index().sort_values("sales", ascending=False).head(10)
            fig_top = px.bar(top_products.sort_values("sales"), x="sales", y="product_name", orientation="h")
            st.plotly_chart(style(fig_top), use_container_width=True)
    else:
        st.info("No data for selected filters.")

    # Filtered data & download tucked away so it doesn't push charts off-screen
    with st.expander("Filtered data & download"):
        st.dataframe(df_filtered.reset_index(drop=True))
        csv = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button("Download filtered data as CSV", csv, "filtered_sales.csv", "text/csv")


if __name__ == "__main__":
    main()
