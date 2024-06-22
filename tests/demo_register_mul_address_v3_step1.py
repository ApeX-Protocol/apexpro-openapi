import os
import sys
import time

from apexpro.http_private_v3 import HttpPrivate_v3

root_path = os.path.abspath(__file__)
root_path = '/'.join(root_path.split('/')[:-2])
sys.path.append(root_path)

from apexpro.constants import APEX_OMNI_HTTP_MAIN, NETWORKID_OMNI_MAIN_ARB

print("Hello, Apex Omni")
priKey = "your eth private key"

client = HttpPrivate_v3(APEX_OMNI_HTTP_MAIN, network_id=NETWORKID_OMNI_MAIN_ARB, eth_private_key=priKey)
configs = client.configs_v3()

zkKeys = client.derive_zk_key(client.default_address)

nonceRes = client.generate_nonce_v3(refresh="false", l2Key=zkKeys['l2Key'],ethAddress=client.default_address, chainId=NETWORKID_OMNI_MAIN_ARB)

regRes = client.register_user_v3(nonce=nonceRes['data']['nonce'],l2Key=zkKeys['l2Key'], seeds=zkKeys['seeds'],ethereum_address=client.default_address,
                                 eth_mul_address="your mul eth address", isLpAccount=True)
print(regRes)
key = regRes['data']['apiKey']['key']
secret = regRes['data']['apiKey']['secret']
passphrase = regRes['data']['apiKey']['passphrase']

time.sleep(10)
accountRes = client.get_account_v3()
print(accountRes)

#back stark_key_pair, apiKey,and accountId for private Api or create-oreder or withdraw

seeds = zkKeys.get('seeds')
l2Key = zkKeys.get('l2Key')
pubKeyHash = zkKeys.get('pubKeyHash')

#back zkKeys, seeds, l2Key and pubKeyHash for register_step2
print(zkKeys)
print(regRes['data']['account']['id'])
print(regRes['data']['apiKey'])

print("end, Apexpro")



