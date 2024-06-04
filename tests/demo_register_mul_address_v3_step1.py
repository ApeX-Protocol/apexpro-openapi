import os
import sys
import time
from threading import Timer

root_path = os.path.abspath(__file__)
root_path = '/'.join(root_path.split('/')[:-2])
sys.path.append(root_path)

from apexpro.http_private import HttpPrivate
from apexpro.constants import APEX_HTTP_TEST, NETWORKID_TEST, APEX_HTTP_MAIN, NETWORKID_MAIN, APEX_OMNI_HTTP_TEST

print("Hello, Apexpro")
priKey = "your eth private key"

client = HttpPrivate(APEX_OMNI_HTTP_TEST, network_id=NETWORKID_TEST, eth_private_key=priKey)
configs = client.configs_v3()

zkKeys = client.derive_zk_key(client.default_address)

nonceRes = client.generate_nonce_v3(refresh="false", l2Key=zkKeys['l2Key'],ethAddress=client.default_address, chainId=NETWORKID_TEST)

regRes = client.register_user_v3(nonce=nonceRes['data']['nonce'],l2Key=zkKeys['l2Key'], seeds=zkKeys['seeds'],ethereum_address=client.default_address,
                                 eth_mul_address="your mul eth address")
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

changeRes = client.change_pub_key_v3(chainId=11, seeds=zkKeys.get('seeds'), zkAccountId = accountRes.get('spotAccount').get('zkAccountId'), subAccountId = accountRes.get('spotAccount').get('defaultSubAccountId'),
                                     newPkHash = zkKeys.get('pubKeyHash'), feeToken="140", fee="0", nonce= accountRes.get('spotAccount').get('nonce'), l2Key= zkKeys.get('l2Key'), ethSignatureType='Onchain')
print(changeRes)
print("end, Apexpro")



