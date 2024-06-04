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
configs = client.configs_v2()


zkKeys = client.derive_zk_key(client.default_address)

nonceRes = client.generate_nonce_v3(refresh="false", l2Key=zkKeys['l2Key'],ethAddress=client.default_address, chainId=NETWORKID_TEST)

#api_key = client.recover_api_key_credentials(nonce=nonceRes['data']['nonce'], ethereum_address=client.default_address)
#print(api_key)
regRes = client.register_user_v3(nonce=nonceRes['data']['nonce'],l2Key=zkKeys['l2Key'], seeds=zkKeys['seeds'],ethereum_address=client.default_address)
key = regRes['data']['apiKey']['key']
secret = regRes['data']['apiKey']['secret']
passphrase = regRes['data']['apiKey']['passphrase']

accountRes = client.get_account_v3()
print(accountRes)


#back stark_key_pair, apiKey,and accountId for private Api or create-oreder or withdraw
print(zkKeys)
print(regRes['data']['account']['id'])
print(regRes['data']['apiKey'])


print("end, Apexpro")

def handle_account():
    print("current time:", time.time())
    accountRes = client.get_account_v3()
    print(accountRes)
    if accountRes.get('spotAccount').get('zkAccountId') == '0':
        changeRes = client.change_pub_key_v3(chainId=3, ethPrivateKey=priKey, zkAccountId = accountRes.get('spotAccount').get('zkAccountId'), subAccountId = accountRes.get('spotAccount').get('defaultSubAccountId'),
                                             newPkHash = zkKeys.get('pubKeyHash'), feeToken="140", fee="0", nonce= accountRes.get('spotAccount').get('nonce'), l2Key= zkKeys.get('l2Key'))
        print(changeRes)
        timer.cancel()

while True:
    # Run your main trading logic here.
    time.sleep(2)
    timer = Timer(10, handle_account)
    timer.start()
    timer.join()
