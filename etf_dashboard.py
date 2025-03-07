import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
import matplotlib.pyplot as plt

# Streamlit page configuration
st.set_page_config(page_title="Stock/ETF Live Monitoring Dashboard", layout="wide")

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
        open_price = round(latest["Open"], 2)
        stop_loss_triggered = price < open_price * (1 - stop_loss_pct)
        exit_triggered = price > open_price * (1 + exit_trigger_pct)
        grid_row = {
            "Ticker": ticker,
            "Date": latest.name.strftime("%m/%d %H:%M"),
            "Price": price,
            "Open": open_price,
            "High": round(latest["High"], 2),
            "Low": round(latest["Low"], 2),
            "Volume": int(latest["Volume"]),
            "Change %": round(((price - open_price) / open_price) * 100, 2),
            "Stop-Loss": "Yes" if stop_loss_triggered else "No",
            "Exit Trigger": "Yes" if exit_triggered else "No"
        }
        grid_data.append(grid_row)
    return pd.DataFrame(grid_data)

# Function to create performance graph
def create_performance_graph(ticker, hist_data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist_data.index,
        y=hist_data["Close"],  # Fixed: Use "Close" instead of "Price"
        mode="lines",
        name=f"{ticker} Price",
        line=dict(color="blue")
    ))
    fig.update_layout(
        title=f"{ticker} Performance (Last 30 Days)",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_white"
    )
    return fig

# Function to color the grid based on price change
def color_price(row):
    if row["Price"] > row["Open"]:
        return ["background-color: #90EE90"] * len(row)
    elif row["Price"] < row["Open"]:  # Fixed: Use row["Open"] instead of open_price
        return ["background-color: #FFB6C1"] * len(row)
    return [""] * len(row)

# Main dashboard loop
placeholder_grid = st.empty()
placeholder_table = st.empty()
placeholder_graph = st.empty()

while True:
    # Fetch data
    data = fetch_data(st.session_state.tickers)
    
    # Compact grid for tracking
    if data:
        grid_df = format_grid_data(data, stop_loss_pct, exit_trigger_pct)
        
        # Apply color formatting
        styled_grid = grid_df.style.apply(color_price, axis=1).format({
            "Price": "{:.2f}",
            "Open": "{:.2f}",
            "High": "{:.2f}",
            "Low": "{:.2f}",
            "Change %": "{:.2f}%"
        })
        
        with placeholder_grid.container():
            st.subheader("Real-Time Stock/ETF Grid")
            st.dataframe(styled_grid, use_container_width=True)
    
    # Detailed table and graph for selected ticker
    selected_ticker = st.selectbox("Select a Ticker for Details", st.session_state.tickers)
    if selected_ticker in data:
        today_data = data[selected_ticker]["today"]
        hist_data = data[selected_ticker]["history"]
        
        # ETF/Stock price history table
        table_df = today_data[["Open", "High", "Low", "Close", "Volume"]].reset_index()
        table_df.columns = ["Date", "Open", "High", "Low", "Price", "Volume"]
        table_df["Change %"] = ((table_df["Price"] - table_df["Open"]) / table_df["Open"]) * 100
        table_df["Date"] = table_df["Date"].dt.strftime("%m/%d/%Y %H:%M")
        
        with placeholder_table.container():
            st.subheader(f"{selected_ticker} Price History (Today)")
            st.dataframe(table_df.tail(10), use_container_width=True)  # Show last 10 entries
        
        # Performance history graph
        fig = create_performance_graph(selected_ticker, hist_data)
        with placeholder_graph.container():
            st.plotly_chart(fig, use_container_width=True)
    
    # Auto-refresh
    time.sleep(update_interval)
