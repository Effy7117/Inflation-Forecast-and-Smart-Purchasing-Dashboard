# oil.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Function to load data
def load_data():
    # Load the data from CSV file
    df = pd.read_csv('Oil.csv')
    # Convert Date column to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    # Convert non-numeric 'Value' entries to NaN and then to numeric
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    return df

# Function to display the Regional Analysis page
def regional_analysis(df):
    st.subheader("Regional Analysis")

    # Sidebar filters
    st.sidebar.header("Filters")

    # Year and month dropdown filters
    years = df['Date'].dt.year.unique()
    selected_year = st.sidebar.selectbox("Select Year", sorted(years))
    months = range(1, 13)
    selected_month = st.sidebar.selectbox("Select Month", months)
    
    # Filter data based on selections
    filtered_df = df[(df['Date'].dt.year == selected_year) & 
                     (df['Date'].dt.month == selected_month)]

    # Ensure the Date column is not duplicated
    filtered_df = filtered_df.copy()
    
    # Group by province and compute average values
    grouped_df = filtered_df.groupby('Province')['Value'].mean().reset_index()
    
    # Remove provinces with no values
    grouped_df = grouped_df[grouped_df['Value'].notna() & (grouped_df['Value'] > 0)]
    
    # Plot data as a bar chart
    st.write(f"Average Oil Prices for Each Province in {selected_month}/0{selected_year}")
    plt.figure(figsize=(12, 6))
    plt.bar(grouped_df['Province'], grouped_df['Value'], color='skyblue')
    plt.xlabel("Province")
    plt.ylabel("Average Oil Price")
    plt.title(f"Average Oil Prices by Province for ({selected_year}-{selected_month})")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(plt)




# Function to display the Product Trend page
def product_trend(df):
    st.subheader("Product Trend")

    # Sidebar filter
    provinces = df['Province'].unique()
    selected_province = st.sidebar.selectbox("Select Province", provinces)
    
    # Filter data from 1990 to 2024
    filtered_df = df[(df['Date'].dt.year >= 1990) & (df['Date'].dt.year <= 2024)]
    
    if selected_province:
        filtered_df = filtered_df[filtered_df['Province'] == selected_province]

    # Plot data
    plt.figure(figsize=(10, 5))
    plt.plot(filtered_df['Date'], filtered_df['Value'], label=selected_province)
    
    plt.xlabel("Date")
    plt.ylabel("Oil Price")
    plt.title("Oil Price Trends from 1990 to 2024")
    plt.legend()
    st.pyplot(plt)

# Function to display the Price Forecasting page
def price_forecasting(df):
    st.subheader("Price Forecasting")

    # Sidebar filters
    st.sidebar.header("Forecasting Options")
    
    # Province filter
    provinces = df['Province'].unique()
    selected_province = st.sidebar.selectbox("Select Province", provinces)
    
    # Dropdown for selecting future date
    future_year = st.sidebar.selectbox("Select Year (2024-2027)", [2024, 2025, 2026, 2027])
    future_month = st.sidebar.selectbox("Select Month", range(1, 13), index=9)

    # Filter data for the selected province
    province_data = df[df['Province'] == selected_province]

    # Ensure data is sorted by date
    province_data = province_data.sort_values(by='Date')
    
    # Handle missing values 
    province_data['Value'].fillna(method='ffill', inplace=True)
    province_data['Value'].fillna(method='bfill', inplace=True)  # In case there are NaNs at the start

    # Create feature and target variables
    province_data = province_data.set_index('Date')
    y = province_data['Value']
    
    # Fit the time series model
    model = ExponentialSmoothing(y, seasonal='mul', seasonal_periods=12)
    model_fit = model.fit()

    # Predict future value
    future_date = pd.Timestamp(f"{future_year}-{future_month:02d}-01")
    future_dates = pd.date_range(start=province_data.index.max(), periods=((future_year - 2024) * 12) + future_month, freq='M')
    forecast = model_fit.predict(start=len(y), end=len(y) + len(future_dates) - 1)
    
    # Get the predicted value for the selected date
    predicted_value = forecast.iloc[-1]

    try:
        june_2024_price = province_data.loc['2024-06']['Value'].mean() if '2024-06' in province_data.index else 'Data not available'
    except KeyError:
        june_2024_price = 'Data not available'

    # Plot historical and forecasted prices
    plt.figure(figsize=(10, 5))
    plt.plot(province_data.index, province_data['Value'], label='Historical Prices')
    plt.plot(future_dates, forecast, label='Forecasted Prices', linestyle='--')
    
    plt.xlabel("Date")
    plt.ylabel("Oil Price")
    plt.title("Oil Price Forecasting")
    plt.legend()
    st.pyplot(plt)

    # Display the predicted value
    st.write(f"The current oil price for 9/2024 is {june_2024_price:.2f}" if isinstance(june_2024_price, (int, float)) else june_2024_price)
    st.write(f"The predicted oil price for {future_month}/{future_year} is {predicted_value:.2f}")

# Function to display the oil price dashboard
def oil_dashboard():
    #st.title("Welcome to Oil Price Analysis Dashboard")

    # Load data
    df = load_data()

    # Main navigation for the oil dashboard 
    page = st.sidebar.selectbox("Select a Page", ["Home","Regional Analysis", "Product Trend", "Price Forecasting"])
    
    if page == "Home":
        st.markdown("""
        <div style='font-size:36px; font-weight:bold;'>Welcome to the Oil Price Analysis Dashboard</div>
        """, unsafe_allow_html=True)
        st.write("Use the navigation menu to explore different analyses and visualizations of Canadian oil prices.")
        st.image('static/oil.jpg', use_column_width=True)


    elif page == "Regional Analysis":
        regional_analysis(df)
    elif page == "Product Trend":
        product_trend(df)
    elif page == "Price Forecasting":
        price_forecasting(df)

if __name__ == "__main__":
    oil_dashboard()
