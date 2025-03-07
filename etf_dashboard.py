import streamlit as st  # ✅ Make sure this is the first import
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

# Ensure Streamlit is imported before it's used!