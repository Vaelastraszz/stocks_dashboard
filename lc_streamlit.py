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


if __name__ == "__main__":
    render_title()
    selected_symbol = render_choice_symbols()
