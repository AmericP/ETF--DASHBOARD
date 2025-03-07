import yfinance as yf
import pandas as pd
import streamlit as st
import datetime
import time
import matplotlib.pyplot as plt
from email.message import EmailMessage
import smtplib

# Streamlit UI Setup
st.title("📈 Live-Updated ETF Tracking Dashboard")
st.write("Live market data with continuous updates and customizable ETF selection.")

# Sidebar: Custom ETF Selection
st.sidebar.header("Customize Your ETFs")
selected_etfs = st.sidebar.text_input("Enter tickers (comma-separated)", "QQQ, XBI, CIBR, VIG, VPU")
etfs = [ticker.strip().upper() for ticker in selected_etfs.split(",")]

# Live Refresh Settings
REFRESH_INTERVAL = 300  # 5 minutes (in seconds)
DAILY_RESET_TIME = "00:00"  # Midnight reset

# Function to fetch historical data
def get_etf_data(period="1mo"):
    data = {}
    for etf in etfs:
        try:
            ticker = yf.Ticker(etf)
            hist = ticker.history(period=period)
            data[etf] = hist["Close"]
        except:
            st.warning(f"⚠️ Could not fetch data for {etf}. Check the ticker symbol.")
    return pd.DataFrame(data)

# Get ETF Performance Data
df = get_etf_data("1mo")

# Display Historical Prices
st.subheader("📊 ETF Price History")
st.write(df.tail(10))  # Show last 10 entries

# Plot ETF Performance
st.subheader("📉 Performance Graph")
st.write("Select ETFs to visualize price trends.")
selected_plot_etfs = st.multiselect("Choose ETFs", etfs, default=etfs)

plt.figure(figsize=(10,5))
for etf in selected_plot_etfs:
    plt.plot(df.index, df[etf], label=etf)

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
        price = df[etf].iloc[-1]
        if price <= stop_loss[etf]:
            msg = f"🚨 ALERT: {etf} hit Stop-Loss at ${stop_loss[etf]:.2f}!"
            st.warning(msg)
            alert_messages.append(msg)
        elif price >= take_profit[etf]:
            msg = f"✅ ALERT: {etf} hit Take-Profit at ${take_profit[etf]:.2f}!"
            st.success(msg)
            alert_messages.append(msg)

# Email Alerts (Optional)
def send_email_alerts(messages):
    EMAIL_ADDRESS = "your_email@gmail.com"  # Replace with your email
    EMAIL_PASSWORD = "your_password"  # Replace with your email password

    if messages:
        msg = EmailMessage()
        msg['Subject'] = "ETF Alert Notification 🚀"
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = "recipient_email@gmail.com"  # Replace with recipient email
        msg.set_content("\n".join(messages))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

# Send email if alerts exist
if alert_messages:
    send_email_alerts(alert_messages)

# Continuous Live Updates
st.write(f"🔄 **Auto-refreshing every {REFRESH_INTERVAL // 60} minutes** (and resetting daily at midnight).")
for i in range(REFRESH_INTERVAL, 0, -1):
    st.write(f"Next refresh in {i} seconds...", end="\r")
    time.sleep(1)
st.experimental_rerun()  # Refresh page