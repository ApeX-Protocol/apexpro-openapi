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



client = HttpPrivateStark(APEX_HTTP_MAIN, network_id=NETWORKID_MAIN,
                          stark_public_key=public_key,
                          stark_private_key=private_key,
                          stark_public_key_y_coordinate=public_key_y_coordinate,
                          api_key_credentials={'key': key, 'secret': secret, 'passphrase': passphrase})
configs = client.configs()
#client.get_user()
print(client.get_account())

currentTime = time.time()

limitFee = client.account['takerFeeRate']
createOrderRes = client.create_order(symbol="ATOM-USDC", side="BUY",
                                           type="LIMIT", size="1",
                                           price="9.1", limitFee=limitFee,
                                     accountId=client.account['positionId'],
                                    expirationEpochSeconds= currentTime)
print(createOrderRes)



worstPrice = client.get_worst_price(symbol="BTC-USDC", side="SELL", size="0.1")
price = worstPrice['data']['worstPrice']
##market order price must not none
createOrderRes = client.create_order(symbol="BTC-USDC", side="SELL",
                                     type="MARKET", size="1", price=price, limitFee=limitFee,
                                     expirationEpochSeconds= currentTime )
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


feeRes = client.uncommon_withdraw_fee(amount='1003',chainId='97')
print(feeRes)
crossWithdrawRes = client.cross_chain_withdraw(amount='1003',expirationEpochSeconds= currentTime,asset='USDC',fee=feeRes['data']['fee'],chainId='97')
print(crossWithdrawRes)

print("end, Apexpro")
