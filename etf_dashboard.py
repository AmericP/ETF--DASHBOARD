import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

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
        st.success(f"Added {new_ticker} to tracking list!")

# Add removal functionality
remove_ticker = st.sidebar.selectbox("Select Ticker to Remove", st.session_state.tickers)
if st.sidebar.button("Remove Ticker") and remove_ticker:
    if remove_ticker in st.session_state.tickers:
        st.session_state.tickers.remove(remove_ticker)
        st.success(f"Removed {remove_ticker} from tracking list!")
        # Force a rerun to update the dashboard immediately
        st.rerun()

update_interval = 300  # 5 minutes in seconds
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
            if not today_data.empty and not hist_data.empty:
                data[ticker] = {"today": today_data, "history": hist_data}
            else:
                st.warning(f"No data found for {ticker}; it may be delisted or invalid.")
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {str(e)}")
    return data

# Function to format grid data with triggers
def format_grid_data(data, stop_loss_pct, exit_trigger_pct):
    grid_data = []
    for ticker, ticker_data in data.items():
        today_data = ticker_data["today"]
        if today_data.empty:
            continue  # Skip if no data
        latest = today_data.iloc[-1]
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
        y=hist_data["Close"],
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

# Function to color the "Price" column based on price change
def color_price(row):
    styles = [""] * len(row)
    price_idx = row.index.get_loc("Price")
    if row["Price"] > row["Open"]:
        styles[price_idx] = "color: green"
    elif row["Price"] < row["Open"]:
        styles[price_idx] = "color: red"
    return styles

# Main dashboard content
def display_dashboard():
    data = fetch_data(st.session_state.tickers)
    
    if data:
        grid_df = format_grid_data(data, stop_loss_pct, exit_trigger_pct)
        if not grid_df.empty:
            styled_grid = grid_df.style.apply(color_price, axis=1).format({
                "Price": "{:.2f}",
                "Open": "{:.2f}",
                "High": "{:.2f}",
                "Low": "{:.2f}",
                "Change %": "{:.2f}%"
            })
            with st.container():
                st.subheader("Real-Time Stock/ETF Grid")
                st.dataframe(styled_grid, use_container_width=True)
        else:
            st.warning("No valid data to display in the grid.")
    
    # Ensure selected_ticker exists in current tickers list
    if st.session_state.tickers:
        selected_ticker = st.selectbox("Select a Ticker for Details", st.session_state.tickers, key="ticker_select")
        if selected_ticker in data:
            today_data = data[selected_ticker]["today"]
            hist_data = data[selected_ticker]["history"]
            
            if not today_data.empty:
                table_df = today_data[["Open", "High", "Low", "Close", "Volume"]].reset_index()
                table_df.columns = ["Date", "Open", "High", "Low", "Price", "Volume"]
                table_df["Change %"] = ((table_df["Price"] - table_df["Open"]) / table_df["Open"]) * 100
                table_df["Date"] = table_df["Date"].dt.strftime("%m/%d/%Y %H:%M")
                
                with st.container():
                    st.subheader(f"{selected_ticker} Price History (Today)")
                    st.dataframe(table_df.tail(10), use_container_width=True)
            
            if not hist_data.empty:
                fig = create_performance_graph(selected_ticker, hist_data)
                with st.container():
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No tickers available to display. Please add some tickers.")

# Initialize last update time
if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()

# Display the dashboard
display_dashboard()

# Auto-refresh logic
current_time = time.time()
if current_time - st.session_state.last_update >= update_interval:
    st.session_state.last_update = current_time
    st.rerun()

# Display next refresh countdown
seconds_until_refresh = int(update_interval - (current_time - st.session_state.last_update))
st.sidebar.write(f"Next refresh in {seconds_until_refresh} seconds")