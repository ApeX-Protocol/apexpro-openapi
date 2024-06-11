import os
import sys
import time

from apexpro.http_private_v3 import HttpPrivate_v3

root_path = os.path.abspath(__file__)
root_path = '/'.join(root_path.split('/')[:-2])
sys.path.append(root_path)

from apexpro.constants import NETWORKID_TEST, APEX_OMNI_HTTP_TEST

print("Hello, Apexpro")
priKey = "your eth private key"

client = HttpPrivate_v3(APEX_OMNI_HTTP_TEST, network_id=NETWORKID_TEST, eth_private_key=priKey)
configs = client.configs_v3()

zkKeys = client.derive_zk_key(client.default_address)
print(zkKeys)

nonceRes = client.generate_nonce_v3(refresh="false", l2Key=zkKeys['l2Key'],ethAddress=client.default_address, chainId=NETWORKID_TEST)

regRes = client.register_user_v3(nonce=nonceRes['data']['nonce'],l2Key=zkKeys['l2Key'], seeds=zkKeys['seeds'],ethereum_address=client.default_address)


key = regRes['data']['apiKey']['key']
secret = regRes['data']['apiKey']['secret']
passphrase = regRes['data']['apiKey']['passphrase']

time.sleep(5)
accountRes = client.get_account_v3()
print(accountRes)


#back stark_key_pair, apiKey,and accountId for private Api or create-oreder or withdraw

print(regRes['data']['account']['id'])
print(regRes['data']['apiKey'])

changeRes = client.change_pub_key_v3(chainId=3, seeds=zkKeys.get('seeds'), ethPrivateKey=priKey, zkAccountId = accountRes.get('spotAccount').get('zkAccountId'), subAccountId = accountRes.get('spotAccount').get('defaultSubAccountId'),
                                     newPkHash = zkKeys.get('pubKeyHash'), feeToken="140", fee="0", nonce= accountRes.get('spotAccount').get('nonce'), l2Key= zkKeys.get('l2Key'))
print(changeRes)

time.sleep(5)
accountRes = client.get_account_v3()
print(accountRes)
print("end, Apexpro")

