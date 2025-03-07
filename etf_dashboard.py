import yfinance as yf
import pandas as pd
import streamlit as st
import datetime
import time
import matplotlib.pyplot as plt

# Streamlit UI Setup
st.title("📈 Live-Updated Stock & ETF Tracking Dashboard")
st.write("Track live market data with real-time updates and customizable stocks/ETFs.")

# Sidebar: Custom ETF Selection
st.sidebar.header("Customize Your Watchlist")
selected_etfs = st.sidebar.text_input("Enter tickers (comma-separated)", "QQQ, XBI, CIBR, VIG, VPU")
etfs = [ticker.strip().upper() for ticker in selected_etfs.split(",")]

# **NEW FEATURE: Add Additional Stocks/ETFs Dynamically**
st.sidebar.header("🔍 Add More Stocks/ETFs")
new_stock = st.sidebar.text_input("Enter a stock/ETF ticker to track", "")

# If user adds a stock, update list
if new_stock:
    if new_stock.upper() not in etfs:
        etfs.append(new_stock.upper())
        st.sidebar.success(f"✅ {new_stock.upper()} added to watchlist!")
    else:
        st.sidebar.warning(f"⚠️ {new_stock.upper()} is already being tracked.")

# Timeframe Selection
st.sidebar.header("Select Timeframe")
timeframe = st.sidebar.selectbox("View Data For", ["Daily", "Weekly", "Monthly"])
custom_date_range = st.sidebar.date_input("Select Date Range", [])

# Function to fetch historical data
def get_etf_data(etf, period="1mo", interval="1d"):
    try:
        ticker = yf.Ticker(etf)
        hist = ticker.history(period=period, interval=interval)
        hist["% Change"] = hist["Close"].pct_change() * 100
        hist = hist.dropna()
        return hist
    except:
        st.warning(f"⚠️ Could not fetch data for {etf}. Check the ticker symbol.")
        return pd.DataFrame()

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
    
    if not df.empty:
        df_display = df[["Open", "Close", "High", "Low", "Volume", "% Change"]].copy()
        df_display.insert(0, "Date", df.index.date)
        df_display.rename(columns={"Close": "Price"}, inplace=True)

        # Apply color formatting to Price based on Open value
        def highlight_price(val, open_val):
            return f"color: {'green' if val > open_val else 'red'}"

        df_styled = df_display.style.apply(lambda x: [highlight_price(v, x["Open"]) for v in x["Price"]], axis=1)

        # Display table
        st.dataframe(df_styled)

# **Plot Stock & ETF Performance**
st.subheader("📉 Performance Graph")
st.write("Select Stocks/ETFs to visualize price trends.")
selected_plot_etfs = st.multiselect("Choose Stocks/ETFs", etfs, default=etfs)

plt.figure(figsize=(10,5))
for etf in selected_plot_etfs:
    df = get_etf_data(etf, selected_period, selected_interval)
    if not df.empty:
        plt.plot(df.index, df["Close"], label=etf)

plt.xlabel("Date")
plt.ylabel("Price ($)")
plt.legend()
plt.grid()
st.pyplot(plt)

# Stop-Loss & Take-Profit Monitoring
st.subheader("⚠️ Stop-Loss & Take-Profit Alerts")
stop_loss = df.iloc[-1] * 0.90  # 10% below last price
take_profit = df.iloc[-1] * 1.20  # 20% above last price

alert_messages = []
for etf in etfs:
    if etf in df.columns:
        price = df["Close"].iloc[-1]
        if price <= stop_loss["Close"]:
            msg = f"🚨 ALERT: {etf} hit Stop-Loss at ${stop_loss['Close']:.2f}!"
            st.warning(msg)
            alert_messages.append(msg)
        elif price >= take_profit["Close"]:
            msg = f"✅ ALERT: {etf} hit Take-Profit at ${take_profit['Close']:.2f}!"
            st.success(msg)
            alert_messages.append(msg)

st.write(f"🔄 **Auto-refreshing every 5 minutes** and resetting daily at midnight.")
time.sleep(300)
st.experimental_rerun()  # Auto-refresh every 5 minutes