from time import sleep

from apexpro.constants import APEX_OMNI_WS_MAIN
from apexpro.websocket_api import WebSocket

key = 'your apiKey-key from register V3'
secret = 'your apiKey-secret from register  V3'
passphrase = 'your apiKey-passphrase from register  V3'


# Connect with authentication!
# APEX_OMNI_WS_MAIN for mainnet, APEX_OMNI_WS_TEST for testnet
ws_client = WebSocket(
    endpoint=APEX_OMNI_WS_MAIN,
    api_key_credentials={'key': key, 'secret': secret, 'passphrase': passphrase},
)

def handle_account(message):
    print(message)
    contents_data = message["contents"]
    print(len(contents_data))

def h1(message):
    print(1, message)
def h2(message):
    print(2, message)
def h3(message):
    print(3, message)
def h4(message):
    print(4, message)

#ws_client.depth_stream(h1,'BTCUSDT',25)
#ws_client.ticker_stream(h2,'BTCUSDT')
ws_client.trade_stream(h3,'BTCUSDT')
ws_client.klines_stream(h4,'BTCUSDT',1)
ws_client.account_info_stream_v3(handle_account)


while True:
    # Run your main trading logic here.
    sleep(1)
