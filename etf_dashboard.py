import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import time

# Streamlit UI Setup
st.title("📈 Live Stock & ETF Tracking Dashboard")
st.write("Monitor real-time stock & ETF prices with performance tracking.")

# Sidebar: Custom Stock & ETF Selection
st.sidebar.header("📌 Watchlist")
selected_etfs = st.sidebar.text_input("Enter tickers (comma-separated)", "QQQ, XBI, CIBR, VIG, VPU")
etfs = [ticker.strip().upper() for ticker in selected_etfs.split(",")]

# Function to fetch historical data
def get_etf_data(etf, period="1mo", interval="1d"):
    try:
        ticker = yf.Ticker(etf)
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            return None
        
        # Calculate Change %
        hist["% Change"] = hist["Close"].pct_change() * 100

        # Keep only relevant columns
        hist = hist[["Open", "Close", "High", "Low", "Volume", "% Change"]]

        # Abbreviate date format
        hist.index = hist.index.strftime("%b %d")  # Example: "Mar 07"

        return hist.dropna()
    except Exception:
        return None

# **Stock & ETF Price Grid**
st.subheader("📊 Watchlist Prices")

grid_data = []
for etf in etfs:
    df = get_etf_data(etf, "1d", "1h")  # Fetch intraday data for the latest price
    if df is not None and not df.empty:
        latest = df.iloc[-1]
        grid_data.append([etf, latest["Close"], latest["% Change"]])

# Convert to DataFrame & Display Grid
if grid_data:
    df_grid = pd.DataFrame(grid_data, columns=["Symbol", "Last Price ($)", "Change %"])
    st.dataframe(df_grid.style.format({"Last Price ($)": "{:.2f}", "Change %": "{:.2f}%"}))
else:
    st.warning("⚠️ No data available. Check ticker symbols.")

# **ETF Price History Table**
st.subheader("📜 Price History")

for etf in etfs:
    df = get_etf_data(etf, "1mo", "1d")
    
    if df is not None and not df.empty:
        df_display = df.copy()
        df_display.insert(0, "Date", df.index)
        df_display.rename(columns={"Close": "Price"}, inplace=True)

        # Apply Color Formatting
        def highlight_price(val, open_val):
            return f"color: {'green' if val > open_val else 'red'}"

        df_styled = df_display.style.apply(lambda x: [highlight_price(v, x["Open"]) for v in x["Price"]], axis=1)

        st.write(f"📌 **{etf}**")
        st.dataframe(df_styled)
    else:
        st.warning(f"⚠️ No data available for {etf}.")

# **ETF Performance Over Time (Graph)**
st.subheader("📉 Performance Chart")

plt.figure(figsize=(12, 6))
for etf in etfs:
    df = get_etf_data(etf, "1mo", "1d")
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
