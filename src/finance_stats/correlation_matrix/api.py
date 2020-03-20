from typing import List, Dict

from pandas import DataFrame


def calculate_correlation_matrix(stock_pct_df: DataFrame) -> List[Dict]:
    return stock_pct_df.corr().to_dict(orient='records')
