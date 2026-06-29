"""
Stream V3 account, trade, and kline updates via WebSocket.

Subscribes to account_info, trade, and 1-minute kline channels for BTCUSDT
and prints incoming messages. Stops on Ctrl-C.

Prerequisites (in .env):
    APEX_API_KEY / APEX_API_SECRET / APEX_API_PASSPHRASE

Run:
    python tests/20_ws_account_v3.py
"""
from time import sleep

from _common import banner, env_ws_endpoint, require
from apexomni.websocket_api import WebSocket


def main():
    ws = WebSocket(
        endpoint=env_ws_endpoint(),
        api_key_credentials={
            "key":        require("APEX_API_KEY"),
            "secret":     require("APEX_API_SECRET"),
            "passphrase": require("APEX_API_PASSPHRASE"),
        },
    )

    def on_account(msg):
        contents = msg.get("contents", {})
        print(f"[account] {len(contents) if hasattr(contents, '__len__') else '?'} updates")

    def on_trade(msg):
        print("[trade]", msg)

    def on_klines(msg):
        print("[klines]", msg)

    banner("subscribing to account / trade / klines streams")
    ws.trade_stream(on_trade, "BTCUSDT")
    ws.klines_stream(on_klines, "BTCUSDT", 1)
    ws.account_info_stream_v3(on_account)

    banner("streaming — Ctrl-C to stop")
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("stopped")


if __name__ == "__main__":
    main()
