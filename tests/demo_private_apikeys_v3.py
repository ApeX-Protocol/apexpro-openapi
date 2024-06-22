import os
import sys

from apexpro.http_private_sign import HttpPrivateSign

root_path = os.path.abspath(__file__)
root_path = '/'.join(root_path.split('/')[:-2])
sys.path.append(root_path)

from apexpro.constants import NETWORKID_TEST, APEX_OMNI_HTTP_TEST

print("Hello, Apex Omni")
# need api_key_credentials={'key': key,'secret': secret, 'passphrase': passphrase} for private api

key = 'your apiKey-key from register V3'
secret = 'your apiKey-secret from register  V3'
passphrase = 'your apiKey-passphrase from register  V3'

seeds = 'your zk seeds from register'
l2Key = 'your l2Key seeds from register'

client = HttpPrivateSign(APEX_OMNI_HTTP_TEST, network_id=NETWORKID_TEST,
                         zk_seeds=seeds,zk_l2Key=l2Key,
                         api_key_credentials={'key': key, 'secret': secret, 'passphrase': passphrase})

configs = client.configs_v3()

userRes = client.get_user_v3()
print(userRes)

accountRes = client.get_account_v3()
print(accountRes)

allApikeys = client.all_apikeys_v3()
print(allApikeys)

nonceRes = client.generate_nonce_v3(refresh="true", l2Key=l2Key,ethAddress=client.default_address, chainId=NETWORKID_TEST)


generateRes = client.generate_api_key_v3(remark="test3",ips="127.0.0.1,127.0.0.2",nonce=nonceRes['data']['nonce'])
print(generateRes)

allApikeys = client.all_apikeys_v3()
print(allApikeys)

print("end, Apexpro")



