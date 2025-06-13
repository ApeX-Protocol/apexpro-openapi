# apexpro

Official Python3 API connector for Apexpro's HTTP and WebSockets APIs.  
You can get Api information from 
[OpenApi-SDK](https://api-docs.pro.apex.exchange/#introduction)

## About
Put simply, `apexpro`  is the official lightweight one-stop-shop module for the Apex pro HTTP and WebSocket APIs. 

## Development
`apexpro` is being actively developed, and new API changes should arrive on `apexpro` very quickly. `apexpro` uses `requests` and `websocket` for its methods, alongside other built-in modules. Anyone is welcome to branch/fork the repository and add their own upgrades. If you think you've made substantial improvements to the module, submit a pull request and we'll gladly take a look.

## Installation
`apexpro` requires Python 3.6.1 - Python 3.10.0 . The module can be installed manually or via [apexpro](https://pypi.org/project/apexpro/) with `pip`:
```
pip3 install apexpro
```

## New Basic Usage V2 
You can create an HTTP session for Inverse on APEX_HTTP_TEST or APEX_HTTP_MAIN:

```python
from apexomni.constants import APEX_HTTP_TEST
from apexomni.http_public import HttpPublic

client = HttpPublic(APEX_HTTP_TEST)
```
### Public endpoints V2

You can get no authentication information from public endpoints.  
Please refer to [demo_public_v2](https://github.com/ApeX-Protocol/apexpro-openapi/blob/main/tests/demo_public_v2.py)

The V2 version supports both USDT and USDC symbols. Users need to request the configs_v2() interface to obtain the configuration of symbols.

```python
from apexomni.constants import APEX_HTTP_TEST, APEX_HTTP_MAIN
from apexomni.http_public import HttpPublic

client = HttpPublic(APEX_HTTP_MAIN)
print(client.configs_v2())
print(client.history_funding_v2(symbol="BTC-USDT"))
print(client.klines(symbol="ETHUSDT", interval=5, start=1681463600, end=1681563600, limit=5))
print(client.server_time())
print(client.depth(symbol="BTC-USDC"))
print(client.trades(symbol="BTC-USDC"))
print(client.klines(symbol="BTC-USDT", interval="15"))
print(client.ticker(symbol="BTC-USDT"))
print(client.history_funding(symbol="BTC-USDT"))

print(client.depth(symbol="ETH-USDT", limit=50))
print(client.trades(symbol="ETH-USDT", limit=50))
print(client.klines(symbol="ETH-USDT", interval="15"))
print(client.history_funding_v2(symbol="ETH-USDT", limit=100, page=0, beginTimeInclusive=1662348573000,
                                endTimeExclusive=1662434973000))
```

### Register  method V2
If the user wants to trade USDT symbols, needs to call the register_user_v2() interface to register a USDT account, 
and fill in 'USDT' for the token parameter. In the same way, to trade USDC symbols, 
call the register_user_v2() interface to register a USDC account, and fill in 'USDC' as the token parameter. 
If the user has previously registered a USDC account using the v1 interface, there is no need to use the register_user_v2() 
interface to register again.      
You need to call client.configs_v2() after init client.   
You can get stark_key_pair, apiKey,and accountId for private Api , create-order and withdraw  
Please refer to [demo_register_v2](https://github.com/ApeX-Protocol/apexpro-openapi/blob/main/tests/demo_register_v2.py)

```python
from apexomni.http_private import HttpPrivate
from apexomni.constants import APEX_HTTP_TEST, NETWORKID_TEST, APEX_HTTP_MAIN, NETWORKID_MAIN

priKey = "your eth private key"

client = HttpPrivate(APEX_HTTP_TEST, network_id=NETWORKID_TEST, eth_private_key=priKey)
configs = client.configs_v2()

stark_key_pair_with_y_coordinate = client.derive_stark_key(client.default_address)
nonceRes = client.generate_nonce(starkKey=stark_key_pair_with_y_coordinate['public_key'],
                                 ethAddress=client.default_address, chainId=NETWORKID_TEST)

regRes = client.register_user_v2(token='USDT', nonce=nonceRes['data']['nonce'],
                                 starkKey=stark_key_pair_with_y_coordinate['public_key'],
                                 stark_public_key_y_coordinate=stark_key_pair_with_y_coordinate[
                                     'public_key_y_coordinate'], ethereum_address=client.default_address)
key = regRes['data']['apiKey']['key']
secret = regRes['data']['apiKey']['secret']
passphrase = regRes['data']['apiKey']['passphrase']

# back stark_key_pair, apiKey,and accountId for private Api or create-order or withdraw
print(stark_key_pair_with_y_coordinate)
print(regRes['data']['account']['positionId'])
print(regRes['data']['apiKey'])
```

### Private endpoints V2
The V2 version supports both USDT and USDC Account. Users need to request the configs_v2() and get_account_v2() interface to obtain the configuration of Account.

some authentication information is required to access private endpoints. 
Please refer to [demo_private](https://github.com/ApeX-Protocol/apexpro-openapi/blob/main/tests/demo_private.py)

```python
from apexomni.http_private import HttpPrivate
from apexomni.constants import APEX_HTTP_TEST, NETWORKID_TEST

# need apiKey={'key': key,'secret': secret, 'passphrase': passphrase} for private api

key = 'your apiKey-key from register'
secret = 'your apiKey-secret from register'
passphrase = 'your apiKey-passphrase from register'

client = HttpPrivate(APEX_HTTP_TEST, network_id=NETWORKID_TEST,
                     api_key_credentials={'key': key, 'secret': secret, 'passphrase': passphrase})
configs = client.configs_v2()

accountRes = client.get_account_v2()
print(accountRes)

fillsRes = client.fills_v2(limit=100, page=0, symbol="BTC-USDT", side="BUY", token="USDT")
print(fillsRes)

transfersRes = client.transfers_v2(limit=100, page=0, currencyId="USDT", chainIds="1,5,13,97")
print(transfersRes)

withdrawListRes = client.withdraw_list_v2(limit=100, page=0, beginTimeInclusive=1651406864000,
                                          endTimeExclusive=1657105971171)
print(withdrawListRes)

uncommon_withdraw_feeRes = client.uncommon_withdraw_fee_v2(amount="101000.1", token="USDT", chainId=5)
print(uncommon_withdraw_feeRes)

transfer_limitRes = client.transfer_limit_v2(currencyId="USDT")
print(transfer_limitRes)

fillsRes = client.fills_v2(limit=100, page=0, symbol="BTC-USDT", side="BUY", token="USDT")
print(fillsRes)

deleteOrderRes = client.delete_order_v2(id="123456")
print(deleteOrderRes)

deleteOrderRes = client.delete_order_by_client_order_id_v2(id="123456")
print(deleteOrderRes)

openOrdersRes = client.open_orders_v2(token='USDT')
print(openOrdersRes)

deleteOrdersRes = client.delete_open_orders_v2(symbol="BTC-USDC,ETH-USDC", token='USDT')
print(deleteOrdersRes)

historyOrdersRes = client.history_orders_v2(token='USDT')
print(historyOrdersRes)

getOrderRes = client.get_order_v2(id="123456")
print(getOrderRes)

getOrderRes = client.get_order_by_client_order_id_v2(id="123456")
print(getOrderRes)

fundingRes = client.funding_v2(limit=100, page=0, symbol="BTC-USDC", side="BUY", token='USDT')
print(fundingRes)

notifyListRes = client.notify_list(limit=100, page=0, unreadOnly="true", notifyCategory="1")
print(notifyListRes)

markNotifyReadRes = client.mark_notify_read(ids="113123,123123123")
print(markNotifyReadRes)

historicalPnlRes = client.historical_pnl_v2(limit=100, page=0, beginTimeInclusive=1651406864000,
                                            endTimeExclusive=1657105971171, symbol="BTC-USDC")
print(historicalPnlRes)

yesterdayPnlRes = client.yesterday_pnl_v2(token='USDT')
print(yesterdayPnlRes)

historyValueRes = client.history_value_v2(token='USDT')
print(historyValueRes)

markAllNotifyReadRes = client.mark_all_notify_read()
print(markAllNotifyReadRes)

setInitialMarginRateRes = client.set_initial_margin_rate_v2(symbol="BTC-USDC", initialMarginRate="0.1", token='USDT')
print(setInitialMarginRateRes)

```

### Stark key sign method
The V2 version supports both USDT and USDC Account. Users need to request the configs_v2() and get_account_v2() interface to obtain the configuration of Account.

Several endpoints require a starkKey signature authentication, namely as following:
- create-order
- withdraw

Please refer to [demo_stark_key_sign](https://github.com/ApeX-Protocol/apexpro-openapi/blob/main/tests/demo_stark_key_sign.py)

```python
import time
from apexomni.http_private_stark_key_sign import HttpPrivateStark

from apexomni.constants import APEX_HTTP_TEST, NETWORKID_TEST

# need api_key_credentials={'key': key,'secret': secret, 'passphrase': passphrase} for private api
# need starkey for withdraw and createOrder

key = 'your apiKey-key from register'
secret = 'your apiKey-secret from register'
passphrase = 'your apiKey-passphrase from register'

public_key = 'your stark_public_key from register'
public_key_y_coordinate = 'your stark_public_key_y_coordinate from register'
private_key = 'your stark_private_key from register'

client = HttpPrivateStark(APEX_HTTP_TEST, network_id=NETWORKID_TEST,
                          stark_public_key=public_key,
                          stark_private_key=private_key,
                          stark_public_key_y_coordinate=public_key_y_coordinate,
                          api_key_credentials={'key': key, 'secret': secret, 'passphrase': passphrase})
configs = client.configs_v2()
client.get_user()
print(client.get_account_v2())

print(client.get_account_balance_v2())

currentTime = time.time()

# feeRes = client.uncommon_withdraw_fee_v2(amount='2',chainId='5', token='USDT',)
# print(feeRes)
# fastWithdrawRes = client.fast_withdrawal_v2(amount='2',expirationEpochSeconds= currentTime,asset='USDT',fee=feeRes['data']['fee'])

# createWithdrawRes = client.create_withdrawal_v2(amount='1',expirationEpochSeconds= currentTime,asset='USDT')
# print(createWithdrawRes)

historyOrdersRes = client.history_orders_v2(token="USDT")
print(historyOrdersRes)

orderFills = client.order_fills_v2(orderId='498441108374684453')
print(orderFills)

limitFeeRate = '0.0005'

deleteOrdersRes = client.delete_open_orders_v2(token="USDT")
print(deleteOrdersRes)

createOrderRes = client.create_order_v2(symbol="BTC-USDT", side="SELL",
                                        type="LIMIT", size="0.01", expirationEpochSeconds=currentTime,
                                        price="36890", limitFeeRate=limitFeeRate, timeInForce="POST_ONLY")

# print(createOrderRes)

fillsRes = client.fills_v2(limit=100, page=0, symbol="BTC-USDT", token="USDT")
print(fillsRes)

openOrderRes = client.open_orders_v2(token='USDT')
print(openOrderRes)

deleteOrdersRes = client.delete_open_orders_v2(token="USDT")
print(deleteOrdersRes)

historyOrdersRes = client.history_orders_v2(token="USDT")
print(historyOrdersRes)

openOrderRes = client.open_orders_v2(token='USDT')
print(openOrderRes)

feeRes = client.uncommon_withdraw_fee_v2(amount='2', chainId='97', token='USDT')
print(feeRes)
crossWithdrawRes = client.cross_chain_withdraw_v2(amount='2', expirationEpochSeconds=currentTime, asset='USDT',
                                                  fee=feeRes['data']['fee'], chainId='97')
print(crossWithdrawRes)

```

### WebSocket
To see comprehensive examples of how to subscribe topics from websockets.
Please refer to [demo_ws](https://github.com/ApeX-Protocol/apexpro-openapi/blob/main/tests/demo_ws.py)

```python
from time import sleep

from apexomni.constants import APEX_WS_TEST
from apexomni.websocket_api import WebSocket

key = 'your apiKey-key from register'
secret = 'your apiKey-secret from register'
passphrase = 'your apiKey-passphrase from register'

# Connect with authentication!
ws_client = WebSocket(
    endpoint=APEX_WS_TEST,
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


#ws_client.depth_stream(h1,'BTCUSDC',25)
#ws_client.ticker_stream(h2,'BTCUSDC')
#ws_client.trade_stream(h3,'BTCUSDC')
#ws_client.klines_stream(h4,'BTCUSDC',1)
ws_client.account_info_stream(handle_account)

while True:
    # Run your main trading logic here.
    sleep(1)

```


## Old Basic Usage V1
You can create an HTTP session for Inverse on APEX_HTTP_TEST or APEX_HTTP_MAIN:

```python
from apexomni.constants import APEX_HTTP_TEST
from apexomni.http_public import HttpPublic

client = HttpPublic(APEX_HTTP_TEST)
```
### Public endpoints
You can get no authentication information from public endpoints.  
Please refer to [demo_public](https://github.com/ApeX-Protocol/apexpro-openapi/blob/main/tests/demo_public.py)

```python
from apexomni.constants import APEX_HTTP_TEST
from apexomni.http_public import HttpPublic

client = HttpPublic(APEX_HTTP_TEST)
print(client.server_time())
print(client.configs())
print(client.ticker(symbol="BTC-USDC"))
print(client.history_funding(symbol="BTC-USDC"))
print(client.depth(symbol="ETH-USDC", limit=100))
print(client.trades(symbol="ETH-USDC", limit=100))
print(client.klines(symbol="ETH-USDC", interval="15"))
print(client.history_funding(symbol="ETH-USDC", limit=100, page=0, beginTimeInclusive=1662348573000,
                             endTimeExclusive=1662434973000))
```

### Register  method
You can get stark_key_pair, apiKey,and accountId for private Api , create-order and withdraw  
Please refer to [demo_register](https://github.com/ApeX-Protocol/apexpro-openapi/blob/main/tests/demo_register.py)

```python
from apexomni.http_private import HttpPrivate
from apexomni.constants import APEX_HTTP_TEST, NETWORKID_TEST, APEX_HTTP_MAIN, NETWORKID_MAIN

priKey = "your eth private key"

client = HttpPrivate(APEX_HTTP_TEST, network_id=NETWORKID_TEST, eth_private_key=priKey)
configs = client.configs()

stark_key_pair_with_y_coordinate = client.derive_stark_key(client.default_address)
nonceRes = client.generate_nonce(starkKey=stark_key_pair_with_y_coordinate['public_key'],
                                 ethAddress=client.default_address, chainId=NETWORKID_TEST)

regRes = client.register_user(nonce=nonceRes['data']['nonce'], starkKey=stark_key_pair_with_y_coordinate['public_key'],
                              stark_public_key_y_coordinate=stark_key_pair_with_y_coordinate['public_key_y_coordinate'],
                              ethereum_address=client.default_address)
key = regRes['data']['apiKey']['key']
secret = regRes['data']['apiKey']['secret']
passphrase = regRes['data']['apiKey']['passphrase']

#back stark_key_pair, apiKey,and accountId for private Api or create-order or withdraw
print(stark_key_pair_with_y_coordinate)
print(regRes['data']['account']['positionId'])
print(regRes['data']['apiKey'])
```

### Private endpoints
some authentication information is required to access private endpoints. 
Please refer to [demo_private](https://github.com/ApeX-Protocol/apexpro-openapi/blob/main/tests/demo_private.py)

```python
from apexomni.http_private import HttpPrivate
from apexomni.constants import APEX_HTTP_TEST, NETWORKID_TEST

# need apiKey={'key': key,'secret': secret, 'passphrase': passphrase} for private api

key = 'your apiKey-key from register'
secret = 'your apiKey-secret from register'
passphrase = 'your apiKey-passphrase from register'

client = HttpPrivate(APEX_HTTP_TEST, network_id=NETWORKID_TEST,
                     api_key_credentials={'key': key, 'secret': secret, 'passphrase': passphrase})
configs = client.configs()

userRes = client.get_user()
print(userRes)

modifyUserRes = client.modify_user(username="pythonTest", email="11@aa.com", emailNotifyGeneralEnable="false")
print(modifyUserRes)

accountRes = client.get_account()
print(accountRes)

openOrdersRes = client.open_orders()
print(openOrdersRes)

historyOrdersRes = client.history_orders()
print(historyOrdersRes)

fundingRes = client.funding(limit=100, page=0, symbol="BTC-USDC", side="BUY")
print(fundingRes)

notifyListRes = client.notify_list(limit=100, page=0, unreadOnly="true", notifyCategory="1")
print(notifyListRes)

...
```

### Stark key sign method
Several endpoints require a starkKey signature authentication, namely as following:
- create-order
- withdraw

Please refer to [demo_stark_key_sign](https://github.com/ApeX-Protocol/apexpro-openapi/blob/main/tests/demo_stark_key_sign.py)

```python
import time
from apexomni.http_private_stark_key_sign import HttpPrivateStark

from apexomni.constants import APEX_HTTP_TEST, NETWORKID_TEST

# need api_key_credentials={'key': key,'secret': secret, 'passphrase': passphrase} for private api
# need starkey for withdraw and createOrder

key = 'your apiKey-key from register'
secret = 'your apiKey-secret from register'
passphrase = 'your apiKey-passphrase from register'

public_key = 'your stark_public_key from register'
public_key_y_coordinate = 'your stark_public_key_y_coordinate from register'
private_key = 'your stark_private_key from register'

client = HttpPrivateStark(APEX_HTTP_TEST, network_id=NETWORKID_TEST,
                          stark_public_key=public_key,
                          stark_private_key=private_key,
                          stark_public_key_y_coordinate=public_key_y_coordinate,
                          api_key_credentials={'key': key, 'secret': secret, 'passphrase': passphrase})
configs = client.configs()
client.get_user()
client.get_account()

currentTime = time.time()

limitFeeRate = client.account['takerFeeRate']
createOrderRes = client.create_order(symbol="BTC-USDC", side="BUY",
                                     type="LIMIT", size="0.01",
                                     price="1991", limitFeeRate=limitFeeRate,
                                     accountId=client.account['positionId'],
                                     expirationEpochSeconds=currentTime)
print(createOrderRes)

worstPrice = client.get_worst_price(symbol="BTC-USDC", side="SELL", size="0.1")
price = worstPrice['data']['worstPrice']
##market order price must not none
createOrderRes = client.create_order(symbol="BTC-USDC", side="SELL",
                                     type="MARKET", size="1", price=price, limitFee=limitFee,
                                     expirationEpochSeconds=currentTime)
print(createOrderRes)

#createWithdrawRes = client.create_withdrawal(amount='1001',expirationEpochSeconds= currentTime,asset='USDC')
#print(createWithdrawRes)

#feeRes = client.uncommon_withdraw_fee(amount='1002',chainId='5')
#print(feeRes)
#fastWithdrawRes = client.fast_withdrawal(amount='1002',expirationEpochSeconds= currentTime,asset='USDC',fee=feeRes['data']['fee'])
#print(fastWithdrawRes)

deleteOrderRes = client.delete_open_orders(symbol="BTC-USDC")
print(deleteOrderRes)

deleteOrderRes = client.delete_open_orders()
print(deleteOrderRes)

feeRes = client.uncommon_withdraw_fee(amount='1003', chainId='97')
print(feeRes)
crossWithdrawRes = client.cross_chain_withdraw(amount='1003', expirationEpochSeconds=currentTime, asset='USDC',
                                               fee=feeRes['data']['fee'], chainId='97')
print(crossWithdrawRes)

```

### WebSocket
To see comprehensive examples of how to subscribe topics from websockets.
Please refer to [demo_ws](https://github.com/ApeX-Protocol/apexpro-openapi/blob/main/tests/demo_ws.py)

```python
from time import sleep

from apexomni.constants import APEX_WS_TEST
from apexomni.websocket_api import WebSocket

key = 'your apiKey-key from register'
secret = 'your apiKey-secret from register'
passphrase = 'your apiKey-passphrase from register'

# Connect with authentication!
ws_client = WebSocket(
    endpoint=APEX_WS_TEST,
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


#ws_client.depth_stream(h1,'BTCUSDC',25)
#ws_client.ticker_stream(h2,'BTCUSDC')
#ws_client.trade_stream(h3,'BTCUSDC')
#ws_client.klines_stream(h4,'BTCUSDC',1)
ws_client.account_info_stream(handle_account)

while True:
    # Run your main trading logic here.
    sleep(1)

```
