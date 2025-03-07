# Function to apply color formatting to Price based on Open value
def highlight_price(row):
    if row["Price"] > row["Open"]:
        return ["color: green"] * len(row)
    else:
        return ["color: red"] * len(row)

# Display ETF Price History
st.subheader("📊 Stock & ETF Price History")

for etf in etfs:
    st.write(f"**{etf} Performance Data**")
    df = get_etf_data(etf, selected_period, selected_interval)
    
    if df is not None and not df.empty:
        df_display = df[["Open", "Close", "High", "Low", "Volume", "% Change"]].copy()
        df_display.insert(0, "Date", df.index.date)
        df_display.rename(columns={"Close": "Price"}, inplace=True)

        # Ensure DataFrame is not empty before applying style
        if not df_display.empty:
            df_styled = df_display.style.apply(highlight_price, axis=1)

            # Display styled table
            st.dataframe(df_styled)
        else:
            st.warning(f"⚠️ No data available for {etf}.")