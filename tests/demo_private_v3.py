import os
import sys

from apexpro.http_private_v3 import HttpPrivate_v3

root_path = os.path.abspath(__file__)
root_path = '/'.join(root_path.split('/')[:-2])
sys.path.append(root_path)

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


print("end, Apexpro")



