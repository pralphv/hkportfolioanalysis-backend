from typing import Dict


def calculate_hedge(beta: float, current_hsi_price: int, sum_of_portfolio: float) -> Dict:
    hsi_loss = current_hsi_price * 0.01
    port_loss = sum_of_portfolio * 0.01 * beta
    if port_loss >= hsi_loss * 50:
        hedge_product = 'HSI Futures'
        lot = port_loss / (hsi_loss * 50)
    elif port_loss >= hsi_loss * 10:
        hedge_product = 'HSI Futures Mini'
        lot = port_loss / (hsi_loss * 10)
    else:
        hedge_product = 'CBBC'
        lot = port_loss / hsi_loss
    hedge_return = {
        'hedge_product': hedge_product,
        'lot': lot,
    }
    return hedge_return
