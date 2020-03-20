from typing import List
from cachetools import LFUCache, cached
from pandas_datareader.data import get_data_yahoo
import pandas as pd

try:
    from .. import business_days
except ImportError:
    from src.data import business_days

STOCK_CACHE = LFUCache(maxsize=500)


@cached(STOCK_CACHE)
def fetch_raw_data(stock: str, start: str) -> pd.Series:
    series = get_data_yahoo(stock, start=start)['Adj Close']  # retries 3 times (retry_count)
    return series


def fetch_data_batch(list_of_stocks: List[str], start: str) -> pd.DataFrame:
    stock_series = []
    for stock in list_of_stocks:
        series = fetch_raw_data(stock, start=start)
        stock_series.append(series)
    stocks_df = pd.concat(stock_series, axis=1)
    stocks_df.columns = list_of_stocks
    return stocks_df


def standardize_stock_df(stock_df: pd.DataFrame, business_days_) -> pd.DataFrame:
    stock_df = stock_df.reindex(business_days_)
    stock_df = stock_df.ffill()
    return stock_df


def fetch_stocks(list_of_stocks: List[str]) -> pd.DataFrame:
    business_days_ = business_days.fetch_data()
    stock_df = fetch_data_batch(list_of_stocks, business_days_[0])
    stock_df = standardize_stock_df(stock_df, business_days_)
    return stock_df


def main():
    stock_list = ['0700.HK', '^HSI']
    df = fetch_stocks(stock_list)
    df = fetch_stocks(stock_list)
    print(df)


if __name__ == '__main__':
    main()
