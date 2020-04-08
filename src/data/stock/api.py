from typing import List
import asyncio
import logging

from cachetools import LFUCache, cached
from dotenv import load_dotenv
from pandas_datareader.data import get_data_yahoo
import pandas as pd

try:
    from .. import business_days
    from ... import utils
except ImportError:
    from src.data import business_days
    from src import utils

STOCK_CACHE = LFUCache(maxsize=500)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s:%(levelname)s: %(message)s")


@utils.async_wrap
@cached(STOCK_CACHE)
def fetch_raw_data(stock: str, start: str) -> pd.Series:
    logging.info(f'Fetching from Yahoo: {stock}')
    series = get_data_yahoo(stock, start=start)['Adj Close']  # retries 3 times (retry_count)
    logging.info(f'Successfully fetched from Yahoo: {stock}')
    return series


async def run_throttled(stock, start, sem):
    async with sem:
        result = await fetch_raw_data(stock, start)
    return result


async def fetch_data_batch(list_of_stocks: List[str], start: str) -> pd.DataFrame:
    coroutines = []
    sem = asyncio.Semaphore(5)
    for stock in list_of_stocks:
        series = run_throttled(stock, start, sem)
        coroutines.append(series)
    stock_series = await asyncio.gather(*coroutines)
    stocks_df = pd.concat(stock_series, axis=1)
    stocks_df.columns = list_of_stocks
    return stocks_df


def standardize_stock_df(stock_df: pd.DataFrame, business_days_) -> pd.DataFrame:
    stock_df = stock_df.reindex(business_days_)
    stock_df = stock_df.ffill()
    return stock_df


async def fetch_stocks(list_of_stocks: List[str]) -> pd.DataFrame:
    business_days_ = business_days.fetch_data()
    stock_df = await fetch_data_batch(list_of_stocks, business_days_[0])
    stock_df = standardize_stock_df(stock_df, business_days_)
    return stock_df


def clear_cache():
    STOCK_CACHE.clear()
    logging.debug(f'Cleared stock data cache')


async def main():
    load_dotenv()

    stock_list = ['0700.HK', '^HSI']
    df = await fetch_stocks(stock_list)
    stock_list = ['0005.HK', '^HSI']
    print(df)
    df = await fetch_stocks(stock_list)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
