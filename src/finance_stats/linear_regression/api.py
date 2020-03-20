from typing import Dict

from pandas import Series
from scipy.stats import linregress


def calculate_beta_alpha(portfolio_return: Series, market_return: Series) -> Dict:
    beta, intercept, r_value, p_value, std_err = linregress(
        x=market_return,
        y=portfolio_return
    )
    return {'alpha': intercept, 'beta': beta}


def main():
    try:
        from .. import data
    except ImportError:
        from src import data
    df = data.stock.fetch_stocks(['0700.HK', '0001.HK'])
    stock_pct_df = df.pct_change()[1:]
    weight_list = [0.9, 0.1]
    portfolio_return = stock_pct_df.dot(weight_list)
    market_returns = data.stock.fetch_stocks(['^HSI']).pct_change()[1:]['^HSI']

    print(calculate_beta_alpha(portfolio_return, market_returns))


if __name__ == '__main__':
    main()
