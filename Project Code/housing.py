import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from io import BytesIO

def load_housing_data():
    try:
        housing_df = pd.read_csv('housing.csv', encoding='utf-8')
    except UnicodeDecodeError:
        try:
            housing_df = pd.read_csv('housing.csv', encoding='latin1')
        except UnicodeDecodeError:
            housing_df = pd.read_csv('housing.csv', encoding='ISO-8859-1')

    # Handle Price column conversion
    if housing_df['Price'].dtype == 'object':
        # Remove commas and convert to numeric
        housing_df['Price'] = pd.to_numeric(housing_df['Price'].str.replace(',', ''), errors='coerce')
    else:
        # Ensure Price is numeric
        housing_df['Price'] = pd.to_numeric(housing_df['Price'], errors='coerce')
    
    # Fill or drop missing values as needed
    housing_df['Price'].fillna(housing_df['Price'].mean(), inplace=True)
    
    return housing_df

def load_and_preprocess_data():
    # Load the data, ignoring the first unnamed column if present
    hpi_df = pd.read_csv('hpi.csv', encoding='latin1', index_col=0)

    # Remove leading and trailing spaces from column names
    hpi_df.columns = hpi_df.columns.str.strip()

    # Convert 'Month-year' to datetime and set as index
    hpi_df['Month-year'] = pd.to_datetime(hpi_df['Month-year'], format='%b-%y')
    hpi_df.set_index('Month-year', inplace=True)

    # Filter out rows where the year is less than 1995
    hpi_df = hpi_df[hpi_df.index.year >= 1995]

    # Drop the unnecessary columns
    hpi_df.drop(columns=['Type', 'Canada', 'year', 'month'], inplace=True)

    # Sort data by date
    hpi_df.sort_index(inplace=True)

    # Handle missing data
    hpi_df = hpi_df.ffill().bfill()

    return hpi_df

def calculate_base_price(current_price, current_hpi):
    base_price = (current_price * 100) / current_hpi
    return base_price

def predict_price(housing_df, city, num_beds, num_baths, province, forecasted_hpi):
    # Filter the data based on user selection
    filtered_data = housing_df[
        (housing_df['City'] == city) &
        (housing_df['Number_Beds'] == num_beds) &
        (housing_df['Number_Baths'] == num_baths) &
        (housing_df['Province'] == province)
    ]
    
    if filtered_data.empty:
        st.error("No data available for the selected criteria.")
        return None, None

    # Calculate the mean price of the filtered data
    current_price = filtered_data['Price'].mean()

    # Calculate the historical price when HPI was 100
    base_price = calculate_base_price(current_price, 100)
    
    # Calculate the forecasted price based on forecasted HPI
    forecasted_price = base_price * (forecasted_hpi / 100)
    
    return current_price, forecasted_price

def plot_hpi(region, data, forecast_dates=None, forecast=None):
    data_resampled = data.resample('M').mean()

    plt.figure(figsize=(14, 8))
    plt.plot(data_resampled.index, data_resampled, label=f'{region} HPI', color='blue', linewidth=2)
    
    if forecast_dates is not None and forecast is not None:
        forecast_resampled = forecast.resample('M').mean()
        plt.plot(forecast_resampled.index, forecast_resampled, label='Forecast', color='red', linestyle='--', linewidth=2)
    
    plt.title(f'Housing Price Index (HPI) for {region}')
    plt.xlabel('Date')
    plt.ylabel('HPI')
    plt.legend(loc='upper left')
    #plt.grid(True)

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    #fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    
    return buf

def forecast_hpi(hpi_df, region, start_date, end_date):
    hpi_df.columns = hpi_df.columns.str.strip()
    
    matching_columns = [col for col in hpi_df.columns if region in col]
    
    if len(matching_columns) == 1:
        column_name = matching_columns[0]
        data = hpi_df[column_name]
    elif len(matching_columns) > 1:
        st.error(f"Multiple columns found for region '{region}'. Please specify more precisely.")
        st.write(f"Matching columns: {', '.join(matching_columns)}")
        return None, None
    else:
        st.error(f"Region '{region}' not found in the data. Available regions are: {', '.join(hpi_df.columns)}")
        return None, None

    model = ExponentialSmoothing(data, trend='add', seasonal=None, seasonal_periods=12)
    fit = model.fit()

    future_dates = pd.date_range(start=start_date, end=end_date, freq='M')
    
    forecast = fit.predict(start=len(data), end=len(data) + len(future_dates) - 1)
    
    forecast_series = pd.Series(forecast.values, index=future_dates)
    
    return future_dates, forecast_series

def plot_regional_hpi(hpi_df, year, month):
    start_date = pd.to_datetime(f'{year}-{month}-01')
    end_date = pd.to_datetime(start_date + pd.DateOffset(months=1) - pd.DateOffset(days=1))
    
    filtered_df = hpi_df.loc[start_date:end_date]

    filtered_df = filtered_df.apply(pd.to_numeric, errors='coerce')

    avg_hpi_per_region = filtered_df.mean()

    plt.figure(figsize=(17, 17))
    avg_hpi_per_region.plot(kind='bar', color='pink')
    plt.title(f'Average HPI for All Regions in {start_date.strftime("%B %Y")}')
    plt.xlabel('Region')
    plt.ylabel('Average HPI')
    plt.xticks(rotation=90)
    #plt.grid(True)

    buf = BytesIO()
    plt.savefig(buf, format='png',bbox_inches='tight')
    buf.seek(0)
    return buf

def housing_dashboard():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ["Home", "Housing Price Trend", "Regional Housing Analysis", "Housing Price Prediction"])

    hpi_df = load_and_preprocess_data()
    housing_df = load_housing_data()

    if page == "Home":
        st.markdown("""
        <div style='font-size:36px; font-weight:bold;'>Welcome to the Housing Price Analysis Dashboard</div>
        """, unsafe_allow_html=True)
        st.write("Use the navigation menu to explore different analyses and visualizations of Canadian housing prices.")
        st.image('static/housing.jpg', use_column_width=True)

    elif page == "Housing Price Trend":
        st.markdown("<div class='subtitle'>Housing Price Trend Analysis</div>", unsafe_allow_html=True)
        
        regions = hpi_df.columns.tolist()
        selected_region = st.selectbox("Select Region", regions)
        
        buf = plot_hpi(region=selected_region, data=hpi_df[selected_region])
        st.image(buf, use_column_width=True)

    elif page == "Regional Housing Analysis":
        st.markdown("<div class='subtitle'>Regional Housing Analysis</div>", unsafe_allow_html=True)
        
        forecast_year = st.slider("Select Year", min_value=1995, max_value=2023, value=2020)
        forecast_month = st.selectbox("Select Month", pd.date_range(start='2023-01-01', periods=12, freq='M').strftime('%B').tolist())

        buf = plot_regional_hpi(hpi_df, forecast_year, forecast_month)
        if buf:
            st.image(buf, use_column_width=True)

    elif page == "Housing Price Prediction":
        st.markdown("<div class='subtitle'>Housing Price Prediction</div>", unsafe_allow_html=True)

        cities = housing_df['City'].unique().tolist()
        selected_city = st.selectbox("Select City", cities)
        
        num_beds = st.slider("Select Number of Beds", min_value=int(housing_df['Number_Beds'].min()), max_value=5, value=int(housing_df['Number_Beds'].mean()))
        num_baths = st.slider("Select Number of Baths", min_value=int(housing_df['Number_Baths'].min()), max_value=5, value=int(housing_df['Number_Baths'].mean()))
        provinces = housing_df['Province'].unique().tolist()
        selected_province = st.selectbox("Select Province", provinces)

        forecast_year = st.slider("Select Forecast Year", min_value=2024, max_value=2027, value=2025)
        forecast_month = st.selectbox("Select Forecast Month", pd.date_range(start='2024-01-01', periods=12, freq='M').strftime('%B').tolist())
        
        start_date = pd.to_datetime(f'{forecast_year}-{forecast_month}-01')
        end_date = pd.to_datetime(f'{forecast_year + 3}-12-31')

        forecast_dates, forecast_series = forecast_hpi(hpi_df, selected_city, start_date, end_date)

        if forecast_dates is not None and forecast_series is not None:
            current_price, forecasted_price = predict_price(housing_df, selected_city, num_beds, num_baths, selected_province, forecast_series.iloc[-1])

            if current_price is not None and forecasted_price is not None:
                st.write(f"Current average price in {selected_city} with {num_beds} beds and {num_baths} baths: ${current_price:.2f}")
                st.write(f"Forecasted HPI: {forecast_series.iloc[-1]:.2f}")  # Added back this line
                st.write(f"Predicted price based on forecasted HPI: ${forecasted_price:.2f}")

            else:
                st.error("No data available for the selected criteria.")

    elif page == "HPI Forecasting":
        st.markdown("<div class='subtitle'>HPI Forecasting</div>", unsafe_allow_html=True)
        
        regions = hpi_df.columns.tolist()
        selected_region = st.selectbox("Select Region", regions)
        
        forecast_year = st.slider("Select Forecast Year", min_value=2024, max_value=2027, value=2025)
        start_date = pd.to_datetime(f'{forecast_year}-01-01')
        end_date = pd.to_datetime(f'{forecast_year + 3}-12-31')

        forecast_dates, forecast_series = forecast_hpi(hpi_df, selected_region, start_date, end_date)
        
        if forecast_dates is not None and forecast_series is not None:
            buf = plot_hpi(region=selected_region, data=hpi_df[selected_region], forecast_dates=forecast_dates, forecast=forecast_series)
            st.image(buf, use_column_width=True)
        else:
            st.error("No forecast could be generated for the selected region.")

if __name__ == "__main__":
    housing_dashboard()
