import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing

def load_data():
    # Load the data from CSV file
    df = pd.read_csv('Wage.csv')
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')

    #df.head()
    df = df[df['Geography'] != 'Canada']
    df['Value'] = df['Value'].str.replace(',', '')  # Remove commas
    df['Value'] = df['Value'].str.extract('(\d+)')  # Extract only numeric parts
    df['Value'] = df['Value'].astype(float)  # Convert to float
    df = df.dropna(subset=['Date', 'Value'])
    return df

def regional_analysis(df):
    st.subheader("Regional Analysis")

    # Sidebar filters
    st.sidebar.header("Filters")

    # Year and month dropdown filters
    years = df['Date'].dt.year.unique()
    #print(years)
    selected_year = st.sidebar.selectbox("Select Year", sorted(years))
    months = range(1, 13)
    selected_month = st.sidebar.selectbox("Select Month", months, index=11)

    
    # Filter data based on selections
    filtered_df = df[(df['Date'].dt.year == selected_year) & 
                     (df['Date'].dt.month == selected_month)]

    # Ensure the Date column is not duplicated
    filtered_df = filtered_df.copy()
    
    # Group by geography and compute average values
    grouped_df = filtered_df.groupby('Geography')['Value'].mean().reset_index()
    
    # Remove geographies with no values
    grouped_df = grouped_df[grouped_df['Value'].notna() & (grouped_df['Value'] > 0)]
    
    # Plot data as a bar chart
    st.write(f"Average Weekly Earnings for Each Region in {selected_month}/{selected_year}")
    if not grouped_df.empty:
        plt.figure(figsize=(12, 6))
        plt.bar(grouped_df['Geography'], grouped_df['Value'], color='skyblue')
        plt.xlabel("Region")
        plt.ylabel("Average Weekly Earnings")
        plt.title(f"Average Weekly Earnings by Region for ({selected_year}-{selected_month})")
        plt.xticks(rotation=45, ha='right')
        st.pyplot(plt)
    else:
        st.write("No data available for the selected month and year.")

def product_trend(df):
    st.subheader("Product Trend")

    # Filter data from 1990 to 2024
    df = df[(df['Date'].dt.year >= 1990) & (df['Date'].dt.year <= 2024)]
    
    # Group by date and compute mean values
    trend_df = df.groupby('Date')['Value'].mean().reset_index()
    
    # Plot the trend
    plt.figure(figsize=(12, 6))
    plt.plot(trend_df['Date'], trend_df['Value'], marker='o', linestyle='-')
    plt.xlabel("Date")
    plt.ylabel("Average Weekly Earnings")
    plt.title("Product Trend from 1990 to 2024")
    plt.grid(True)
    st.pyplot(plt)

def price_forecasting(df):
    st.subheader("Price Forecasting")

    # Sidebar filters
    st.sidebar.header("Forecasting Options")
    
    # Region filter
    regions = df['Geography'].unique()
    selected_region = st.sidebar.selectbox("Select Region", regions)
    
    # Dropdown for selecting future date
    future_year = st.sidebar.selectbox("Select Year (2024-2027)", [2024, 2025, 2026, 2027])
    future_month = st.sidebar.selectbox("Select Month", range(1, 13), index=11)


    # Filter data for the selected region
    region_data = df[df['Geography'] == selected_region]

    # Ensure data is sorted by date
    region_data = region_data.sort_values(by='Date')
    
    # Handle missing values (e.g., by filling forward)
    region_data['Value'] = region_data['Value'].ffill()
    region_data['Value'] = region_data['Value'].bfill()  # In case there are NaNs at the start

    # Filter out non-positive values
    region_data = region_data[region_data['Value'] > 0]

    # Ensure there are at least 24 months of data
    if len(region_data) < 24:
        st.write("Not enough data to compute initial seasonals. Please select a region with more data.")
        return

    # Create feature and target variables
    region_data = region_data.set_index('Date')
    y = region_data['Value']
    
    # Fit the time series model
    model = ExponentialSmoothing(y, seasonal='mul', seasonal_periods=12)
    model_fit = model.fit()

    # Predict future value
    future_date = pd.Timestamp(f"{future_year}-{future_month:02d}-01")
    future_dates = pd.date_range(start=region_data.index.max(), periods=((future_year - 2024) * 12) + future_month, freq='M')
    forecast = model_fit.predict(start=len(y), end=len(y) + len(future_dates) - 1)
    
    # Get the predicted value for the selected date
    predicted_value = forecast.iloc[-1]

    # Current data for June 2024
    try:
        june_2024_value = region_data.loc['2024-05']['Value'].mean() if '2024-05' in region_data.index else 'Data not available'
    except KeyError:
        june_2024_value = 'Data not available'

    # Plot historical and forecasted values
    plt.figure(figsize=(10, 5))
    plt.plot(region_data.index, region_data['Value'], label='Historical Earnings')
    plt.plot(future_dates, forecast, label='Forecasted Earnings', linestyle='--')
    
    plt.xlabel("Date")
    plt.ylabel("Weekly Earnings")
    plt.title("Weekly Earnings Forecasting")
    plt.legend()
    st.pyplot(plt)

    # Display the predicted value
    st.write(f"The current weekly earnings for 9/2024 is {june_2024_value:.2f}" if isinstance(june_2024_value, (int, float)) else june_2024_value)
    st.write(f"The predicted weekly earnings for {future_month}/{future_year} is {predicted_value:.2f}")

def wage_dashboard():
    #st.title("Welcome to Weekly Earnings Analysis Dashboard")

    # Load data
    df = load_data()

    # Main navigation for the wage dashboard
    page = st.sidebar.selectbox("Select a Page", ["Home","Regional Analysis", "Product Trend", "Price Forecasting"])
    
    if page == "Home":
        st.markdown("""
        <div style='font-size:36px; font-weight:bold;'>Welcome to the Weekly earnings Analysis Dashboard</div>
        """, unsafe_allow_html=True)
        st.write("Use the navigation menu to explore different analyses and visualizations of Canadian weekly earnings.")
        st.image('static/wage.jpeg', use_column_width=True)

    elif page == "Regional Analysis":
        regional_analysis(df)
    elif page == "Product Trend":
        product_trend(df)
    elif page == "Price Forecasting":
        price_forecasting(df)

if __name__ == "__main__":
    wage_dashboard()
