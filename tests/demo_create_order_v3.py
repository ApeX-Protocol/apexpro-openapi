import decimal
import os
import sys
import time

from apexpro.helpers.util import round_size
from apexpro.http_private_sign import HttpPrivateSign
from apexpro.http_private_stark_key_sign import HttpPrivateStark

root_path = os.path.abspath(__file__)
root_path = '/'.join(root_path.split('/')[:-2])
sys.path.append(root_path)

from apexpro.constants import APEX_HTTP_TEST, NETWORKID_TEST, APEX_HTTP_MAIN, NETWORKID_MAIN

print("Hello, Apexpro")

key = 'your apiKey-key from register'
secret = 'your apiKey-secret from register'
passphrase = 'your apiKey-passphrase from register'

seeds = 'your zk seeds from register'
l2Key = 'your l2Key seeds from register'


client = HttpPrivateSign(APEX_HTTP_TEST, network_id=NETWORKID_TEST,
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
#createTransferRes = client.create_transfer_out_v3(amount='1.1',asset='USDT')
#print(createTransferRes)

#smple4 contract transfer_out
currentTime = time.time()
createOrderRes = client.create_order_v3(symbol="BTC-USDT", side="SELL",
                                        type="MARKET", size="0.001", timestampSeconds= currentTime,
                                        price="60000")
print(createOrderRes)


print("end, Apexpro")


