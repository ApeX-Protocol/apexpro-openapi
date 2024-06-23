import os
import sys
import time

from apexpro.http_private_v3 import HttpPrivate_v3

root_path = os.path.abspath(__file__)
root_path = '/'.join(root_path.split('/')[:-2])
sys.path.append(root_path)

from apexpro.constants import APEX_OMNI_HTTP_MAIN, NETWORKID_OMNI_MAIN_ARB, NETWORKID_MAIN

print("Hello, Apex Omni")
priKey = "your eth private key"

client = HttpPrivate_v3(APEX_OMNI_HTTP_MAIN, network_id=NETWORKID_MAIN, eth_private_key=priKey)
configs = client.configs_v3()

zkKeys = client.derive_zk_key(client.default_address)
print(zkKeys)
print(zkKeys['seeds'])
print(zkKeys['l2Key'])
print(zkKeys['pubKeyHash'])

nonceRes = client.generate_nonce_v3(refresh="false", l2Key=zkKeys['l2Key'],ethAddress=client.default_address, chainId=NETWORKID_OMNI_MAIN_ARB)

regRes = client.register_user_v3(nonce=nonceRes['data']['nonce'],l2Key=zkKeys['l2Key'], seeds=zkKeys['seeds'],ethereum_address=client.default_address)

print(regRes['data']['apiKey']['key'])
print(regRes['data']['apiKey']['secret'])
print(regRes['data']['apiKey']['passphrase'])

time.sleep(10)
accountRes = client.get_account_v3()
print(accountRes)

#back zkKeys, apiKey,and accountId for private Api or create-order transfer or withdraw

print(regRes['data']['apiKey'])

changeRes = client.change_pub_key_v3(chainId=NETWORKID_OMNI_MAIN_ARB, seeds=zkKeys.get('seeds'), ethPrivateKey=priKey, zkAccountId = accountRes.get('spotAccount').get('zkAccountId'), subAccountId = accountRes.get('spotAccount').get('defaultSubAccountId'),
                                     newPkHash = zkKeys.get('pubKeyHash'),  nonce= accountRes.get('spotAccount').get('nonce'), l2Key= zkKeys.get('l2Key'))
print(changeRes)

time.sleep(10)
accountRes = client.get_account_v3()
print(accountRes)
print("end, Apexpro")

