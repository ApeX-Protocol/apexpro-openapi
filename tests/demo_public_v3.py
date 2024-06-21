import os
import sys

root_path = os.path.abspath(__file__)
root_path = '/'.join(root_path.split('/')[:-2])
sys.path.append(root_path)


from apexpro.constants import APEX_OMNI_HTTP_MAIN
from apexpro.http_public import HttpPublic

print("Hello, ApexOmni")

# APEX_OMNI_HTTP_MAIN for mainnet, APEX_OMNI_HTTP_TEST for testnet
client = HttpPublic(APEX_OMNI_HTTP_MAIN)
print(client.klines_v3(symbol="ETHUSDT",interval=5,start=1718358480, end=1718950620, limit=5))
print(client.configs_v3())
print(client.depth_v3(symbol="BTCUSDT"))
print(client.trades_v3(symbol="BTCUSDT"))
print(client.klines_v3(symbol="BTCUSDT",interval="15"))
print(client.ticker_v3(symbol="BTCUSDT"))
print(client.history_funding_v3(symbol="BTC-USDT"))

