from pandas import Series


def calculate_sortino(portfolio_return: Series):
    mean = portfolio_return.mean()
    portfolio_return = portfolio_return[portfolio_return >= 0]
    std = portfolio_return.std()
    return mean / std
