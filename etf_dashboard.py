import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Streamlit page configuration
st.set_page_config(page_title="Stock/ETF Live Dashboard", layout="wide")

# Title
st.title("Stock & ETF Live Monitoring Dashboard")

# Sidebar for user input
st.sidebar.header("Settings")
default_tickers = "AAPL, SPY, QQQ"
if "tickers" not in st.session_state:
    st.session_state.tickers = [ticker.strip().upper() for ticker in default_tickers.split(",")]

tickers_input = st.sidebar.text_input("Enter Stock/ETF Tickers (comma-separated)", default_tickers)
new_ticker = st.sidebar.text_input("Add New Ticker", "")
if st.sidebar.button("Add Ticker") and new_ticker:
    new_ticker = new_ticker.strip().upper()
    if new_ticker not in st.session_state.tickers:
        st.session_state.tickers.append(new_ticker)

update_interval = 300  # Fixed 5 minutes (300 seconds)
stop_loss_pct = st.sidebar.slider("Stop-Loss Trigger (% below Open)", 1, 10, 5) / 100
exit_trigger_pct = st.sidebar.slider("Exit Trigger (% above Open)", 1, 20, 10) / 100

# Function to fetch real-time data
def fetch_data(tickers):
    data = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            today_data = stock.history(period="1d", interval="1m")
            hist_data = stock.history(period="30d")
            data[ticker] = {
                "today": today_data,
                "history": hist_data
            }
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {str(e)}")
    return data

# Function to format grid data with triggers
def format_grid_data(data, stop_loss_pct, exit_trigger_pct):
    grid_data = []
    for ticker, ticker_data in data.items():
        latest = ticker_data["today"].iloc[-1]
        price = round(latest["Close"], 2)
        open_price
