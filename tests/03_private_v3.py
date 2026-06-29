"""
Private read endpoints (account, positions, fills, transfers, orders, PnL).

This demo exercises the read-only side of the private API. It is safe to
run repeatedly — none of the calls below modify state apart from the final
delete_open_orders / set_initial_margin_rate examples, which are commented
out by default.

Prerequisites (in .env):
    APEX_API_KEY / APEX_API_SECRET / APEX_API_PASSPHRASE

Run:
    python tests/03_private_v3.py
"""
from _common import banner, make_client


def main():
    client = make_client()

    banner("get_user_v3")
    print(client.get_user_v3())

    banner("get_account_v3 (cached during make_client)")
    print(client.accountV3)

    banner("positions")
    print((client.accountV3 or {}).get("positions"))

    banner("get_account_balance_v3")
    print(client.get_account_balance_v3())

    banner("fills_v3 BTC-USDT")
    print(client.fills_v3(limit=100, page=0, symbol="BTC-USDT", side="BUY", token="USDT"))

    banner("transfers_v3 (last 100)")
    print(client.transfers_v3(limit=100))

    banner("contract_transfers_v3 (last 100)")
    print(client.contract_transfers_v3(limit=100))

    banner("open_orders_v3")
    print(client.open_orders_v3())

    banner("history_orders_v3 USDT")
    print(client.history_orders_v3(token="USDT"))

    banner("funding_v3 (last 100)")
    print(client.funding_v3(limit=100))

    banner("historical_pnl_v3 (last 100)")
    print(client.historical_pnl_v3(limit=100))

    banner("yesterday_pnl_v3")
    print(client.yesterday_pnl_v3())

    banner("history_value_v3")
    print(client.history_value_v3())

    # Uncomment when you actually want to cancel open orders or change margin:
    # print(client.delete_open_orders_v3(symbol="BTC-USDT"))
    # print(client.set_initial_margin_rate_v3(symbol="BTC-USDT", initialMarginRate="0.05"))


if __name__ == "__main__":
    main()
