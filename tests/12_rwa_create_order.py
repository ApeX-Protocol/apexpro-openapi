"""
Place an order against the RWA sub-account (e.g. AAPL-USDT).

Prerequisites (in .env):
    APEX_API_KEY / APEX_API_SECRET / APEX_API_PASSPHRASE
    APEX_ZK_SEEDS / APEX_ZK_L2KEY
    APEX_RWA_API_KEY / APEX_RWA_API_SECRET / APEX_RWA_API_PASSPHRASE

Run:
    python tests/12_rwa_create_order.py
"""
import time

from _common import banner, make_rwa_signing_client
from apexomni.helpers.util import round_size


def _find_rwa_symbol(config_data, symbol):
    for entry in (config_data.get("symbolConfig") or []):
        if entry.get("symbol") == symbol:
            return entry
    return {}


def main():
    client = make_rwa_signing_client()

    symbol = "AAPL-USDT"
    cfg = _find_rwa_symbol(client.configV3, symbol)
    step = cfg.get("stepSize")
    tick = cfg.get("tickSize")

    size = round_size("0.01", step) if step else "0.01"
    price = round_size("150", tick) if tick else "150"
    client_order_id = f"demo-{int(time.time())}"

    banner(f"limit BUY {symbol} size={size} price={price}")
    print(client.create_order_v3(
        symbol=symbol, side="BUY", type="LIMIT",
        size=size, price=price,
        clientId=client_order_id,
        account_type="rwa",
    ))


if __name__ == "__main__":
    main()
