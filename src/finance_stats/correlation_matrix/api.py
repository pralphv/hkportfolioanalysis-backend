from typing import List, Dict

from pandas import DataFrame


def calculate_correlation_matrix(stock_pct_df: DataFrame) -> List[Dict]:
    corr_df = stock_pct_df.corr().reset_index()
    dict_ = corr_df.to_dict(orient='records')
    return dict_
