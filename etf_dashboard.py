import yfinance as yf
import pandas as pd
import streamlit as st
import time

# Define ETFs to track
etfs = ["QQQ", "XBI", "CIBR", "VIG", "VPU"]

# Function to fetch live prices
def get_etf_data():
    data = {}
    for etf in etfs:
        ticker = yf.Ticker(etf)
        data[etf] = ticker.history(period="1d")["Close"].values[-1]
    return data

# Initialize Streamlit App
st.title("📈 Real-Time ETF Tracking Dashboard")
st.write("Live market data with stop-loss & take-profit monitoring.")

# Set stop-loss and take-profit levels
stop_loss = {etf: price * 0.90 for etf, price in get_etf_data().items()}
take_profit = {etf: price * 1.20 for etf, price in get_etf_data().items()}

# Display data
st.header("ETF Prices & Risk Levels")
df = pd.DataFrame(get_etf_data().items(), columns=["ETF", "Current Price"])
df["Stop-Loss"] = df["ETF"].map(stop_loss)
df["Take-Profit"] = df["ETF"].map(take_profit)
st.dataframe(df)

# Alerts for Stop-Loss / Take-Profit Hits
st.subheader("⚠️ Alerts")
for etf, price in get_etf_data().items():
    if price <= stop_loss[etf]:
        st.warning(f"🚨 {etf} hit Stop-Loss at ${stop_loss[etf]:.2f}!")
    elif price >= take_profit[etf]:
        st.success(f"✅ {etf} hit Take-Profit at ${take_profit[etf]:.2f}!")

# Auto-refresh every minute
st.write("Updating every 60 seconds...")
time.sleep(60)
