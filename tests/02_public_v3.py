"""
Public market-data endpoints (no credentials required).

Demonstrates the read-only HTTP API: configs, klines, depth, recent trades,
ticker, and funding history.

Run:
    python tests/02_public_v3.py
"""
from _common import banner, make_public_client


def main():
    client = make_public_client()

    banner("configs_v3")
    print(client.configs_v3())

    banner("klines_v3 BTCUSDT 15m")
    print(client.klines_v3(symbol="BTCUSDT", interval="15"))

    banner("depth_v3 BTCUSDT")
    print(client.depth_v3(symbol="BTCUSDT"))

    banner("trades_v3 BTCUSDT")
    print(client.trades_v3(symbol="BTCUSDT"))

    banner("ticker_v3 BTCUSDT")
    print(client.ticker_v3(symbol="BTCUSDT"))

    banner("history_funding_v3 BTC-USDT")
    print(client.history_funding_v3(symbol="BTC-USDT"))


if __name__ == "__main__":
    main()
