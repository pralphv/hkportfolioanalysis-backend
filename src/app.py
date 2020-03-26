from datetime import datetime, time
import logging
import traceback

from flask import Flask, make_response, request, jsonify

from src import data
from src import finance_stats

logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(levelname)s: %(message)s")

app = Flask(__name__)

LAST_CACHE_RESET = {'date': None}


def clear_cache(time_now):
    data.business_days.clear_cache()
    data.stock.clear_cache()
    LAST_CACHE_RESET['date'] = time_now


@app.route('/api/hkportfolioanalysis_bundle', methods=['POST'])
def run_hkportfolioanalysis_bundle():
    now = datetime.utcnow()
    market_closed = now.time() > time(8, 35)  # HKT 4:35pm
    is_weekday = now.weekday() < 5

    if market_closed and is_weekday:
        if LAST_CACHE_RESET['date']:
            if now.day != LAST_CACHE_RESET['date'].day:
                clear_cache(now)
        else:
            clear_cache(now)

    try:
        parameters = request.json
        stock_list = parameters['stockList']
        money_list = parameters['moneyList']
        buy_date = parameters['buyDate']

        stock_df = data.stock.fetch_stocks(stock_list)
        stock_pct_df = stock_df.pct_change()[1:]
        portfolio_sum = sum(money_list)
        weight_list = list(map(lambda x: x / portfolio_sum, money_list))

        portfolio_return = stock_pct_df.dot(weight_list)
        market_df = data.stock.fetch_stocks(['^HSI'])
        market_returns = market_df.pct_change()[1:]['^HSI']

        sortino = finance_stats.calculate_sortino(portfolio_return)
        sharpe = finance_stats.calculate_sharpe(portfolio_return)
        lr = finance_stats.calculate_beta_alpha(portfolio_return, market_returns)
        corr_matrix = finance_stats.calculate_correlation_matrix(stock_pct_df)
        hedge_obj = finance_stats.calculate_hedge(
            lr['beta'],
            market_df.iloc[-1].item(),
            portfolio_sum
        )
        equity_curves_obj = finance_stats.generate_equity_curves(
            portfolio_return,
            market_returns,
            buy_date
        )
        bundle = {
            'sortino': sortino,
            'sharpe': sharpe,
            'lr': lr,
            'correlation_matrix': corr_matrix,
            'hedge': hedge_obj,
            'equityCurves': equity_curves_obj
        }
        return make_response(jsonify(bundle), 200)
    except Exception as e:
        # print(e)
        # traceback.print_exc()
        return make_response('Bad Request', 400)


if __name__ == '__main__':
    app.run(debug=True)
