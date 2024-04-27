import streamlit as st
import pandas as pd
import requests
import plotly.express as px


def render_title() -> None:
    st.title("Stock Dashboard Analysis")


def get_api_key(
    file_api_path="/Users/romainlejeune/Desktop/Python/APIs/alpha_v.txt",
) -> str:
    with open(file_api_path, "r") as file:
        first_line = file.readline()
        return first_line.split(":")[1]


def fetch_data(symbol: str, api_key=get_api_key()) -> pd.DataFrame:
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()["Time Series (Daily)"]
        df = pd.DataFrame(data).T
        df.index = pd.to_datetime(df.index)
        return df
    else:
        st.error("Error fetching data")


def render_choice_symbol() -> str:
    ticker_symbol = ["NVDA", "AAPL", "GOOGL", "AMZN", "MSFT"]
    selected_symbol = st.selectbox("Select a symbol", ticker_symbol)
    return selected_symbol


if __name__ == "__main__":
    render_title()
    symbol = render_choice_symbol()
