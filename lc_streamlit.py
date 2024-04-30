import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go


def render_title():
    st.title("My Stocks Dashboard")


def render_choice_symbols() -> str:
    ticker_symbol = ["NVDA", "AAPL", "GOOGL", "AMZN", "MSFT"]
    selected_symbol = st.selectbox("Select a symbol", ticker_symbol)
    return selected_symbol


def get_api_key(
    path: str = "/Users/romainlejeune/Desktop/Python/APIs/alpha_v.txt",
) -> tuple[str]:
    with open(path, "r") as file_api:
        first_line = file_api.readline()
        second_line = file_api.readline()
        return first_line.split(":")[1].strip(), second_line.split(":")[1].strip()


@st.cache_data
def fetch_daily_data(symbol: str, api_key: str = get_api_key()[0]) -> pd.DataFrame:
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data["Time Series (Daily)"]).T
        df.index = pd.to_datetime(df.index)
        return df
    else:
        st.write("Error fetching data")
        return None


@st.cache_data
def fetch_news(symbol: str, api_key: str = get_api_key()[1]) -> pd.DataFrame:
    url = f"https://newsapi.org/v2/everything?q={symbol}&sortBy=publishedAt&apiKey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data["articles"])
        return df
    else:
        st.write("Error fetching data")
        return None


def calculate_moving_average(data: pd.DataFrame, window: int = 25) -> pd.Series:
    data["MA"] = data["4. close"].rolling(window=window).mean()
    return data


def render_candle_chart(data: pd.DataFrame) -> None:
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
                y=calculate_moving_average(data, 20)["MA"],
                mode="lines",
                line=go.scatter.Line(color="red"),
                name="Moving average",
            ),
        ]
    )

    fig.update_layout(
        title="Candlestick chart",
        xaxis_title="Date",
        yaxis_title="Price",
    )

    st.plotly_chart(fig)


if __name__ == "__main__":
    render_title()
    selected_symbol = render_choice_symbols()
    if selected_symbol:
        st.header(f"Daily data for {selected_symbol}")
        data = fetch_daily_data(selected_symbol)
        st.dataframe(data.head(), use_container_width=True)
        st.subheader("Candlestick chart")
        render_candle_chart(data)
