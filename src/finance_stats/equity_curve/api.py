from typing import List, Dict

from pandas import DataFrame, Series, concat


def generate_equity_curves(
        portfolio_return: Series,
        stock_pct_df: DataFrame,
        market_pct_df: DataFrame,
        buy_date: str
) -> List[Dict]:
    """
    Generates cumprod of df returns.
    This builds an equity curve.
    :param portfolio_return:
    :param stock_pct_df:
    :param market_pct_df:
    :param buy_date: etc. 2020-01-01
    :return:
    """
    dfs = concat([portfolio_return, stock_pct_df, market_pct_df], axis=1)
    dfs = dfs.rename(columns={0: 'portfolio'})
    dfs = dfs[buy_date:]
    for i in range(dfs.shape[1]):  # to make equity curve start at 0
        dfs.iat[0, i] = 0
    dfs = dfs + 1
    dfs = dfs.cumprod()
    dfs = dfs - 1
    dfs['date'] = dfs.index.strftime('%Y-%m-%d')
    return dfs.to_dict(orient='record')
