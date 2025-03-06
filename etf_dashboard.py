import yfinance as yf
import pandas as pd
import streamlit as st
import datetime
import matplotlib.pyplot as plt

# Define ETFs to track
etfs = ["QQQ", "XBI", "CIBR", "VIG", "VPU"]

# Function to fetch historical data
def get_etf_data(period="1mo"):
    data = {}
    for etf in etfs:
        ticker = yf.Ticker(etf)
        hist = ticker.history(period=period)
        data[etf] = hist["Close"]
    return pd.DataFrame(data)

# Streamlit UI Setup
st.title("📈 Real-Time ETF Tracking Dashboard")
st.write("Live market data with stop-loss & take-profit monitoring.")

# Date Range Selection
st.sidebar.header("Select Date Range")
timeframe = st.sidebar.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y", "5y"])

# Get ETF Performance Data
df = get_etf_data(timeframe)

# Display Historical Prices
st.subheader("📊 ETF Price History")
st.write(df.tail(10))  # Show last 10 entries

# Plot ETF Performance
st.subheader("📉 Performance Graph")
st.write("Select ETFs to visualize price trends.")
selected_etfs = st.multiselect("Choose ETFs", etfs, default=etfs)

# Plotting Graph
plt.figure(figsize=(10,5))
for etf in selected_etfs:
    plt.plot(df.index, df[etf], label=etf)

plt.xlabel("Date")
plt.ylabel("Price ($)")
plt.legend()
plt.grid()
st.pyplot(plt)

# Display Alerts
st.subheader("⚠️ Stop-Loss & Take-Profit Alerts")
stop_loss = df.iloc[-1] * 0.90  # 10% below last price
take_profit = df.iloc[-1] * 1.20  # 20% above last price

for etf in etfs:
    price = df[etf].iloc[-1]
    if price <= stop_loss[etf]:
        st.warning(f"🚨 {etf} hit Stop-Loss at ${stop_loss[etf]:.2f}!")
    elif price >= take_profit[etf]:
        st.success(f"✅ {etf} hit Take-Profit at ${take_profit[etf]:.2f}!")

st.write("Updating every 60 seconds...")
