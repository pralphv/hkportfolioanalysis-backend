from datetime import datetime, time
import logging
import json
import os
import requests
import traceback

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src import models
from src import data
from src import finance_stats

load_dotenv()

def send_slack_msg(msg):
    slack_hook = os.environ.get("SLACK_HOOK")
    obj = {'text': msg}
    requests.put(slack_hook, data=json.dumps(obj))


send_slack_msg('HKPORTFOLIOANALYSIS BACKEND has been initiated')


logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(levelname)s: %(message)s")

LAST_CACHE_RESET = {'date': None}

DEBUG = True if os.name == 'nt' else False  # assume windows is not server
app = FastAPI()

origins = [
    'http://localhost:5000',
    'https://hkportfolioanalysis.firebaseapp.com/'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def clear_cache(time_now):
    data.business_days.clear_cache()
    data.stock.clear_cache()
    LAST_CACHE_RESET['date'] = time_now


def clear_cache_scheduler():
    now = datetime.utcnow()
    market_closed = now.time() > time(8, 35)  # HKT 4:35pm
    is_weekday = now.weekday() < 5

    #  CACHE RESET
    if market_closed and is_weekday:
        if LAST_CACHE_RESET['date']:
            if now.day != LAST_CACHE_RESET['date'].day:
                clear_cache(now)
        else:
            clear_cache(now)


def buy_date_adaptor(buy_date: str):
    """
    20200101 -> 2020-01-01
    :param buy_date:
    :return:
    """
    if len(buy_date) == 8:
        buy_date = f'{buy_date[:4]}-{buy_date[4:-2]}-{buy_date[-2:]}'
    return buy_date


@app.post('/api/hkportfolioanalysis_bundle')
async def run_hkportfolioanalysis_bundle(parameters: models.Bundle):
    clear_cache_scheduler()
    try:
        stockObj = parameters.stockObj
        stock_list = stockObj.keys()
        stock_list = list(map(lambda string: f'{string}.HK', stock_list))
        money_list = list(stockObj.values())
        buy_date = buy_date_adaptor(parameters.buyDate)
    except KeyError:
        return 'Bad Input'
    try:
        stock_df = await data.stock.fetch_stocks(stock_list)
        stock_pct_df = stock_df.pct_change()[1:]
        portfolio_sum = sum(money_list)
        weight_list = list(map(lambda x: x / portfolio_sum, money_list))

        portfolio_return = stock_pct_df.dot(weight_list)
        market_df = await data.stock.fetch_stocks(['^HSI'])
        market_returns = market_df.pct_change()[1:]['^HSI']

        sortino = finance_stats.calculate_sortino(portfolio_return)
        sharpe = finance_stats.calculate_sharpe(portfolio_return)
        linear_regression = finance_stats.calculate_beta_alpha(portfolio_return, market_returns)
        corr_matrix = finance_stats.calculate_correlation_matrix(stock_pct_df)
        hedge_obj = finance_stats.calculate_hedge(
            linear_regression['beta'],
            market_df.iloc[-1].item(),
            portfolio_sum
        )
        equity_curves_obj = finance_stats.generate_equity_curves(
            portfolio_return,
            stock_pct_df,
            market_returns,
            buy_date
        )
        bundle = {
            'sortino': sortino,
            'sharpe': sharpe,
            'linearRegression': linear_regression,
            'correlation_matrix': corr_matrix,
            'hedge': hedge_obj,
            'equityCurves': equity_curves_obj
        }
        return bundle
    except Exception as e:
        print(e)
        traceback.print_exc()
        return 'Bad Request'


