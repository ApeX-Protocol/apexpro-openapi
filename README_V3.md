# apex omni

Official Python3 API connector for Apex omni's HTTP and WebSockets APIs.  
You can get Api information from 
[OpenApi-SDK](https://api-docs.pro.apex.exchange/#introduction)

## About
Put simply, `apex omni` is the official lightweight one-stop-shop module for the Apex omni HTTP and WebSocket APIs. 

## Development
`apex omni` is being actively developed, and new API changes should arrive on `apex omni` very quickly. `apex omni` uses `requests` and `websocket` for its methods, alongside other built-in modules. Anyone is welcome to branch/fork the repository and add their own upgrades. If you think you've made substantial improvements to the module, submit a pull request and we'll gladly take a look.    
If the user's computer using  arm chip,  change libzklink_sdk-arm.dylib to libzklink_sdk.dylib and replace old libzklink_sdk.dylib in the directory  ./apexpro/ and ./test/   
If the user's computer using  x86 chip,  change libzklink_sdk-x86.dylib to libzklink_sdk.dylib and replace old libzklink_sdk.dylib in the directory  ./apexpro/ and ./test/     

## New Basic Usage V3 
You can create an HTTP session for Inverse on APEX_OMNI_HTTP_TEST or APEX_OMNI_HTTP_MAIN:
```python
from apexpro.constants import APEX_OMNI_HTTP_TEST
from apexpro.http_public import HttpPublic

client = HttpPublic(APEX_OMNI_HTTP_TEST)
```
### Public endpoints V3

You can get no authentication information from public endpoints.  
Please refer to [demo_public_v3](https://github.com/ApeX-Protocol/apexpro-openapi/blob/main/tests/demo_public_v3.py)

The V3 version supports  USDT symbols. Users need to request the configs_v3() interface to obtain the configuration of symbols.
```python
client = HttpPublic(APEX_OMNI_HTTP_MAIN)
print(client.configs_v3())
print(client.klines_v3(symbol="ETHUSDT",interval=5,start=1718358480, end=1718950620, limit=5))
print(client.depth_v3(symbol="BTCUSDT"))
print(client.trades_v3(symbol="BTCUSDT"))
print(client.klines_v3(symbol="BTCUSDT",interval="15"))
print(client.ticker_v3(symbol="BTCUSDT"))
print(client.history_funding_v3(symbol="BTC-USDT"))
```

### Register OMNI method V3
- You can get zkKeys from client.derive_zk_key(), for regiter-user, create-order or transfer and withdraw.    
- If the user wants to trade OMNI's symbols, needs to call the register_user_v3() interface to register a OMNI account.   
- If the user has previously registered a pro apex account using the v1 or v2 interface, you also need to use the register_user_v3()   
    interface to register again.        
- You need to call client.configs_v3() after init client.      
- You can get apiKey and accountId for private Api    
- After call register_user_v3(), the user must call change_pub_key_v3() to complete register v3 account.   
- Since the register_user_v3  is a non-blocking process, you need to sleep for 10 sec before call the change_pub_key_v3() action.
Please refer to [demo_register_v3](https://github.com/ApeX-Protocol/apexpro-openapi/blob/main/tests/demo_register_v3.py)


```python
from apexpro.constants import APEX_OMNI_HTTP_MAIN, NETWORKID_OMNI_MAIN_ARB, NETWORKID_MAIN

print("Hello, Apex Omni")
priKey = "your eth private key"

client = HttpPrivate_v3(APEX_OMNI_HTTP_MAIN, network_id=NETWORKID_MAIN, eth_private_key=priKey)
configs = client.configs_v3()

zkKeys = client.derive_zk_key(client.default_address)
print(zkKeys)

nonceRes = client.generate_nonce_v3(refresh="false", l2Key=zkKeys['l2Key'],ethAddress=client.default_address, chainId=NETWORKID_OMNI_MAIN_ARB)

regRes = client.register_user_v3(nonce=nonceRes['data']['nonce'],l2Key=zkKeys['l2Key'], seeds=zkKeys['seeds'],ethereum_address=client.default_address)


key = regRes['data']['apiKey']['key']
secret = regRes['data']['apiKey']['secret']
passphrase = regRes['data']['apiKey']['passphrase']

time.sleep(10)
accountRes = client.get_account_v3()
print(accountRes)


#back zkKeys, apiKey,and accountId for private Api or create-oreder transfer or withdraw

print(regRes['data']['account']['id'])
print(regRes['data']['apiKey'])

changeRes = client.change_pub_key_v3(chainId=NETWORKID_OMNI_MAIN_ARB, seeds=zkKeys.get('seeds'), ethPrivateKey=priKey, zkAccountId = accountRes.get('spotAccount').get('zkAccountId'), subAccountId = accountRes.get('spotAccount').get('defaultSubAccountId'),
                                     newPkHash = zkKeys.get('pubKeyHash'),  nonce= accountRes.get('spotAccount').get('nonce'), l2Key= zkKeys.get('l2Key'))
print(changeRes)

time.sleep(10)
accountRes = client.get_account_v3()
print(accountRes)
```

### Private endpoints V3
Users need to request the configs_v3() and get_account_v3() interface to obtain the configuration of Account.   

some authentication information is required to access private endpoints.   
Please refer to [demo_private_v3](https://github.com/ApeX-Protocol/apexpro-openapi/blob/main/tests/demo_private_v3.py)

```python
from apexpro.constants import APEX_OMNI_HTTP_MAIN, \
    NETWORKID_OMNI_MAIN_ARB

print("Hello, Apex Omni")
# need api_key_credentials={'key': key,'secret': secret, 'passphrase': passphrase} for private api

key = 'your apiKey-key from register V3'
secret = 'your apiKey-secret from register  V3'
passphrase = 'your apiKey-passphrase from register  V3'

client = HttpPrivate_v3(APEX_OMNI_HTTP_MAIN, network_id=NETWORKID_OMNI_MAIN_ARB, api_key_credentials={'key': key,'secret': secret, 'passphrase': passphrase})
configs = client.configs_v3()

userRes = client.get_user_v3()
print(userRes)


accountRes = client.get_account_v3()
print(accountRes)

accountBalanceRes = client.get_account_balance_v3()
print(accountBalanceRes)

fillsRes = client.fills_v3(limit=100,page=0,symbol="BTC-USDT",side="BUY",token="USDT")
print(fillsRes)

transfersRes = client.transfers_v3(limit=100)
print(transfersRes)

transferRes = client.transfer_v3(ids='586213648326721628')
print(transferRes)

transfersRes = client.contract_transfers_v3(limit=100)
print(transfersRes)

transferRes = client.contract_transfer_v3(ids='588301879870489180')
print(transferRes)

#deleteOrderRes = client.delete_order_v3(id="588302655921587036")
#print(deleteOrderRes)

#deleteOrderRes = client.delete_order_by_client_order_id_v3(id="123456")
#print(deleteOrderRes)

openOrdersRes = client.open_orders_v3()
print(openOrdersRes)

deleteOrdersRes = client.delete_open_orders_v3(symbol="BTC-USDT",)
print(deleteOrdersRes)

historyOrdersRes = client.history_orders_v3(token='USDT')
print(historyOrdersRes)

getOrderRes = client.get_order_v3(id="123456")
print(getOrderRes)

getOrderRes = client.get_order_by_client_order_id_v3(id="123456")
print(getOrderRes)

fundingRes = client.funding_v3(limit=100)
print(fundingRes)

historicalPnlRes = client.historical_pnl_v3(limit=100)
print(historicalPnlRes)

yesterdayPnlRes = client.yesterday_pnl_v3()
print(yesterdayPnlRes)

historyValueRes = client.history_value_v3()
print(historyValueRes)

setInitialMarginRateRes = client.set_initial_margin_rate_v3(symbol="BTC-USDT",initialMarginRate="0.05")
print(setInitialMarginRateRes)

```

### zkKey sign withdraw or transfer method
Users need to request the configs_v3() and get_account_v3() interface to obtain the configuration of Account.    

Several endpoints require a seeds and l2Key signature authentication, namely as following:    
- create_withdrawal_v3()  to withdraw or fast withdraw
- create_transfer_out_v3()   to transfer asset from spot account to contract account   
- create_contract_transfer_out_v3()   to transfer asset from contract account to spot account    

Please refer to [demo_transfer_v3](https://github.com/ApeX-Protocol/apexpro-openapi/blob/main/tests/demo_transfer_v3.py)

```python
key = 'your apiKey-key from register'
secret = 'your apiKey-secret from register'
passphrase = 'your apiKey-passphrase from register'

seeds = 'your zk seeds from register'
l2Key = 'your l2Key seeds from register'

client = HttpPrivateSign(APEX_OMNI_HTTP_TEST, network_id=NETWORKID_TEST,
                          zk_seeds=seeds,zk_l2Key=l2Key,
                          api_key_credentials={'key': key, 'secret': secret, 'passphrase': passphrase})
configs = client.configs_v3()
accountData = client.get_account_v3()

#smple1 withdraw
#createWithdrawRes = client.create_withdrawal_v3(amount='3',asset='USDT', toChainId=3)
#print(createWithdrawRes)

#smple2 fast withdraw
#withdraw_feeRes = client.withdraw_fee_v3(amount="3",chainIds="3",tokenId='140')
#print(withdraw_feeRes)
#createWithdrawRes = client.create_withdrawal_v3(amount='3',asset='USDT', toChainId=3, fee=withdraw_feeRes.get('data').get('withdrawFeeAndPoolBalances')[0].get('fee'), isFastWithdraw=True)
#print(createWithdrawRes)

#smple3 transfer_out
#createTransferRes = client.create_transfer_out_v3(amount='3.4359738368',asset='USDT')
#print(createTransferRes)

#smple4 contract transfer_out
createContractTransferRes = client.create_contract_transfer_out_v3(amount='3.4359738368',asset='USDT')
print(createContractTransferRes)

```


### zkKey sign create order method
Users need to request the configs_v3() and get_account_v3() interface to obtain the configuration of Account.    
Several endpoints require a seeds and l2Key signature authentication, namely as following:    
- create_order_v3()  to create order

```python
from apexpro.constants import NETWORKID_TEST, APEX_OMNI_HTTP_TEST

print("Hello, Apex omni")

key = 'your apiKey-key from register'
secret = 'your apiKey-secret from register'
passphrase = 'your apiKey-passphrase from register'

seeds = 'your zk seeds from register'
l2Key = 'your l2Key seeds from register'


client = HttpPrivateSign(APEX_OMNI_HTTP_TEST, network_id=NETWORKID_TEST,
                          zk_seeds=seeds,zk_l2Key=l2Key,
                          api_key_credentials={'key': key, 'secret': secret, 'passphrase': passphrase})
configs = client.configs_v3()
accountData = client.get_account_v3()


currentTime = time.time()
createOrderRes = client.create_order_v3(symbol="BTC-USDT", side="SELL",
                                        type="MARKET", size="0.001", timestampSeconds= currentTime,
                                        price="60000")
print(createOrderRes)

# sample6
# Create a  TP/SL order
# first, Set a slippage to get an acceptable slPrice or tpPrice
#slippage is recommended to be greater than 0.1
# when buying, the price = price*(1 + slippage). when selling, the price = price*(1 - slippage)
slippage = decimal.Decimal("-0.1")
slPrice =  decimal.Decimal("58000") * (decimal.Decimal("1") + slippage)
tpPrice =  decimal.Decimal("79000") * (decimal.Decimal("1") - slippage)

createOrderRes = client.create_order_v3(symbol="BTC-USDT", side="BUY",
                                     type="LIMIT", size="0.01",
                                     price="65000",
                                     isOpenTpslOrder=True,
                                     isSetOpenSl=True,
                                     slPrice=slPrice,
                                     slSide="SELL",
                                     slSize="0.01",
                                     slTriggerPrice="58000",
                                     isSetOpenTp=True,
                                     tpPrice=tpPrice,
                                     tpSide="SELL",
                                     tpSize="0.01",
                                     tpTriggerPrice="79000",
                                     )
print(createOrderRes)

print("end, Apexpro")

```

### WebSocket
To see comprehensive examples of how to subscribe topics from websockets.
Please refer to [demo_ws_v3](https://github.com/ApeX-Protocol/apexpro-openapi/blob/main/tests/demo_ws_v3.py)


```python
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

