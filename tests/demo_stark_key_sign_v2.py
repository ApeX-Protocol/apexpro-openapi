import os
import sys
import time

from apexpro.http_private_stark_key_sign import HttpPrivateStark

root_path = os.path.abspath(__file__)
root_path = '/'.join(root_path.split('/')[:-2])
sys.path.append(root_path)

from apexpro.constants import APEX_HTTP_TEST, NETWORKID_TEST, APEX_HTTP_MAIN, NETWORKID_MAIN

print("Hello, Apexpro")

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

#feeRes = client.uncommon_withdraw_fee_v2(amount='2',chainId='5', token='USDT',)
#print(feeRes)
#fastWithdrawRes = client.fast_withdrawal_v2(amount='2',expirationEpochSeconds= currentTime,asset='USDT',fee=feeRes['data']['fee'])

#createWithdrawRes = client.create_withdrawal_v2(amount='1',expirationEpochSeconds= currentTime,asset='USDT')
#print(createWithdrawRes)

historyOrdersRes = client.history_orders_v2(token="USDT")
print(historyOrdersRes)

orderFills = client.order_fills_v2(orderId='498441108374684453')
print(orderFills)

limitFeeRate = '0.0005'

deleteOrdersRes = client.delete_open_orders_v2(token="USDT")
print(deleteOrdersRes)
createOrderRes = client.create_order_v2(symbol="BTC-USDT", side="SELL",
                                           type="LIMIT", size="0.01",expirationEpochSeconds= currentTime,
                                           price="36890", limitFeeRate=limitFeeRate)


#print(createOrderRes)

fillsRes = client.fills_v2(limit=100,page=0,symbol="BTC-USDT",token="USDT")
print(fillsRes)


openOrderRes = client.open_orders_v2(token='USDT')
print(openOrderRes)


deleteOrdersRes = client.delete_open_orders_v2(token="USDT")
print(deleteOrdersRes)

historyOrdersRes = client.history_orders_v2(token="USDT")
print(historyOrdersRes)

openOrderRes = client.open_orders_v2(token='USDT')
print(openOrderRes)

feeRes = client.uncommon_withdraw_fee_v2(amount='2',chainId='97', token='USDT')
print(feeRes)
crossWithdrawRes = client.cross_chain_withdraw_v2(amount='2',expirationEpochSeconds= currentTime,asset='USDT',fee=feeRes['data']['fee'],chainId='97')
print(crossWithdrawRes)

print("end, Apexpro")
