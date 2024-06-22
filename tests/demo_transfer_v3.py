import os
import sys

from apexpro.http_private_sign import HttpPrivateSign
import os
import sys

from apexpro.http_private_sign import HttpPrivateSign

root_path = os.path.abspath(__file__)
root_path = '/'.join(root_path.split('/')[:-2])
sys.path.append(root_path)

from apexpro.constants import NETWORKID_TEST, APEX_OMNI_HTTP_TEST

print("Hello, Apex Omni")

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

#smple5 contract contract_transfer_to_address
#createContractTransferRes = client.create_contract_transfer_to_address_v3(amount='1.1',asset='USDT',receiverAddress='0xfab6256aeef3be7805d3138be8fe1369f716ebc5',receiverAccountId='585750146675900485',receiverL2Key='0x04a234f299958150707451f649208fd085680bf3e1be432acb533eb2cc06082a')
#print(createContractTransferRes)


print("end, Apexpro")


