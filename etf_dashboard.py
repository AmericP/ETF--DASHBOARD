import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import time
import matplotlib.pyplot as plt

# Streamlit UI Setup
st.title("📈 Live Stock & ETF Tracking Dashboard")
st.write("Track live market data with real-time updates and customizable stocks/ETFs.")

# Sidebar: Custom ETF Selection
st.sidebar.header("Customize Your Watchlist")
selected_etfs = st.sidebar.text_input("Enter tickers (comma-separated)", "QQQ, XBI, CIBR, VIG, VPU")
etfs = [ticker.strip().upper() for ticker in selected_etfs.split(",")]

# Timeframe Selection
st.sidebar.header("Select Timeframe")
timeframe = st.sidebar.selectbox("View Data For", ["Daily", "Weekly", "Monthly"])

# Function to fetch historical data
def get_etf_data(etf, period="1mo", interval="1d"):
    try:
        ticker = yf.Ticker(etf)
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            st.warning(f"⚠️ No data found for {etf}. It may be an invalid ticker or unavailable.")
            return None
        
        # Add % Change column
        hist["% Change"] = hist["Close"].pct_change() * 100

        # Select relevant columns and remove unwanted ones
        hist = hist[["Open", "Close", "High", "Low", "% Change"]]
        
        return hist.dropna()
    except Exception as e:
        st.error(f"❌ Error fetching data for {etf}: {e}")
        return None

# Map timeframe selection to Yahoo Finance intervals
timeframe_map = {
    "Daily": ("1mo", "1d"),
    "Weekly": ("3mo", "1wk"),
    "Monthly": ("6mo", "1mo")
}
selected_period, selected_interval = timeframe_map[timeframe]

# **Display ETF Price History**
st.subheader("📊 Stock & ETF Price History")

for etf in etfs:
    st.write(f"**{etf} Performance Data**")
    df = get_etf_data(etf, selected_period, selected_interval)
    
    if df is not None and not df.empty:
        df_display = df.copy()
        df_display.insert(0, "Date", df.index.date)
        df_display.rename(columns={"Close": "Price"}, inplace=True)

        # Display cleaned table
        st.dataframe(df_display)
    else:
        st.warning(f"⚠️ No available data for {etf}. Please check the ticker symbol.")

# **Enhanced Performance Graph**
st.subheader("📉 ETF Performance Over Time")
st.write("Select Stocks/ETFs to visualize trends.")
selected_plot_etfs = st.multiselect("Choose Stocks/ETFs", etfs, default=etfs)

plt.figure(figsize=(12, 6))
for etf in selected_plot_etfs:
    df = get_etf_data(etf, selected_period, selected_interval)
    if df is not None and not df.empty:
        plt.plot(df.index, df["Price"], label=etf, linewidth=2)

plt.xlabel("Date")
plt.ylabel("Price ($)")
plt.title("ETF Price Trends Over Time")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)
st.pyplot(plt)

st.write("🔄 **Auto-refreshing every 5 minutes** and resetting daily at midnight.")
time.sleep(300)
st.experimental_rerun()  # Auto-refresh every 5 minutes