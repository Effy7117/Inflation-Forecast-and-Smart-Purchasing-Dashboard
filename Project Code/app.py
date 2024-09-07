# app.py
import streamlit as st
from food import food_dashboard
from oil import oil_dashboard
from housing import housing_dashboard
from wage import wage_dashboard
import os

# Setting up the page configuration
st.set_page_config(page_title="Inflation Dashboard", page_icon="📊", layout="wide")

# Function to hide the Streamlit sidebar for the front screen
def hide_streamlit_style():
    hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .css-18e3th9 {padding-top: 2rem;} /* Adjust padding */
    body {
        background-color: #d3d3d3;
        font-family: Arial, sans-serif;
    }
    .stButton>button {
        font-size: 18px;
        background-color: #216f61; /* Warm color for buttons */
        color: white;
        border-radius: 12px;
        border: none;
        padding: 15px 30px;
        transition: 0.3s;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .stButton>button:hover {
        background-color: #f53b2f;
    }
    .stButton>button img {
        margin-right: 10px;
    }
    .css-1aumxhk {background: rgba(255, 255, 255, 0.9);} /* Adjust background for readability */
    .css-1a1fntz {color: #4e54c8;} /* Adjust title color */
    .css-1y34u37 {background: rgba(255, 255, 255, 0.9);} /* Adjust background for readability */
    .button-container {text-align: center; margin-top: 20px;}
    .info-container {display: flex; justify-content: space-between; margin-top: 20px;}
    .info-container img {width: 100%; max-width: 400px;}
    .table-container {margin-top: 20px;}
    </style>
    """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

# Front screen with inflation details, CPI image, and navigation buttons
def front_screen():
    st.markdown("<h1 style='text-align: center; color: #4e54c8;'>Inflation Forecast and Smart Purchasing Dashboard</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div style='background-color: rgba(255, 255, 255, 0.8); padding: 20px; border-radius: 10px; margin-top: 20px;'>
            <p style='font-size: 18px; text-align: justify;'>
            Welcome to the Inflation Forecast and Smart Purchasing Tool. This platform offers insights into the future of inflation and helps you make informed purchasing decisions by analyzing key economic indicators.
            </p>
            <p style='font-size: 18px; text-align: justify;'>
            Inflation affects the cost of living and purchasing power. This dashboard focuses on four critical factors that influence inflation in Canada:
            </p>
            <ul style='font-size: 18px;'>
                <li><b>Food Prices:</b> Track historical trends and forecast future prices to help you plan grocery budgets.</li>
                <li><b>Oil Prices:</b> Understand fluctuations in oil prices and their impact on transportation and energy costs.</li>
                <li><b>Housing Prices:</b> Analyze the housing market and forecast price changes to guide real estate decisions.</li>
                <li><b>Weekly Earnings:</b> Monitor wage growth to assess purchasing power and affordability.</li>
            </ul>
            </div>
        """, unsafe_allow_html=True)

        st.image("static/cpi.png", caption="Consumer Price Index (CPI) Trend in Canada", use_column_width=True)

        


        st.markdown("""
            <div class='info-container'>
                <div>
                    <h3 style='color: #4e54c8;'>Causes of Inflation</h3>
                    <p style='font-size: 18px; text-align: justify;'>
                    Inflation can be driven by various factors including demand-pull inflation, cost-push inflation, and built-in inflation. Each of these causes can impact the overall economy and cost of living in different ways.
                    </p>
                    <p style='font-size: 18px; text-align: justify;'>
                    The image on right illustrates some common causes of inflation.
                    </p>
                </div>

            </div>
        """, unsafe_allow_html=True)
        
        
    with col2:
        st.image("static/inflation.jpg", width=600)

        st.markdown("""
            <div style='background-color: rgba(255, 255, 255, 0.8); padding: 20px; border-radius: 10px; margin-top: 20px;'>
            <h3 style='color: #4e54c8;'>Understanding the Consumer Price Index (CPI)</h3>
            <p style='font-size: 18px; text-align: justify;'>
            The Consumer Price Index (CPI) measures the average change in prices over time that consumers pay for a basket of goods and services. It is a key indicator for inflation and reflects the cost of living.
            The CPI is used to assess price changes associated with the cost of living and is a crucial metric for economic policy, wage adjustments, and understanding inflation trends.
            </p>
            <p style='font-size: 18px; text-align: justify;'>
            This is the trend of CPI in Canada over the years, showcasing the changes in consumer prices.
            </p>
            </div>
        """, unsafe_allow_html=True)

        st.image("static/inflation_causes.png", caption="Inflation Causes", width=600)

    # Winners and Losers Table
    st.markdown("""
        <div class='table-container'>
            <h3 style='color: #4e54c8;'>Possible Winners and Losers from High Inflation</h3>
            <table style='width: 100%; border-collapse: collapse;'>
                <thead>
                    <tr style='background-color: #f2f2f2;'>
                        <th style='border: 1px solid #ddd; padding: 8px;'>Category</th>
                        <th style='border: 1px solid #ddd; padding: 8px;'>Group</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style='border: 1px solid #ddd; padding: 8px;'>Winners</td>
                        <td style='border: 1px solid #ddd; padding: 8px;'>
                            <ul style='margin: 0; padding-left: 20px;'>
                                <li>Workers with strong wage bargaining power</li>
                                <li>Debtors if real interest rates are negative</li>
                                <li>Producers if prices rise faster than costs</li>
                            </ul>
                        </td>
                    </tr>
                    <tr>
                        <td style='border: 1px solid #ddd; padding: 8px;'>Losers</td>
                        <td style='border: 1px solid #ddd; padding: 8px;'>
                            <ul style='margin: 0; padding-left: 20px;'>
                                <li>Retirees on fixed incomes</li>
                                <li>Lenders if real interest rates are negative</li>
                                <li>Savers if real returns are negative</li>
                            </ul>
                        </td>
                    </tr>
                    <tr>
                        <td style='border: 1px solid #ddd; padding: 8px;'>Additional Insights</td>
                        <td style='border: 1px solid #ddd; padding: 8px;'>
                            <ul style='margin: 0; padding-left: 20px;'>
                                <li>Small business owners may struggle due to increased costs and reduced consumer spending.</li>
                                <li>Investors in assets like real estate or commodities may benefit as their investments may appreciate in value.</li>
                            </ul>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    """, unsafe_allow_html=True)

    # Buttons for navigation
    st.markdown("<div class='button-container'>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🍞 Food Prices", help="Analyze food price trends and forecasts"):
            st.session_state.page = "Food"
    with col2:
        if st.button("🛢️ Oil Prices", help="Explore oil price trends and forecasts"):
            st.session_state.page = "Oil"
    with col3:
        if st.button("🏠 Housing Prices", help="Examine housing market trends and forecasts"):
            st.session_state.page = "Housing"
    with col4:
        if st.button("💼 Weekly Earnings", help="Review weekly earnings trends and forecasts"):
            st.session_state.page = "Wage"
    st.markdown("</div>", unsafe_allow_html=True)

if 'page' not in st.session_state:
    st.session_state.page = "Home"

if st.session_state.page == "Home":
    hide_streamlit_style()
    front_screen()
elif st.session_state.page == "Food":
    food_dashboard()
elif st.session_state.page == "Oil":
    oil_dashboard()
elif st.session_state.page == "Housing":
    housing_dashboard()
elif st.session_state.page == "Wage":
    wage_dashboard()
