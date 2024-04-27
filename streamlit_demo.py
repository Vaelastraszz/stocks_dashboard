import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


def render_title() -> None:
    st.title("Stock Dashboard Analysis")


def get_api_key(
    file_api_path="/Users/romainlejeune/Desktop/Python/APIs/alpha_v.txt",
) -> str:
    with open(file_api_path, "r") as file:
        first_line = file.readline()
        second_line = file.readline()
        return first_line.split(":")[1], second_line.split(":")[1]


def fetch_data(symbol: str, api_key=get_api_key()[0]) -> pd.DataFrame:
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key.strip()}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()["Time Series (Daily)"]
        df = pd.DataFrame(data).T
        df.index = pd.to_datetime(df.index)
        return df
    else:
        st.error("Error fetching data")


def fetch_news(symbol: str, api_key=get_api_key()[1]) -> pd.DataFrame:
    url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey={api_key.strip()}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()["articles"]
        return pd.DataFrame(data)
    else:
        st.error("Error fetching data")


def render_choice_symbol() -> str:
    ticker_symbol = ["NVDA", "AAPL", "GOOGL", "AMZN", "MSFT"]
    selected_symbol = st.selectbox("Select a symbol", ticker_symbol)
    return selected_symbol


def calculate_moving_average(data: pd.DataFrame, window: int) -> pd.DataFrame:
    data["moving_average"] = data["4. close"].rolling(window=window).mean()
    return data


def calculate_variations(data: pd.DataFrame) -> pd.DataFrame:
    data[["1. open", "2. high", "3. low", "4. close"]] = data[
        ["1. open", "2. high", "3. low", "4. close"]
    ].astype(float)
    last_day_change = data["4. close"].pct_change().iloc[-1] * 100
    last_week_change = data["4. close"].pct_change(7).iloc[-1] * 100
    last_month_change = data["4. close"].pct_change(30).iloc[-1] * 100
    last_year_change = data["4. close"].pct_change(365).iloc[-1] * 100
    return last_day_change, last_week_change, last_month_change, last_year_change


def render_candle_chart(data: pd.DataFrame, symbol: str) -> None:
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=data.index,
                open=data["1. open"],
                high=data["2. high"],
                low=data["3. low"],
                close=data["4. close"],
            ),
            go.Scatter(
                x=data.index,
                y=calculate_moving_average(data, 20)["moving_average"],
                mode="lines",
                line=go.scatter.Line(color="red"),
                name="20 days SMA",
            ),
        ]
    )

    fig.update_layout(
        title=f"Candlestick Chart for {symbol}", xaxis_title="Date", yaxis_title="Price"
    )
    st.plotly_chart(fig)


if __name__ == "__main__":
    render_title()
    symbol = render_choice_symbol()

    if symbol:
        st.subheader(f"Displaying data for {symbol}")
        st.write(fetch_data(symbol))

        last_day_change, last_week_change, last_month_change, last_year_change = (
            calculate_variations(fetch_data(symbol))
        )

        st.metric(
            label="Last Day % Change",
            value=fetch_data(symbol)["4. close"].iloc[-1],
            delta=f"{last_day_change:.2f}%",
        )

        st.metric(
            label="Last Week % Change",
            value=fetch_data(symbol)["4. close"].iloc[-1],
            delta=f"{last_week_change:.2f}%",
        )

        st.metric(
            label="Last Month % Change",
            value=fetch_data(symbol)["4. close"].iloc[-1],
            delta=f"{last_month_change:.2f}%",
        )

        st.metric(
            label="Last Year % Change",
            value=fetch_data(symbol)["4. close"].iloc[-1],
            delta=f"{last_year_change:.2f}%",
        )

        render_candle_chart(fetch_data(symbol), symbol)
        st.header("Latest News")
        for index, row in fetch_news(symbol).head(5).iterrows():
            st.subheader(row["title"])
            st.write(row["description"])
            st.write(row["url"])
