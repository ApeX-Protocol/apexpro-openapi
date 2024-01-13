from time import sleep

from apexpro.constants import APEX_WS_TEST, APEX_HTTP_TEST
from apexpro.http_public import HttpPublic
from apexpro.websocket_api import WebSocket

key = 'your apiKey-key from register'
secret = 'your apiKey-secret from register'
passphrase = 'your apiKey-passphrase from register'

# Connect with authentication!
ws_client = WebSocket(
    endpoint=APEX_WS_TEST,
    api_key_credentials={'key': key, 'secret': secret, 'passphrase': passphrase},
)
client = HttpPublic(APEX_HTTP_TEST)
symbol_list = client.configs().get("data").get("perpetualContract")
print("symbol_list:", symbol_list)

positions = {}
wallets = {}
orders = {}

def handle_account(message):
    print("all account: ", message)
    if message.get("contents") is not None and message.get("contents").get("positions") is not None:
        positions = message.get("contents").get("positions")
        print("positions: ", positions)

def h2(message):
    print("ticker: ", message)

#ws_client.depth_stream(h1,'BTCUSDC',25)
ws_client.ticker_stream(h2,'All')
#ws_client.trade_stream(h3,'BTCUSDC')
#ws_client.klines_stream(h4,'BTCUSDC',1)
ws_client.account_info_stream(handle_account)



while True:
    # Run your main trading logic here.
    sleep(1)
