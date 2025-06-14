import os
import sys

root_path = os.path.abspath(__file__)
root_path = '/'.join(root_path.split('/')[:-2])
sys.path.append(root_path)


from apexomni.constants import APEX_HTTP_TEST, APEX_HTTP_MAIN
from apexomni.http_public import HttpPublic

print("Hello, Apexpro")

client = HttpPublic(APEX_HTTP_MAIN)
#print(client.history_funding(symbol="BTC-USDC"))
print(client.klines(symbol="BTCUSDC",interval=60,start=1718683200, end=1718683200, limit=1))
print(client.server_time())
print(client.configs())
print(client.depth(symbol="BTC-USDC"))
print(client.trades(symbol="BTC-USDC"))
print(client.klines(symbol="BTC-USDC",interval="15"))
print(client.ticker(symbol="BTC-USDC"))
print(client.history_funding(symbol="BTC-USDC"))

print(client.depth(symbol="ETH-USDC",limit=50))
print(client.trades(symbol="ETH-USDC",limit=50))
print(client.klines(symbol="ETH-USDC",interval="15"))
print(client.history_funding(symbol="ETH-USDC",limit=100,page=0,beginTimeInclusive=1662348573000,endTimeExclusive=1662434973000))

