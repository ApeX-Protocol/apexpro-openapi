"""
Place perpetual orders on V3 — limit, conditional, market, position TP/SL,
and opening TP/SL bundles.

Each sample below is a self-contained example; they are independent and
you can run / comment them as you like. Sizes and prices are deliberately
small / out-of-the-money so the demo is safe on testnet.

Prerequisites (in .env):
    APEX_API_KEY / APEX_API_SECRET / APEX_API_PASSPHRASE
    APEX_ZK_SEEDS / APEX_ZK_L2KEY      (from 01_register_v3.py)

Run:
    python tests/04_create_order_v3.py
"""
import decimal

from _common import banner, make_signing_client
from apexomni.helpers.util import round_size


def _find_symbol(config_data, symbol):
    for entry in (config_data.get("contractConfig") or {}).get("perpetualContract", []):
        if entry.get("symbol") == symbol:
            return entry
    return {}


def _has_position(client, symbol):
    for pos in (client.accountV3 or {}).get("positions") or []:
        if pos.get("symbol") == symbol and pos.get("size") not in (None, "", "0", 0):
            return True
    return False


def main():
    client = make_signing_client()

    btc = _find_symbol(client.configV3, "BTC-USDT")
    eth = _find_symbol(client.configV3, "ETH-USDT")
    if not btc or not eth:
        raise SystemExit("BTC-USDT / ETH-USDT not found in configV3; check APEX_ENV")

    banner("sample 1 — limit BUY BTC-USDT")
    size = round_size("0.01", btc["stepSize"])
    price = round_size("20000", btc["tickSize"])
    print(client.create_order_v3(
        symbol="BTC-USDT", side="BUY", type="LIMIT",
        size=size, price=price,
    ))

    banner("sample 2 — STOP_LIMIT BUY ETH-USDT")
    print(client.create_order_v3(
        symbol="ETH-USDT", side="BUY", type="STOP_LIMIT",
        size="0.01", price="2000",
        triggerPriceType="INDEX", triggerPrice="1811",
    ))

    banner("sample 3 — MARKET SELL BTC-USDT (price acts as max slippage)")
    market_price = round_size("18000", btc["tickSize"])
    print(client.create_order_v3(
        symbol="BTC-USDT", side="SELL", type="MARKET",
        size="0.01", price=market_price,
    ))

    banner("sample 4 — position TAKE_PROFIT_MARKET (needs an open BTC-USDT position)")
    # reduceOnly=True targets an existing position; the API rejects it otherwise.
    # Skip cleanly on a fresh account instead of erroring out.
    if _has_position(client, "BTC-USDT"):
        print(client.create_order_v3(
            symbol="BTC-USDT", side="BUY", type="TAKE_PROFIT_MARKET",
            size="0.02", price="110000",
            isPositionTpsl=True, reduceOnly=True,
            triggerPrice="100000", triggerPriceType="INDEX",
        ))
    else:
        print("skipped — no open BTC-USDT position to reduce")

    banner("sample 5 — limit BUY with attached SL + TP")
    slippage = decimal.Decimal("-0.1")
    sl_price = decimal.Decimal("58000") * (decimal.Decimal("1") + slippage)
    tp_price = decimal.Decimal("79000") * (decimal.Decimal("1") - slippage)
    print(client.create_order_v3(
        symbol="BTC-USDT", side="BUY", type="LIMIT",
        size="0.01", price="65000",
        isOpenTpslOrder=True,
        isSetOpenSl=True, slPrice=sl_price, slSide="SELL", slSize="0.01", slTriggerPrice="58000",
        isSetOpenTp=True, tpPrice=tp_price, tpSide="SELL", tpSize="0.01", tpTriggerPrice="79000",
    ))


if __name__ == "__main__":
    main()
