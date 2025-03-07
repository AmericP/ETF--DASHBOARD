import yfinance as yf
import pandas as pd
import streamlit as st
import datetime
import smtplib
import time
import matplotlib.pyplot as plt
from email.message import EmailMessage

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
st.title("📈 Automated ETF Tracking Dashboard")
st.write("Live market data with daily updates, alerts, and performance history.")

# Auto-refresh interval
REFRESH_INTERVAL = 86400  # 1 day (in seconds)

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
selected_etfs = st.multiselect("Choose ETFs", etfs, default=etfs)

plt.figure(figsize=(10,5))
for etf in selected_etfs:
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

st.write(f"🔄 **Next auto-refresh in {REFRESH_INTERVAL // 3600} hours.**")
time.sleep(REFRESH_INTERVAL)  # Auto-refresh daily