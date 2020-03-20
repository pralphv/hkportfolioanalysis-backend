from pandas import Series

def calculate_sharpe(portfolio_return: Series):
    return portfolio_return.mean() / portfolio_return.std()
